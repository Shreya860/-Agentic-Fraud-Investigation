import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { dataService } from "../services/dataService";
import type {
  InvestigationCase,
  EvidenceItem,
  TimelineEvent,
  RiskAssessment,
  RecommendedAction,
  ApprovalRequest,
  Uncertainty,
  HistoricalCase,
  GraphData,
} from "../types";
import Card from "../components/Card";
import Badge, { RiskBadge, StatusBadge } from "../components/Badge";
import InvestigationTimeline from "../components/InvestigationTimeline";
import EvidencePanel from "../components/EvidencePanel";
import RiskPanel from "../components/RiskPanel";
import FraudGraph from "../components/FraudGraph";
import CaseMemory from "../components/CaseMemory";
import ActionPanel from "../components/ActionPanel";
import ApprovalPanel from "../components/ApprovalPanel";
import EmptyState from "../components/EmptyState";
import { useApp } from "../context/AppContext";

export default function InvestigationDetails() {
  const { caseId = "" } = useParams<{ caseId: string }>();
  const { pushToast, selectedGraphNodeId, setSelectedGraphNodeId } = useApp();

  const [c, setC] = useState<InvestigationCase | null | undefined>(undefined);
  const [evidence, setEvidence] = useState<EvidenceItem[]>([]);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [risk, setRisk] = useState<RiskAssessment | null>(null);
  const [action, setAction] = useState<RecommendedAction | null>(null);
  const [approval, setApproval] = useState<ApprovalRequest | null>(null);
  const [uncertainty, setUncertainty] = useState<Uncertainty | null>(null);
  const [history, setHistory] = useState<HistoricalCase[]>([]);
  const [graph, setGraph] = useState<GraphData>({ nodes: [], edges: [] });

  useEffect(() => {
    let alive = true;
    Promise.all([
      dataService.getInvestigation(caseId),
      dataService.getEvidence(caseId),
      dataService.getTimeline(caseId),
      dataService.getRiskAssessment(caseId),
      dataService.getRecommendedAction(caseId),
      dataService.getApprovalRequest(caseId),
      dataService.getUncertainty(caseId),
      dataService.getHistoricalCasesForCase(caseId),
      dataService.getGraphData(caseId),
    ]).then(([cc, ev, tl, rk, ac, ap, un, hi, gr]) => {
      if (!alive) return;
      setC(cc ?? null);
      setEvidence(ev);
      setTimeline(tl);
      setRisk(rk);
      setAction(ac);
      setApproval(ap);
      setUncertainty(un);
      setHistory(hi);
      setGraph(gr);
    });
    return () => {
      alive = false;
    };
  }, [caseId]);

  if (c === undefined) return <div className="muted">Loading case…</div>;
  if (c === null) return <EmptyState title="Case not found" subtitle={`No case with id ${caseId}`} />;

  const flaggedTxn = {
    id: c.flaggedTransactionId,
    amount: c.amount,
    channel: c.channel,
  };

  return (
    <div className="stack">
      {/* Header */}
      <div className="card" style={{ padding: 16 }}>
        <div className="row-between">
          <div>
            <div className="row" style={{ gap: 12 }}>
              <h1 className="mono" style={{ fontSize: 18 }}>{c.caseId}</h1>
              <StatusBadge status={c.status} />
              <RiskBadge level={c.riskLevel} score={c.riskScore} />
            </div>
            <div className="small muted mt-1">
              Customer: <Link to={`/customers/${c.customerId}`}>{c.customerName}</Link> · Analyst: {c.assignedAnalyst} · Created {new Date(c.createdAt).toLocaleString()}
            </div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div className="section-title">Risk Score</div>
            <div style={{ fontSize: 26, fontWeight: 700, letterSpacing: "-0.01em" }}>
              {(c.riskScore * 100).toFixed(0)}
              <span className="muted" style={{ fontSize: 13, fontWeight: 500 }}> / 100</span>
            </div>
          </div>
        </div>

        <div className="divider" />

        <div className="grid grid-2">
          <div>
            <div className="section-title">Trigger</div>
            <div style={{ fontSize: 13 }}>{c.triggerType} — {c.triggerText}</div>
          </div>
          <div>
            <div className="section-title">Flagged Transaction</div>
            <div className="row" style={{ gap: 16, fontSize: 13 }}>
              <span className="mono">{flaggedTxn.id}</span>
              <span>${flaggedTxn.amount.toFixed(2)}</span>
              <span>{flaggedTxn.channel}</span>
              {c.pattern && <Badge variant="neutral">{c.pattern}</Badge>}
            </div>
          </div>
        </div>
      </div>

      {/* Main grid */}
      <div className="grid grid-2">
        <Card title="Investigation Timeline" padded>
          <InvestigationTimeline events={timeline} />
        </Card>

        <div className="stack">
          {risk && <RiskPanel risk={risk} />}
          {uncertainty && (
            <Card title="Uncertainty Assessment">
              <div className="section-title">Known</div>
              <ul style={{ marginTop: 0 }}>
                {uncertainty.known.map((k) => <li key={k}>{k}</li>)}
              </ul>
              <div className="section-title mt-3">Unknown</div>
              <ul style={{ marginTop: 0 }}>
                {uncertainty.unknown.map((k) => <li key={k}>{k}</li>)}
              </ul>
              <div className="section-title mt-3">Missing Evidence</div>
              <ul style={{ marginTop: 0 }}>
                {uncertainty.missingEvidence.map((k) => <li key={k}>{k}</li>)}
              </ul>
            </Card>
          )}
        </div>
      </div>

      <Card title="Investigation Reasoning" subtitle="Structured assessment">
        <div className="grid grid-2">
          <div>
            <div className="section-title">Evidence Considered</div>
            <ul>
              {evidence.slice(0, 5).map((e) => (
                <li key={e.id}>
                  <strong>{e.title}</strong> — {e.description}
                </li>
              ))}
            </ul>
            <div className="section-title mt-3">Key Findings</div>
            <ul>
              {risk?.factors.map((f) => (
                <li key={f.id}>{f.label} ({f.severity})</li>
              ))}
            </ul>
          </div>
          <div>
            <div className="section-title">Risk Assessment</div>
            <p style={{ marginTop: 0 }}>{risk?.summary}</p>
            <div className="section-title mt-3">Recommended Next Step</div>
            <p style={{ marginTop: 0 }}>{action?.label}</p>
          </div>
        </div>
      </Card>

      <EvidencePanel items={evidence} />

      <div className="grid grid-2">
        <Card title="Graph Relationships" padded>
          <FraudGraph
            data={graph}
            selectedId={selectedGraphNodeId}
            onSelect={setSelectedGraphNodeId}
          />
          {selectedGraphNodeId && (
            <div className="small muted mt-2">
              Selected node: <span className="mono">{selectedGraphNodeId}</span>
            </div>
          )}
        </Card>
        <CaseMemory cases={history} />
      </div>

      <div className="grid grid-2">
        {action && (
          <ActionPanel
            action={action}
            onRequestApproval={() =>
              pushToast("Approval request sent (mock — backend will handle later).")
            }
            onViewPolicy={() => pushToast(`Policy ${action.policy ?? "—"} (mock view).`)}
            onViewEvidence={() => pushToast("Evidence view opened below (scroll down).")}
            onExecute={() => pushToast("Action executed (mock).")}
          />
        )}
        {approval && <ApprovalPanel request={approval} />}
      </div>
    </div>
  );
}