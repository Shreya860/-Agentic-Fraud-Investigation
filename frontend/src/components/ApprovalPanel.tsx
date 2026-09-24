import { useState } from "react";
import type { ApprovalRequest } from "../types";
import { useApp } from "../context/AppContext";
import Badge from "./Badge";
import ConfirmDialog from "./ConfirmDialog";

interface Props {
  request: ApprovalRequest;
}

export default function ApprovalPanel({ request }: Props) {
  const { approvals, registerApproval, setApprovalStatus, pushToast } = useApp();
  const [confirm, setConfirm] = useState<null | "approve" | "reject">(null);

  // register on first render if not yet known
  if (!approvals[request.caseId]) {
    registerApproval(request);
  }
  const live = approvals[request.caseId] ?? request;

  const onConfirm = () => {
    const choice = confirm;
    setConfirm(null);
    if (!choice) return;
    const status = choice === "approve" ? "approved" : "rejected";
    setApprovalStatus(live.caseId, status);
    pushToast(
      `Approval ${status} for ${live.caseId}`,
      status === "approved" ? "ok" : "error"
    );
  };

  const badge =
    live.status === "pending" ? (
      <Badge variant="warn">Pending</Badge>
    ) : live.status === "approved" ? (
      <Badge variant="ok">Approved</Badge>
    ) : (
      <Badge variant="danger">Rejected</Badge>
    );

  return (
    <section className="card">
      <header className="card-header">
        <h2>Approval Required</h2>
        <span style={{ marginLeft: "auto" }}>{badge}</span>
      </header>

      <div className="card-body">
        <dl className="kv">
          <dt>Action</dt>       <dd>{live.action}</dd>
          <dt>Requested By</dt> <dd>{live.requestedBy}</dd>
          <dt>Reason</dt>       <dd>{live.reason}</dd>
          <dt>Policy</dt>       <dd className="mono">{live.policy}</dd>
          <dt>Status</dt>       <dd>{live.status}</dd>
        </dl>

        <div className="divider" />

        {live.status === "pending" ? (
          <div className="row" style={{ gap: 8 }}>
            <button className="btn btn-ok" onClick={() => setConfirm("approve")}>
              Approve
            </button>
            <button className="btn btn-danger" onClick={() => setConfirm("reject")}>
              Reject
            </button>
          </div>
        ) : (
          <div className="small muted">
            {live.status === "approved"
              ? "Approved by A. Kapoor — confirmation recorded locally."
              : "Rejected by A. Kapoor — confirmation recorded locally."}
          </div>
        )}
      </div>

      <ConfirmDialog
        open={confirm !== null}
        title={confirm === "approve" ? "Approve action?" : "Reject action?"}
        message={
          confirm === "approve"
            ? `You are approving "${live.action}" for ${live.caseId}.`
            : `You are rejecting "${live.action}" for ${live.caseId}.`
        }
        confirmLabel={confirm === "approve" ? "Approve" : "Reject"}
        danger={confirm === "reject"}
        onCancel={() => setConfirm(null)}
        onConfirm={onConfirm}
      />
    </section>
  );
}