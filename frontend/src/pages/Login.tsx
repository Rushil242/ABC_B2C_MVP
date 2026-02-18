
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Loader2, CheckCircle2 } from "lucide-react";
import { api } from "@/api/client";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { toast } from "sonner";
import { useSync } from "@/context/SyncContext";

const Login = () => {
  const navigate = useNavigate();
  const [pan, setPan] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const { startSync } = useSync();

  const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]$/;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const upperPan = pan.toUpperCase();
    if (!panRegex.test(upperPan)) {
      setError("Please enter a valid PAN (e.g., ABCDE1234F)");
      return;
    }
    if (!password) {
      setError("Please enter your password");
      return;
    }

    setIsLoading(true);

    try {
      // Pass questionnaire data to login
      const response = await api.login(upperPan, password);
      sessionStorage.setItem("auth_token", response.access_token);
      sessionStorage.setItem("abc_pan", upperPan);

      // Auto-sync on login and cache password for session
      sessionStorage.setItem("itr_password", password);
      try {
        startSync(password).catch(e => console.error("Auto-sync failed trigger", e));
        toast.success("Background sync started automatically.");
      } catch (e) {
        console.error("Failed to trigger auto-sync", e);
      }

      toast.success("Logged in successfully!");
      navigate("/dashboard");

    } catch (err: any) {
      console.error(err);
      const msg = err.response?.data?.detail || "Invalid credentials. Please register if you haven't.";
      setError(msg);
      setIsLoading(false);
    }
  };

  return (
    <div className="dark min-h-screen bg-background text-foreground">
      <Navbar />
      <div className="flex min-h-[calc(100vh-8rem)] items-center justify-center px-4 py-12">
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
            Back to Home
          </button>

          <div className="rounded-2xl border border-border bg-card p-8 gold-glow">
            <div className="text-center">
              <h1 className="font-display text-3xl font-bold gold-text-gradient">
                Welcome Back
              </h1>
              <p className="mt-2 text-sm text-muted-foreground">
                Login with your ITR Credentials
              </p>
            </div>

            <form onSubmit={handleSubmit} className="mt-8 space-y-4">
              <div>
                <label className="mb-2 block text-sm font-medium text-foreground">PAN Number</label>
                <input
                  type="text"
                  required
                  maxLength={10}
                  placeholder="ABCDE1234F"
                  value={pan}
                  onChange={(e) => setPan(e.target.value.toUpperCase())}
                  className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm text-foreground focus:border-gold/50 focus:outline-none focus:ring-1 focus:ring-gold/30"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-foreground">ITR Password</label>
                <input
                  type="password"
                  required
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm text-foreground focus:border-gold/50 focus:outline-none focus:ring-1 focus:ring-gold/30"
                />
              </div>

              {error && (
                <p className="text-sm text-destructive font-medium">{error}</p>
              )}

              <button
                type="submit"
                disabled={isLoading}
                className="w-full gradient-gold rounded-lg py-3 text-sm font-semibold text-primary-foreground transition-all hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
                {isLoading ? "Logging in..." : "Login & Analyze"}
              </button>
            </form>

            <div className="mt-6 text-center text-sm">
              <span className="text-muted-foreground">New User? </span>
              <Link to="/register" className="text-gold hover:underline font-medium">
                Create Account
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
      <Footer />
    </div>
  );
};

export default Login;
