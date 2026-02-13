import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

interface Question {
  id: string;
  question: string;
  options: string[];
  multiSelect?: boolean;
}

const questions: Question[] = [
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
    id: "income_pattern",
    question: "How would you describe your income pattern?",
    options: ["Stable", "Variable", "Mixed"],
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
  {
    id: "income_sources",
    question: "Sources of Income (select all that apply)",
    options: [
      "Salary",
      "Rent",
      "Business",
      "Capital Gains",
      "Trading",
      "FD Interest",
      "Bank Interest",
      "Dividends",
      "Agriculture",
      "Other",
    ],
    multiSelect: true,
  },
];

const Questionnaire = () => {
  const navigate = useNavigate();
  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string | string[]>>({});

  const q = questions[currentQ];

  const handleSelect = (option: string) => {
    if (q.multiSelect) {
      const current = (answers[q.id] as string[]) || [];
      const updated = current.includes(option)
        ? current.filter((o) => o !== option)
        : [...current, option];
      setAnswers({ ...answers, [q.id]: updated });
    } else {
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

  const handleNext = () => {
    if (currentQ < questions.length - 1) {
      setCurrentQ((prev) => prev + 1);
    } else {
      navigate("/dashboard");
    }
  };

  const progress = ((currentQ + 1) / questions.length) * 100;

  return (
    <div className="dark min-h-screen bg-background text-foreground">
      <Navbar />

      <div className="flex min-h-[calc(100vh-8rem)] items-center justify-center px-4">
        <motion.div
          key={currentQ}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4 }}
          className="w-full max-w-xl"
        >
          <button
            onClick={() => navigate("/")}
            className="mb-4 flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Home
          </button>

          {/* Progress */}
          <div className="mb-8">
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>Question {currentQ + 1} of {questions.length}</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-secondary">
              <motion.div
                className="h-full gradient-gold rounded-full"
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.4 }}
              />
            </div>
          </div>

          <div className="rounded-2xl border border-border bg-card p-8">
            <h2 className="font-display text-xl font-semibold md:text-2xl">{q.question}</h2>

            <div className={`mt-6 ${q.multiSelect ? "flex flex-wrap gap-3" : "space-y-3"}`}>
              {q.options.map((option) => (
                <button
                  key={option}
                  onClick={() => handleSelect(option)}
                  className={`rounded-lg border px-5 py-3 text-sm font-medium transition-all ${
                    isSelected(option)
                      ? "border-gold/50 bg-primary/10 text-gold"
                      : "border-border bg-background text-muted-foreground hover:border-gold/30 hover:text-foreground"
                  } ${q.multiSelect ? "" : "block w-full text-left"}`}
                >
                  {option}
                </button>
              ))}
            </div>

            {q.multiSelect && (
              <button
                onClick={handleNext}
                disabled={!answers[q.id] || (answers[q.id] as string[]).length === 0}
                className="mt-6 w-full gradient-gold rounded-lg py-3 text-sm font-semibold text-primary-foreground transition-all hover:opacity-90 disabled:opacity-50"
              >
                {currentQ === questions.length - 1 ? "View Dashboard" : "Next"}
              </button>
            )}

            {currentQ > 0 && (
              <button
                onClick={() => setCurrentQ((prev) => prev - 1)}
                className="mt-3 w-full py-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                ← Back
              </button>
            )}
          </div>
        </motion.div>
      </div>

      <Footer />
    </div>
  );
};

export default Questionnaire;
