import { motion } from "framer-motion";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

const notices = [
  { type: "Notice", section: "143(1)", date: "15-Dec-2024", description: "Intimation under section 143(1) for AY 2024-25", status: "Pending" },
  { type: "Notice", section: "139(9)", date: "10-Sep-2023", description: "Defective return notice for AY 2023-24", status: "Resolved" },
  { type: "Order", section: "154", date: "20-Mar-2023", description: "Rectification order for AY 2022-23", status: "Completed" },
  { type: "Notice", section: "245", date: "05-Jan-2022", description: "Set off of refund against demand for AY 2021-22", status: "Resolved" },
];

const NoticeHistory = () => {
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
                {notices.map((item, i) => (
                  <tr key={i} className="border-b border-border last:border-0 hover:bg-card/50 transition-colors">
                    <td className="px-4 py-3">
                      <span className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${
                        item.type === "Notice"
                          ? "bg-yellow-900/30 text-yellow-400"
                          : "bg-blue-900/30 text-blue-400"
                      }`}>
                        {item.type}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-medium">{item.section}</td>
                    <td className="px-4 py-3">{item.date}</td>
                    <td className="px-4 py-3">{item.description}</td>
                    <td className="px-4 py-3 text-center">
                      <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${
                        item.status === "Pending"
                          ? "bg-red-900/30 text-red-400"
                          : item.status === "Resolved"
                          ? "bg-green-900/30 text-green-400"
                          : "bg-secondary text-muted-foreground"
                      }`}>
                        {item.status}
                      </span>
                    </td>
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

export default NoticeHistory;
