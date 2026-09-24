import { Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "../layouts/AppLayout";

import Dashboard from "../pages/Dashboard";
import Investigations from "../pages/Investigations";
import InvestigationDetails from "../pages/InvestigationDetails";
import Customers from "../pages/Customers";
import CustomerDetails from "../pages/CustomerDetails";
import Transactions from "../pages/Transactions";
import TransactionDetails from "../pages/TransactionDetails";
import KnowledgeGraph from "../pages/KnowledgeGraph";
import CaseMemoryPage from "../pages/CaseMemoryPage";
import Analytics from "../pages/Analytics";
import Reports from "../pages/Reports";
import Settings from "../pages/Settings";

export default function AppRoutes() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/investigations" element={<Investigations />} />
        <Route path="/investigations/:caseId" element={<InvestigationDetails />} />
        <Route path="/customers" element={<Customers />} />
        <Route path="/customers/:customerId" element={<CustomerDetails />} />
        <Route path="/transactions" element={<Transactions />} />
        <Route path="/transactions/:transactionId" element={<TransactionDetails />} />
        <Route path="/graph" element={<KnowledgeGraph />} />
        <Route path="/case-memory" element={<CaseMemoryPage />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Route>
    </Routes>
  );
}