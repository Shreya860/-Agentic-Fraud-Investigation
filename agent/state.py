from dataclasses import dataclass, field
from typing import Any

@dataclass
class InvestigationState:
    """
    Shared state for a fraud investigation.
    """

    customer_id: str
    case_id: str | None = None

    investigation: dict[str, Any] = field(default_factory=dict)
    assessment: dict[str, Any] = field(default_factory=dict)
    memory: dict[str, Any] = field(default_factory=dict)
    plan: dict[str, Any] = field(default_factory=dict)
    decision: dict[str, Any] = field(default_factory=dict)
    critique: dict[str, Any] = field(default_factory=dict)

    status: str = "initialized"

    def update_investigation(self, investigation: dict[str, Any]) -> None:
        self.investigation = investigation
        self.status = "investigated"

    def update_assessment(self, assessment: dict[str, Any]) -> None:
        self.assessment = assessment
        self.status = "assessed"

    def update_memory(self, memory: dict[str, Any]) -> None:
        self.memory = memory

    def update_plan(self, plan: dict[str, Any]) -> None:
        self.plan = plan
        self.status = "planned"

    def update_decision(self, decision: dict[str, Any]) -> None:
        self.decision = decision
        self.status = "decision_ready"

    def update_critique(self, critique: dict[str, Any]) -> None:
        self.critique = critique
        self.status = "reviewed"

    def to_dict(self) -> dict[str, Any]:
        return {
            "customer_id": self.customer_id,
            "case_id": self.case_id,
            "investigation": self.investigation,
            "assessment": self.assessment,
            "memory": self.memory,
            "plan": self.plan,
            "decision": self.decision,
            "critique": self.critique,
            "status": self.status,
        }