from typing import Any
def create_action(
    action: str,
    reason: str = "",
    approval_required: bool = False,
    approval_route: str | None = None,
    execution_status: str = "not_executed",
) -> dict[str, Any]:
    """
    Create a structured case action.

    The action itself is supplied dynamically by the decision engine.
    This function only standardizes the action record.
    """

    return {
        "action": action,
        "reason": reason,
        "approval_required": approval_required,
        "approval_route": approval_route,
        "execution_status": execution_status,
    }