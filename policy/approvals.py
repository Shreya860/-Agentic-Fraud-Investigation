from datetime import datetime, timezone
from typing import Any
class ApprovalManager:
    """Manage human approval for actions that require authorization."""
    def request_approval(
        self,
        action: str,
        reason: str,
        approval_route: str,
    ) -> dict[str, Any]:
        return {
            "approval_id": self._generate_approval_id(action),
            "action": action,
            "reason": reason,
            "approval_route": approval_route,
            "status": "pending",
            "requested_at": self._now(),
            "approved_at": None,
            "approved_by": None,
            "decision": None,
        }
    def approve(
        self,
        approval: dict[str, Any],
        approved_by: str,
    ) -> dict[str, Any]:
        if approval.get("status") != "pending":
            return {
                **approval,
                "status": "unchanged",
                "error": "Only pending approvals can be approved.",
            }
        return {
            **approval,
            "status": "approved",
            "approved_at": self._now(),
            "approved_by": approved_by,
            "decision": "approved",
        }
    def reject(
        self,
        approval: dict[str, Any],
        rejected_by: str,
        reason: str = "",
    ) -> dict[str, Any]:
        if approval.get("status") != "pending":
            return {
                **approval,
                "status": "unchanged",
                "error": "Only pending approvals can be rejected.",
            }
        return {
            **approval,
            "status": "rejected",
            "approved_at": None,
            "approved_by": rejected_by,
            "decision": "rejected",
            "rejection_reason": reason,
        }
    @staticmethod
    def _generate_approval_id(action: str) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        safe_action = action.replace(" ", "_")
        return f"APR-{safe_action}-{timestamp}"
    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

def get_approval_manager() -> ApprovalManager:
    return ApprovalManager()