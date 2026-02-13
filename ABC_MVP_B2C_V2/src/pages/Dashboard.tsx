import { useState } from "react";
import { motion } from "framer-motion";
import { TrendingUp, AlertTriangle, Calendar, FileText } from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle } from
"@/components/ui/dialog";

// Mock data
const missedOpportunities = [
{ ay: "2023-24", opportunity: "Section 80C – PPF contribution not claimed", savings: "₹46,800" },
{ ay: "2023-24", opportunity: "Section 80D – Health Insurance premium", savings: "₹7,800" },
{ ay: "2022-23", opportunity: "HRA exemption under Section 10(13A)", savings: "₹36,000" },
{ ay: "2021-22", opportunity: "NPS additional deduction u/s 80CCD(1B)", savings: "₹15,600" }];


const probableProblems = [
{
  ay: "2023-24",
  wrong: "Mismatch in TDS claimed vs Form 26AS",
  why: "TDS amount claimed ₹12,000 more than reflected in 26AS",
  solutions: ["Verify Form 26AS with employer", "File rectification u/s 154", "Collect corrected TDS certificate"]
},
{
  ay: "2022-23",
  wrong: "Interest income not declared",
  why: "FD interest of ₹45,000 from SBI not reported",
  solutions: ["File revised return if within time", "Declare in next year's return", "Maintain bank statements as proof"]
}];


const advanceTax = [
{ quarter: "Q1", section: "234C", dueDate: "15-Jun-2025", amount: "₹25,000", status: "Paid", reminder: "—" },
{ quarter: "Q2", section: "234C", dueDate: "15-Sep-2025", amount: "₹25,000", status: "Pending", reminder: "45 days" },
{ quarter: "Q3", section: "234C", dueDate: "15-Dec-2025", amount: "₹25,000", status: "Upcoming", reminder: "135 days" },
{ quarter: "Q4", section: "234C", dueDate: "15-Mar-2026", amount: "₹25,000", status: "Upcoming", reminder: "225 days" }];


const tdsTcs = [
{ type: "TDS", section: "192", date: "31-Mar-2025", tdsAmount: "₹1,20,000", amount: "₹12,00,000" },
{ type: "TDS", section: "194A", date: "31-Mar-2025", tdsAmount: "₹4,500", amount: "₹45,000" },
{ type: "TCS", section: "206C", date: "15-Jan-2025", tdsAmount: "₹5,000", amount: "₹5,00,000" }];


const Dashboard = () => {
  const [solutionDialog, setSolutionDialog] = useState<{
    open: boolean;
    problem?: (typeof probableProblems)[0];
  }>({ open: false });

  const pan = sessionStorage.getItem("abc_pan") || "ABCDE1234F";
  const fullName = "Rajesh Kumar Sharma";
  const dob = "15-08-1985";

  // Calculate age in years and months
  const dobDate = new Date(1985, 7, 15); // Aug 15, 1985
  const now = new Date();
  let ageYears = now.getFullYear() - dobDate.getFullYear();
  let ageMonths = now.getMonth() - dobDate.getMonth();
  if (ageMonths < 0 || ageMonths === 0 && now.getDate() < dobDate.getDate()) {
    ageYears--;
    ageMonths += 12;
  }
  if (now.getDate() < dobDate.getDate()) {
    ageMonths--;
    if (ageMonths < 0) ageMonths += 12;
  }

  const panLower = pan.toLowerCase();
  const dobFormatted = "15081985"; // DDMMYYYY
  const userId = `${panLower}${dobFormatted}`;

  return (
    <div className="dark min-h-screen bg-background text-foreground">
      <Navbar isLoggedIn />

      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 rounded-2xl border border-border bg-card p-6">

          <h1 className="font-display text-2xl font-bold">
            Welcome, <span className="text-gold">{fullName}</span>
          </h1>
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
                  {missedOpportunities.map((item, i) =>
                  <tr key={i} className="border-b border-border last:border-0 hover:bg-card/50 transition-colors">
                      <td className="px-4 py-3 text-gold font-medium">{item.ay}</td>
                      <td className="px-4 py-3">{item.opportunity}</td>
                      <td className="px-4 py-3 text-right font-semibold text-gold">{item.savings}</td>
                    </tr>
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
                  {probableProblems.map((item, i) =>
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
                  {advanceTax.map((item, i) =>
                  <tr key={i} className="border-b border-border last:border-0 hover:bg-card/50 transition-colors">
                      <td className="px-4 py-3 font-medium">{item.quarter}</td>
                      <td className="px-4 py-3">{item.section}</td>
                      <td className="px-4 py-3">{item.dueDate}</td>
                      <td className="px-4 py-3 text-right">{item.amount}</td>
                      <td className="px-4 py-3 text-center">
                        <span
                        className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${
                        item.status === "Paid" ?
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
                  {tdsTcs.map((item, i) =>
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
                  )}
                </tbody>
              </table>
            </div>
          </motion.section>
        </div>
      </div>

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
                  {solutionDialog.problem.solutions.map((s, i) =>
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