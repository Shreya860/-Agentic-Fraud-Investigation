from typing import Any
class OutcomeMemory:
    """Extract reusable outcome information from historical cases."""

    def summarize(self, historical_case: dict[str, Any]) -> dict[str, Any]:
        actions = self._parse_actions(
            historical_case.get("actions_taken")
        )
        return {
            "case_id": historical_case.get("case_id"),
            "pattern": historical_case.get("pattern"),
            "outcome": historical_case.get("outcome"),
            "actions": actions,
            "report_filed": historical_case.get("report_filed"),
            "exposure_usd": historical_case.get("exposure_usd"),
            "transaction_count": historical_case.get("n_txns"),
            "analyst_notes": historical_case.get("analyst_notes"),
        }

    @staticmethod
    def _parse_actions(actions_taken: Any) -> list[str]:
        if not actions_taken:
            return []
        if isinstance(actions_taken, list):
            return [
                str(action).strip()
                for action in actions_taken
                if str(action).strip()
            ]
        return [
            action.strip()
            for action in str(actions_taken).split("|")
            if action.strip()
        ]

def get_outcome_memory() -> OutcomeMemory:
    return OutcomeMemory()