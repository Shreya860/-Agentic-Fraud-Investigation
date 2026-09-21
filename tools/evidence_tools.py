from typing import Any
from tools.transaction_tools import TransactionTools
from tools.graph_tools import GraphTools

class EvidenceTools:
    """
    Tools for collecting evidence used during fraud investigation.
    """

    def __init__(
        self,
        transaction_tools: TransactionTools | None = None,
        graph_tools: GraphTools | None = None,
    ):
        self.transaction_tools = transaction_tools or TransactionTools()
        self.graph_tools = graph_tools or GraphTools()

    def get_transaction(
        self,
        transaction_id: str,
    ) -> dict[str, Any] | None:
        return self.transaction_tools.get_transaction(transaction_id)

    def get_customer_transactions(
        self,
        customer_id: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        return self.transaction_tools.get_customer_transactions(
            customer_id=customer_id,
            limit=limit,
        )

    def get_high_risk_transactions(
        self,
        customer_id: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        return self.transaction_tools.get_high_risk_transactions(
            customer_id,
            limit=limit,
        )

    def get_customer_summary(
        self,
        customer_id: str,
    ) -> dict[str, Any]:
        return self.transaction_tools.get_customer_summary(
            customer_id=customer_id,
        )

    def get_customer_network(
        self,
        customer_id: str,
        limit: int = 10,
    ) -> dict[str, Any]:
        return self.graph_tools.get_customer_network(
            customer_id=customer_id,
            limit=limit,
        )

    def get_card_network(
        self,
        customer_id: str,
        limit: int = 10,
    ) -> dict[str, Any]:
        return self.graph_tools.get_card_network(
            customer_id=customer_id,
            limit=limit,
        )

    def get_device_network(
        self,
        customer_id: str,
        limit: int = 10,
    ) -> dict[str, Any]:
        return self.graph_tools.get_device_network(
            customer_id=customer_id,
            limit=limit,
        )

    def get_device_rarity(
        self,
        customer_id: str,
    ) -> list[dict[str, Any]]:
        return self.graph_tools.get_device_rarity(
            customer_id=customer_id,
        )