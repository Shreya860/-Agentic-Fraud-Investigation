from typing import Any
from policy.permissions import PermissionEngine

class PolicyTools:
    """
    Tools for checking and authorizing fraud-investigation actions
    through the policy engine.
    """

    def __init__(
        self,
        permission_engine: PermissionEngine | None = None,
    ):
        self.permission_engine = (
            permission_engine or PermissionEngine()
        )

    def authorize_action(
        self,
        action: str,
        reason: str = "",
        approval_route: str | None = None,
    ) -> dict[str, Any]:
        """
        Authorize an action through the existing policy engine.
        """

        decision: dict[str, Any] = {
            "recommended_action": action,
            "reason": reason,
        }

        if approval_route:
            decision["approval_route"] = approval_route

        return self.permission_engine.authorize_decision(
            decision
        )

    def is_allowed(
        self,
        action: str,
    ) -> bool:
        """
        Check whether an action is allowed by policy.
        """

        policy = self.get_policy(action)

        if not policy:
            return False

        return bool(policy.get("allowed", False))

    def get_policy(
        self,
        action: str,
    ) -> dict[str, Any] | None:
        """
        Get the policy definition for an action.
        """

        return self.permission_engine.get_policy(action)