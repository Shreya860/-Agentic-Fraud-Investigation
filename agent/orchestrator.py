from __future__ import annotations

from typing import Any

from agent.assessor import FraudAssessor
from agent.decision import FraudDecisionEngine
from agent.investigator import FraudInvestigator
from agent.pattern_analyser import FraudPatternAnalyzer
from agent.planner import InvestigationPlanner
from cases.case_manager import CaseManager
from memory.memory_service import MemoryService


class InvestigationOrchestrator:

    def __init__(self) -> None:
        self.investigator = FraudInvestigator()
        self.pattern_analyzer = FraudPatternAnalyzer()

        self.case_manager = CaseManager()
        self.assessor = FraudAssessor()
        self.memory = MemoryService()
        self.planner = InvestigationPlanner()
        self.decision_engine = FraudDecisionEngine()

    def investigate_customer(
        self,
        customer_id: str,
        limit: int = 10,
        trigger_type: str = "risk_signal",
        trigger_text: str = "Automated fraud risk investigation",
        flagged_txn_id: str | None = None,
    ) -> dict[str, Any]:

        # ---------------------------------------------------------
        # 1. Investigate customer
        # ---------------------------------------------------------

        investigation = self.investigator.investigate_customer(
            customer_id=customer_id,
            limit=limit,
            flagged_txn_id=flagged_txn_id,
        )

        # ---------------------------------------------------------
        # 2. Pattern analysis
        # ---------------------------------------------------------

        pattern_analysis = None

        if flagged_txn_id:
            pattern_analysis = self.pattern_analyzer.analyze_transaction(
                flagged_txn_id
            )

            investigation["pattern_analysis"] = pattern_analysis

        # ---------------------------------------------------------
        # 3. Create case
        # ---------------------------------------------------------

        case = self.case_manager.create_case(
            customer_id=customer_id,
            trigger_type=trigger_type,
            trigger_text=trigger_text,
            flagged_txn_id=flagged_txn_id,
        )

        case_id = case["case_id"]

        # Add investigation information to the case.
        case["customer_id"] = customer_id
        case["flagged_txn_id"] = flagged_txn_id
        case["trigger_type"] = trigger_type
        case["trigger_text"] = trigger_text
        case["investigation"] = investigation

        # ---------------------------------------------------------
        # 4. Store investigation evidence
        # ---------------------------------------------------------

        for evidence in investigation.get("evidence", []):
            self.case_manager.add_evidence(
                case_id,
                evidence,
            )

        # ---------------------------------------------------------
        # 5. Store findings
        # ---------------------------------------------------------

        for finding in investigation.get("findings", []):
            self.case_manager.add_finding(
                case_id,
                finding,
            )

        # ---------------------------------------------------------
        # 6. Add pattern evidence
        # ---------------------------------------------------------

        if pattern_analysis:
            for evidence in pattern_analysis.get("evidence", []):
                self.case_manager.add_evidence(
                    case_id,
                    evidence,
                )

        # ---------------------------------------------------------
        # 7. Fraud assessment
        # ---------------------------------------------------------

        assessment = self.assessor.assess(
            investigation=investigation,
        )

        case["assessment"] = assessment

        # ---------------------------------------------------------
        # 8. Retrieve historical memory
        # ---------------------------------------------------------

        memory = self.memory.build_memory_context(
            case,
            limit=5,
        )

        # ---------------------------------------------------------
        # 9. Investigation plan
        # ---------------------------------------------------------

        plan = self.planner.create_plan(
            investigation=investigation,
            assessment=assessment,
            memory_context=memory,
        )

        case["plan"] = plan

        # ---------------------------------------------------------
        # 10. Decision
        # ---------------------------------------------------------

        decision = self.decision_engine.decide(
            investigation=investigation,
            assessment=assessment,
            plan=plan,
        )

        case["decision"] = decision

        # ---------------------------------------------------------
        # 11. Store completed case in memory
        # ---------------------------------------------------------

        try:
            self.memory.store_case(case)
        except Exception as exc:
            # Memory persistence should not prevent the investigation
            # result from being returned.
            case["memory_store_error"] = str(exc)

        # ---------------------------------------------------------
        # 12. Return complete investigation result
        # ---------------------------------------------------------

        return {
            "customer_id": customer_id,
            "case_id": case_id,
            "investigation": investigation,
            "assessment": assessment,
            "memory": memory,
            "plan": plan,
            "decision": decision,
        }


def get_orchestrator() -> InvestigationOrchestrator:
    return InvestigationOrchestrator()