from pathlib import Path
from typing import Any

import yaml


class PermissionEngine:
    def __init__(self, policy_path: str | None = None):
        if policy_path is None:
            policy_path = str(
                Path(__file__).resolve().parent / "action_matrix.yaml"
            )

        self.policy_path = Path(policy_path)
        self._policy = None

    def _load_policy(self) -> dict[str, Any]:
        if self._policy is None:
            with self.policy_path.open("r", encoding="utf-8") as file:
                self._policy = yaml.safe_load(file) or {}

        return self._policy

    def check_action(self, action: str) -> dict[str, Any]:
        policy = self._load_policy()
        actions = policy.get("actions", {})

        action_policy = actions.get(action)

        if action_policy is None:
            return {
                "action": action,
                "allowed": False,
                "requires_approval": True,
                "approval_route": "policy_admin",
                "category": "unknown",
                "status": "blocked_by_policy",
                "reason": f"Action '{action}' is not defined in the policy.",
            }

        allowed = bool(action_policy.get("allowed", False))
        requires_approval = bool(
            action_policy.get("requires_approval", False)
        )
        approval_route = action_policy.get(
            "approval_route",
            "none",
        )
        category = action_policy.get(
            "category",
            "unknown",
        )

        if not allowed:
            status = "blocked_by_policy"
            reason = f"Action '{action}' is not allowed by policy."

        elif requires_approval:
            status = "awaiting_approval"
            reason = (
                f"Action '{action}' is allowed but requires "
                f"approval from {approval_route}."
            )

        else:
            status = "permitted"
            reason = f"Action '{action}' is permitted by policy."

        return {
            "action": action,
            "allowed": allowed,
            "requires_approval": requires_approval,
            "approval_route": approval_route,
            "category": category,
            "status": status,
            "reason": reason,
        }

    def authorize_decision(self, decision: dict[str, Any]) -> dict[str, Any]:
        """
        Apply the action policy to an agent decision.

        The decision is not executed here.
        This method only determines whether the recommended
        action is permitted and whether approval is required.
        """

        action = decision.get("recommended_action")

        policy_result = self.check_action(action)

        # Attach the complete policy result to the decision.
        decision["policy"] = policy_result

        # Keep a simple top-level policy status for easy access.
        decision["policy_status"] = policy_result.get("status")

        # Update execution status without actually executing anything.
        if not policy_result.get("allowed", False):
            decision["execution_status"] = "blocked_by_policy"

        elif policy_result.get("requires_approval", False):
            decision["execution_status"] = "awaiting_approval"

        else:
            decision["execution_status"] = "permitted"

        return decision


def get_permission_engine() -> PermissionEngine:
    return PermissionEngine()