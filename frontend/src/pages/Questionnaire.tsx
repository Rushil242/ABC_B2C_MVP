
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Loader2 } from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { api } from "@/api/client";
import { toast } from "sonner";

interface Question {
    id: string;
    question: string;
    options: string[];
    multiSelect?: boolean;
}

const questions: Question[] = [
    {
        id: "residentialStatus",
        question: "What is your Residential Status for tax purposes?",
        options: ["Resident", "NRI"],
    },
    {
        id: "newRegime",
        question: "Which Tax Regime do you prefer/use?",
        options: ["Old Regime", "New Regime"],
    },
    {
        id: "income_sources",
        question: "Sources of Income (select all that apply)",
        options: [
            "Salary",
            "House Property (Rent)",
            "Business / Profession",
            "Capital Gains (Stocks/Property)",
            "Other Sources (Interest, Dividend)",
        ],
        multiSelect: true,
    },
    {
        id: "risk",
        question: "What is your risk appetite for tax planning strategies?",
        options: ["Conservative", "Balanced", "Aggressive"],
    },
    {
        id: "compliance",
        question: "How important is staying ahead of compliance requirements?",
        options: ["Proactive", "Standard", "Minimal"],
    },
    {
        id: "scrutiny",
        question: "What is your tolerance for potential tax scrutiny?",
        options: ["Zero tolerance", "Moderate", "High"],
    },
    {
        id: "horizon",
        question: "What is your tax planning time horizon?",
        options: ["Short-Term", "Medium-Term", "Long-Term"],
    },
    {
        id: "priority",
        question: "What matters more to you in tax planning?",
        options: ["Max Savings", "Max Safety", "Balanced Approach"],
    },
];

const Questionnaire = () => {
    const navigate = useNavigate();
    const [currentQ, setCurrentQ] = useState(0);
    const [answers, setAnswers] = useState<Record<string, string | string[]>>({});
    const [isSubmitting, setIsSubmitting] = useState(false);

    const q = questions[currentQ];

    const handleSelect = (option: string) => {
        if (q.multiSelect) {
            const current = (answers[q.id] as string[]) || [];
            const updated = current.includes(option)
                ? current.filter((o) => o !== option)
                : [...current, option];
            setAnswers({ ...answers, [q.id]: updated });
        } else {
            // For boolean-like fields, we could convert here, but storing strings is safer for display/API consistent
            setAnswers({ ...answers, [q.id]: option });
            // Auto advance for single select
            if (currentQ < questions.length - 1) {
                setTimeout(() => setCurrentQ((prev) => prev + 1), 300);
            }
        }
    };

    const isSelected = (option: string) => {
        const answer = answers[q.id];
        if (Array.isArray(answer)) return answer.includes(option);
        return answer === option;
    };

    const handleNext = async () => {
        if (currentQ < questions.length - 1) {
            setCurrentQ((prev) => prev + 1);
        } else {
            // Submit Data
            setIsSubmitting(true);
            try {
                // Transform answers if needed to match expected backend format?
                // Backend expects Dict, so this `answers` object is perfect.
                // We might want to map "Old Regime" -> false, "New Regime" -> true if strict boolean needed,
                // but string is fine for now as schema allows Dict.
                await api.updateProfileQuestionnaire(answers);
                toast.success("Profile updated successfully!");
                navigate("/dashboard");
            } catch (err) {
                console.error(err);
                toast.error("Failed to save profile.");
            } finally {
                setIsSubmitting(false);
            }
        }
    };

    const progress = ((currentQ + 1) / questions.length) * 100;

    return (
        <div className="dark min-h-screen bg-background text-foreground">
            <Navbar />

            <div className="flex min-h-[calc(100vh-8rem)] items-center justify-center px-4 py-12">
                <motion.div
                    key={currentQ}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.3 }}
                    className="w-full max-w-xl"
                >
                    {/* Progress */}
                    <div className="mb-8">
                        <div className="flex items-center justify-between text-xs text-muted-foreground mb-2">
                            <span>Question {currentQ + 1} of {questions.length}</span>
                            <span>{Math.round(progress)}%</span>
                        </div>
                        <div className="h-1.5 w-full overflow-hidden rounded-full bg-secondary">
                            <motion.div
                                className="h-full gradient-gold rounded-full"
                                animate={{ width: `${progress}%` }}
                                transition={{ duration: 0.4 }}
                            />
                        </div>
                    </div>

                    <div className="rounded-2xl border border-border bg-card p-8 gold-glow">
                        <h2 className="font-display text-xl font-semibold md:text-2xl mb-6">{q.question}</h2>

                        <div className={`space-y-3 ${q.multiSelect ? "grid grid-cols-1 gap-3 space-y-0" : ""}`}>
                            {q.options.map((option) => (
                                <button
                                    key={option}
                                    onClick={() => handleSelect(option)}
                                    className={`w-full rounded-lg border px-5 py-4 text-sm font-medium transition-all text-left flex items-center justify-between group ${isSelected(option)
                                            ? "border-gold bg-gold/10 text-gold"
                                            : "border-border bg-background text-muted-foreground hover:border-gold/50 hover:text-foreground"
                                        }`}
                                >
                                    <span>{option}</span>
                                    {isSelected(option) && <div className="h-2 w-2 rounded-full bg-gold" />}
                                </button>
                            ))}
                        </div>

                        <div className="mt-8 flex gap-3">
                            {currentQ > 0 && (
                                <button
                                    onClick={() => setCurrentQ((prev) => prev - 1)}
                                    className="flex-1 py-3 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors border border-transparent hover:border-border rounded-lg"
                                >
                                    Back
                                </button>
                            )}

                            <button
                                onClick={handleNext}
                                disabled={(!answers[q.id] || (Array.isArray(answers[q.id]) && (answers[q.id] as string[]).length === 0)) || isSubmitting}
                                className={`flex-1 gradient-gold rounded-lg py-3 text-sm font-semibold text-primary-foreground transition-all hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2 ${currentQ === 0 ? 'w-full' : ''}`}
                            >
                                {isSubmitting ? (
                                    <>
                                        <Loader2 className="h-4 w-4 animate-spin" />
                                        Saving...
                                    </>
                                ) : (
                                    currentQ === questions.length - 1 ? "Complete Profile" : "Next Step"
                                )}
                            </button>
                        </div>
                    </div>
                </motion.div>
            </div>

            <Footer />
        </div>
    );
};

export default Questionnaire;
