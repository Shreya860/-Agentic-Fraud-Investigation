// ─────────────────────────────────────────────────────────────
// FRONTEND DATA SERVICE
// ─────────────────────────────────────────────────────────────
// This module is the ONLY place the UI talks to "data". Today it
// returns in-memory mock objects. When the backend is ready, the
// developer replaces ONLY the bodies below with real API calls.
//
// Rules to keep this file backend-independent:
//   1. No fetch() / axios in mock mode (see USE_BACKEND below).
//   2. Every function is async and returns a Promise, so swapping
//      to fetch() later does not change any calling component.
//   3. Return shapes must match the TypeScript interfaces in
//      src/types/index.ts.
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

// Optional backend integration flag. Left false for the hackathon
// demo so the app runs with zero network dependency.
const USE_BACKEND = false;
const API_BASE = ""; // e.g. "http://localhost:8000"

// Small helper used only if USE_BACKEND is flipped on later.
async function _fetch<T>(path: string, fallback: T): Promise<T> {
  if (!USE_BACKEND) return fallback;
  try {
    const res = await fetch(`${API_BASE}${path}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return (await res.json()) as T;
  } catch {
    return fallback;
  }
}

// Simulate the async nature of real I/O without slowing the UI.
const resolve = <T>(value: T): Promise<T> => Promise.resolve(value);

// ─────────────────────────────────────────────────────────────
// Public API
// ─────────────────────────────────────────────────────────────
export const dataService = {
  // Cases
  getInvestigations(): Promise<InvestigationCase[]> {
    // TODO: replace with _fetch("/cases", mockCases)
    return resolve(mockCases);
  },

  getInvestigation(caseId: string): Promise<InvestigationCase | undefined> {
    // TODO: replace with _fetch(`/cases/${caseId}`, mockCases.find(...))
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
    // In mock data, devices are not directly linked to customers;
    // link via transactions the customer has made.
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
    // In mock data, just return the full list sorted by similarity.
    // Real backend would filter by pattern / signals.
    const sorted = [...mockHistory].sort((a, b) => b.similarity - a.similarity);
    void caseId; // reserved for future use
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