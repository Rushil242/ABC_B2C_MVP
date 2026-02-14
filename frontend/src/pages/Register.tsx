
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";
import { api } from "@/api/client";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "sonner";

const Register = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        pan: "",
        name: "",
        email: "",
        dob: "",
        password: "",
        confirmPassword: ""
    });
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]$/;

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setIsLoading(true);

        // Validation
        if (!panRegex.test(formData.pan.toUpperCase())) {
            setError("Invalid PAN format (e.g., ABCDE1234F)");
            setIsLoading(false);
            return;
        }
        if (formData.password !== formData.confirmPassword) {
            setError("Passwords do not match");
            setIsLoading(false);
            return;
        }
        if (formData.password.length < 6) {
            setError("Password must be at least 6 characters");
            setIsLoading(false);
            return;
        }

        try {
            const payload = {
                pan: formData.pan.toUpperCase(),
                name: formData.name,
                email: formData.email,
                dob: formData.dob, // Format: YYYY-MM-DD from input type="date" matches typical needs or needs formatting?
                // Backend expects string. Frontend input date gives YYYY-MM-DD.
                // Dashboard expects DD-MM-YYYY sometimes. Let's check schemas.
                // Schemas just say str. Dashboard uses split('-').
                // If input is YYYY-MM-DD (2000-01-31), split('-') gives [2000, 01, 31].
                // Dashboard logic: const [d, m, y] = dob.split('-'); 
                // This implies Dashboard expects DD-MM-YYYY. 
                // So we should format it.
                password: formData.password
            };

            // Format DOB to DD-MM-YYYY
            const [y, m, d] = formData.dob.split('-');
            payload.dob = `${d}-${m}-${y}`;

            const response = await api.register(payload);
            sessionStorage.setItem("auth_token", response.access_token);
            sessionStorage.setItem("abc_pan", payload.pan);

            toast.success("Account created successfully!");
            navigate("/loading");
        } catch (err: any) {
            console.error(err);
            setError(err.response?.data?.detail || "Registration failed. Please try again.");
        } finally {
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
                                Create Account
                            </h1>
                            <p className="mt-2 text-sm text-muted-foreground">
                                Sign up to analyze your tax returns
                            </p>
                        </div>

                        <form onSubmit={handleSubmit} className="mt-8 space-y-4">
                            <div>
                                <label className="mb-2 block text-sm font-medium text-foreground">Full Name</label>
                                <input
                                    name="name"
                                    type="text"
                                    required
                                    placeholder="John Doe"
                                    value={formData.name}
                                    onChange={handleChange}
                                    className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm text-foreground focus:border-gold/50 focus:outline-none focus:ring-1 focus:ring-gold/30"
                                />
                            </div>

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

                            <div>
                                <label className="mb-2 block text-sm font-medium text-foreground">Date of Birth</label>
                                <input
                                    name="dob"
                                    type="date"
                                    required
                                    value={formData.dob}
                                    onChange={handleChange}
                                    className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm text-foreground focus:border-gold/50 focus:outline-none focus:ring-1 focus:ring-gold/30"
                                />
                            </div>

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
                                <label className="mb-2 block text-sm font-medium text-foreground">Confirm Password</label>
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

                            {error && (
                                <p className="text-sm text-destructive font-medium">{error}</p>
                            )}

                            <button
                                type="submit"
                                disabled={isLoading}
                                className="w-full gradient-gold rounded-lg py-3 text-sm font-semibold text-primary-foreground transition-all hover:opacity-90 disabled:opacity-50"
                            >
                                {isLoading ? "Creating Account..." : "Register"}
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
