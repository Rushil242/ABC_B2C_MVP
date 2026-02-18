
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Loading from "./pages/Loading";
import Questionnaire from "./pages/Questionnaire";

import Dashboard from "./pages/Dashboard";
import ReturnHistory from "./pages/ReturnHistory";
import NoticeHistory from "./pages/NoticeHistory";
import Profile from "./pages/Profile";
import NotFound from "./pages/NotFound";
import { SyncProvider } from "@/context/SyncContext";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <SyncProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/loading" element={<Loading />} />

            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/questionnaire" element={<Questionnaire />} />
            <Route path="/return-history" element={<ReturnHistory />} />
            <Route path="/notice-history" element={<NoticeHistory />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </SyncProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
