import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import api from "@/api/client";

interface Notice {
  category: string;
  section: string;
  date: string;
  description: string;
  status: string;
  pdf_link: string;
}

const NoticeHistory = () => {
  const [notices, setNotices] = useState<Notice[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await api.getNoticeHistory();
        setNotices(data);
      } catch (error) {
        console.error("Failed to fetch notice history:", error);
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
            Notices & <span className="text-gold">Orders History</span>
          </h1>
          <p className="text-sm text-muted-foreground mb-8">
            All income tax notices and orders received
          </p>

          <div className="overflow-x-auto rounded-xl border border-border">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-card">
                  <th className="px-4 py-3 text-left font-medium text-muted-foreground">Type</th>
                  <th className="px-4 py-3 text-left font-medium text-muted-foreground">Section</th>
                  <th className="px-4 py-3 text-left font-medium text-muted-foreground">Date</th>
                  <th className="px-4 py-3 text-left font-medium text-muted-foreground">Description</th>
                  <th className="px-4 py-3 text-center font-medium text-muted-foreground">Status</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={5} className="text-center py-4 text-muted-foreground">Loading notices...</td>
                  </tr>
                ) : notices.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="text-center py-4 text-muted-foreground">No notices found.</td>
                  </tr>
                ) : (
                  notices.map((item, i) => (
                    <tr key={i} className="border-b border-border last:border-0 hover:bg-card/50 transition-colors">
                      <td className="px-4 py-3">
                        <span className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${item.category === "Notice" || item.category === "Defective Notice"
                            ? "bg-yellow-900/30 text-yellow-400"
                            : "bg-blue-900/30 text-blue-400"
                          }`}>
                          {item.category}
                        </span>
                      </td>
                      <td className="px-4 py-3 font-medium">{item.section}</td>
                      <td className="px-4 py-3">{item.date}</td>
                      <td className="px-4 py-3">{item.description}</td>
                      <td className="px-4 py-3 text-center">
                        <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${item.status === "Pending"
                            ? "bg-red-900/30 text-red-400"
                            : item.status === "Resolved"
                              ? "bg-green-900/30 text-green-400"
                              : "bg-secondary text-muted-foreground"
                          }`}>
                          {item.status}
                        </span>
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
export default NoticeHistory;
