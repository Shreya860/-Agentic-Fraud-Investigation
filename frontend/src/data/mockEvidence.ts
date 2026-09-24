import type {
  EvidenceItem,
  TimelineEvent,
  RiskAssessment,
  RecommendedAction,
  ApprovalRequest,
  Uncertainty,
  GraphData,
} from "../types";

// ─────────────────────────────────────────────────────────────
// Per-case evidence. Keyed by caseId. Falls back to a default
// set for any case not explicitly present.
// ─────────────────────────────────────────────────────────────
export const mockEvidence: Record<string, EvidenceItem[]> = {
  "CASE-48291": [
    { id: "EV-1", category: "transaction", type: "supporting", title: "High-risk transaction",       description: "Transaction TXN-847291 of $1,249.00 on an e-commerce channel from an unrecognized merchant.", confidence: "high",   source: "Transaction Service", timestamp: "2024-06-11T09:14:00Z" },
    { id: "EV-2", category: "device",      type: "supporting", title: "Shared device fingerprint",   description: "Device DEV-91A2 fingerprint shared with 3 other customer accounts.",                            confidence: "high",   source: "Knowledge Graph",     timestamp: "2024-06-11T09:15:00Z" },
    { id: "EV-3", category: "behavioral",  type: "supporting", title: "Unusual transaction amount",  description: "Amount is 12x the customer's 90-day average transaction value.",                                confidence: "high",   source: "Behavioral Engine",   timestamp: "2024-06-11T09:16:00Z" },
    { id: "EV-4", category: "historical",  type: "supporting", title: "Historical case similarity",  description: "Matches pattern of CASE-48291 'Account Takeover' with 92% similarity.",                          confidence: "high",   source: "Case Memory",         timestamp: "2024-06-11T09:17:00Z" },
    { id: "EV-5", category: "identity",    type: "supporting", title: "Recently registered email",   description: "Customer email domain registered only 3 days before the flagged transaction.",                  confidence: "medium", source: "Identity Service",    timestamp: "2024-06-11T09:18:00Z" },
    { id: "EV-6", category: "customer",    type: "contradicting", title: "Long-standing account",    description: "Account has been open for 6 years with no prior fraud history.",                                 confidence: "medium", source: "Customer Profile",    timestamp: "2024-06-11T09:19:00Z" },
  ],
};

export const defaultEvidence: EvidenceItem[] = [
  { id: "EV-D1", category: "transaction", type: "supporting", title: "Flagged transaction",     description: "Transaction flagged by the rule engine for review.",   confidence: "high",   source: "Rule Engine",     timestamp: "2024-06-11T09:00:00Z" },
  { id: "EV-D2", category: "behavioral",  type: "supporting", title: "Behavioral deviation",    description: "Transaction deviates from the customer's baseline.",    confidence: "medium", source: "Behavioral Engine", timestamp: "2024-06-11T09:01:00Z" },
];

// ─────────────────────────────────────────────────────────────
// Timeline (same for every case, driven by case.createdAt where used)
// ─────────────────────────────────────────────────────────────
export const buildTimeline = (createdAt: string): TimelineEvent[] => {
  const base = new Date(createdAt).getTime();
  const at = (mins: number) => new Date(base + mins * 60_000).toISOString();
  return [
    { id: "T1",  step: 1,  label: "Fraud signal received",            status: "done",    timestamp: at(0) },
    { id: "T2",  step: 2,  label: "Case created",                     status: "done",    timestamp: at(1) },
    { id: "T3",  step: 3,  label: "Transaction history retrieved",    status: "done",    timestamp: at(2) },
    { id: "T4",  step: 4,  label: "Customer evidence analyzed",       status: "done",    timestamp: at(3) },
    { id: "T5",  step: 5,  label: "Device relationship analyzed",     status: "done",    timestamp: at(4) },
    { id: "T6",  step: 6,  label: "Historical cases searched",        status: "done",    timestamp: at(5) },
    { id: "T7",  step: 7,  label: "Risk assessed",                    status: "done",    timestamp: at(6) },
    { id: "T8",  step: 8,  label: "Uncertainty evaluated",            status: "done",    timestamp: at(7) },
    { id: "T9",  step: 9,  label: "Next-best-action generated",       status: "done",    timestamp: at(8) },
    { id: "T10", step: 10, label: "Approval requested",               status: "active" },
    { id: "T11", step: 11, label: "Action executed",                  status: "pending" },
    { id: "T12", step: 12, label: "Case memory updated",              status: "pending" },
  ];
};

// ─────────────────────────────────────────────────────────────
// Per-case risk assessment. Falls back to defaultRisk.
// ─────────────────────────────────────────────────────────────
export const mockRisk: Record<string, RiskAssessment> = {
  "CASE-48291": {
    score: 94, level: "very_high",
    summary: "The available evidence indicates elevated fraud risk. Multiple independent signals support further intervention.",
    factors: [
      { id: "RF-1", label: "High-risk transaction",       severity: "critical", description: "Transaction above fraud threshold on an unfamiliar merchant.",  confidence: "high" },
      { id: "RF-2", label: "Shared device",               severity: "high",     description: "Device fingerprint linked to 3 unrelated customer accounts.",    confidence: "high" },
      { id: "RF-3", label: "Unusual transaction amount",  severity: "high",     description: "Amount 12x customer's 90-day average.",                          confidence: "high" },
      { id: "RF-4", label: "Historical case similarity",  severity: "medium",   description: "92% match to a confirmed account-takeover case.",                confidence: "high" },
      { id: "RF-5", label: "New device",                  severity: "medium",   description: "Device first observed 4 days ago.",                              confidence: "medium" },
      { id: "RF-6", label: "Geographic anomaly",          severity: "medium",   description: "Transaction originating country differs from customer profile.", confidence: "medium" },
    ],
  },
};

export const defaultRisk: RiskAssessment = {
  score: 55, level: "moderate",
  summary: "Risk signals are present but not conclusive. Additional evidence is required.",
  factors: [
    { id: "RF-D1", label: "Behavioral deviation", severity: "medium", description: "Transaction deviates from baseline.", confidence: "medium" },
  ],
};

// ─────────────────────────────────────────────────────────────
// Recommended action (one per case, falls back)
// ─────────────────────────────────────────────────────────────
export const mockRecommendedAction: Record<string, RecommendedAction> = {
  "CASE-48291": {
    type: "request_customer_validation",
    label: "Request Customer Validation",
    reason:
      "Customer authorization has not yet been established and additional evidence is required before taking a stronger action.",
    status: "awaiting_approval",
    policy: "FRAUD-TRX-001",
  },
};

export const defaultRecommendedAction: RecommendedAction = {
  type: "monitor_transaction",
  label: "Monitor Transaction",
  reason: "Risk is moderate; continue monitoring for additional signals.",
  status: "proposed",
};

// ─────────────────────────────────────────────────────────────
// Approval request
// ─────────────────────────────────────────────────────────────
export const mockApproval: Record<string, ApprovalRequest> = {
  "CASE-48291": {
    id: "APR-001",
    caseId: "CASE-48291",
    action: "Block Transaction",
    requestedBy: "Fraud Investigation Agent",
    reason: "Very high fraud risk",
    policy: "FRAUD-TRX-001",
    status: "pending",
  },
};

export const defaultApproval = (caseId: string): ApprovalRequest => ({
  id: `APR-${caseId}`,
  caseId,
  action: "Escalate to Analyst",
  requestedBy: "Fraud Investigation Agent",
  reason: "Requires analyst review.",
  policy: "FRAUD-GEN-000",
  status: "pending",
});

// ─────────────────────────────────────────────────────────────
// Uncertainty
// ─────────────────────────────────────────────────────────────
export const mockUncertainty: Record<string, Uncertainty> = {
  "CASE-48291": {
    known: [
      "Transaction is high risk",
      "Device is associated with other accounts",
      "Similar historical cases exist",
    ],
    unknown: [
      "Whether customer authorized the transaction",
      "Whether device sharing is legitimate",
      "Whether additional identity verification will clear the risk",
    ],
    missingEvidence: [
      "Customer validation",
      "Step-up authentication",
      "Additional identity verification",
    ],
  },
};

export const defaultUncertainty: Uncertainty = {
  known: ["Transaction flagged for review"],
  unknown: ["Whether the customer authorized the transaction"],
  missingEvidence: ["Customer validation"],
};

// ─────────────────────────────────────────────────────────────
// Graph data (mock). Keys are graph focus IDs.
// ─────────────────────────────────────────────────────────────
export const mockGraph: Record<string, GraphData> = {
  "CASE-48291": {
    nodes: [
      { id: "CUS-10482", label: "Priya Sharma",    type: "customer",    x: 0.10, y: 0.50 },
      { id: "TXN-847291", label: "TXN-847291",     type: "transaction", x: 0.30, y: 0.50 },
      { id: "CARD-8831", label: "Card ••••4421",   type: "card",        x: 0.50, y: 0.30 },
      { id: "DEV-91A2",  label: "DEV-91A2",        type: "device",      x: 0.50, y: 0.70 },
      { id: "CUS-70014", label: "Sneha Patel",     type: "customer",    x: 0.70, y: 0.85 },
      { id: "CASE-48291",label: "CASE-48291",      type: "case",        x: 0.90, y: 0.50 },
      { id: "IDN-001",   label: "new email",       type: "identity",    x: 0.70, y: 0.20 },
    ],
    edges: [
      { id: "E1", from: "CUS-10482",  to: "TXN-847291", label: "initiated" },
      { id: "E2", from: "TXN-847291", to: "CARD-8831",  label: "used card" },
      { id: "E3", from: "TXN-847291", to: "DEV-91A2",   label: "from device" },
      { id: "E4", from: "DEV-91A2",   to: "CUS-70014",  label: "shared with" },
      { id: "E5", from: "CUS-10482",  to: "CASE-48291", label: "subject of" },
      { id: "E6", from: "IDN-001",    to: "CUS-10482",  label: "identity signal" },
    ],
  },
};