from typing import Any

from policy.approvals import ApprovalManager
from agent.assessor import FraudAssessor
from agent.decision import FraudDecisionEngine
from agent.investigator import FraudInvestigator
from agent.planner import InvestigationPlanner
from memory.memory_service import MemoryService
from policy.permissions import PermissionEngine
from cases.case_manager import get_case_manager


class InvestigationOrchestrator:
    def __init__(
        self,
        investigator: FraudInvestigator | None = None,
        assessor: FraudAssessor | None = None,
        planner: InvestigationPlanner | None = None,
        memory_service: MemoryService | None = None,
        decision_engine: FraudDecisionEngine | None = None,
        approval_manager: ApprovalManager | None = None,
    ):
        self.investigator = investigator or FraudInvestigator()
        self.assessor = assessor or FraudAssessor()
        self.planner = planner or InvestigationPlanner()
        self.memory_service = memory_service or MemoryService()
        self.decision_engine = decision_engine or FraudDecisionEngine()

        self.permission_engine = PermissionEngine()
        self.case_manager = get_case_manager()
        self.approval_manager = approval_manager or ApprovalManager()

    def investigate_customer(
        self,
        customer_id: str,
        limit: int = 10,
        trigger_type: str = "risk_signal",
        trigger_text: str = "Automated fraud risk investigation",
        flagged_txn_id: str | None = None,
    ) -> dict[str, Any]:

        # ---------------------------------------------------------
        # 1. Investigate the customer
        # ---------------------------------------------------------
        investigation = self.investigator.investigate_customer(
            customer_id=customer_id,
            limit=limit,
        )

        # ---------------------------------------------------------
        # 2. Create the case
        # ---------------------------------------------------------
        case = self.case_manager.create_case(
            customer_id=customer_id,
            trigger_type=trigger_type,
            trigger_text=trigger_text,
            flagged_txn_id=flagged_txn_id,
        )

        case_id = case["case_id"]

        # ---------------------------------------------------------
        # 3. Store investigation evidence
        # ---------------------------------------------------------
        for evidence in investigation.get("evidence", []):
            self.case_manager.add_evidence(
                case_id,
                evidence,
            )

        # ---------------------------------------------------------
        # 4. Store investigation findings
        # ---------------------------------------------------------
        for finding in investigation.get("findings", []):
            self.case_manager.add_finding(
                case_id,
                finding,
            )

        # ---------------------------------------------------------
        # 5. Initial assessment
        #
        # This assessment is performed before historical memory
        # because it generates the current fraud-pattern hypotheses
        # that will be used for historical retrieval.
        # ---------------------------------------------------------
        initial_assessment = self.assessor.assess(
            investigation=investigation,
        )

        # ---------------------------------------------------------
        # 6. Build memory-search case from the assessor's
        #    dynamically generated fraud patterns.
        #
        # No hard-coded mapping between finding types and historical
        # fraud patterns is used here.
        # ---------------------------------------------------------
        temporary_case = {
            "case_id": case_id,
            "customer_id": customer_id,
            "risk_level": initial_assessment.get(
                "risk_level",
                "unknown",
            ),
            "trigger_type": trigger_type,
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
                    "fraud_patterns": [
                        pattern.get("pattern")
                        for pattern in initial_assessment.get(
                            "fraud_patterns",
                            [],
                        )
                        if isinstance(pattern, dict)
                        and pattern.get("pattern")
                    ]
                }
            ],
            "actions": [],
        }

        # ---------------------------------------------------------
        # 7. Retrieve historical memory
        # ---------------------------------------------------------
        memory_context = self.memory_service.build_memory_context(
            case=temporary_case,
        )

        # ---------------------------------------------------------
        # 8. Final assessment using current evidence +
        #    historical memory
        # ---------------------------------------------------------
        assessment = self.assessor.assess(
            investigation=investigation,
            memory=memory_context,
        )

        # ---------------------------------------------------------
        # 9. Update case risk level
        # ---------------------------------------------------------
        self.case_manager.update_risk_level(
            case_id,
            assessment.get(
                "risk_level",
                "unknown",
            ),
        )

        # ---------------------------------------------------------
        # 10. Build investigation plan
        # ---------------------------------------------------------
        plan = self.planner.create_plan(
            investigation=investigation,
            assessment=assessment,
            memory_context=memory_context,
        )

        # ---------------------------------------------------------
        # 11. Generate decision
        # ---------------------------------------------------------
        decision = self.decision_engine.decide(
            investigation=investigation,
            assessment=assessment,
            plan=plan,
        )

        # ---------------------------------------------------------
        # 12. Apply policy / permission rules
        # ---------------------------------------------------------
        authorized_decision = self.permission_engine.authorize_decision(
            decision,
        )

        # ---------------------------------------------------------
        # 13. Store authorized decision in case
        # ---------------------------------------------------------
        self.case_manager.add_decision(
            case_id,
            authorized_decision,
        )

        # ---------------------------------------------------------
        # 14. Return complete investigation result
        # ---------------------------------------------------------
        return {
            "customer_id": customer_id,
            "case_id": case_id,
            "investigation": investigation,
            "assessment": assessment,
            "memory": memory_context,
            "plan": plan,
            "decision": authorized_decision,
        }