from typing import Any

class FraudDecisionEngine:
    """
    Converts investigation assessment into a next-best-action
    recommendation.

    This component recommends actions only.
    It does not execute them.
    """

    def decide(
        self,
        investigation: dict[str, Any],
        assessment: dict[str, Any],
        plan: dict[str, Any],
    ) -> dict[str, Any]:

        risk_level = assessment.get(
            "risk_level",
            "unknown",
        )

        requires_more_evidence = plan.get(
            "requires_more_evidence",
            False,
        )

        uncertainty = assessment.get(
            "uncertainty",
            [],
        )

        fraud_patterns = assessment.get(
            "fraud_patterns",
            [],
        )

        # If important evidence is still missing
       
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
                "fraud_patterns": fraud_patterns,
                "uncertainty": uncertainty,
                "execution_status": "not_executed",
            }

        # Evidence is considered sufficient for an action
        # recommendation
        
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
            "fraud_patterns": fraud_patterns,
            "uncertainty": uncertainty,
            "execution_status": "not_executed",
        }

    # EVIDENCE-GATHERING DECISION
 
    @staticmethod
    def _select_evidence_action(
        uncertainty: list[str],
    ) -> dict[str, Any]:

        # Customer validation provides a direct signal about
        # whether the customer recognizes the activity.

        if any(
            "Customer validation" in item
            for item in uncertainty
        ):

            return {
                "action": "request_customer_validation",
                "approval_required": True,
                "approval_route": "authorized_analyst",
                "priority": "high",
                "reason": (
                    "Important transaction-risk evidence is "
                    "available, but customer validation is "
                    "still missing."
                ),
            }

        # Step-up authentication is another controlled
        # evidence-gathering action.

        if any(
            "Step-up authentication" in item
            for item in uncertainty
        ):

            return {
                "action": "request_step_up_authentication",
                "approval_required": True,
                "approval_route": "authorized_analyst",
                "priority": "high",
                "reason": (
                    "Additional authentication evidence is "
                    "needed before making a final risk action."
                ),
            }

        # Historical cases can provide useful contextual
        # evidence without taking an immediate customer action.

        if any(
            "Historical case similarity" in item
            for item in uncertainty
        ):

            return {
                "action": "retrieve_similar_cases",
                "approval_required": False,
                "approval_route": "none",
                "priority": "high",
                "reason": (
                    "Historical case similarity has not yet "
                    "been evaluated."
                ),
            }

        # Fallback when uncertainty exists but no specific
        # evidence action has been identified.

        return {
            "action": "escalate_to_analyst",
            "approval_required": False,
            "approval_route": "authorized_analyst",
            "priority": "high",
            "reason": (
                "The investigation contains unresolved "
                "uncertainty and requires analyst review."
            ),
        }

    # RISK-MITIGATION DECISION
   
    @staticmethod
    def _select_risk_action(
        risk_level: str,
    ) -> dict[str, Any]:

        if risk_level == "very_high":

            return {
                "action": "block_transaction",
                "approval_required": True,
                "approval_route": "authorized_analyst",
                "priority": "critical",
                "reason": (
                    "The investigation indicates very high "
                    "risk and supports a transaction-blocking "
                    "recommendation."
                ),
            }

        if risk_level == "high":

            return {
                "action": "monitor_transaction",
                "approval_required": True,
                "approval_route": "authorized_analyst",
                "priority": "high",
                "reason": (
                    "The investigation indicates high risk. "
                    "Enhanced monitoring is recommended."
                ),
            }

        if risk_level == "moderate":

            return {
                "action": "monitor_transaction",
                "approval_required": False,
                "approval_route": "none",
                "priority": "medium",
                "reason": (
                    "The investigation indicates moderate "
                    "risk and supports continued monitoring."
                ),
            }

        return {
            "action": "allow_transaction",
            "approval_required": False,
            "approval_route": "none",
            "priority": "low",
            "reason": (
                "Available evidence does not currently "
                "support a restrictive transaction action."
            ),
        }
    # EVIDENCE BASIS
    @staticmethod
    def _build_evidence_basis(
        assessment: dict[str, Any],
    ) -> list[dict[str, Any]]:

        basis = []

        risk_score = assessment.get(
            "risk_score"
        )

        if risk_score is not None:

            basis.append(
                {
                    "evidence": "maximum_risk_score",
                    "value": risk_score,
                    "description": (
                        "Maximum observed transaction "
                        "risk score."
                    ),
                }
            )

        for item in assessment.get(
            "supporting_evidence",
            [],
        ):

            basis.append(
                {
                    "evidence": item.get("type"),
                    "severity": item.get("severity"),
                    "description": item.get(
                        "description"
                    ),
                }
            )

        return basis


def get_decision_engine() -> FraudDecisionEngine:
    return FraudDecisionEngine()