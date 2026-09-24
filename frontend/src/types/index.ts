// ─────────────────────────────────────────────────────────────
// Shared domain types for the Fraud Investigation frontend.
// These interfaces define the shape the UI expects from the
// data layer. When the real backend is connected, the API
// responses should match these shapes (or be adapted in
// src/services/dataService.ts).
// ─────────────────────────────────────────────────────────────

export type RiskLevel = "low" | "moderate" | "high" | "very_high";

export type InvestigationStatus =
  | "open"
  | "investigating"
  | "awaiting_approval"
  | "action_executed"
  | "resolved"
  | "closed";

export type ApprovalStatus = "pending" | "approved" | "rejected";

export type ActionType =
  | "allow_transaction"
  | "monitor_transaction"
  | "block_transaction"
  | "block_account"
  | "request_customer_validation"
  | "request_step_up_auth"
  | "retrieve_similar_cases"
  | "escalate_to_analyst"
  | "create_investigation_case";

export type ActionStatus =
  | "proposed"
  | "awaiting_approval"
  | "approved"
  | "rejected"
  | "executed";

export type EvidenceCategory =
  | "transaction"
  | "customer"
  | "card"
  | "device"
  | "identity"
  | "behavioral"
  | "historical"
  | "external";

export type EvidenceType = "supporting" | "contradicting" | "neutral";
export type Confidence = "low" | "medium" | "high";
export type Severity = "low" | "medium" | "high" | "critical";

export interface InvestigationCase {
  caseId: string;
  status: InvestigationStatus;
  riskLevel: RiskLevel;
  riskScore: number;              // 0..1
  triggerType: string;
  triggerText: string;
  customerId: string;
  customerName: string;
  flaggedTransactionId: string;
  amount: number;
  channel: string;
  createdAt: string;              // ISO date string
  assignedAnalyst: string;
  nextBestAction: ActionType;
  pattern?: string;
}

export interface Customer {
  customerId: string;
  name: string;
  email: string;
  riskLevel: RiskLevel;
  riskScore: number;              // 0..1
  transactionCount: number;
  deviceCount: number;
  cardCount: number;
  openCases: number;
  lastActivity: string;
  country: string;
  accountAgeYears: number;
}

export interface Transaction {
  transactionId: string;
  customerId: string;
  customerName: string;
  amount: number;
  currency: string;
  channel: string;
  timestamp: string;
  riskScore: number;              // 0..1
  riskLevel: RiskLevel;
  status: "approved" | "pending" | "flagged" | "blocked";
  cardId: string;
  deviceId: string;
  merchant: string;
  location: string;
}

export interface Card {
  cardId: string;
  customerId: string;
  last4: string;
  network: string;
  type: "credit" | "debit";
  status: "active" | "frozen" | "cancelled";
}

export interface Device {
  deviceId: string;
  fingerprint: string;
  os: string;
  firstSeen: string;
  lastSeen: string;
  linkedCustomers: number;
}

export interface Identity {
  identityId: string;
  customerId: string;
  signal: string;
  value: string;
  confidence: Confidence;
}

export interface HistoricalCase {
  caseId: string;
  pattern: string;
  customerId: string;
  customerName: string;
  riskLevel: RiskLevel;
  similarity: number;             // 0..1
  outcome: "confirmed_fraud" | "false_positive" | "inconclusive";
  date: string;
  summary: string;
}

export interface EvidenceItem {
  id: string;
  category: EvidenceCategory;
  type: EvidenceType;
  title: string;
  description: string;
  confidence: Confidence;
  source: string;
  timestamp: string;
}

export interface RiskFactor {
  id: string;
  label: string;
  severity: Severity;
  description: string;
  confidence: Confidence;
}

export interface RiskAssessment {
  score: number;                  // 0..100
  level: RiskLevel;
  summary: string;
  factors: RiskFactor[];
}

export interface TimelineEvent {
  id: string;
  step: number;
  label: string;
  status: "done" | "active" | "pending";
  timestamp?: string;
}

export interface GraphNode {
  id: string;
  label: string;
  type: "customer" | "transaction" | "card" | "device" | "identity" | "case";
  x: number;                      // normalized 0..1 for simple layout
  y: number;                      // normalized 0..1
}

export interface GraphEdge {
  id: string;
  from: string;
  to: string;
  label: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface RecommendedAction {
  type: ActionType;
  label: string;
  reason: string;
  status: ActionStatus;
  policy?: string;
}

export interface ApprovalRequest {
  id: string;
  caseId: string;
  action: string;
  requestedBy: string;
  reason: string;
  policy: string;
  status: ApprovalStatus;
}

export interface Uncertainty {
  known: string[];
  unknown: string[];
  missingEvidence: string[];
}