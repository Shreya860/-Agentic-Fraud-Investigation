from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_case(
    case_id: str,
    customer_id: str,
    trigger_type: str,
    trigger_text: str,
    flagged_txn_id: str | None = None,
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "customer_id": customer_id,
        "trigger_type": trigger_type,
        "trigger_text": trigger_text,
        "flagged_txn_id": flagged_txn_id,
        "status": "open",
        "risk_level": "unknown",
        "findings": [],
        "evidence": [],
        "decisions": [],
        "actions": [],
        "approval_requests": [],
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "closed_at": None,
    }