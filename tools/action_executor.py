from datetime import datetime, timezone
from typing import Any


class ActionExecutor:
    """Execute approved fraud-investigation actions using safe mock/stub handlers."""

    def execute(
        self,
        action: str,
        case_id: str,
        customer_id: str | None = None,
        transaction_id: str | None = None,
        reason: str = "",
    ) -> dict[str, Any]:

        handlers = {
            "allow_transaction": self._allow_transaction,
            "monitor_transaction": self._monitor_transaction,
            "block_transaction": self._block_transaction,
            "monitor_account": self._monitor_account,
            "block_account": self._block_account,
            "request_customer_validation": self._request_customer_validation,
            "request_step_up_authentication": self._request_step_up_authentication,
            "retrieve_similar_cases": self._retrieve_similar_cases,
            "check_external_fraud_intelligence": self._check_external_fraud_intelligence,
            "create_case": self._create_case,
            "escalate_to_analyst": self._escalate_to_analyst,
        }

        handler = handlers.get(action)

        if handler is None:
            return {
                "status": "rejected",
                "action": action,
                "case_id": case_id,
                "reason": "Unknown action.",
                "executed_at": self._now(),
            }

        result = handler(
            case_id=case_id,
            customer_id=customer_id,
            transaction_id=transaction_id,
            reason=reason,
        )

        return {
            "status": "executed",
            "action": action,
            "case_id": case_id,
            "executed_at": self._now(),
            **result,
        }

    def _allow_transaction(self, **kwargs) -> dict[str, Any]:
        return {
            "message": "Transaction allowed.",
            "execution_mode": "mock",
        }

    def _monitor_transaction(self, **kwargs) -> dict[str, Any]:
        return {
            "message": "Transaction placed under monitoring.",
            "execution_mode": "mock",
        }

    def _block_transaction(self, **kwargs) -> dict[str, Any]:
        return {
            "message": "Transaction blocked.",
            "execution_mode": "mock",
        }

    def _monitor_account(self, **kwargs) -> dict[str, Any]:
        return {
            "message": "Account placed under monitoring.",
            "execution_mode": "mock",
        }

    def _block_account(self, **kwargs) -> dict[str, Any]:
        return {
            "message": "Account blocked.",
            "execution_mode": "mock",
        }

    def _request_customer_validation(self, **kwargs) -> dict[str, Any]:
        return {
            "message": "Customer validation requested.",
            "execution_mode": "mock",
        }

    def _request_step_up_authentication(self, **kwargs) -> dict[str, Any]:
        return {
            "message": "Step-up authentication requested.",
            "execution_mode": "mock",
        }

    def _retrieve_similar_cases(self, **kwargs) -> dict[str, Any]:
        return {
            "message": "Similar historical cases retrieved.",
            "execution_mode": "internal",
        }

    def _check_external_fraud_intelligence(self, **kwargs) -> dict[str, Any]:
        return {
            "message": "External fraud intelligence check requested.",
            "execution_mode": "mock",
        }

    def _create_case(self, **kwargs) -> dict[str, Any]:
        return {
            "message": "Fraud case created.",
            "execution_mode": "internal",
        }

    def _escalate_to_analyst(self, **kwargs) -> dict[str, Any]:
        return {
            "message": "Case escalated to an authorized analyst.",
            "execution_mode": "internal",
        }

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()


def get_action_executor() -> ActionExecutor:
    return ActionExecutor()