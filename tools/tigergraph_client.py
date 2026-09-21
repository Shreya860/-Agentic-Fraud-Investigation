import os

import pyTigerGraph
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
        self.username = os.getenv("TIGERGRAPH_USERNAME")
        self.password = os.getenv("TIGERGRAPH_PASSWORD")
        self.token = os.getenv("TIGERGRAPH_TOKEN")

        self._connection = None

    def is_configured(self) -> bool:
        """Return True when TigerGraph connection settings are available."""
        return bool(
            self.host
            and (
                self.token
                or (
                    self.username
                    and self.password
                )
            )
        )

    def get_graph_name(self) -> str:
        return self.graph_name

    def connect(self):
        """Create and return a TigerGraph connection."""
        if not self.is_configured():
            raise RuntimeError(
                "TigerGraph is not configured. "
                "Set TIGERGRAPH_HOST and authentication credentials."
            )

        if self._connection is not None:
            return self._connection

        if self.token:
            self._connection = pyTigerGraph.TigerGraphConnection(
                host=self.host,
                graphname=self.graph_name,
                apiToken=self.token,
            )
        else:
            self._connection = pyTigerGraph.TigerGraphConnection(
                host=self.host,
                graphname=self.graph_name,
                username=self.username,
                password=self.password,
            )

        return self._connection
    def run_query(
        self,
        query_name: str,
        params: dict | None = None,
    ):
        """Run a TigerGraph installed query."""
        connection = self.connect()

        return connection.runInstalledQuery(
            query_name,
            params or {},
        )


def get_tigergraph_client() -> TigerGraphClient:
    return TigerGraphClient()