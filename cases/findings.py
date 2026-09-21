from typing import Any
def create_finding(
    finding: str,
    confidence: str,
    description: str,
    supporting_evidence: list[str] | None = None,
) -> dict[str, Any]:
    """
    Create a structured investigation finding.
    """

    return {
        "finding": finding,
        "confidence": confidence,
        "description": description,
        "supporting_evidence": supporting_evidence or [],
    }