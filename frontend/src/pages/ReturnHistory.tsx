import { motion } from "framer-motion";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

const returns = [
  { ay: "2024-25", itr: "ITR 2", status: "Filed", filingDate: "31-Jul-2024", refund: "₹18,500" },
  { ay: "2023-24", itr: "ITR 1", status: "Processed", filingDate: "28-Jul-2023", refund: "₹12,000" },
  { ay: "2022-23", itr: "ITR 1", status: "Processed", filingDate: "31-Jul-2022", refund: "—" },
  { ay: "2021-22", itr: "ITR 1", status: "Processed", filingDate: "15-Mar-2022", refund: "₹8,200" },
  { ay: "2020-21", itr: "ITR 1", status: "Processed", filingDate: "10-Jan-2021", refund: "—" },
];

const ReturnHistory = () => {
  return (
    <div className="dark min-h-screen bg-background text-foreground">
      <Navbar isLoggedIn />

      <div className="container mx-auto px-4 py-8">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="font-display text-3xl font-bold mb-2">
            Income Tax <span className="text-gold">Return History</span>
          </h1>
          <p className="text-sm text-muted-foreground mb-8">
            Status of all previously filed income tax returns
          </p>

          <div className="overflow-x-auto rounded-xl border border-border">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-card">
                  <th className="px-4 py-3 text-left font-medium text-muted-foreground">AY</th>
                  <th className="px-4 py-3 text-left font-medium text-muted-foreground">ITR Type</th>
                  <th className="px-4 py-3 text-center font-medium text-muted-foreground">Status</th>
                  <th className="px-4 py-3 text-left font-medium text-muted-foreground">Filing Date</th>
                  <th className="px-4 py-3 text-right font-medium text-muted-foreground">Refund Claimed</th>
                </tr>
              </thead>
              <tbody>
                {returns.map((item, i) => (
                  <tr key={i} className="border-b border-border last:border-0 hover:bg-card/50 transition-colors">
                    <td className="px-4 py-3 font-medium text-gold">{item.ay}</td>
                    <td className="px-4 py-3">{item.itr}</td>
                    <td className="px-4 py-3 text-center">
                      <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${
                        item.status === "Filed"
                          ? "bg-blue-900/30 text-blue-400"
                          : "bg-green-900/30 text-green-400"
                      }`}>
                        {item.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">{item.filingDate}</td>
                    <td className="px-4 py-3 text-right font-medium">{item.refund}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>

      <Footer />
    </div>
  );
};

export default ReturnHistory;
