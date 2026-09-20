from typing import Any

from cases.models import create_case, utc_now


class CaseManager:
    """Manage the lifecycle and investigation records of fraud cases."""

    def __init__(self):
        self._cases: dict[str, dict[str, Any]] = {}

    def create_case(
        self,
        case_id: str,
        customer_id: str,
        trigger_type: str,
        trigger_text: str,
        flagged_txn_id: str | None = None,
    ) -> dict[str, Any]:
        if case_id in self._cases:
            return self._cases[case_id]

        case = create_case(
            case_id=case_id,
            customer_id=customer_id,
            trigger_type=trigger_type,
            trigger_text=trigger_text,
            flagged_txn_id=flagged_txn_id,
        )

        self._cases[case_id] = case
        return case

    def get_case(self, case_id: str) -> dict[str, Any] | None:
        return self._cases.get(case_id)

    def add_evidence(
        self,
        case_id: str,
        evidence: dict[str, Any],
    ) -> dict[str, Any]:
        case = self._require_case(case_id)

        case["evidence"].append(evidence)
        case["updated_at"] = utc_now()

        return case

    def add_finding(
        self,
        case_id: str,
        finding: dict[str, Any],
    ) -> dict[str, Any]:
        case = self._require_case(case_id)

        case["findings"].append(finding)
        case["updated_at"] = utc_now()

        return case

    def add_decision(
        self,
        case_id: str,
        decision: dict[str, Any],
    ) -> dict[str, Any]:
        case = self._require_case(case_id)

        case["decisions"].append(decision)
        case["updated_at"] = utc_now()

        return case

    def add_action(
        self,
        case_id: str,
        action: dict[str, Any],
    ) -> dict[str, Any]:
        case = self._require_case(case_id)

        case["actions"].append(action)
        case["updated_at"] = utc_now()

        return case

    def add_approval_request(
        self,
        case_id: str,
        approval: dict[str, Any],
    ) -> dict[str, Any]:
        case = self._require_case(case_id)

        case["approval_requests"].append(approval)
        case["updated_at"] = utc_now()

        return case

    def update_risk_level(
        self,
        case_id: str,
        risk_level: str,
    ) -> dict[str, Any]:
        case = self._require_case(case_id)

        case["risk_level"] = risk_level
        case["updated_at"] = utc_now()

        return case

    def update_status(
        self,
        case_id: str,
        status: str,
    ) -> dict[str, Any]:
        case = self._require_case(case_id)

        case["status"] = status
        case["updated_at"] = utc_now()

        if status == "closed":
            case["closed_at"] = utc_now()

        return case

    def close_case(
        self,
        case_id: str,
    ) -> dict[str, Any]:
        return self.update_status(case_id, "closed")

    def list_cases(self) -> list[dict[str, Any]]:
        return list(self._cases.values())

    def _require_case(self, case_id: str) -> dict[str, Any]:
        case = self.get_case(case_id)

        if case is None:
            raise ValueError(f"Case '{case_id}' does not exist.")

        return case


def get_case_manager() -> CaseManager:
    return CaseManager()