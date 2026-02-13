import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

const Login = () => {
  const navigate = useNavigate();
  const [pan, setPan] = useState("ABCDE1234F");
  const [password, setPassword] = useState("Demo@1234");
  const [error, setError] = useState("");
  const [disclosureOpen, setDisclosureOpen] = useState(false);
  const [privacyOpen, setPrivacyOpen] = useState(false);
  const [disclosureAccepted, setDisclosureAccepted] = useState(false);
  const [privacyAccepted, setPrivacyAccepted] = useState(false);

  const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]$/;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!disclosureAccepted || !privacyAccepted) {
      setError("Please accept both the Disclosure and Privacy Policy to continue.");
      return;
    }

    const upperPan = pan.toUpperCase();
    if (!panRegex.test(upperPan)) {
      setError("Please enter a valid PAN (e.g., ABCDE1234F)");
      return;
    }
    if (!password) {
      setError("Please enter your password");
      return;
    }

    sessionStorage.setItem("abc_pan", upperPan);
    navigate("/loading");
  };

  return (
    <div className="dark min-h-screen bg-background text-foreground">
      <Navbar />

      <div className="flex min-h-[calc(100vh-8rem)] items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="w-full max-w-md"
        >
          <button
            onClick={() => navigate("/")}
            className="mb-4 flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Back
          </button>
          <div className="rounded-2xl border border-border bg-card p-8 gold-glow">
            <div className="text-center">
              <h1 className="font-display text-3xl font-bold gold-text-gradient">
                Welcome Back
              </h1>
              <p className="mt-2 text-sm text-muted-foreground">
                Login with your Income Tax credentials
              </p>
            </div>

            <form onSubmit={handleSubmit} className="mt-8 space-y-5">
              <div>
                <label className="mb-2 block text-sm font-medium text-foreground">
                  PAN Number
                </label>
                <input
                  type="text"
                  placeholder="ABCDE1234F"
                  maxLength={10}
                  value={pan}
                  onChange={(e) => setPan(e.target.value.toUpperCase())}
                  className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:border-gold/50 focus:outline-none focus:ring-1 focus:ring-gold/30 transition-colors"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-foreground">
                  Password
                </label>
                <input
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:border-gold/50 focus:outline-none focus:ring-1 focus:ring-gold/30 transition-colors"
                />
              </div>

              {error && (
                <p className="text-sm text-destructive">{error}</p>
              )}

              {/* Consent Checkboxes */}
              <div className="space-y-3">
                <label className="flex items-start gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={disclosureAccepted}
                    onChange={(e) => setDisclosureAccepted(e.target.checked)}
                    className="mt-1 h-4 w-4 rounded border-border accent-gold"
                  />
                  <span className="text-xs text-muted-foreground">
                    I have read and agree to the{" "}
                    <button
                      type="button"
                      onClick={() => setDisclosureOpen(true)}
                      className="text-gold hover:underline font-medium"
                    >
                      Disclosure Agreement
                    </button>
                  </span>
                </label>
                <label className="flex items-start gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={privacyAccepted}
                    onChange={(e) => setPrivacyAccepted(e.target.checked)}
                    className="mt-1 h-4 w-4 rounded border-border accent-gold"
                  />
                  <span className="text-xs text-muted-foreground">
                    I have read and agree to the{" "}
                    <button
                      type="button"
                      onClick={() => setPrivacyOpen(true)}
                      className="text-gold hover:underline font-medium"
                    >
                      Privacy Policy
                    </button>
                  </span>
                </label>
              </div>

              <button
                type="submit"
                className="w-full gradient-gold rounded-lg py-3 text-sm font-semibold text-primary-foreground transition-all hover:opacity-90"
              >
                Login & Analyze
              </button>
            </form>

            <p className="mt-6 text-center text-xs text-muted-foreground">
              Your credentials are used solely to access your Income Tax e-filing portal.
              We do not store your password.
            </p>
          </div>
        </motion.div>
      </div>

      {/* Disclosure Dialog */}
      <Dialog open={disclosureOpen} onOpenChange={setDisclosureOpen}>
        <DialogContent className="dark border-border bg-card text-foreground max-w-lg">
          <DialogHeader>
            <DialogTitle className="font-display text-xl gold-text-gradient">
              Draft Disclosure Agreement
            </DialogTitle>
            <DialogDescription className="text-muted-foreground text-xs">
              Please read carefully before proceeding.
            </DialogDescription>
          </DialogHeader>
          <ScrollArea className="max-h-[60vh] pr-4">
            <div className="space-y-3 text-sm text-muted-foreground leading-relaxed">
              <p>By using ABC (AnyBody can Consult), you acknowledge and agree to the following:</p>
              <p><strong className="text-foreground">1. Nature of Service:</strong> ABC is an AI-powered tax analysis and advisory tool. It provides informational guidance based on the data you supply and publicly available tax regulations. It does not constitute professional tax advice, legal counsel, or chartered accountancy services.</p>
              <p><strong className="text-foreground">2. Credential Usage:</strong> Your Income Tax e-filing portal credentials (PAN & password) are used solely to fetch your tax data from the government portal. We act as an intermediary to retrieve and analyze this data on your behalf.</p>
              <p><strong className="text-foreground">3. No Guarantee:</strong> While we strive for accuracy, ABC does not guarantee that the analysis, missed opportunities, or probable problems identified are exhaustive or error-free. Tax laws change frequently, and individual circumstances vary.</p>
              <p><strong className="text-foreground">4. User Responsibility:</strong> You are solely responsible for any actions taken based on the insights provided by ABC. We recommend consulting a qualified Chartered Accountant before making significant tax decisions.</p>
              <p><strong className="text-foreground">5. Data Retention:</strong> Your tax data is processed in real-time and is not stored permanently on our servers beyond the duration of your active session unless you explicitly opt in to data storage features.</p>
            </div>
          </ScrollArea>
          <button
            onClick={() => {
              setDisclosureAccepted(true);
              setDisclosureOpen(false);
            }}
            className="w-full gradient-gold rounded-lg py-2.5 text-sm font-semibold text-primary-foreground transition-all hover:opacity-90 mt-2"
          >
            I Accept
          </button>
        </DialogContent>
      </Dialog>

      {/* Privacy Policy Dialog */}
      <Dialog open={privacyOpen} onOpenChange={setPrivacyOpen}>
        <DialogContent className="dark border-border bg-card text-foreground max-w-lg">
          <DialogHeader>
            <DialogTitle className="font-display text-xl gold-text-gradient">
              Draft Privacy Policy
            </DialogTitle>
            <DialogDescription className="text-muted-foreground text-xs">
              How we handle your personal information.
            </DialogDescription>
          </DialogHeader>
          <ScrollArea className="max-h-[60vh] pr-4">
            <div className="space-y-3 text-sm text-muted-foreground leading-relaxed">
              <p>ABC respects your privacy and is committed to protecting your personal data.</p>
              <p><strong className="text-foreground">1. Information We Collect:</strong> PAN number, income tax return data, personal details as available on the e-filing portal (name, address, contact information), and questionnaire responses you provide.</p>
              <p><strong className="text-foreground">2. How We Use Your Data:</strong> Your data is used exclusively to generate personalized tax analysis, identify missed deductions, flag probable issues, and provide actionable tax insights within the ABC platform.</p>
              <p><strong className="text-foreground">3. Data Security:</strong> We employ industry-standard encryption (AES-256) for data in transit and at rest. Your e-filing credentials are never stored — they are used in a single session to fetch data and are immediately discarded.</p>
              <p><strong className="text-foreground">4. Third-Party Sharing:</strong> We do not sell, trade, or share your personal or financial data with any third parties. Your data remains within the ABC platform environment.</p>
              <p><strong className="text-foreground">5. Data Deletion:</strong> You may request complete deletion of your data at any time by contacting our support team. Session data is automatically purged after logout.</p>
              <p><strong className="text-foreground">6. Cookies & Analytics:</strong> We use minimal analytics cookies to improve user experience. No personally identifiable information is shared with analytics providers.</p>
            </div>
          </ScrollArea>
          <button
            onClick={() => {
              setPrivacyAccepted(true);
              setPrivacyOpen(false);
            }}
            className="w-full gradient-gold rounded-lg py-2.5 text-sm font-semibold text-primary-foreground transition-all hover:opacity-90 mt-2"
          >
            I Accept
          </button>
        </DialogContent>
      </Dialog>

      <Footer />
    </div>
  );
};

export default Login;
