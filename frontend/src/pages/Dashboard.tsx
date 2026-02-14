import { useState } from "react";
import { motion } from "framer-motion";
import { TrendingUp, AlertTriangle, Calendar, FileText, Loader2, RefreshCw } from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle
} from
  "@/components/ui/dialog";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";

const Dashboard = () => {
  const [solutionDialog, setSolutionDialog] = useState<{
    open: boolean;
    problem?: any;
  }>({ open: false });
  const [syncLoading, setSyncLoading] = useState(false);
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: api.getDashboard,
    retry: false
  });

  const [syncDialog, setSyncDialog] = useState(false);
  const [password, setPassword] = useState("");

  const handleSyncClick = () => {
    setSyncDialog(true);
  };

  const confirmSync = async () => {
    if (!password) {
      alert("Please enter password");
      return;
    }
    setSyncLoading(true);
    setSyncDialog(false);
    try {
      await api.triggerSync(password);
      setPassword(""); // Clear password
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['dashboard'] });
        setSyncLoading(false);
        alert("Sync started! Data will update shortly.");
      }, 2000);
    } catch (e) {
      console.error("Sync failed", e);
      setSyncLoading(false);
      alert("Failed to trigger sync: " + (e as any).response?.data?.detail || "Unknown error");
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-background text-foreground">
        <Loader2 className="h-10 w-10 animate-spin text-gold" />
        <span className="ml-3 font-display">Loading Tax Intelligence...</span>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-background text-foreground flex-col">
        <AlertTriangle className="h-10 w-10 text-destructive mb-4" />
        <h2 className="text-xl font-bold">Failed to load data</h2>
        <p className="text-muted-foreground mt-2">Please try logging in again.</p>
      </div>
    );
  }

  const { user, risks, opportunities, advance_tax, tds_tcs } = data;

  // ... (Mappings remain same)
  const missedOpportunities = opportunities.map((op: any) => ({
    ay: op.ay || "2024-25", // Default if missing
    opportunity: op.title,
    savings: `â‚¹${op.potential_savings.toLocaleString()}`
  }));

  const probableProblems = risks.map((r: any) => ({
    ay: r.ay || "2024-25",
    wrong: r.title,
    why: r.description,
    solutions: r.solutions ? JSON.parse(r.solutions) : [] // Parse JSON string
  }));

  const advanceTax = advance_tax.map((at: any) => ({
    quarter: at.quarter,
    section: at.section,
    dueDate: at.due_date,
    amount: at.amount,
    status: at.status,
    reminder: at.reminder
  }));

  const tdsTcs = tds_tcs.map((t: any) => ({
    type: t.type,
    section: t.section,
    date: t.date,
    tdsAmount: t.tds_amount,
    amount: t.total_amount
  }));

  const pan = user.pan;
  const fullName = user.name || "User";
  const dob = user.dob || "—";

  // Calculate age
  let ageYears = 0, ageMonths = 0;
  if (dob !== "—") {
    try {
      const [d, m, y] = dob.split('-');
      const dobDate = new Date(parseInt(y), parseInt(m) - 1, parseInt(d));
      const now = new Date();
      ageYears = now.getFullYear() - dobDate.getFullYear();
      ageMonths = now.getMonth() - dobDate.getMonth();
      if (ageMonths < 0 || (ageMonths === 0 && now.getDate() < dobDate.getDate())) {
        ageYears--;
        ageMonths += 12;
      }
      if (now.getDate() < dobDate.getDate()) {
        ageMonths--;
        if (ageMonths < 0) ageMonths += 12;
      }
    } catch (e) { console.error("Invalid DOB format", dob); }
  }

  const userId = `${pan.toLowerCase()}${dob.replace(/-/g, '')}`;

  return (
    <div className="dark min-h-screen bg-background text-foreground">
      <Navbar isLoggedIn />

      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 rounded-2xl border border-border bg-card p-6">

          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
            <h1 className="font-display text-2xl font-bold">
              Welcome, <span className="text-gold">{fullName}</span>
            </h1>
            <button
              onClick={handleSyncClick}
              disabled={syncLoading}
              className="flex items-center gap-2 px-4 py-2 bg-primary/10 hover:bg-primary/20 text-gold rounded-lg transition-colors disabled:opacity-50"
            >
              {syncLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
              {syncLoading ? "Syncing..." : "Sync Data"}
            </button>
          </div>

          <div className="mt-3 grid gap-1.5 text-sm text-muted-foreground sm:grid-cols-2 md:grid-cols-4">
            <div>
              <span className="text-xs uppercase tracking-wider">Full Name</span>
              <p className="font-medium text-foreground">{fullName}</p>
            </div>
            <div>
              <span className="text-xs uppercase tracking-wider">PAN</span>
              <p className="font-medium text-gold">{pan}</p>
            </div>
            <div>
              <span className="text-xs uppercase tracking-wider">Date of Birth</span>
              <p className="font-medium text-foreground">{dob}</p>
            </div>
            <div>
              <span className="text-xs uppercase tracking-wider">Age</span>
              <p className="font-medium text-foreground">{ageYears} Years {ageMonths} Months</p>
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-border">
            <span className="text-xs text-muted-foreground">Doc Pwd: </span>
            <span className="text-xs font-mono text-gold">{userId}</span>
          </div>
        </motion.div>

        <div className="space-y-8">
          {/* Missed Opportunities */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}>

            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="h-5 w-5 text-gold" />
              <h2 className="font-display text-xl font-semibold">Missed Opportunities</h2>
            </div>
            <div className="overflow-x-auto rounded-xl border border-border">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border bg-card">
                    <th className="px-4 py-3 text-left font-medium text-muted-foreground">AY</th>
                    <th className="px-4 py-3 text-left font-medium text-muted-foreground">Missed Opportunity</th>
                    <th className="px-4 py-3 text-right font-medium text-muted-foreground">Probable Savings</th>
                  </tr>
                </thead>
                <tbody>
                  {missedOpportunities.length > 0 ? missedOpportunities.map((item: any, i: number) =>
                    <tr key={i} className="border-b border-border last:border-0 hover:bg-card/50 transition-colors">
                      <td className="px-4 py-3 text-gold font-medium">{item.ay}</td>
                      <td className="px-4 py-3">{item.opportunity}</td>
                      <td className="px-4 py-3 text-right font-semibold text-gold">{item.savings}</td>
                    </tr>
                  ) : (
                    <tr><td colSpan={3} className="px-4 py-6 text-center text-muted-foreground">No missed opportunities found.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </motion.section>

          {/* Probable Problems */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}>

            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="h-5 w-5 text-destructive" />
              <h2 className="font-display text-xl font-semibold">Probable Problems</h2>
            </div>
            <div className="overflow-x-auto rounded-xl border border-border">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border bg-card">
                    <th className="px-4 py-3 text-left font-medium text-muted-foreground">AY</th>
                    <th className="px-4 py-3 text-left font-medium text-muted-foreground">What's Wrong</th>
                    <th className="px-4 py-3 text-left font-medium text-muted-foreground">Why is it Wrong</th>
                    <th className="px-4 py-3 text-right font-medium text-muted-foreground">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {probableProblems.length > 0 ? probableProblems.map((item: any, i: number) =>
                    <tr key={i} className="border-b border-border last:border-0 hover:bg-card/50 transition-colors">
                      <td className="px-4 py-3 font-medium">{item.ay}</td>
                      <td className="px-4 py-3">{item.wrong}</td>
                      <td className="px-4 py-3 text-muted-foreground">{item.why}</td>
                      <td className="px-4 py-3 text-right">
                        <button
                          onClick={() => setSolutionDialog({ open: true, problem: item })}
                          className="text-gold hover:underline text-xs font-medium">

                          View Solutions
                        </button>
                      </td>
                    </tr>
                  ) : (
                    <tr><td colSpan={4} className="px-4 py-6 text-center text-muted-foreground">No problems detected.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </motion.section>

          {/* Page Divider */}
          <div className="relative flex items-center justify-center py-4">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t-2 border-gold/40" style={{ borderImage: 'linear-gradient(90deg, transparent, hsl(var(--gold)), transparent) 1' }} />
            </div>
            <span className="relative bg-background px-4 font-display text-lg font-semibold text-gold tracking-wide">Current Year - Adv Tax, TDS & TCS

            </span>
          </div>

          {/* Advance Tax Schedule */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}>

            <div className="flex items-center gap-2 mb-4">
              <Calendar className="h-5 w-5 text-gold" />
              <h2 className="font-display text-xl font-semibold">Current Year Advance Tax Schedule</h2>
            </div>
            <div className="overflow-x-auto rounded-xl border border-border">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border bg-card">
                    <th className="px-4 py-3 text-left font-medium text-muted-foreground">Quarter</th>
                    <th className="px-4 py-3 text-left font-medium text-muted-foreground">Section</th>
                    <th className="px-4 py-3 text-left font-medium text-muted-foreground">Due Date</th>
                    <th className="px-4 py-3 text-right font-medium text-muted-foreground">Amount</th>
                    <th className="px-4 py-3 text-center font-medium text-muted-foreground">Status</th>
                    <th className="px-4 py-3 text-right font-medium text-muted-foreground">Reminder</th>
                  </tr>
                </thead>
                <tbody>
                  {advanceTax.length > 0 ? advanceTax.map((item: any, i: number) =>
                    <tr key={i} className="border-b border-border last:border-0 hover:bg-card/50 transition-colors">
                      <td className="px-4 py-3 font-medium">{item.quarter}</td>
                      <td className="px-4 py-3">{item.section}</td>
                      <td className="px-4 py-3">{item.dueDate}</td>
                      <td className="px-4 py-3 text-right">{item.amount}</td>
                      <td className="px-4 py-3 text-center">
                        <span
                          className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${item.status === "Paid" ?
                            "bg-green-900/30 text-green-400" :
                            item.status === "Pending" ?
                              "bg-yellow-900/30 text-yellow-400" :
                              "bg-secondary text-muted-foreground"}`
                          }>

                          {item.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right text-muted-foreground">{item.reminder}</td>
                    </tr>
                  ) : (
                    <tr><td colSpan={6} className="px-4 py-6 text-center text-muted-foreground">No advance tax entries.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </motion.section>

          {/* TDS/TCS */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}>

            <div className="flex items-center gap-2 mb-4">
              <FileText className="h-5 w-5 text-gold" />
              <h2 className="font-display text-xl font-semibold">Current Year TDS & TCS</h2>
            </div>
            <div className="overflow-x-auto rounded-xl border border-border">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border bg-card">
                    <th className="px-4 py-3 text-left font-medium text-muted-foreground">Type</th>
                    <th className="px-4 py-3 text-left font-medium text-muted-foreground">Section</th>
                    <th className="px-4 py-3 text-left font-medium text-muted-foreground">Date</th>
                    <th className="px-4 py-3 text-right font-medium text-muted-foreground">TDS Amount</th>
                    <th className="px-4 py-3 text-right font-medium text-muted-foreground">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {tdsTcs.length > 0 ? tdsTcs.map((item: any, i: number) =>
                    <tr key={i} className="border-b border-border last:border-0 hover:bg-card/50 transition-colors">
                      <td className="px-4 py-3">
                        <span className="rounded bg-primary/10 px-2 py-0.5 text-xs font-medium text-gold">
                          {item.type}
                        </span>
                      </td>
                      <td className="px-4 py-3">{item.section}</td>
                      <td className="px-4 py-3">{item.date}</td>
                      <td className="px-4 py-3 text-right font-medium">{item.tdsAmount}</td>
                      <td className="px-4 py-3 text-right">{item.amount}</td>
                    </tr>
                  ) : (
                    <tr><td colSpan={5} className="px-4 py-6 text-center text-muted-foreground">No TDS entries found.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </motion.section>
        </div>
      </div>

      {/* Sync Dialog */}
      <Dialog open={syncDialog} onOpenChange={setSyncDialog}>
        <DialogContent className="dark border-border bg-card text-foreground">
          <DialogHeader>
            <DialogTitle>Enter Portal Credentials</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Please enter your Income Tax Portal password to proceed.
              Your PAN ({pan}) will be used as the username.
            </p>
            <div className="space-y-2">
              <label className="text-sm font-medium">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                placeholder="Enter password"
              />
            </div>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setSyncDialog(false)}
                className="px-4 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground rounded-md"
              >
                Cancel
              </button>
              <button
                onClick={confirmSync}
                className="px-4 py-2 text-sm font-medium bg-gold text-black hover:bg-gold/90 rounded-md"
              >
                Start Sync
              </button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Solutions Dialog */}
      <Dialog
        open={solutionDialog.open}
        onOpenChange={(open) => setSolutionDialog({ open })}>

        <DialogContent className="dark border-border bg-card text-foreground">
          <DialogHeader>
            <DialogTitle className="font-display text-xl">
              Probable Solutions
            </DialogTitle>
          </DialogHeader>
          {solutionDialog.problem &&
            <div className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Issue</p>
                <p className="font-medium">{solutionDialog.problem.wrong}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-2">Recommended Actions</p>
                <ul className="space-y-2">
                  {solutionDialog.problem.solutions.map((s: string, i: number) =>
                    <li key={i} className="flex items-start gap-2 text-sm">
                      <span className="text-gold mt-0.5">•</span>
                      <span>{s}</span>
                    </li>
                  )}
                </ul>
              </div>
            </div>
          }
        </DialogContent>
      </Dialog>

      <Footer />
    </div>);
};

export default Dashboard;