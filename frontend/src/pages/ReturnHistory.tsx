import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import api from "@/api/client";

interface ITRFiling {
  ay: string;
  itr_type: string;
  status: string;
  filing_date: string;
  refund_amount: string;
  ack_num: string;
}

const ReturnHistory = () => {
  const [returns, setReturns] = useState<ITRFiling[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await api.getReturnHistory();
        setReturns(data);
      } catch (error) {
        console.error("Failed to fetch return history:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

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
                {loading ? (
                  <tr>
                    <td colSpan={5} className="text-center py-4 text-muted-foreground">Loading history...</td>
                  </tr>
                ) : returns.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="text-center py-4 text-muted-foreground">No returns filed yet.</td>
                  </tr>
                ) : (
                  returns.map((item, i) => (
                    <tr key={i} className="border-b border-border last:border-0 hover:bg-card/50 transition-colors">
                      <td className="px-4 py-3 font-medium text-gold">{item.ay}</td>
                      <td className="px-4 py-3">{item.itr_type}</td>
                      <td className="px-4 py-3 text-center">
                        <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${item.status === "Filed"
                          ? "bg-blue-900/30 text-blue-400"
                          : item.status === "Processed"
                            ? "bg-green-900/30 text-green-400"
                            : "bg-secondary text-muted-foreground"
                          }`}>
                          {item.status}
                        </span>
                      </td>
                      <td className="px-4 py-3">{item.filing_date}</td>
                      <td className="px-4 py-3 text-right font-medium">
                        ₹{Number(item.refund_amount).toLocaleString()}
                      </td>
                    </tr>
                  ))
                )}
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
