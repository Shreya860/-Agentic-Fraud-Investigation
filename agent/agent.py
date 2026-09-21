from typing import Any

from agent.orchestrator import InvestigationOrchestrator
from agent.state import InvestigationState
from agent.critic import InvestigationCritic


class FraudInvestigationAgent:
    """
    High-level agent interface for fraud investigations.

    The agent delegates investigation, assessment, memory,
    planning, and decision-making to the existing components.
    It then performs a final critic review.
    """

    def __init__(
        self,
        orchestrator: InvestigationOrchestrator | None = None,
        critic: InvestigationCritic | None = None,
    ):
        self.orchestrator = orchestrator or InvestigationOrchestrator()
        self.critic = critic or InvestigationCritic()

    def investigate(
        self,
        customer_id: str,
        limit: int = 10,
    ) -> dict[str, Any]:

        result = self.orchestrator.investigate_customer(
            customer_id=customer_id,
            limit=limit,
        )

        state = InvestigationState(
            customer_id=customer_id,
            case_id=result.get("case_id"),
        )

        state.update_investigation(
            result.get("investigation", {})
        )

        state.update_assessment(
            result.get("assessment", {})
        )

        state.update_memory(
            result.get("memory", {})
        )

        state.update_plan(
            result.get("plan", {})
        )

        state.update_decision(
            result.get("decision", {})
        )

        critique = self.critic.critique(
            investigation=state.investigation,
            assessment=state.assessment,
            memory=state.memory,
            plan=state.plan,
            decision=state.decision,
        )

        state.update_critique(critique)

        return state.to_dict()