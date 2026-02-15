import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Loader2 } from "lucide-react";
import { api } from "@/api/client";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { toast } from "sonner";

const Register = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        pan: "",
        email: "",
        password: "",
        confirmPassword: ""
    });

    const [isLoading, setIsLoading] = useState(false);
    const [loadingMessage, setLoadingMessage] = useState("");
    const [error, setError] = useState("");

    const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]$/;

    // Handlers
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");

        // Validation
        if (!panRegex.test(formData.pan.toUpperCase())) {
            setError("Invalid PAN format (e.g., ABCDE1234F)");
            return;
        }
        if (formData.password !== formData.confirmPassword) {
            setError("Passwords do not match");
            return;
        }
        if (formData.password.length < 6) {
            setError("Password must be at least 6 characters");
            return;
        }

        setIsLoading(true);
        setLoadingMessage("Verifying credentials with Income Tax Portal...");

        try {
            const payload = {
                pan: formData.pan.toUpperCase(),
                name: null, // Will be fetched
                email: formData.email,
                dob: null, // Will be fetched
                password: formData.password,
                questionnaire_data: null // Questionnaire moved to separate step
            };

            const response = await api.register(payload);
            sessionStorage.setItem("auth_token", response.access_token);
            sessionStorage.setItem("abc_pan", payload.pan);

            setLoadingMessage("Syncing data...");
            toast.success("Account verified & created!");

            // Redirect to Questionnaire
            setTimeout(() => {
                navigate("/questionnaire");
            }, 1000);

        } catch (err: any) {
            console.error(err);
            const msg = err.response?.data?.detail || "Registration failed. Please verify your credentials.";
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
                    className="w-full max-w-lg"
                >
                    <button
                        onClick={() => navigate("/")}
                        className="mb-4 flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
                    >
                        <ArrowLeft className="h-4 w-4" />
                        Back to Home
                    </button>

                    <div className="rounded-2xl border border-border bg-card p-8 gold-glow">
                        <div className="text-center mb-6">
                            <h1 className="font-display text-3xl font-bold gold-text-gradient">
                                Create Account
                            </h1>
                            <p className="mt-2 text-sm text-muted-foreground">
                                Sign up to analyze your tax returns
                            </p>
                        </div>

                        <form onSubmit={handleSubmit} className="space-y-5">
                            <motion.div
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="space-y-4"
                            >
                                <div>
                                    <label className="mb-2 block text-sm font-medium text-foreground">PAN Number</label>
                                    <input
                                        name="pan"
                                        type="text"
                                        required
                                        maxLength={10}
                                        placeholder="ABCDE1234F"
                                        value={formData.pan}
                                        onChange={(e) => setFormData({ ...formData, pan: e.target.value.toUpperCase() })}
                                        className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm text-foreground focus:border-gold/50 focus:outline-none focus:ring-1 focus:ring-gold/30"
                                    />
                                </div>

                                <div>
                                    <label className="mb-2 block text-sm font-medium text-foreground">Email</label>
                                    <input
                                        name="email"
                                        type="email"
                                        required
                                        placeholder="john@example.com"
                                        value={formData.email}
                                        onChange={handleChange}
                                        className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm text-foreground focus:border-gold/50 focus:outline-none focus:ring-1 focus:ring-gold/30"
                                    />
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="mb-2 block text-sm font-medium text-foreground">Password</label>
                                        <input
                                            name="password"
                                            type="password"
                                            required
                                            placeholder="••••••••"
                                            value={formData.password}
                                            onChange={handleChange}
                                            className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm text-foreground focus:border-gold/50 focus:outline-none focus:ring-1 focus:ring-gold/30"
                                        />
                                    </div>
                                    <div>
                                        <label className="mb-2 block text-sm font-medium text-foreground">Confirm</label>
                                        <input
                                            name="confirmPassword"
                                            type="password"
                                            required
                                            placeholder="••••••••"
                                            value={formData.confirmPassword}
                                            onChange={handleChange}
                                            className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm text-foreground focus:border-gold/50 focus:outline-none focus:ring-1 focus:ring-gold/30"
                                        />
                                    </div>
                                </div>

                                <p className="text-xs text-muted-foreground">
                                    Note: Use your ITR Portal Password to enable auto-sync.
                                </p>
                            </motion.div>

                            {error && (
                                <p className="text-sm text-destructive font-medium bg-destructive/10 p-3 rounded-lg border border-destructive/20">
                                    {error}
                                </p>
                            )}

                            <button
                                type="submit"
                                disabled={isLoading}
                                className="w-full gradient-gold rounded-lg py-3 text-sm font-semibold text-primary-foreground transition-all hover:opacity-90 disabled:opacity-70 flex items-center justify-center gap-2"
                            >
                                {isLoading ? (
                                    <>
                                        <Loader2 className="h-4 w-4 animate-spin" />
                                        {loadingMessage || "Processing..."}
                                    </>
                                ) : (
                                    "Verify & Create Account"
                                )}
                            </button>
                        </form>

                        <div className="mt-6 text-center text-sm">
                            <span className="text-muted-foreground">Already have an account? </span>
                            <Link to="/login" className="text-gold hover:underline font-medium">
                                Login here
                            </Link>
                        </div>
                    </div>
                </motion.div>
            </div>
            <Footer />
        </div>
    );
};

export default Register;
