import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { User, MapPin, Phone, Mail, Briefcase, Shield, RefreshCw, Loader2 } from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { api } from "@/api/client";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const Profile = () => {
  const [profileData, setProfileData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [isSyncDialogOpen, setIsSyncDialogOpen] = useState(false);
  const [itrPassword, setItrPassword] = useState("");
  const [isSyncing, setIsSyncing] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await api.getProfile();

        // Calculate age from DOB
        let calculatedAge = "N/A";
        if (data.personal_info.dob && data.personal_info.dob !== "N/A") {
          try {
            // DOB format from backend: YYYY-MM-DD (e.g., "1999-01-03")
            const dobDate = new Date(data.personal_info.dob);
            const today = new Date();
            let age = today.getFullYear() - dobDate.getFullYear();
            const monthDiff = today.getMonth() - dobDate.getMonth();

            // Adjust age if birthday hasn't occurred yet this year
            if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dobDate.getDate())) {
              age--;
            }
            calculatedAge = age.toString();
          } catch (e) {
            console.error("Error calculating age:", e);
          }
        }

        setProfileData({
          fullName: data.personal_info.name,
          pan: data.personal_info.pan,
          dob: data.personal_info.dob || "N/A",
          age: calculatedAge,
          address: data.address,
          phone: data.phone,
          email: data.personal_info.email,
          sourcesOfIncome: ["Salary", "House Property", "Other Sources"], // Placeholder or derived from ITR
          aoDetails: data.ao_details
        });
      } catch (error) {
        console.error("Failed to fetch profile", error);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const handleSync = async () => {
    if (!itrPassword) {
      toast.error("Please enter your ITR password");
      return;
    }
    setIsSyncing(true);
    try {
      await api.triggerSync(itrPassword);
      toast.success("Sync started! Your dashboard will update shortly.");
      setIsSyncDialogOpen(false);
      setItrPassword("");
    } catch (error: any) {
      console.error("Sync failed:", error);
      toast.error(error.response?.data?.detail || "Failed to trigger sync");
    } finally {
      setIsSyncing(false);
    }
  };

  if (loading) {
    return <div className="flex h-screen items-center justify-center dark bg-background text-foreground">Loading Profile...</div>;
  }

  if (!profileData) {
    return <div className="flex h-screen items-center justify-center dark bg-background text-foreground">Failed to load profile.</div>;
  }

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
            variant="outline"
            className="border-gold/50 text-gold hover:bg-gold/10 hover:text-gold gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh Data
          </Button>
        </motion.div>

        <div className="grid gap-6 md:grid-cols-2">
          {/* Personal Information */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="rounded-2xl border border-border bg-card p-6 gold-glow"
          >
            <div className="flex items-center gap-2 mb-5">
              <User className="h-5 w-5 text-gold" />
              <h2 className="font-display text-lg font-semibold">Personal Information</h2>
            </div>
            <div className="space-y-4">
              <InfoRow label="Full Name" value={profileData.fullName} />
              <InfoRow label="PAN" value={profileData.pan} highlight />
              <InfoRow label="Date of Birth" value={profileData.dob} />
              <InfoRow label="Age" value={`${profileData.age} years`} />
            </div>
          </motion.div>

          {/* Contact Details */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="rounded-2xl border border-border bg-card p-6"
          >
            <div className="flex items-center gap-2 mb-5">
              <Mail className="h-5 w-5 text-gold" />
              <h2 className="font-display text-lg font-semibold">Contact Details</h2>
            </div>
            <div className="space-y-4">
              <InfoRow label="Email" value={profileData.email} icon={<Mail className="h-3.5 w-3.5 text-muted-foreground" />} />
              <InfoRow label="Phone" value={profileData.phone} icon={<Phone className="h-3.5 w-3.5 text-muted-foreground" />} />
              <InfoRow label="Address" value={profileData.address} icon={<MapPin className="h-3.5 w-3.5 text-muted-foreground" />} />
            </div>
          </motion.div>

          {/* Sources of Income */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="rounded-2xl border border-border bg-card p-6"
          >
            <div className="flex items-center gap-2 mb-5">
              <Briefcase className="h-5 w-5 text-gold" />
              <h2 className="font-display text-lg font-semibold">Sources of Income</h2>
            </div>
            <div className="flex flex-wrap gap-2">
              {profileData.sourcesOfIncome.map((source: string) => (
                <span
                  key={source}
                  className="rounded-full border border-border bg-secondary px-3 py-1.5 text-xs font-medium text-foreground"
                >
                  {source}
                </span>
              ))}
            </div>
          </motion.div>

          {/* AO Details */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="rounded-2xl border border-border bg-card p-6"
          >
            <div className="flex items-center gap-2 mb-5">
              <Shield className="h-5 w-5 text-gold" />
              <h2 className="font-display text-lg font-semibold">Assessing Officer (AO) Details</h2>
            </div>
            <div className="space-y-4">
              <InfoRow label="AO Code" value={profileData.aoDetails.aoCode} highlight />
              <InfoRow label="AO Type" value={profileData.aoDetails.aoType} />
              <InfoRow label="Range" value={profileData.aoDetails.range} />
              <InfoRow label="Circle / Ward" value={`${profileData.aoDetails.circle} / ${profileData.aoDetails.ward}`} />
              <InfoRow label="City" value={profileData.aoDetails.city} />
            </div>
          </motion.div>
        </div>
      </div>

      <Footer />

      {/* Sync Dialog */}
      <Dialog open={isSyncDialogOpen} onOpenChange={setIsSyncDialogOpen}>
        <DialogContent className="sm:max-w-md bg-card border-border">
          <DialogHeader>
            <DialogTitle className="text-foreground">Refresh Tax Data</DialogTitle>
            <DialogDescription className="text-muted-foreground">
              To fetch the latest data from the Income Tax Portal, please enter your ITR password.
            </DialogDescription>
          </DialogHeader>
          <div className="flex items-center space-x-2 py-4">
            <div className="grid flex-1 gap-2">
              <Label htmlFor="itr-password" className="sr-only">
                ITR Password
              </Label>
              <Input
                id="itr-password"
                type="password"
                placeholder="Enter ITR Password"
                value={itrPassword}
                onChange={(e) => setItrPassword(e.target.value)}
                className="bg-background border-border text-foreground"
              />
            </div>
          </div>
          <DialogFooter className="sm:justify-start">
            <Button
              type="button"
              variant="default"
              className="gradient-gold text-primary-foreground"
              onClick={handleSync}
              disabled={isSyncing}
            >
              {isSyncing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Syncing...
                </>
              ) : (
                "Sync Now"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

const InfoRow = ({
  label,
  value,
  highlight,
  icon,
}: {
  label: string;
  value: string;
  highlight?: boolean;
  icon?: React.ReactNode;
}) => (
  <div className="flex items-start justify-between gap-4">
    <span className="text-sm text-muted-foreground whitespace-nowrap">{label}</span>
    <span className={`text-sm text-right flex items-center gap-1.5 ${highlight ? "text-gold font-semibold" : "text-foreground"}`}>
      {icon}
      {value}
    </span>
  </div>
);

export default Profile;
