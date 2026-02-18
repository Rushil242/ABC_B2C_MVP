
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { User, MapPin, Phone, Mail, Briefcase, Shield, RefreshCw, Loader2, FileText, Download, AlertCircle, CheckCircle, ChevronDown, ChevronUp, Lock } from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { api } from "@/api/client";
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useSync } from "@/context/SyncContext";

const Profile = () => {
  const [profileData, setProfileData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [isSyncDialogOpen, setIsSyncDialogOpen] = useState(false);
  const [itrPassword, setItrPassword] = useState("");
  const [activeSync, setActiveSync] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Global Sync Context
  const { isSyncing, syncStatus, startSync } = useSync();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await api.getProfile();
        let calculatedAge = "N/A";
        if (data.personal_info.dob && data.personal_info.dob !== "N/A") {
          const dobDate = new Date(data.personal_info.dob);
          const today = new Date();
          let age = today.getFullYear() - dobDate.getFullYear();
          const monthDiff = today.getMonth() - dobDate.getMonth();
          if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dobDate.getDate())) age--;
          calculatedAge = age.toString();
        }

        setProfileData({
          fullName: data.personal_info.name,
          pan: data.personal_info.pan,
          dob: data.personal_info.dob || "N/A",
          age: calculatedAge,
          address: data.address,
          phone: data.phone,
          email: data.personal_info.email,
          sourcesOfIncome: ["Salary", "House Property", "Other Sources"],
          aoDetails: data.ao_details
        });
      } catch (error) {
        console.error("Failed to fetch profile", error);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();

    const cachedPwd = sessionStorage.getItem("itr_password");
    if (cachedPwd) {
      setItrPassword(cachedPwd);
    }
  }, []);

  // Sync local active state with global context
  useEffect(() => {
    if (isSyncing) {
      setActiveSync("ALL");
    } else if (activeSync === "ALL" && !isSyncing) {
      setActiveSync(null);
    }
  }, [isSyncing]);

  const handleSync = async (type: string) => {
    const pwdToUse = itrPassword || sessionStorage.getItem("itr_password");

    if (!pwdToUse) {
      toast.error("Please enter your ITR password");
      return;
    }

    if (type === "ALL") {
      setActiveSync("ALL");
      // Use global context to start sync (updates Navbar too)
      await startSync(pwdToUse);
      // Note: Context handles successful toast
    } else {
      // Individual syncs (not yet in global context for simplicity)
      setActiveSync(type);
      try {
        if (type === "ITR") {
          await api.triggerITRSync(pwdToUse);
          toast.success("ITR Sync started!");
        } else if (type === "AIS") {
          await api.triggerAISSync(pwdToUse);
          toast.success("AIS Sync started!");
        } else if (type === "26AS") {
          await api.trigger26ASSync(pwdToUse);
          toast.success("Form 26AS Download started!");
        } else if (type === "Notices") {
          await api.triggerNoticesSync(pwdToUse);
          toast.success("Notices Sync started!");
        } else if (type === "Verify") {
          await api.verifyCredentials(pwdToUse);
          toast.success("Verifying credentials...");
        }
      } catch (error: any) {
        console.error("Sync failed:", error);
        toast.error(error.response?.data?.detail || "Failed to trigger sync");
      } finally {
        setActiveSync(null);
      }
    }
  };

  if (loading) return <div className="flex h-screen items-center justify-center dark bg-background text-foreground"><Loader2 className="animate-spin text-gold h-8 w-8" /></div>;
  if (!profileData) return <div className="flex h-screen items-center justify-center dark bg-background text-foreground">Failed to load profile.</div>;

  return (
    <div className="dark min-h-screen bg-background text-foreground">
      <Navbar isLoggedIn />

      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4"
        >
          <div>
            <h1 className="font-display text-3xl font-bold">
              <span className="gold-text-gradient">Profile</span>
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Your personal and tax-related details
            </p>
          </div>

          <Button
            onClick={() => setIsSyncDialogOpen(true)}
            size="lg"
            className="bg-gold hover:bg-gold-dark text-primary-foreground font-semibold shadow-lg shadow-gold/20 transition-all hover:scale-105"
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            Sync Data
          </Button>
        </motion.div>

        {/* Profile Grid (Same as before) */}
        <div className="grid gap-6 md:grid-cols-2">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="rounded-2xl border border-border bg-card p-6 gold-glow relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-10"><User className="h-24 w-24 text-gold" /></div>
            <div className="flex items-center gap-2 mb-5 relative z-10">
              <User className="h-5 w-5 text-gold" />
              <h2 className="font-display text-lg font-semibold">Personal Information</h2>
            </div>
            <div className="space-y-4 relative z-10">
              <InfoRow label="Full Name" value={profileData.fullName} />
              <InfoRow label="PAN" value={profileData.pan} highlight />
              <InfoRow label="Date of Birth" value={profileData.dob} />
              <InfoRow label="Age" value={`${profileData.age} years`} />
            </div>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="rounded-2xl border border-border bg-card p-6">
            <div className="flex items-center gap-2 mb-5">
              <Mail className="h-5 w-5 text-gold" />
              <h2 className="font-display text-lg font-semibold">Contact Details</h2>
            </div>
            <div className="space-y-4">
              <InfoRow label="Email" value={profileData.email} />
              <InfoRow label="Phone" value={profileData.phone} />
              <InfoRow label="Address" value={profileData.address} />
            </div>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="rounded-2xl border border-border bg-card p-6">
            <div className="flex items-center gap-2 mb-5">
              <Briefcase className="h-5 w-5 text-gold" />
              <h2 className="font-display text-lg font-semibold">Sources of Income</h2>
            </div>
            <div className="flex flex-wrap gap-2">
              {profileData.sourcesOfIncome.map((source: string) => (
                <span key={source} className="rounded-full border border-border bg-secondary px-3 py-1.5 text-xs font-medium">{source}</span>
              ))}
            </div>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="rounded-2xl border border-border bg-card p-6">
            <div className="flex items-center gap-2 mb-5">
              <Shield className="h-5 w-5 text-gold" />
              <h2 className="font-display text-lg font-semibold">AO Details</h2>
            </div>
            <div className="space-y-4">
              <InfoRow label="AO Code" value={profileData.aoDetails.aoCode} highlight />
              <InfoRow label="AO Type" value={profileData.aoDetails.aoType} />
              <InfoRow label="City" value={profileData.aoDetails.city} />
            </div>
          </motion.div>
        </div>
      </div>

      <Footer />

      {/* Modern Sync Dialog */}
      <Dialog open={isSyncDialogOpen} onOpenChange={setIsSyncDialogOpen}>
        <DialogContent className="sm:max-w-md bg-card border border-gold/20 p-0 overflow-hidden shadow-2xl shadow-black/50">
          <div className="bg-gradient-gold h-2 w-full" />

          <div className="p-6">
            <div className="flex flex-col items-center justify-center mb-6 text-center">
              <div className="h-12 w-12 rounded-full bg-gold/10 flex items-center justify-center mb-4">
                <RefreshCw className={`h-6 w-6 text-gold ${activeSync ? 'animate-spin' : ''}`} />
              </div>
              <h2 className="font-display text-2xl font-bold text-foreground">Sync Center</h2>
              {activeSync === "ALL" && syncStatus && isSyncing ? (
                <div className="mt-4 w-full bg-secondary/50 rounded-lg p-3">
                  <p className="text-sm font-semibold text-gold mb-1">{syncStatus.step}</p>
                  <p className="text-xs text-muted-foreground">{syncStatus.message}</p>
                  <div className="w-full bg-background h-1.5 rounded-full mt-2 overflow-hidden">
                    <motion.div
                      className="bg-gold h-full"
                      initial={{ width: "0%" }}
                      animate={{
                        width: syncStatus.step === "Verify" ? "20%" :
                          syncStatus.step === "ITR" ? "40%" :
                            syncStatus.step === "AIS" ? "60%" :
                              syncStatus.step === "26AS" ? "80%" :
                                syncStatus.step === "Complete" ? "100%" : "10%"
                      }}
                    />
                  </div>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground mt-1 max-w-xs">
                  Connect securely to the Income Tax Portal to fetch your latest financial data.
                </p>
              )}
            </div>

            <div className="space-y-5">
              <div className="space-y-2">
                <Label htmlFor="itr-password" className="text-xs uppercase tracking-wider text-gold font-semibold ml-1">ITR Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="itr-password"
                    type="password"
                    placeholder="Enter your ITR Password"
                    value={itrPassword}
                    onChange={(e) => setItrPassword(e.target.value)}
                    className="bg-secondary/50 border-border focus:border-gold pl-9 py-5"
                  />
                </div>
              </div>

              <div className="pt-2">
                <Button
                  onClick={() => handleSync("ALL")}
                  disabled={activeSync !== null}
                  className="w-full bg-gold hover:bg-gold-dark text-black font-bold h-12 shadow-lg shadow-gold/20"
                >
                  {activeSync === "ALL" ? (
                    <><Loader2 className="mr-2 h-5 w-5 animate-spin" /> Syncing in Progress...</>
                  ) : (
                    "Start Full Sync"
                  )}
                </Button>
              </div>

              {/* Advanced Options Toggle */}
              <div className="border-t border-border pt-4">
                <button
                  onClick={() => setShowAdvanced(!showAdvanced)}
                  className="flex items-center justify-center w-full text-xs text-muted-foreground hover:text-gold transition-colors gap-1"
                >
                  {showAdvanced ? "Hide Advanced Options" : "Show Advanced Options"}
                  {showAdvanced ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                </button>

                <AnimatePresence>
                  {showAdvanced && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="grid grid-cols-2 gap-3 mt-4 overflow-hidden"
                    >
                      <SyncOption title="ITR Only" icon={<FileText className="h-4 w-4" />} onClick={() => handleSync("ITR")} active={activeSync === "ITR"} />
                      <SyncOption title="AIS Only" icon={<RefreshCw className="h-4 w-4" />} onClick={() => handleSync("AIS")} active={activeSync === "AIS"} />
                      <SyncOption title="26AS Only" icon={<Download className="h-4 w-4" />} onClick={() => handleSync("26AS")} active={activeSync === "26AS"} />
                      <SyncOption title="Credentials" icon={<CheckCircle className="h-4 w-4" />} onClick={() => handleSync("Verify")} active={activeSync === "Verify"} />
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

const InfoRow = ({ label, value, highlight }: any) => (
  <div className="flex items-start justify-between gap-4">
    <span className="text-sm text-muted-foreground whitespace-nowrap">{label}</span>
    <span className={`text-sm text-right ${highlight ? "text-gold font-semibold" : "text-foreground"}`}>
      {value}
    </span>
  </div>
);

const SyncOption = ({ title, icon, onClick, active }: any) => (
  <Button
    variant="outline"
    size="sm"
    onClick={onClick}
    disabled={active}
    className={`w-full justify-start gap-2 border-border/50 hover:bg-secondary/50 hover:text-gold hover:border-gold/50 ${active ? 'bg-secondary text-gold' : 'text-muted-foreground'}`}
  >
    {active ? <Loader2 className="h-4 w-4 animate-spin" /> : icon}
    {title}
  </Button>
)

export default Profile;
