import type { ActionType, RecommendedAction } from "../types";
import { actionLabels } from "../data/mockCases";
import Badge from "./Badge";

interface Props {
  action: RecommendedAction;
  onRequestApproval?: () => void;
  onViewPolicy?: () => void;
  onViewEvidence?: () => void;
  onExecute?: () => void;
}

const allActions: ActionType[] = [
  "allow_transaction",
  "monitor_transaction",
  "block_transaction",
  "block_account",
  "request_customer_validation",
  "request_step_up_auth",
  "retrieve_similar_cases",
  "escalate_to_analyst",
  "create_investigation_case",
];

function statusBadge(a: RecommendedAction) {
  switch (a.status) {
    case "awaiting_approval": return <Badge variant="warn">Awaiting Approval</Badge>;
    case "approved":          return <Badge variant="ok">Approved</Badge>;
    case "rejected":          return <Badge variant="danger">Rejected</Badge>;
    case "executed":          return <Badge variant="ok">Executed</Badge>;
    default:                  return <Badge variant="neutral">Proposed</Badge>;
  }
}

export default function ActionPanel({
  action,
  onRequestApproval,
  onViewPolicy,
  onViewEvidence,
  onExecute,
}: Props) {
  const isAwaiting = action.status === "awaiting_approval";

  return (
    <section className="card">
      <header className="card-header">
        <h2>Next Best Action</h2>
        <span className="card-title-sub">AI-recommended</span>
      </header>

      <div className="card-body">
        <div className="section-title">Recommended Action</div>
        <div className="row-between mb-3">
          <div style={{ fontSize: 16, fontWeight: 700, letterSpacing: "-0.01em" }}>
            {action.label}
          </div>
          {statusBadge(action)}
        </div>

        <div className="section-title">Reason</div>
        <p style={{ margin: "0 0 16px", fontSize: 13, color: "var(--text-2)", lineHeight: 1.6 }}>
          {action.reason}
        </p>

        {action.policy && (
          <>
            <div className="section-title">Policy</div>
            <div className="mono mb-3">{action.policy}</div>
          </>
        )}

        <div className="row" style={{ gap: 8, flexWrap: "wrap" }}>
          <button
            className="btn btn-primary"
            onClick={onRequestApproval}
            disabled={isAwaiting || action.status === "approved" || action.status === "executed"}
          >
            Request Approval
          </button>
          <button className="btn" onClick={onViewPolicy}>
            View Policy
          </button>
          <button className="btn" onClick={onViewEvidence}>
            View Evidence
          </button>
          <button
            className="btn btn-ok"
            onClick={onExecute}
            disabled={action.status !== "approved"}
            style={{ marginLeft: "auto" }}
          >
            Execute Action
          </button>
        </div>

        <div className="divider" />

        <details>
          <summary className="small muted" style={{ cursor: "pointer" }}>
            Other possible actions
          </summary>
          <ul className="small muted" style={{ marginTop: 8, paddingLeft: 18 }}>
            {allActions
              .filter((a) => a !== action.type)
              .map((a) => (
                <li key={a}>{actionLabels[a]}</li>
              ))}
          </ul>
        </details>
      </div>
    </section>
  );
}