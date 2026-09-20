from pathlib import Path
from typing import Any
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]

HISTORICAL_CASE_FILE = (
    ROOT / "data" / "raw" / "HHGOA_IEEE" / "closed_cases_history.csv"
)

class CaseMemory:
    """Store active cases and retrieve similar historical investigations."""

    def __init__(
        self,
        historical_case_file: Path = HISTORICAL_CASE_FILE,
    ):
        self.historical_case_file = Path(historical_case_file)

        self._cases: dict[str, dict[str, Any]] = {}
        self._historical_cases: pd.DataFrame | None = None

    # Active / newly created cases
   
    def store_case(self, case: dict[str, Any]) -> dict[str, Any]:
        case_id = case.get("case_id")

        if not case_id:
            raise ValueError("Case must contain a case_id.")

        self._cases[case_id] = case

        return case

    def get_case(self, case_id: str) -> dict[str, Any] | None:
        return self._cases.get(case_id)

    def list_cases(self) -> list[dict[str, Any]]:
        return list(self._cases.values())

    # Historical cases
    
    def _load_historical_cases(self) -> pd.DataFrame:
        if self._historical_cases is None:
            if not self.historical_case_file.exists():
                raise FileNotFoundError(
                    f"Historical case file not found: "
                    f"{self.historical_case_file}"
                )

            self._historical_cases = pd.read_csv(
                self.historical_case_file
            )

        return self._historical_cases

    def find_similar_historical_cases(
        self,
        customer_id: str | None = None,
        risk_level: str | None = None,
        fraud_pattern: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        df = self._load_historical_cases()

        matches = []

        for _, row in df.iterrows():
            score = 0
            reasons = []

            row_customer = self._clean_value(row.get("customer_id"))
            row_pattern = self._clean_value(row.get("pattern"))

            # Customer match
            if (
                customer_id
                and row_customer is not None
                and str(row_customer) == str(customer_id)
            ):
                score += 3
                reasons.append("same_customer")

            # Historical pattern match
            if fraud_pattern and row_pattern:
                if str(fraud_pattern).lower() in str(row_pattern).lower():
                    score += 3
                    reasons.append("same_fraud_pattern")

            # Risk level is not directly stored in the historical
            # dataset, so we do not infer it from other fields.
            if risk_level:
                pass

            if score > 0:
                matches.append(
                    {
                        "case_id": self._clean_value(row.get("case_id")),
                        "customer_id": row_customer,
                        "card_id": self._clean_value(row.get("card_id")),
                        "outcome": self._clean_value(row.get("outcome")),
                        "pattern": row_pattern,
                        "first_fraud_txn_id": self._clean_value(
                            row.get("first_fraud_txn_id")
                        ),
                        "n_txns": self._clean_value(row.get("n_txns")),
                        "exposure_usd": self._clean_value(
                            row.get("exposure_usd")
                        ),
                        "actions_taken": self._clean_value(
                            row.get("actions_taken")
                        ),
                        "report_filed": self._clean_value(
                            row.get("report_filed")
                        ),
                        "analyst_notes": self._clean_value(
                            row.get("analyst_notes")
                        ),
                        "similarity_score": score,
                        "similarity_reasons": reasons,
                    }
                )

        matches.sort(
            key=lambda item: item["similarity_score"],
            reverse=True,
        )

        return matches[:limit]

    # ------------------------------------------------------------------
    # Similarity for active cases
    # ------------------------------------------------------------------

    def find_similar_cases(
        self,
        customer_id: str | None = None,
        risk_level: str | None = None,
        fraud_pattern: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        matches = []

        for case in self._cases.values():
            score = 0
            reasons = []

            if customer_id and case.get("customer_id") == customer_id:
                score += 3
                reasons.append("same_customer")

            if risk_level and case.get("risk_level") == risk_level:
                score += 2
                reasons.append("same_risk_level")

            if fraud_pattern:
                case_patterns = self._extract_patterns(case)

                if fraud_pattern in case_patterns:
                    score += 3
                    reasons.append("same_fraud_pattern")

            if score > 0:
                matches.append(
                    {
                        "case": case,
                        "similarity_score": score,
                        "similarity_reasons": reasons,
                    }
                )

        matches.sort(
            key=lambda item: item["similarity_score"],
            reverse=True,
        )

        return matches[:limit]

    @staticmethod
    def _extract_patterns(
        case: dict[str, Any],
    ) -> list[str]:
        patterns = []

        for finding in case.get("findings", []):
            if isinstance(finding, dict):
                finding_type = finding.get("type")

                if finding_type:
                    patterns.append(str(finding_type))

        for decision in case.get("decisions", []):
            if isinstance(decision, dict):
                for pattern in decision.get("fraud_patterns", []):
                    patterns.append(str(pattern))

        return list(dict.fromkeys(patterns))

    @staticmethod
    def _clean_value(value: Any) -> Any:
        if pd.isna(value):
            return None

        if hasattr(value, "item"):
            try:
                return value.item()
            except (ValueError, TypeError):
                pass

        return value


def get_case_memory() -> CaseMemory:
    return CaseMemory()