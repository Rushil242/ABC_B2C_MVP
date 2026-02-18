
import React, { createContext, useContext, useState, useEffect, useRef } from "react";
import { api } from "@/api/client";
import { toast } from "sonner";

interface SyncStatus {
    status: "idle" | "starting" | "running" | "completed" | "failed";
    step?: string;
    message?: string;
    timestamp?: number;
}

interface SyncContextType {
    isSyncing: boolean;
    syncStatus: SyncStatus | null;
    startSync: (password: string) => Promise<void>;
}

const SyncContext = createContext<SyncContextType | undefined>(undefined);

export const SyncProvider = ({ children }: { children: React.ReactNode }) => {
    const [isSyncing, setIsSyncing] = useState(false);
    const [syncStatus, setSyncStatus] = useState<SyncStatus | null>(null);
    const pollingRef = useRef<NodeJS.Timeout | null>(null);

    const checkStatus = async () => {
        try {
            const status = await api.getSyncStatus();
            setSyncStatus(status);

            if (status.status === "running" || status.status === "starting") {
                setIsSyncing(true);
            } else if (status.status === "completed" || status.status === "failed") {
                setIsSyncing(false);
                if (pollingRef.current) {
                    clearInterval(pollingRef.current);
                    pollingRef.current = null;
                }
                if (status.status === "completed") {
                    toast.success("Sync Completed Successfully: " + status.message);
                } else {
                    toast.error("Sync Failed: " + status.message);
                }
            } else {
                setIsSyncing(false);
                if (pollingRef.current) {
                    clearInterval(pollingRef.current);
                    pollingRef.current = null;
                }
            }
        } catch (e) {
            console.error("Failed to poll sync status", e);
            setIsSyncing(false);
        }
    };

    const startSync = async (password: string) => {
        setIsSyncing(true);
        setSyncStatus({ status: "starting", message: "Initializing...", step: "Start" });

        try {
            await api.triggerAllSync(password);
            // Start polling
            if (pollingRef.current) clearInterval(pollingRef.current);
            pollingRef.current = setInterval(checkStatus, 2000);
        } catch (error: any) {
            setIsSyncing(false);
            console.error("Sync failed to start", error);
            toast.error("Failed to start sync: " + (error.response?.data?.detail || error.message));
        }
    };

    // Check status on mount in case a sync is already running from a reload/page nav
    useEffect(() => {
        checkStatus();
        return () => {
            if (pollingRef.current) clearInterval(pollingRef.current);
        };
    }, []);

    return (
        <SyncContext.Provider value={{ isSyncing, syncStatus, startSync }}>
            {children}
        </SyncContext.Provider>
    );
};

export const useSync = () => {
    const context = useContext(SyncContext);
    if (context === undefined) {
        throw new Error("useSync must be used within a SyncProvider");
    }
    return context;
};
