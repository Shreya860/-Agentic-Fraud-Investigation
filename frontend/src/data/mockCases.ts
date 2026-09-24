import type { InvestigationCase, InvestigationStatus, ActionType } from "../types";

export const mockCases: InvestigationCase[] = [
  {
    caseId: "CASE-48291", status: "investigating", riskLevel: "very_high", riskScore: 0.94,
    triggerType: "Customer Report", triggerText: "Customer reported an unfamiliar transaction.",
    customerId: "CUS-10482", customerName: "Priya Sharma", flaggedTransactionId: "TXN-847291",
    amount: 1249.00, channel: "E-commerce", createdAt: "2024-06-11T09:14:00Z",
    assignedAnalyst: "A. Kapoor", nextBestAction: "request_customer_validation", pattern: "Account Takeover",
  },
  {
    caseId: "CASE-48292", status: "awaiting_approval", riskLevel: "high", riskScore: 0.78,
    triggerType: "Rule Engine", triggerText: "Wire transfer to high-risk jurisdiction.",
    customerId: "CUS-20391", customerName: "Rahul Mehta", flaggedTransactionId: "TXN-923812",
    amount: 3200.00, channel: "Wire", createdAt: "2024-06-11T07:45:00Z",
    assignedAnalyst: "S. Rao", nextBestAction: "block_transaction", pattern: "Wire Fraud",
  },
  {
    caseId: "CASE-48293", status: "open", riskLevel: "high", riskScore: 0.91,
    triggerType: "Device Signal", triggerText: "New device linked to 4 customer accounts.",
    customerId: "CUS-50911", customerName: "Meera Krishnan", flaggedTransactionId: "TXN-931045",
    amount: 890.00, channel: "E-commerce", createdAt: "2024-06-11T07:25:00Z",
    assignedAnalyst: "A. Kapoor", nextBestAction: "request_step_up_auth", pattern: "New Device Fraud",
  },
  {
    caseId: "CASE-48294", status: "action_executed", riskLevel: "very_high", riskScore: 0.97,
    triggerType: "Amount Anomaly", triggerText: "Transaction 12x customer baseline.",
    customerId: "CUS-70014", customerName: "Sneha Patel", flaggedTransactionId: "TXN-931047",
    amount: 4500.00, channel: "Wire", createdAt: "2024-06-11T09:58:00Z",
    assignedAnalyst: "M. Iyer", nextBestAction: "block_account", pattern: "Account Takeover",
  },
  {
    caseId: "CASE-48295", status: "open", riskLevel: "high", riskScore: 0.81,
    triggerType: "Rule Engine", triggerText: "Repeated wire transfers to unknown recipient.",
    customerId: "CUS-98765", customerName: "Rohit Bansal", flaggedTransactionId: "TXN-931050",
    amount: 1800.00, channel: "Wire", createdAt: "2024-06-11T06:35:00Z",
    assignedAnalyst: "S. Rao", nextBestAction: "escalate_to_analyst", pattern: "Wire Fraud",
  },
  {
    caseId: "CASE-48296", status: "resolved", riskLevel: "moderate", riskScore: 0.62,
    triggerType: "Behavioral", triggerText: "Unusual transaction timing.",
    customerId: "CUS-34821", customerName: "Ananya Iyer", flaggedTransactionId: "TXN-923813",
    amount: 210.75, channel: "E-commerce", createdAt: "2024-06-10T21:35:00Z",
    assignedAnalyst: "M. Iyer", nextBestAction: "allow_transaction", pattern: "Card Not Present",
  },
  {
    caseId: "CASE-48297", status: "investigating", riskLevel: "moderate", riskScore: 0.55,
    triggerType: "Behavioral", triggerText: "Velocity spike in low-value transactions.",
    customerId: "CUS-92017", customerName: "Divya Menon", flaggedTransactionId: "TXN-931049",
    amount: 600.00, channel: "E-commerce", createdAt: "2024-06-10T16:05:00Z",
    assignedAnalyst: "A. Kapoor", nextBestAction: "monitor_transaction", pattern: "Card Testing",
  },
  {
    caseId: "CASE-48298", status: "closed", riskLevel: "low", riskScore: 0.23,
    triggerType: "Rule Engine", triggerText: "Low-risk anomaly auto-closed.",
    customerId: "CUS-41120", customerName: "Vikram Nair", flaggedTransactionId: "TXN-931044",
    amount: 45.00, channel: "UPI", createdAt: "2024-06-10T18:15:00Z",
    assignedAnalyst: "S. Rao", nextBestAction: "allow_transaction", pattern: "Benign",
  },
  {
    caseId: "CASE-48299", status: "open", riskLevel: "moderate", riskScore: 0.49,
    triggerType: "Behavioral", triggerText: "New merchant category for customer.",
    customerId: "CUS-60233", customerName: "Arjun Verma", flaggedTransactionId: "TXN-931057",
    amount: 740.00, channel: "E-commerce", createdAt: "2024-06-10T10:35:00Z",
    assignedAnalyst: "M. Iyer", nextBestAction: "retrieve_similar_cases", pattern: "Merchant Anomaly",
  },
  {
    caseId: "CASE-48300", status: "resolved", riskLevel: "low", riskScore: 0.31,
    triggerType: "Rule Engine", triggerText: "Verified by customer via SMS.",
    customerId: "CUS-81200", customerName: "Karthik Rao", flaggedTransactionId: "TXN-931048",
    amount: 120.00, channel: "UPI", createdAt: "2024-06-08T11:35:00Z",
    assignedAnalyst: "A. Kapoor", nextBestAction: "allow_transaction", pattern: "Benign",
  },
];

export const actionLabels: Record<ActionType, string> = {
  allow_transaction: "Allow Transaction",
  monitor_transaction: "Monitor Transaction",
  block_transaction: "Block Transaction",
  block_account: "Block Account",
  request_customer_validation: "Request Customer Validation",
  request_step_up_auth: "Request Step-Up Authentication",
  retrieve_similar_cases: "Retrieve Similar Cases",
  escalate_to_analyst: "Escalate to Analyst",
  create_investigation_case: "Create Investigation Case",
};

export const statusLabels: Record<InvestigationStatus, string> = {
  open: "Open",
  investigating: "Investigating",
  awaiting_approval: "Awaiting Approval",
  action_executed: "Action Executed",
  resolved: "Resolved",
  closed: "Closed",
};