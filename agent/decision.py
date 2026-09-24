from typing import Any


class FraudDecisionEngine:
    """
    Converts investigation + assessment + planning results into a
    policy-aligned HHGOA next-best-action recommendation.

    The engine recommends actions only. It does not execute them.
    """

    def decide(
        self,
        investigation: dict[str, Any],
        assessment: dict[str, Any],
        plan: dict[str, Any],
    ) -> dict[str, Any]:

        risk_level = assessment.get("risk_level", "unknown")
        uncertainty = assessment.get("uncertainty", [])

        # Pattern detected by the HHGOA-specific pattern analyzer.
        pattern_analysis = investigation.get("pattern_analysis", {})

        primary_pattern = pattern_analysis.get(
            "primary_pattern",
            "none",
        )

        pattern_confidence = pattern_analysis.get(
            "confidence",
            "low",
        )

        # ---------------------------------------------------------
        # 1. Apply explicit HHGOA pattern rules first.
        #
        # This prevents the generic "missing evidence" pathway
        # from overriding a sufficiently strong fraud pattern.
        # ---------------------------------------------------------
        pattern_decision = self._select_pattern_action(
            primary_pattern,
            pattern_confidence,
            investigation,
            assessment,
        )

        if pattern_decision is not None:
            return {
                "status": "decision_ready",
                "recommended_action": pattern_decision["action"],
                "action_category": pattern_decision["action_category"],
                "approval_required": pattern_decision["approval_required"],
                "approval_route": pattern_decision["approval_route"],
                "priority": pattern_decision["priority"],
                "reason": pattern_decision["reason"],
                "evidence_basis": self._build_evidence_basis(assessment),
                "fraud_patterns": assessment.get(
                    "fraud_patterns",
                    [],
                ),
                "detected_pattern": primary_pattern,
                "pattern_confidence": pattern_confidence,
                "uncertainty": uncertainty,
                "execution_status": "not_executed",
            }

        # ---------------------------------------------------------
        # 2. Preserve uncertainty-driven evidence gathering.
        # ---------------------------------------------------------
        requires_more_evidence = plan.get(
            "requires_more_evidence",
            False,
        )

        if requires_more_evidence:
            action = self._select_evidence_action(
                uncertainty
            )

            return {
                "status": "decision_ready",
                "recommended_action": action["action"],
                "action_category": "evidence_gathering",
                "approval_required": action["approval_required"],
                "approval_route": action["approval_route"],
                "priority": action["priority"],
                "reason": action["reason"],
                "evidence_basis": self._build_evidence_basis(
                    assessment
                ),
                "fraud_patterns": assessment.get(
                    "fraud_patterns",
                    [],
                ),
                "detected_pattern": primary_pattern,
                "pattern_confidence": pattern_confidence,
                "uncertainty": uncertainty,
                "execution_status": "not_executed",
            }

        # ---------------------------------------------------------
        # 3. Generic risk-based fallback.
        # ---------------------------------------------------------
        action = self._select_risk_action(
            risk_level
        )

        return {
            "status": "decision_ready",
            "recommended_action": action["action"],
            "action_category": "risk_mitigation",
            "approval_required": action["approval_required"],
            "approval_route": action["approval_route"],
            "priority": action["priority"],
            "reason": action["reason"],
            "evidence_basis": self._build_evidence_basis(
                assessment
            ),
            "fraud_patterns": assessment.get(
                "fraud_patterns",
                [],
            ),
            "detected_pattern": primary_pattern,
            "pattern_confidence": pattern_confidence,
            "uncertainty": uncertainty,
            "execution_status": "not_executed",
        }

    # =============================================================
    # HHGOA PATTERN-BASED DECISION LOGIC
    # =============================================================

    def _select_pattern_action(
        self,
        pattern: str,
        confidence: str,
        investigation: dict[str, Any],
        assessment: dict[str, Any],
    ) -> dict[str, Any] | None:
        """
        Apply explicit HHGOA policy rules to the pattern detected
        by FraudPatternAnalyzer.

        Returns None when the pattern is not sufficiently strong
        to drive a policy-specific action.
        """

        # ---------------------------------------------------------
        # R5: CARD TESTING
        #
        # Policy:
        # 3+ small online authorizations within an hour followed
        # by a larger purchase -> DECLINE_TRANSACTION +
        # STEP_UP_AUTH.
        #
        # If > $100 cleared -> BLOCK_CARD.
        # ---------------------------------------------------------
        if (
            pattern == "card_testing"
            and confidence in {"high", "medium"}
        ):
            flagged = investigation.get(
                "flagged_transaction",
                {},
            )

            amount = self._get_transaction_amount(
                flagged
            )

            if amount > 100:
                return {
                    "action": "BLOCK_CARD",
                    "action_category": "risk_mitigation",
                    "approval_required": True,
                    "approval_route": "L1",
                    "priority": "critical",
                    "reason": (
                        "Card testing was detected with sufficient "
                        "confidence. Under HHGOA rule R5, the "
                        "cleared transaction exceeds $100, so "
                        "BLOCK_CARD is recommended."
                    ),
                }

            return {
                "action": "DECLINE_TRANSACTION",
                "action_category": "risk_mitigation",
                "approval_required": True,
                "approval_route": "L1",
                "priority": "critical",
                "reason": (
                    "Card testing was detected with sufficient "
                    "confidence. Under HHGOA rule R5, the "
                    "transaction should be declined and "
                    "step-up authentication requested."
                ),
            }

        # ---------------------------------------------------------
        # R6: SHARED ORIGIN / COORDINATED ACTIVITY
        # ---------------------------------------------------------
        if (
            pattern == "shared_origin"
            and confidence in {"high", "medium"}
        ):
            return {
                "action": "CREATE_CASE",
                "action_category": "case_creation",
                "approval_required": False,
                "approval_route": None,
                "priority": "high",
                "reason": (
                    "Shared-origin activity was detected. Under "
                    "HHGOA rule R6, a case should be created and "
                    "connected cards should be monitored."
                ),
            }

        # ---------------------------------------------------------
        # R9: UNDOCUMENTED COORDINATED / REPEATED ABUSE
        #
        # Low-confidence undocumented activity should continue
        # through the uncertainty pathway rather than triggering
        # an aggressive action.
        # ---------------------------------------------------------
        if (
            pattern == "undocumented"
            and confidence == "high"
        ):
            return {
                "action": "CREATE_CASE",
                "action_category": "case_creation",
                "approval_required": False,
                "approval_route": None,
                "priority": "high",
                "reason": (
                    "Coordinated or repeated undocumented abuse "
                    "was detected. Under HHGOA rule R9, a case "
                    "should be created and the investigation "
                    "should be escalated."
                ),
            }

        # ---------------------------------------------------------
        # Recognized but insufficiently strong patterns remain
        # evidence-dependent.
        # ---------------------------------------------------------
        return None

    # =============================================================
    # TRANSACTION HELPERS
    # =============================================================

    @staticmethod
    def _get_transaction_amount(
        transaction: dict[str, Any],
    ) -> float:
        """
        Safely extract the transaction amount from the various
        field names that may appear in investigation output.
        """

        if not transaction:
            return 0.0

        possible_fields = (
            "amount",
            "TransactionAmt",
            "transaction_amount",
            "fare",
            "value",
        )

        for field in possible_fields:
            value = transaction.get(field)

            if value is None:
                continue

            try:
                return float(value)
            except (TypeError, ValueError):
                continue

        return 0.0

    # =============================================================
    # EVIDENCE-GATHERING DECISIONS
    # =============================================================

    def _select_evidence_action(
        self,
        uncertainty: list[str],
    ) -> dict[str, Any]:
        """
        Select the most useful next evidence-gathering action
        when the investigation is still uncertain.
        """

        uncertainty_text = " ".join(
            str(item)
            for item in uncertainty
        ).lower()

        # Customer validation is the preferred route when
        # transaction legitimacy can be settled directly.
        if "customer validation" in uncertainty_text:
            return {
                "action": "VERIFY_WITH_CUSTOMER",
                "approval_required": True,
                "approval_route": "authorized_analyst",
                "priority": "high",
                "reason": (
                    "Customer validation evidence is unavailable. "
                    "HHGOA policy supports verification before "
                    "taking stronger action when the signal is "
                    "not yet conclusive."
                ),
            }

        # Step-up authentication is useful when additional
        # authentication can resolve uncertainty.
        if "step-up authentication" in uncertainty_text:
            return {
                "action": "STEP_UP_AUTH",
                "approval_required": True,
                "approval_route": "authorized_analyst",
                "priority": "high",
                "reason": (
                    "Step-up authentication evidence is unavailable. "
                    "Additional authentication can help resolve "
                    "transaction legitimacy."
                ),
            }

        # Historical similarity can provide supporting evidence.
        if "historical case similarity" in uncertainty_text:
            return {
                "action": "CREATE_CASE",
                "approval_required": False,
                "approval_route": None,
                "priority": "medium",
                "reason": (
                    "Historical case similarity is unavailable. "
                    "Create or retain the investigation case so "
                    "additional evidence can be gathered."
                ),
            }

        # Default uncertainty action.
        return {
            "action": "ESCALATE_TO_ANALYST",
            "approval_required": False,
            "approval_route": "authorized_analyst",
            "priority": "high",
            "reason": (
                "The investigation remains uncertain and requires "
                "authorized analyst review before a stronger action "
                "is taken."
            ),
        }

    # =============================================================
    # GENERIC RISK FALLBACK
    # =============================================================

    def _select_risk_action(
        self,
        risk_level: str,
    ) -> dict[str, Any]:
        """
        Generic fallback when no policy-specific pattern and no
        evidence-gathering requirement determines the decision.
        """

        if risk_level == "very_high":
            return {
                "action": "ESCALATE_TO_ANALYST",
                "approval_required": False,
                "approval_route": "authorized_analyst",
                "priority": "critical",
                "reason": (
                    "The investigation indicates very high risk. "
                    "The case should be escalated for authorized "
                    "review before a blocking action is executed."
                ),
            }

        if risk_level == "high":
            return {
                "action": "MONITOR_CARD",
                "approval_required": True,
                "approval_route": "authorized_analyst",
                "priority": "high",
                "reason": (
                    "The investigation indicates high risk. "
                    "Monitoring the affected card is recommended "
                    "while preserving the investigation evidence."
                ),
            }

        if risk_level == "moderate":
            return {
                "action": "MONITOR_CARD",
                "approval_required": False,
                "approval_route": None,
                "priority": "medium",
                "reason": (
                    "The investigation indicates moderate risk. "
                    "Monitoring the affected card is recommended."
                ),
            }

        return {
            "action": "ALLOW_TRANSACTION",
            "approval_required": False,
            "approval_route": None,
            "priority": "low",
            "reason": (
                "The available evidence does not indicate sufficient "
                "risk for a stronger intervention."
            ),
        }

    # =============================================================
    # EVIDENCE SUMMARY
    # =============================================================

    @staticmethod
    def _build_evidence_basis(
        assessment: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Return the evidence supporting the recommendation.
        """

        evidence: list[dict[str, Any]] = []

        for item in assessment.get(
            "supporting_evidence",
            [],
        ):
            evidence.append(item)

        for item in assessment.get(
            "source_findings",
            [],
        ):
            evidence.append(item)

        return evidence