"""
Retrieval-Augmented Generation utilities for Fraud Investigation.
"""

from rag.embeddings import (
    EmbeddingDocument,
    EmbeddingProvider,
    LocalEmbeddingProvider,
    get_embedding_provider,
)

from rag.ingest import (
    DocumentChunk,
    DocumentIngester,
)

from rag.retriever import (
    RetrievedDocument,
    Retriever,
)

from rag.graph_rag import (
    GraphEvidenceProvider,
    GraphRAG,
    GraphRAGResult,
)


__all__ = [
    "EmbeddingDocument",
    "EmbeddingProvider",
    "LocalEmbeddingProvider",
    "get_embedding_provider",
    "DocumentChunk",
    "DocumentIngester",
    "RetrievedDocument",
    "Retriever",
    "GraphEvidenceProvider",
    "GraphRAG",
    "GraphRAGResult",
]