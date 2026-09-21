from typing import Any
class FraudAssessor:
    """
    Assesses fraud risk from investigation evidence.

    The assessor remains deterministic and data-driven. Historical
    case memory can be supplied to update the uncertainty assessment.
    """

    def assess(
        self,
        investigation: dict[str, Any],
        memory: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        memory = memory or {}

        summary = investigation.get(
            "investigation_summary",
            {},
        )

        findings = investigation.get(
            "findings",
            [],
        )

        evidence = investigation.get(
            "evidence",
            [],
        )

        maximum_risk = self._to_float(
            summary.get("maximum_observed_risk", 0.0)
        )

        high_risk_count = int(
            summary.get("high_risk_transaction_count", 0)
        )

        rare_device_count = int(
            summary.get("rare_device_count", 0)
        )

        fraud_patterns = self._build_patterns(
            maximum_risk=maximum_risk,
            high_risk_count=high_risk_count,
            rare_device_count=rare_device_count,
        )

        risk_level = self._determine_risk_level(
            maximum_risk=maximum_risk,
            high_risk_count=high_risk_count,
            rare_device_count=rare_device_count,
        )

        supporting_evidence = self._get_supporting_evidence(
            evidence=evidence,
            fraud_patterns=fraud_patterns,
        )

        uncertainty = self._build_uncertainty(
            investigation=investigation,
            memory=memory,
            findings=findings,
        )

        assessment_text = self._build_assessment_text(
            risk_level=risk_level,
            maximum_risk=maximum_risk,
            high_risk_count=high_risk_count,
            fraud_patterns=fraud_patterns,
            uncertainty=uncertainty,
        )

        return {
            "status": "assessed",
            "risk_level": risk_level,
            "risk_score": maximum_risk,
            "fraud_patterns": fraud_patterns,
            "supporting_evidence": supporting_evidence,
            "uncertainty": uncertainty,
            "assessment": assessment_text,
            "source_findings": findings,
        }

    def _build_patterns(
        self,
        maximum_risk: float,
        high_risk_count: int,
        rare_device_count: int,
    ) -> list[dict[str, Any]]:
        patterns: list[dict[str, Any]] = []

        if high_risk_count > 0:
            patterns.append(
                {
                    "pattern": "high_risk_transaction_activity",
                    "confidence": "medium",
                    "reason": (
                        "The customer has transaction activity "
                        "with elevated risk scores."
                    ),
                }
            )

        if rare_device_count > 0:
            patterns.append(
                {
                    "pattern": "rare_device_fingerprint",
                    "confidence": "low",
                    "reason": (
                        "The customer is associated with "
                        "relatively rare device fingerprints."
                    ),
                }
            )

        return patterns

    def _determine_risk_level(
        self,
        maximum_risk: float,
        high_risk_count: int,
        rare_device_count: int,
    ) -> str:

        if maximum_risk >= 0.95:
            return "very_high"

        if maximum_risk >= 0.80 or high_risk_count >= 3:
            return "high"

        if (
            maximum_risk >= 0.50
            or rare_device_count > 0
        ):
            return "moderate"

        return "low"

    def _get_supporting_evidence(
        self,
        evidence: list[dict[str, Any]],
        fraud_patterns: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        pattern_names = {
            pattern.get("pattern")
            for pattern in fraud_patterns
        }

        supporting: list[dict[str, Any]] = []

        for item in evidence:
            evidence_type = item.get("type")

            if (
                evidence_type == "high_risk_transactions"
                and "high_risk_transaction_activity"
                in pattern_names
            ):
                supporting.append(
                    {
                        "type": item.get("type"),
                        "severity": item.get("severity"),
                        "description": item.get("description"),
                    }
                )

            elif (
                evidence_type == "rare_device_fingerprint"
                and "rare_device_fingerprint"
                in pattern_names
            ):
                supporting.append(
                    {
                        "type": item.get("type"),
                        "severity": item.get("severity"),
                        "description": item.get("description"),
                    }
                )

            elif evidence_type == "shared_card_network":
                connections = (
                    item.get("data", {})
                    .get("connections", [])
                )

                if connections:
                    supporting.append(
                        {
                            "type": item.get("type"),
                            "severity": item.get("severity"),
                            "description": item.get("description"),
                        }
                    )

        return supporting

    def _build_uncertainty(
        self,
        investigation: dict[str, Any],
        memory: dict[str, Any],
        findings: list[dict[str, Any]],
    ) -> list[str]:

        uncertainty: list[str] = []

        summary = investigation.get(
            "investigation_summary",
            {},
        )

        if summary.get("connected_customer_count_card", 0) == 0:
            uncertainty.append(
                "No shared-card customer connection was identified."
            )

        evidence_types = {
            item.get("type")
            for item in investigation.get("evidence", [])
        }

        if "customer_validation" not in evidence_types:
            uncertainty.append(
                "Customer validation evidence is not currently available."
            )

        if "step_up_authentication" not in evidence_types:
            uncertainty.append(
                "Step-up authentication evidence is not currently available."
            )

        if "external_fraud_intelligence" not in evidence_types:
            uncertainty.append(
                "External fraud intelligence is not currently available."
            )

        historical_matches = memory.get(
            "historical_matches",
            [],
        )

        historical_match_count = memory.get(
            "historical_match_count",
        )

        if historical_match_count is None:
            historical_match_count = len(
                historical_matches
            )

        if historical_match_count == 0:
            uncertainty.append(
                "No similar historical cases were identified."
            )
        else:
            uncertainty.append(
                f"Historical case similarity was evaluated; "
                f"{historical_match_count} matching historical case(s) "
                f"were found."
            )

        return uncertainty

    def _build_assessment_text(
        self,
        risk_level: str,
        maximum_risk: float,
        high_risk_count: int,
        fraud_patterns: list[dict[str, Any]],
        uncertainty: list[str],
    ) -> str:

        pattern_names = [
            pattern["pattern"]
            for pattern in fraud_patterns
        ]

        pattern_text = (
            ", ".join(pattern_names)
            if pattern_names
            else "none identified"
        )

        if uncertainty:
            conclusion = (
                "Additional evidence is required before treating "
                "the assessment as conclusive."
            )
        else:
            conclusion = (
                "The available evidence is currently sufficient "
                "for the assessment."
            )

        return (
            f"Preliminary assessment: {risk_level} risk. "
            f"Maximum observed transaction risk score: "
            f"{maximum_risk:.2f}. "
            f"High-risk transactions identified: "
            f"{high_risk_count}. "
            f"Current pattern hypotheses: {pattern_text}. "
            f"{conclusion}"
        )

    @staticmethod
    def _to_float(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0