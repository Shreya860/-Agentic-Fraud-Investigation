from typing import Any


class FraudAssessor:
    """
    Assesses investigation evidence and produces a preliminary
    fraud risk assessment.

    This component does not execute actions.
    It evaluates the evidence collected by FraudInvestigator.
    """

    def assess(
        self,
        investigation: dict[str, Any],
    ) -> dict[str, Any]:

        if investigation.get("status") != "investigated":
            return {
                "status": "insufficient_data",
                "risk_level": "unknown",
                "risk_score": None,
                "fraud_patterns": [],
                "uncertainty": [
                    "Customer investigation data is unavailable."
                ],
                "assessment": "Unable to assess the case.",
            }

        evidence = investigation.get(
            "evidence",
            [],
        )

        findings = investigation.get(
            "findings",
            [],
        )

        summary = investigation.get(
            "investigation_summary",
            {},
        )

        # --------------------------------------------------------
        # Collect evidence signals
        # --------------------------------------------------------

        maximum_risk = summary.get(
            "maximum_observed_risk"
        )

        high_risk_count = summary.get(
            "high_risk_transaction_count",
            0,
        )

        rare_device_count = summary.get(
            "rare_device_count",
            0,
        )

        shared_card_count = summary.get(
            "connected_customer_count_card",
            0,
        )

        shared_device_count = summary.get(
            "connected_customer_count_device",
            0,
        )

        # --------------------------------------------------------
        # Determine risk level
        # --------------------------------------------------------

        risk_level = self._determine_risk_level(
            maximum_risk=maximum_risk,
            high_risk_count=high_risk_count,
            rare_device_count=rare_device_count,
            shared_card_count=shared_card_count,
            shared_device_count=shared_device_count,
        )

        # --------------------------------------------------------
        # Build fraud-pattern hypotheses
        # --------------------------------------------------------

        fraud_patterns = self._identify_patterns(
            investigation=investigation,
        )

        # --------------------------------------------------------
        # Identify uncertainty
        # --------------------------------------------------------

        uncertainty = self._identify_uncertainty(
            investigation=investigation,
        )

        # --------------------------------------------------------
        # Evidence summary
        # --------------------------------------------------------

        supporting_evidence = self._supporting_evidence(
            evidence
        )

        # --------------------------------------------------------
        # Assessment statement
        # --------------------------------------------------------

        assessment = self._build_assessment(
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
            "assessment": assessment,
            "source_findings": findings,
        }

    # ============================================================
    # RISK
    # ============================================================

    @staticmethod
    def _determine_risk_level(
        maximum_risk: float | None,
        high_risk_count: int,
        rare_device_count: int,
        shared_card_count: int,
        shared_device_count: int,
    ) -> str:

        risk = float(maximum_risk or 0.0)

        # Very high transaction risk combined with
        # additional network evidence.
        if risk >= 0.95 and (
            rare_device_count > 0
            or shared_card_count > 0
            or shared_device_count > 0
        ):
            return "very_high"

        if risk >= 0.95:
            return "high"

        if risk >= 0.80:
            return "high"

        if risk >= 0.60:
            return "moderate"

        if high_risk_count > 0:
            return "moderate"

        return "low"

    # ============================================================
    # PATTERN IDENTIFICATION
    # ============================================================

    def _identify_patterns(
        self,
        investigation: dict[str, Any],
    ) -> list[dict[str, Any]]:

        patterns: list[dict[str, Any]] = []

        summary = investigation.get(
            "investigation_summary",
            {},
        )

        maximum_risk = float(
            summary.get(
                "maximum_observed_risk"
            ) or 0.0
        )

        rare_device_count = summary.get(
            "rare_device_count",
            0,
        )

        shared_card_count = summary.get(
            "connected_customer_count_card",
            0,
        )

        # --------------------------------------------------------
        # High-risk transaction activity
        # --------------------------------------------------------

        if maximum_risk >= 0.80:

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

        # --------------------------------------------------------
        # Shared card pattern
        # --------------------------------------------------------

        if shared_card_count > 0:

            patterns.append(
                {
                    "pattern": "shared_card_network",
                    "confidence": "medium",
                    "reason": (
                        "The customer is connected to other "
                        "customers through shared card information."
                    ),
                }
            )

        # --------------------------------------------------------
        # Rare device pattern
        # --------------------------------------------------------

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

        # --------------------------------------------------------
        # No identified pattern
        # --------------------------------------------------------

        if not patterns:

            patterns.append(
                {
                    "pattern": "no_confirmed_pattern",
                    "confidence": "low",
                    "reason": (
                        "Available evidence does not yet "
                        "support a specific fraud pattern."
                    ),
                }
            )

        return patterns

    # ============================================================
    # UNCERTAINTY
    # ============================================================

    def _identify_uncertainty(
        self,
        investigation: dict[str, Any],
    ) -> list[str]:

        uncertainty: list[str] = []

        summary = investigation.get(
            "investigation_summary",
            {},
        )

        if summary.get(
            "connected_customer_count_card",
            0,
        ) == 0:

            uncertainty.append(
                "No shared-card customer connection was identified."
            )

        if summary.get(
            "rare_device_count",
            0,
        ) == 0:

            uncertainty.append(
                "No rare device fingerprint was identified."
            )

        if summary.get(
            "high_risk_transaction_count",
            0,
        ) == 0:

            uncertainty.append(
                "No high-risk transaction was identified "
                "by the current threshold."
            )

        # The current graph tool does not yet provide
        # customer validation, authentication, external data,
        # or confirmed fraud outcomes.
        uncertainty.extend(
            [
                "Customer validation evidence is not currently available.",
                "Step-up authentication evidence is not currently available.",
                "External fraud intelligence is not currently available.",
                "Historical case similarity has not yet been evaluated.",
            ]
        )

        return uncertainty

    # ============================================================
    # SUPPORTING EVIDENCE
    # ============================================================

    @staticmethod
    def _supporting_evidence(
        evidence: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        supported = []

        for item in evidence:

            severity = item.get(
                "severity",
                "informational",
            )

            if severity in {
                "very_high",
                "high",
                "suspicious",
                "moderate",
            }:

                supported.append(
                    {
                        "type": item.get("type"),
                        "severity": severity,
                        "description": item.get(
                            "description"
                        ),
                    }
                )

        return supported

    # ============================================================
    # ASSESSMENT TEXT
    # ============================================================

    @staticmethod
    def _build_assessment(
        risk_level: str,
        maximum_risk: float | None,
        high_risk_count: int,
        fraud_patterns: list[dict[str, Any]],
        uncertainty: list[str],
    ) -> str:

        risk_text = (
            f"{maximum_risk:.2f}"
            if maximum_risk is not None
            else "unavailable"
        )

        pattern_names = [
            pattern["pattern"]
            for pattern in fraud_patterns
            if pattern["pattern"]
            != "no_confirmed_pattern"
        ]

        if pattern_names:

            pattern_text = ", ".join(
                pattern_names
            )

        else:

            pattern_text = (
                "no specific fraud pattern identified"
            )

        return (
            f"Preliminary assessment: {risk_level} risk. "
            f"Maximum observed transaction risk score: "
            f"{risk_text}. "
            f"High-risk transactions identified: "
            f"{high_risk_count}. "
            f"Current pattern hypotheses: "
            f"{pattern_text}. "
            f"Additional evidence is required before treating "
            f"the assessment as conclusive."
        )


def get_assessor() -> FraudAssessor:
    return FraudAssessor()