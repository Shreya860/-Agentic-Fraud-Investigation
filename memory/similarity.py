from typing import Any
class CaseSimilarity:
    """Calculate explainable similarity between investigation profiles."""

    def compare(
        self,
        current_profile: dict[str, Any],
        historical_case: dict[str, Any],
    ) -> dict[str, Any]:
        score = 0
        reasons = []
        current_customer = current_profile.get("customer_id")
        historical_customer = historical_case.get("customer_id")
        if (
            current_customer
            and historical_customer
            and str(current_customer) == str(historical_customer)
        ):
            score += 3
            reasons.append("same_customer")
        current_patterns = set(
            current_profile.get("fraud_patterns", [])
        )
        historical_pattern = historical_case.get("pattern")
        if historical_pattern in current_patterns:
            score += 3
            reasons.append("same_fraud_pattern")
        current_risk = current_profile.get("risk_level")
        if current_risk:
            reasons.append(
                f"current_risk_level:{current_risk}"
            )

        return {
            "historical_case_id": historical_case.get("case_id"),
            "similarity_score": score,
            "similarity_reasons": reasons,
            "historical_pattern": historical_pattern,
            "historical_outcome": historical_case.get("outcome"),
            "historical_actions": historical_case.get(
                "actions_taken"
            ),
            "historical_exposure_usd": historical_case.get(
                "exposure_usd"
            ),
        }

def get_case_similarity() -> CaseSimilarity:
    return CaseSimilarity()