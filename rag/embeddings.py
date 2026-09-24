"""
Embedding utilities for the Fraud Investigation RAG system.

This module provides a small abstraction around text embeddings so the
rest of the RAG pipeline does not depend on a specific embedding model.

The embedding implementation can be replaced later without changing
the retriever or GraphRAG logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass
class EmbeddingDocument:
    """A document together with its generated embedding."""

    text: str
    embedding: list[float]


class EmbeddingProvider:
    """
    Base interface for embedding providers.

    The rest of the RAG system should depend on this interface rather
    than directly depending on a particular embedding library/model.
    """

    def embed_text(self, text: str) -> list[float]:
        """
        Generate an embedding for a single piece of text.

        Implementations should return a numeric vector.
        """
        raise NotImplementedError

    def embed_documents(
        self,
        documents: Sequence[str],
    ) -> list[list[float]]:
        """Generate embeddings for multiple documents."""

        return [self.embed_text(document) for document in documents]


class LocalEmbeddingProvider(EmbeddingProvider):
    """
    Lightweight local embedding provider.

    This is intentionally dependency-free for now so the RAG pipeline
    can be developed and tested before selecting the final embedding
    model.

    IMPORTANT:
    This is NOT intended to be the final semantic embedding model.
    It provides a deterministic vector representation for development
    and testing.

    A real embedding model can later replace this class without
    changing the rest of the RAG architecture.
    """

    def __init__(self, dimensions: int = 128):
        if dimensions <= 0:
            raise ValueError("dimensions must be greater than zero")

        self.dimensions = dimensions

    def embed_text(self, text: str) -> list[float]:
        """
        Create a deterministic development embedding.

        The same input text always produces the same vector.
        """

        if not isinstance(text, str):
            raise TypeError("text must be a string")

        vector = [0.0] * self.dimensions

        normalized = text.strip().lower()

        if not normalized:
            return vector

        # Deterministic hashing of tokens into vector positions.
        tokens = normalized.split()

        for token in tokens:
            index = hash(token) % self.dimensions
            vector[index] += 1.0

        # Normalize the vector.
        magnitude = sum(value * value for value in vector) ** 0.5

        if magnitude > 0:
            vector = [
                value / magnitude
                for value in vector
            ]

        return vector


def get_embedding_provider() -> EmbeddingProvider:
    """
    Return the embedding provider used by the RAG system.

    Keeping provider creation in one place makes it easy to replace
    the development provider with a production embedding model later.
    """

    return LocalEmbeddingProvider()