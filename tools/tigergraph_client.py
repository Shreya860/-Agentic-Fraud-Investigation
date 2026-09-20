import os

from dotenv import load_dotenv

load_dotenv()


class TigerGraphClient:
    """TigerGraph connection wrapper."""

    def __init__(self):
        self.host = os.getenv("TIGERGRAPH_HOST")
        self.graph_name = os.getenv(
            "TIGERGRAPH_GRAPH",
            "FraudInvestigationGraph",
        )

    def is_configured(self) -> bool:
        """Return True when TigerGraph credentials are available."""
        return bool(
            self.host
            and os.getenv("TIGERGRAPH_USERNAME")
            and os.getenv("TIGERGRAPH_PASSWORD")
        )

    def get_graph_name(self) -> str:
        return self.graph_name


def get_tigergraph_client() -> TigerGraphClient:
    return TigerGraphClient()