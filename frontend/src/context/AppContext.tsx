import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { ApprovalRequest, ApprovalStatus } from "../types";

export interface Toast {
  id: number;
  message: string;
  kind?: "info" | "ok" | "error";
}

interface AppContextValue {
  toasts: Toast[];
  pushToast: (message: string, kind?: Toast["kind"]) => void;
  dismissToast: (id: number) => void;

  approvals: Record<string, ApprovalRequest>;
  registerApproval: (req: ApprovalRequest) => void;
  setApprovalStatus: (caseId: string, status: ApprovalStatus) => void;

  selectedGraphNodeId: string | null;
  setSelectedGraphNodeId: (id: string | null) => void;
}

const AppContext = createContext<AppContextValue | null>(null);

let toastSeq = 1;

export function AppProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [approvals, setApprovals] = useState<Record<string, ApprovalRequest>>({});
  const [selectedGraphNodeId, setSelectedGraphNodeId] = useState<string | null>(null);

  const pushToast = useCallback((message: string, kind: Toast["kind"] = "info") => {
    const id = toastSeq++;
    setToasts((t) => [...t, { id, message, kind }]);
    window.setTimeout(() => {
      setToasts((t) => t.filter((x) => x.id !== id));
    }, 4000);
  }, []);

  const dismissToast = useCallback((id: number) => {
    setToasts((t) => t.filter((x) => x.id !== id));
  }, []);

  const registerApproval = useCallback((req: ApprovalRequest) => {
    setApprovals((prev) => (prev[req.caseId] ? prev : { ...prev, [req.caseId]: req }));
  }, []);

  const setApprovalStatus = useCallback((caseId: string, status: ApprovalStatus) => {
    setApprovals((prev) => {
      const existing = prev[caseId];
      if (!existing) return prev;
      return { ...prev, [caseId]: { ...existing, status } };
    });
  }, []);

  const value = useMemo<AppContextValue>(
    () => ({
      toasts,
      pushToast,
      dismissToast,
      approvals,
      registerApproval,
      setApprovalStatus,
      selectedGraphNodeId,
      setSelectedGraphNodeId,
    }),
    [
      toasts,
      pushToast,
      dismissToast,
      approvals,
      registerApproval,
      setApprovalStatus,
      selectedGraphNodeId,
    ]
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp(): AppContextValue {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used inside <AppProvider>");
  return ctx;
}