from typing import Any
class CaseDNA:
    """Create a compact investigation fingerprint for a fraud case."""

    def build(self, case: dict[str, Any]) -> dict[str, Any]:
        findings = case.get("findings", [])
        decisions = case.get("decisions", [])
        evidence = case.get("evidence", [])

        finding_types = self._unique_values(
            finding.get("type")
            for finding in findings
            if isinstance(finding, dict)
        )
        fraud_patterns = self._unique_values(
            pattern
            for decision in decisions
            if isinstance(decision, dict)
            for pattern in decision.get("fraud_patterns", [])
        )
        evidence_types = self._unique_values(
            item.get("evidence_type")
            for item in evidence
            if isinstance(item, dict)
        )
        actions = self._unique_values(
            action.get("action")
            for action in case.get("actions", [])
            if isinstance(action, dict)
        )
        return {
            "case_id": case.get("case_id"),
            "customer_id": case.get("customer_id"),
            "risk_level": case.get("risk_level"),
            "trigger_type": case.get("trigger_type"),
            "finding_types": finding_types,
            "fraud_patterns": fraud_patterns,
            "evidence_types": evidence_types,
            "actions": actions,
        }

    @staticmethod
    def _unique_values(values) -> list[str]:
        return list(
            dict.fromkeys(
                str(value)
                for value in values
                if value is not None
            )
        )

    def build_search_profile(
        self,
        case: dict[str, Any],
    ) -> dict[str, Any]:
        """Create search parameters from the case DNA."""
        dna = self.build(case)
        return {
            "customer_id": dna["customer_id"],
            "risk_level": dna["risk_level"],
            "fraud_patterns": dna["fraud_patterns"],
            "finding_types": dna["finding_types"],
            "evidence_types": dna["evidence_types"],
        }

def get_case_dna() -> CaseDNA:
    return CaseDNA()