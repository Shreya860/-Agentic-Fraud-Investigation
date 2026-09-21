from typing import Any
from cases.case_manager import get_case_manager
class CaseTools:
    """
    Tools for creating and managing investigation cases.
    """

    def __init__(self):
        self.case_manager = get_case_manager()

    def create_case(
        self,
        customer_id: str,
        trigger_type: str = "analyst_request",
        trigger_text: str = "",
        flagged_txn_id: str | None = None,
    ) -> dict[str, Any]:
        return self.case_manager.create_case(
            customer_id=customer_id,
            trigger_type=trigger_type,
            trigger_text=trigger_text,
            flagged_txn_id=flagged_txn_id,
        )

    def get_case(self, case_id: str) -> dict[str, Any] | None:
        return self.case_manager.get_case(case_id)

    def add_evidence(
        self,
        case_id: str,
        evidence: dict[str, Any],
    ) -> dict[str, Any]:
        return self.case_manager.add_evidence(
            case_id=case_id,
            evidence=evidence,
        )

    def add_finding(
        self,
        case_id: str,
        finding: dict[str, Any],
    ) -> dict[str, Any]:
        return self.case_manager.add_finding(
            case_id=case_id,
            finding=finding,
        )

    def add_decision(
        self,
        case_id: str,
        decision: dict[str, Any],
    ) -> dict[str, Any]:
        return self.case_manager.add_decision(
            case_id=case_id,
            decision=decision,
        )

    def add_action(
        self,
        case_id: str,
        action: dict[str, Any],
    ) -> dict[str, Any]:
        return self.case_manager.add_action(
            case_id=case_id,
            action=action,
        )

    def update_risk_level(
        self,
        case_id: str,
        risk_level: str,
    ) -> dict[str, Any]:
        return self.case_manager.update_risk_level(
            case_id=case_id,
            risk_level=risk_level,
        )

    def close_case(self, case_id: str) -> dict[str, Any]:
        return self.case_manager.close_case(case_id)