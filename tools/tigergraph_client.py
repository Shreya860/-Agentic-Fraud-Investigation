import os

import pyTigerGraph
from dotenv import load_dotenv

load_dotenv()


class TigerGraphClient:
    def __init__(self):
        self.host = os.getenv("TIGERGRAPH_HOST")
        self.graph_name = os.getenv(
            "TIGERGRAPH_GRAPH",
            "FraudInvestigationGraph",
        )
        self.secret = os.getenv("TIGERGRAPH_SECRET")
        self._connection = None

    def is_configured(self) -> bool:
        return bool(self.host and self.graph_name and self.secret)

    def get_graph_name(self) -> str:
        return self.graph_name

    def connect(self):
        if not self.is_configured():
            raise RuntimeError(
                "TigerGraph is not configured. "
                "Set TIGERGRAPH_HOST, TIGERGRAPH_GRAPH, "
                "and TIGERGRAPH_SECRET."
            )

        if self._connection is not None:
            return self._connection

        self._connection = pyTigerGraph.TigerGraphConnection(
            host=self.host,
            graphname=self.graph_name,
            gsqlSecret=self.secret,
        )

        self._connection.getToken(self.secret)

        return self._connection

    def run_query(self, query_name: str, params: dict | None = None):
        connection = self.connect()
        return connection.runInstalledQuery(
            query_name,
            params or {},
        )


def get_tigergraph_client() -> TigerGraphClient:
    return TigerGraphClient()