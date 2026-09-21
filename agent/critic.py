from typing import Any
class InvestigationCritic:
    """
    Reviews an investigation for evidence gaps, uncertainty,
    contradictions, and decision support.
    """

    def critique(
        self,
        investigation: dict[str, Any],
        assessment: dict[str, Any],
        memory: dict[str, Any] | None = None,
        plan: dict[str, Any] | None = None,
        decision: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        memory = memory or {}
        plan = plan or {}
        decision = decision or {}

        strengths: list[str] = []
        concerns: list[str] = []
        missing_evidence: list[str] = []
        contradictions: list[str] = []

        # Review investigation
        
        evidence = investigation.get("evidence", [])
        findings = investigation.get("findings", [])

        if evidence:
            strengths.append("Investigation contains collected evidence.")
        else:
            concerns.append("No investigation evidence is available.")

        if findings:
            strengths.append("Investigation contains findings.")
        else:
            concerns.append("No investigation findings are available.")

        # Review assessment
       
        risk_level = assessment.get("risk_level")

        if risk_level:
            strengths.append("A risk level has been assigned.")
        else:
            concerns.append("Risk level has not been assigned.")

        uncertainty = assessment.get("uncertainty", [])

        if uncertainty:
            concerns.append("The assessment contains unresolved uncertainty.")
            missing_evidence.extend(
                self._extract_uncertainty_items(uncertainty)
            )

        # Review historical memory
       
        historical_match_count = memory.get("historical_match_count")

        if historical_match_count is not None:
            if historical_match_count > 0:
                strengths.append(
                    f"Historical memory contains {historical_match_count} matching case(s)."
                )
            else:
                concerns.append(
                    "No historical case matches were found."
                )
        else:
            concerns.append(
                "Historical case similarity has not been evaluated."
            )

        # Review investigation plan
       
        plan_steps = plan.get("steps", [])

        if plan_steps:
            strengths.append("An investigation plan is available.")
        else:
            concerns.append("No investigation plan is available.")

        # Review decision
        
        recommended_action = decision.get("recommended_action")

        if recommended_action:
            strengths.append(
                "A next-best action has been recommended."
            )
        else:
            concerns.append(
                "No next-best action has been recommended."
            )

        approval_required = decision.get("approval_required")

        if approval_required is True:
            strengths.append(
                "The recommended action requires approval."
            )

        # Basic contradiction checks
        
        if risk_level in {"low", "moderate"} and recommended_action in {
            "block_transaction",
            "block_account",
        }:
            contradictions.append(
                "The recommended blocking action may not align with the assessed risk level."
            )

        if risk_level == "very_high" and recommended_action == "allow_transaction":
            contradictions.append(
                "Allowing the transaction may not align with a very-high risk assessment."
            )

        # Determine review status
       
        if contradictions:
            review_status = "needs_review"
        elif missing_evidence or concerns:
            review_status = "incomplete"
        else:
            review_status = "complete"

        return {
            "review_status": review_status,
            "strengths": strengths,
            "concerns": concerns,
            "missing_evidence": missing_evidence,
            "contradictions": contradictions,
            "recommended_follow_up": self._build_follow_up(
                missing_evidence=missing_evidence,
                contradictions=contradictions,
                decision=decision,
            ),
        }

    @staticmethod
    def _extract_uncertainty_items(
        uncertainty: list[Any],
    ) -> list[str]:
        items: list[str] = []

        for item in uncertainty:
            if isinstance(item, str):
                items.append(item)
            elif isinstance(item, dict):
                description = item.get("description")
                if description:
                    items.append(str(description))

        return items

    @staticmethod
    def _build_follow_up(
        missing_evidence: list[str],
        contradictions: list[str],
        decision: dict[str, Any],
    ) -> list[str]:

        follow_up: list[str] = []

        if contradictions:
            follow_up.append(
                "Review the conflicting risk and action signals before execution."
            )

        if missing_evidence:
            follow_up.append(
                "Collect or evaluate the missing evidence before making a final determination."
            )

        if decision.get("approval_required") is True:
            follow_up.append(
                "Obtain the required approval before executing the recommended action."
            )

        if not follow_up:
            follow_up.append(
                "No additional critical review step was identified."
            )

        return follow_up