// ─────────────────────────────────────────────────────────────
// FRONTEND DATA SERVICE
// ─────────────────────────────────────────────────────────────
// Live benchmark and static datasets are adapted to the UI domain types here.
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
  ActionType,
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

const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? "";
const STATIC_API_BASE = "";

async function fetchStatic<T>(name: string): Promise<T> {
  const res = await fetch(`${STATIC_API_BASE}/api/${name}.json`);
  if (!res.ok) throw new Error(`${name} fetch failed: ${res.status}`);
  return (await res.json()) as T;
}

export interface AnalyticsData {
  riskDistribution: Record<string, number>;
  recommendedActionDistribution: Partial<Record<ActionType, number>>;
  averageRiskScore: number;
  totalCases: number;
  casesPerCustomer: Record<string, number>;
  casesPerTriggerType: Record<string, number>;
}

// ─────────────────────────────────────────────────────────────
// Public API
// ─────────────────────────────────────────────────────────────
export const dataService = {
  // Cases — LIVE from backend
  async getInvestigations(): Promise<InvestigationCase[]> {
    try {
      const res = await fetch(`${API_BASE}/api/benchmark/summary.json`);
      if (!res.ok) throw new Error(`Benchmark fetch failed: ${res.status}`);
      const rows: any[] = await res.json();

      return rows.map((b): InvestigationCase => {
        const rawTrigger = String(b.benchmark_input?.trigger_type ?? "risk_score");
        const triggerType =
          rawTrigger === "risk_score" ? "Rule Engine" : rawTrigger;

        return {
          caseId: String(b.case_id),
          customerId: String(b.customer_id),
          customerName: String(b.customer_id),
          riskLevel: (b.risk_level ?? "low") as InvestigationCase["riskLevel"],
          riskScore: typeof b.risk_score === "number" ? b.risk_score : 0,
          status: "investigating",
          triggerType,
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
          nextBestAction: (b.recommended_action ??
            "monitor_transaction") as InvestigationCase["nextBestAction"],
          pattern: "",
        };
      });
    } catch (error) {
      console.error("getInvestigations failed:", error);
      return mockCases;
    }
  },

  async getInvestigation(caseId: string): Promise<InvestigationCase | undefined> {
    try {
      const res = await fetch(
        `${API_BASE}/api/benchmark/cases/${caseId}.json`
      );
      if (!res.ok) {
        throw new Error(`Benchmark case fetch failed: ${res.status}`);
      }
      const b = await res.json();

      return {
        caseId: String(b.case_id),
        customerId: String(b.customer_id),
        customerName: String(b.customer_id),
        riskLevel: (b.assessment?.risk_level ?? "low") as InvestigationCase["riskLevel"],
        riskScore:
          typeof b.assessment?.risk_score === "number"
            ? b.assessment.risk_score
            : 0,
        status: "investigating",
        triggerType: "Rule Engine",
        triggerText: String(
          b.benchmark_input?.trigger_text ?? "Automated fraud investigation"
        ),
        flaggedTransactionId: String(b.benchmark_input?.flagged_txn_id ?? ""),
        amount: 0,
        channel: "online",
        assignedAnalyst: "auto",
        createdAt: new Date().toISOString(),
        nextBestAction: (b.decision?.recommended_action ??
          "monitor") as InvestigationCase["nextBestAction"],
        pattern: "",
      };
    } catch (error) {
      console.error(`getInvestigation failed for ${caseId}:`, error);
      return mockCases.find((c) => c.caseId === caseId);
    }
  },

  // Customers
  async getCustomers(): Promise<Customer[]> {
    try {
      return await fetchStatic<Customer[]>("customers");
    } catch (error) {
      console.error("getCustomers failed:", error);
      return mockCustomers;
    }
  },

  async getCustomer(customerId: string): Promise<Customer | undefined> {
    const customers = await this.getCustomers();
    return customers.find((c) => c.customerId === customerId);
  },

  // Transactions
  async getTransactions(): Promise<Transaction[]> {
    try {
      return await fetchStatic<Transaction[]>("transactions");
    } catch (error) {
      console.error("getTransactions failed:", error);
      return mockTransactions;
    }
  },

  async getTransaction(transactionId: string): Promise<Transaction | undefined> {
    const transactions = await this.getTransactions();
    return transactions.find((t) => t.transactionId === transactionId);
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
  async getHistoricalCases(): Promise<HistoricalCase[]> {
    try {
      return await fetchStatic<HistoricalCase[]>("historical-cases");
    } catch (error) {
      console.error("getHistoricalCases failed:", error);
      return mockHistory;
    }
  },

  async getHistoricalCasesForCase(caseId: string): Promise<HistoricalCase[]> {
    const cases = await this.getHistoricalCases();
    void caseId;
    return [...cases].sort((a, b) => b.similarity - a.similarity);
  },

  async getAnalytics(): Promise<AnalyticsData> {
    try {
      return await fetchStatic<AnalyticsData>("analytics");
    } catch (error) {
      console.error("getAnalytics failed:", error);
      return {
        riskDistribution: {},
        recommendedActionDistribution: {},
        averageRiskScore: 0,
        totalCases: 0,
        casesPerCustomer: {},
        casesPerTriggerType: {},
      };
    }
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
  async getGraphData(caseId: string): Promise<GraphData> {
    try {
      const res = await fetch(`${STATIC_API_BASE}/api/graph.json`);
      if (!res.ok) throw new Error(`Graph fetch failed: ${res.status}`);
      return (await res.json()) as GraphData;
    } catch (error) {
      console.error(`getGraphData failed for ${caseId}:`, error);
      return mockGraph[caseId] ?? mockGraph["CASE-48291"];
    }
  },
};

export type DataService = typeof dataService;