from datetime import datetime, timezone
from typing import Any


def create_evidence(
    evidence_type: str,
    source: str,
    description: str,
    strength: str = "medium",
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "evidence_id": _generate_evidence_id(),
        "evidence_type": evidence_type,
        "source": source,
        "description": description,
        "strength": strength,
        "data": data or {},
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }


def _generate_evidence_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"EVD-{timestamp}"