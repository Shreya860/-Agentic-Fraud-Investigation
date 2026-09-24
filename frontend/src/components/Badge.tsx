import type { ReactNode } from "react";
import type { RiskLevel, InvestigationStatus, ApprovalStatus } from "../types";

type Variant = "low" | "moderate" | "high" | "very_high" | "neutral" | "ok" | "warn" | "danger";

interface BadgeProps {
  variant?: Variant;
  children: ReactNode;
}

export default function Badge({ variant = "neutral", children }: BadgeProps) {
  return <span className={`badge badge-${variant}`}>{children}</span>;
}

export function RiskBadge({ level, score }: { level: RiskLevel; score?: number }) {
  const label: Record<RiskLevel, string> = {
    low: "Low",
    moderate: "Moderate",
    high: "High",
    very_high: "Very High",
  };
  return (
    <Badge variant={level}>
      {label[level]}
      {typeof score === "number" && ` · ${(score * 100).toFixed(0)}`}
    </Badge>
  );
}

export function StatusBadge({ status }: { status: InvestigationStatus }) {
  const labels: Record<InvestigationStatus, string> = {
    open: "Open",
    investigating: "Investigating",
    awaiting_approval: "Awaiting Approval",
    action_executed: "Action Executed",
    resolved: "Resolved",
    closed: "Closed",
  };
  const variant: Record<InvestigationStatus, Variant> = {
    open: "moderate",
    investigating: "warn",
    awaiting_approval: "warn",
    action_executed: "ok",
    resolved: "ok",
    closed: "neutral",
  };
  return <Badge variant={variant[status]}>{labels[status]}</Badge>;
}

export function ApprovalBadge({ status }: { status: ApprovalStatus }) {
  const variant: Record<ApprovalStatus, Variant> = {
    pending: "warn",
    approved: "ok",
    rejected: "danger",
  };
  const label: Record<ApprovalStatus, string> = {
    pending: "Pending",
    approved: "Approved",
    rejected: "Rejected",
  };
  return <Badge variant={variant[status]}>{label[status]}</Badge>;
}