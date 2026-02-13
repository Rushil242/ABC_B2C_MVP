import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Shield, Search, AlertTriangle, TrendingUp } from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

const features = [
  {
    icon: Search,
    title: "Domain Specific AI",
    description: "AI trained on Indian tax law to analyze your filings with precision and context.",
  },
  {
    icon: TrendingUp,
    title: "Missed Opportunities",
    description: "Discover deductions, exemptions, and tax-saving opportunities you may have overlooked.",
  },
  {
    icon: AlertTriangle,
    title: "Probable Issues",
    description: "Identify errors, inconsistencies, and compliance risks in your past returns.",
  },
  {
    icon: Shield,
    title: "Suggested Resolutions",
    description: "Get actionable recommendations to fix problems and optimize your tax position.",
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.15 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6 } },
};

const Index = () => {
  return (
    <div className="dark min-h-screen bg-background text-foreground">
      <Navbar />

      {/* Hero */}
      <section className="relative overflow-hidden py-24 md:py-36">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,hsl(43_76%_55%/0.08),transparent_60%)]" />
        <div className="container relative mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="font-display text-4xl font-bold leading-tight md:text-6xl lg:text-7xl">
              <span className="gold-text-gradient">AnyBody can Consult</span>
            </h1>
            <p className="mt-2 font-display text-lg text-muted-foreground md:text-xl">
              By <span className="gold-text-gradient font-semibold">Nuthan Kaparthy</span>
            </p>
          </motion.div>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="mx-auto mt-8 max-w-2xl text-lg text-silver-light leading-relaxed"
          >
            Your AI-powered tax intelligence platform. We analyze your income tax history, 
            identify missed opportunities, flag probable issues, and suggest actionable resolutions 
            — all in one place.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
            className="mt-10 flex items-center justify-center gap-4"
          >
            <Link
              to="/login"
              className="gradient-gold animate-pulse-gold rounded-lg px-8 py-3 text-lg font-semibold text-primary-foreground transition-all hover:opacity-90"
            >
              Get Started
            </Link>
            <a
              href="https://abcweb2.lovable.app"
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-lg border border-border px-8 py-3 text-lg font-medium text-muted-foreground transition-colors hover:border-gold/40 hover:text-foreground"
            >
              ABC Web
            </a>
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <motion.h2
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center font-display text-3xl font-bold md:text-4xl"
          >
            What <span className="text-gold">ABC</span> Does for You
          </motion.h2>

          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="mt-16 grid gap-6 md:grid-cols-2 lg:grid-cols-4"
          >
            {features.map((feature) => (
              <motion.div
                key={feature.title}
                variants={itemVariants}
                className="group rounded-xl border border-border bg-card p-6 transition-all hover:border-gold/30 hover:gold-glow"
              >
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                  <feature.icon className="h-6 w-6 text-gold" />
                </div>
                <h3 className="font-display text-lg font-semibold">{feature.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="rounded-2xl border border-gold/20 bg-card p-12 text-center gold-glow">
            <h2 className="font-display text-3xl font-bold">
              Ready to uncover your <span className="text-gold">tax potential</span>?
            </h2>
            <p className="mx-auto mt-4 max-w-lg text-muted-foreground">
              Log in with your PAN and password to get a comprehensive AI-powered analysis of your tax history.
            </p>
            <Link
              to="/login"
              className="mt-8 inline-block gradient-gold rounded-lg px-10 py-3 text-lg font-semibold text-primary-foreground transition-all hover:opacity-90"
            >
              Login Now
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default Index;
