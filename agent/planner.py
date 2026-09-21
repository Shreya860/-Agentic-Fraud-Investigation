from typing import Any
class InvestigationPlanner:
    """
    Determines what the fraud investigation should do next.

    The planner does not execute actions and does not make the
    final fraud decision. It creates the next investigation steps.
    """

    def create_plan(
        self,
        investigation: dict[str, Any],
        assessment: dict[str, Any],
        memory_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        memory_context = memory_context or {}

        historical_match_count = memory_context.get(
            "historical_match_count",
            0,
        )

        risk_level = assessment.get(
            "risk_level",
            "unknown",
        )

        uncertainty = assessment.get(
            "uncertainty",
            [],
        )

        fraud_patterns = assessment.get(
            "fraud_patterns",
            [],
        )

        steps: list[dict[str, Any]] = []

        # Review transaction evidence
        
        steps.append(
            {
                "step": 1,
                "action": "review_transaction_history",
                "reason": (
                    "Review recent transaction activity and "
                    "risk scores supporting the current assessment."
                ),
                "priority": "high",
            }
        )

        # Investigate network relationships
        
        steps.append(
            {
                "step": 2,
                "action": "investigate_connected_entities",
                "reason": (
                    "Investigate customer, card, and device "
                    "relationships for corroborating evidence."
                ),
                "priority": "high",
            }
        )

        # Historical case comparison
        
        if any(
            "Historical case similarity"
            in item
            for item in uncertainty
        ):

            steps.append(
                {
                    "step": 3,
                    "action": "retrieve_similar_cases",
                    "reason": (
                        "Historical case similarity has not yet "
                        "been evaluated."
                    ),
                    "priority": "high",
                }
            )

        # Customer validation
       
        if any(
            "Customer validation"
            in item
            for item in uncertainty
        ):

            steps.append(
                {
                    "step": 4,
                    "action": "request_customer_validation",
                    "reason": (
                        "Customer validation could provide "
                        "additional evidence about the transaction."
                    ),
                    "priority": "medium",
                    "requires_approval": True,
                }
            )

        # Step-up authentication
      
        if any(
            "Step-up authentication"
            in item
            for item in uncertainty
        ):

            steps.append(
                {
                    "step": 5,
                    "action": "request_step_up_authentication",
                    "reason": (
                        "Additional authentication evidence "
                        "is currently unavailable."
                    ),
                    "priority": "medium",
                    "requires_approval": True,
                }
            )

        # External intelligence
       
        if any(
            "External fraud intelligence"
            in item
            for item in uncertainty
        ):

            steps.append(
                {
                    "step": 6,
                    "action": "check_external_fraud_intelligence",
                    "reason": (
                        "External fraud intelligence has not "
                        "yet been evaluated."
                    ),
                    "priority": "low",
                    "requires_approval": False,
                }
            )

        # Determine whether more evidence is required
      
        requires_more_evidence = self._requires_more_evidence(
            risk_level=risk_level,
            uncertainty=uncertainty,
        )

        # Investigation stopping condition
      
        if requires_more_evidence:

            next_phase = "gather_additional_evidence"

        else:

            next_phase = "prepare_action_decision"

        # Build planner output
        
        return {
            "status": "planned",
            "risk_level": risk_level,
            "requires_more_evidence": requires_more_evidence,
            "next_phase": next_phase,
            "fraud_patterns": fraud_patterns,
            "historical_memory": {
                "match_count": historical_match_count,
                "available": historical_match_count > 0,
            },
            "plan": steps,
            "plan_summary": self._build_summary(
                risk_level=risk_level,
                requires_more_evidence=requires_more_evidence,
                steps=steps,
            ),
        }

    # STOP / CONTINUE LOGIC
   
    @staticmethod
    def _requires_more_evidence(
        risk_level: str,
        uncertainty: list[str],
    ) -> bool:

        # A very-high/high risk case with unresolved evidence
        # should continue investigation rather than immediately
        # producing a final action.
        if risk_level in {"very_high", "high"}:
            return len(uncertainty) > 0

        # Moderate risk with unresolved evidence should also
        # continue gathering evidence.
        if risk_level == "moderate":
            return len(uncertainty) > 0

        return False
    
    # SUMMARY
    
    @staticmethod
    def _build_summary(
        risk_level: str,
        requires_more_evidence: bool,
        steps: list[dict[str, Any]],
    ) -> str:

        if requires_more_evidence:

            return (
                f"The investigation currently indicates "
                f"{risk_level} risk. Additional evidence is "
                f"required before a final action decision. "
                f"{len(steps)} investigation steps have been "
                f"planned."
            )

        return (
            f"The investigation currently indicates "
            f"{risk_level} risk and has sufficient evidence "
            f"to proceed toward an action decision."
        )


def get_planner() -> InvestigationPlanner:
    return InvestigationPlanner()