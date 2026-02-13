import { motion } from "framer-motion";
import { User, MapPin, Phone, Mail, Briefcase, Shield } from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

const profileData = {
  fullName: "Rajesh Kumar Sharma",
  pan: sessionStorage.getItem("abc_pan") || "ABCDE1234F",
  dob: "15-Aug-1985",
  age: 40,
  address: "42, Sector 18, Dwarka, New Delhi – 110078",
  phone: "+91 98765 43210",
  email: "rajesh.sharma@email.com",
  sourcesOfIncome: ["Salary", "House Property (Rental)", "Fixed Deposits"],
  aoDetails: {
    aoCode: "DEL-C-24(1)",
    aoType: "Non-Corporate",
    range: "Range 24(1)",
    circle: "Circle 24",
    ward: "Ward 24(1)",
    city: "New Delhi",
  },
};

const Profile = () => {
  const pan = sessionStorage.getItem("abc_pan") || profileData.pan;

  return (
    <div className="dark min-h-screen bg-background text-foreground">
      <Navbar isLoggedIn />

      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="font-display text-3xl font-bold">
            <span className="gold-text-gradient">Profile</span>
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Your personal and tax-related details
          </p>
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
              <InfoRow label="PAN" value={pan} highlight />
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
              {profileData.sourcesOfIncome.map((source) => (
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
