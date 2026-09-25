// ─────────────────────────────────────────────────────────────
// FRONTEND DATA SERVICE
// ─────────────────────────────────────────────────────────────
// The Investigations list now reads live benchmark output from
// the FastAPI backend (/api/benchmark/summary). Everything else
// still uses in-memory mock data.
// ─────────────────────────────────────────────────────────────

import type {
  InvestigationCase,
  Customer,
  Transaction,
  Card,
  Device,
  Identity,
  HistoricalCase,
  EvidenceItem,
  TimelineEvent,
  RiskAssessment,
  RecommendedAction,
  ApprovalRequest,
  Uncertainty,
  GraphData,
} from "../types";

import { mockCases } from "../data/mockCases";
import { mockCustomers } from "../data/mockCustomers";
import {
  mockTransactions,
  mockCards,
  mockDevices,
  mockIdentities,
} from "../data/mockTransactions";
import { mockHistory } from "../data/mockHistory";
import {
  mockEvidence,
  defaultEvidence,
  buildTimeline,
  mockRisk,
  defaultRisk,
  mockRecommendedAction,
  defaultRecommendedAction,
  mockApproval,
  defaultApproval,
  mockUncertainty,
  defaultUncertainty,
  mockGraph,
} from "../data/mockEvidence";

// Simulate the async nature of real I/O without slowing the UI.
const resolve = <T>(value: T): Promise<T> => Promise.resolve(value);

const API_BASE = "http://127.0.0.1:8000";

// ─────────────────────────────────────────────────────────────
// Public API
// ─────────────────────────────────────────────────────────────
export const dataService = {
  // Cases — LIVE from backend
  async getInvestigations(): Promise<InvestigationCase[]> {
    const res = await fetch(`${API_BASE}/api/benchmark/summary`);
    if (!res.ok) {
      throw new Error(`Benchmark fetch failed: ${res.status}`);
    }
    const rows: any[] = await res.json();

    return rows.map((b): InvestigationCase => {
      const rawTrigger = String(b.benchmark_input?.trigger_type ?? "risk_score");
      const triggerType =
        rawTrigger === "risk_score" ? "Rule Engine" : rawTrigger;

      return {
        caseId: String(b.case_id),
        customerId: String(b.customer_id),
        customerName: String(b.customer_id),
        riskLevel: (b.risk_level ?? "low") as any,
        riskScore: typeof b.risk_score === "number" ? b.risk_score : 0,
        status: "investigating" as any,
        triggerType: triggerType as any,
        triggerText:
          b.benchmark_input?.trigger_text ??
          "Automated fraud investigation",
        flaggedTransactionId: String(
          b.benchmark_input?.flagged_txn_id ?? ""
        ),
        amount: 0,
        channel: "online",
        assignedAnalyst: "auto",
        createdAt: new Date().toISOString(),
        nextBestAction: (b.recommended_action ?? "monitor") as any,
        pattern: "",
      } as unknown as InvestigationCase;
    });
  },

  getInvestigation(caseId: string): Promise<InvestigationCase | undefined> {
    return resolve(mockCases.find((c) => c.caseId === caseId));
  },

  // Customers
  getCustomers(): Promise<Customer[]> {
    return resolve(mockCustomers);
  },

  getCustomer(customerId: string): Promise<Customer | undefined> {
    return resolve(mockCustomers.find((c) => c.customerId === customerId));
  },

  // Transactions
  getTransactions(): Promise<Transaction[]> {
    return resolve(mockTransactions);
  },

  getTransaction(transactionId: string): Promise<Transaction | undefined> {
    return resolve(
      mockTransactions.find((t) => t.transactionId === transactionId)
    );
  },

  // Cards / Devices / Identities
  getCards(): Promise<Card[]> {
    return resolve(mockCards);
  },

  getDevices(): Promise<Device[]> {
    return resolve(mockDevices);
  },

  getIdentities(): Promise<Identity[]> {
    return resolve(mockIdentities);
  },

  getCardsForCustomer(customerId: string): Promise<Card[]> {
    return resolve(mockCards.filter((c) => c.customerId === customerId));
  },

  getDevicesForCustomer(customerId: string): Promise<Device[]> {
    const deviceIds = new Set(
      mockTransactions
        .filter((t) => t.customerId === customerId)
        .map((t) => t.deviceId)
    );
    return resolve(mockDevices.filter((d) => deviceIds.has(d.deviceId)));
  },

  getIdentitiesForCustomer(customerId: string): Promise<Identity[]> {
    return resolve(mockIdentities.filter((i) => i.customerId === customerId));
  },

  // Historical cases
  getHistoricalCases(): Promise<HistoricalCase[]> {
    return resolve(mockHistory);
  },

  getHistoricalCasesForCase(caseId: string): Promise<HistoricalCase[]> {
    const sorted = [...mockHistory].sort((a, b) => b.similarity - a.similarity);
    void caseId;
    return resolve(sorted);
  },

  // Case-scoped
  getEvidence(caseId: string): Promise<EvidenceItem[]> {
    return resolve(mockEvidence[caseId] ?? defaultEvidence);
  },

  getTimeline(caseId: string): Promise<TimelineEvent[]> {
    const c = mockCases.find((x) => x.caseId === caseId);
    const createdAt = c?.createdAt ?? new Date().toISOString();
    return resolve(buildTimeline(createdAt));
  },

  getRiskAssessment(caseId: string): Promise<RiskAssessment> {
    return resolve(mockRisk[caseId] ?? defaultRisk);
  },

  getRecommendedAction(caseId: string): Promise<RecommendedAction> {
    return resolve(mockRecommendedAction[caseId] ?? defaultRecommendedAction);
  },

  getApprovalRequest(caseId: string): Promise<ApprovalRequest> {
    return resolve(mockApproval[caseId] ?? defaultApproval(caseId));
  },

  getUncertainty(caseId: string): Promise<Uncertainty> {
    return resolve(mockUncertainty[caseId] ?? defaultUncertainty);
  },

  // Graph
  getGraphData(caseId: string): Promise<GraphData> {
    return resolve(mockGraph[caseId] ?? mockGraph["CASE-48291"]);
  },
};

export type DataService = typeof dataService;