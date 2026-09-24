"""
GraphRAG orchestration for the Fraud Investigation Agent.

Combines:
1. Graph-based investigation evidence
2. Retrieved fraud knowledge

The graph provider is intentionally abstract so TigerGraph can be
connected later without changing the RAG layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from rag.retriever import RetrievedDocument, Retriever


class GraphEvidenceProvider(Protocol):
    """
    Interface expected from a graph evidence provider.

    A TigerGraph implementation can satisfy this interface later.
    """

    def get_customer_context(
        self,
        customer_id: str,
    ) -> dict[str, Any]:
        """Return graph evidence for a customer."""
        ...


@dataclass
class GraphRAGResult:
    """Combined graph and textual evidence."""

    customer_id: str

    graph_evidence: dict[str, Any] = field(
        default_factory=dict
    )

    retrieved_documents: list[RetrievedDocument] = field(
        default_factory=list
    )

    query: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert the result to a serializable dictionary."""

        return {
            "customer_id": self.customer_id,
            "query": self.query,
            "graph_evidence": self.graph_evidence,
            "retrieved_documents": [
                {
                    "chunk_id": result.chunk.chunk_id,
                    "source": result.chunk.source,
                    "text": result.chunk.text,
                    "score": result.score,
                }
                for result in self.retrieved_documents
            ],
        }


class GraphRAG:
    """
    Combines graph evidence with retrieved fraud knowledge.
    """

    def __init__(
        self,
        retriever: Retriever,
        graph_provider: GraphEvidenceProvider | None = None,
    ):
        self.retriever = retriever
        self.graph_provider = graph_provider

    def retrieve_knowledge(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievedDocument]:
        """Retrieve relevant fraud knowledge."""

        return self.retriever.search(
            query=query,
            top_k=top_k,
        )

    def get_graph_evidence(
        self,
        customer_id: str,
    ) -> dict[str, Any]:
        """Retrieve graph evidence when a graph provider is available."""

        if self.graph_provider is None:
            return {}

        return self.graph_provider.get_customer_context(
            customer_id
        )

    def investigate(
        self,
        customer_id: str,
        query: str,
        top_k: int = 5,
    ) -> GraphRAGResult:
        """
        Combine graph evidence and retrieved knowledge.
        """

        graph_evidence = self.get_graph_evidence(
            customer_id=customer_id
        )

        retrieved_documents = self.retrieve_knowledge(
            query=query,
            top_k=top_k,
        )

        return GraphRAGResult(
            customer_id=customer_id,
            graph_evidence=graph_evidence,
            retrieved_documents=retrieved_documents,
            query=query,
        )