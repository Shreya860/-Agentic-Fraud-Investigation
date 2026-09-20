from policy.approvals import ApprovalManager
from typing import Any
from agent.assessor import FraudAssessor
from agent.decision import FraudDecisionEngine
from agent.investigator import FraudInvestigator
from agent.planner import InvestigationPlanner
from memory.memory_service import MemoryService
from policy.permissions import PermissionEngine


class InvestigationOrchestrator:
    def __init__(
        self,
        investigator=None,
        assessor=None,
        planner=None,
        memory_service=None,
        decision_engine=None,
        approval_manager=None,
    ):
        self.investigator = investigator or FraudInvestigator()
        self.assessor = assessor or FraudAssessor()
        self.planner = planner or InvestigationPlanner()
        self.memory_service = memory_service or MemoryService()
        self.decision_engine = decision_engine or FraudDecisionEngine()
        self.permission_engine = PermissionEngine()

    def investigate_customer(
        self,
        customer_id: str,
        case_id: str = "CASE-001",
        limit: int = 10,
    ) -> dict[str, Any]:

        # 1. Investigate the customer
        investigation = self.investigator.investigate_customer(
            customer_id=customer_id,
            limit=limit,
        )

        # 2. Assess fraud risk and patterns
        assessment = self.assessor.assess(investigation)

        # 3. Build the temporary case profile for memory lookup
        case = {
            "case_id": case_id,
            "customer_id": customer_id,
            "risk_level": assessment.get(
                "risk_level",
                "unknown",
            ),
            "trigger_type": "risk_signal",
            "findings": investigation.get(
                "findings",
                [],
            ),
            "evidence": investigation.get(
                "evidence",
                [],
            ),
            "decisions": [
                {
                    "fraud_patterns": assessment.get(
                        "fraud_patterns",
                        [],
                    )
                }
            ],
            "actions": [],
        }

        # 4. Retrieve historical case memory
        memory_context = self.memory_service.build_memory_context(
            case,
            limit=5,
        )

        # 5. Create investigation plan
        plan = self.planner.create_plan(
            investigation=investigation,
            assessment=assessment,
            memory_context=memory_context,
        )

        # 6. Make next-best-action decision
        decision = self.decision_engine.decide(
            investigation=investigation,
            assessment=assessment,
            plan=plan,
        )

        # 7. Apply policy and permission checks
        authorized_decision = self.permission_engine.authorize_decision(
            decision
        )

        # 8. Return the complete investigation result
        return {
            "customer_id": customer_id,
            "case_id": case_id,
            "investigation": investigation,
            "assessment": assessment,
            "memory": memory_context,
            "plan": plan,
            "decision": authorized_decision,
        }


def get_orchestrator() -> InvestigationOrchestrator:
    return InvestigationOrchestrator()