import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Pause, Play, Square } from "lucide-react";

const steps = [
  "Connecting to Income Tax Portal...",
  "Logging in with your credentials...",
  "Fetching filed returns...",
  "Downloading notices & orders...",
  "Analyzing tax history with AI...",
  "Preparing your dashboard...",
];

const Loading = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [paused, setPaused] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (paused) {
      if (intervalRef.current) clearInterval(intervalRef.current);
      return;
    }

    intervalRef.current = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev >= steps.length - 1) {
          if (intervalRef.current) clearInterval(intervalRef.current);
          setTimeout(() => navigate("/dashboard"), 800);
          return prev;
        }
        return prev + 1;
      });
    }, 1200);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [navigate, paused]);

  const progress = ((currentStep + 1) / steps.length) * 100;

  return (
    <div className="dark flex min-h-screen items-center justify-center bg-background text-foreground">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-lg px-4 text-center"
      >
        <div className="font-display text-4xl font-bold gold-text-gradient">ABC</div>
        <p className="mt-2 text-sm text-muted-foreground">
          {paused ? "Paused — take your time" : "Processing your data"}
        </p>

        <div className="mt-12">
          <div className="mx-auto h-2 w-full max-w-sm overflow-hidden rounded-full bg-secondary">
            <motion.div
              className="h-full gradient-gold rounded-full"
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            />
          </div>
        </div>

        <div className="mt-8 space-y-3">
          {steps.map((step, i) => (
            <motion.div
              key={step}
              initial={{ opacity: 0, x: -10 }}
              animate={{
                opacity: i <= currentStep ? 1 : 0.3,
                x: 0,
              }}
              transition={{ duration: 0.4, delay: i * 0.1 }}
              className="flex items-center justify-center gap-2 text-sm"
            >
              <span
                className={
                  i < currentStep
                    ? "text-gold"
                    : i === currentStep
                      ? "text-foreground"
                      : "text-muted-foreground"
                }
              >
                {i < currentStep ? "✓" : i === currentStep ? "●" : "○"}
              </span>
              <span
                className={
                  i < currentStep
                    ? "text-muted-foreground"
                    : i === currentStep
                      ? "text-foreground font-medium"
                      : "text-muted-foreground"
                }
              >
                {step}
              </span>
            </motion.div>
          ))}
        </div>

        {/* Pause & Stop buttons */}
        <div className="mt-10 flex items-center justify-center gap-4">
          <button
            onClick={() => setPaused((p) => !p)}
            className="flex items-center gap-2 rounded-lg border border-border px-5 py-2.5 text-sm text-muted-foreground hover:text-foreground hover:border-gold/30 transition-colors"
          >
            {paused ? <Play className="h-4 w-4" /> : <Pause className="h-4 w-4" />}
            {paused ? "Resume" : "Pause"}
          </button>
          <button
            onClick={() => navigate("/")}
            className="flex items-center gap-2 rounded-lg border border-destructive/30 px-5 py-2.5 text-sm text-destructive hover:bg-destructive/10 transition-colors"
          >
            <Square className="h-4 w-4" />
            Stop
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default Loading;
