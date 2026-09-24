"""
Document retrieval for the Fraud Investigation RAG system.

The retriever searches ingested document chunks and returns the most
relevant pieces of fraud knowledge for an investigation.

This initial implementation is dependency-free and uses token overlap.
A semantic/vector retriever can replace this later without changing
the public interface.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from rag.ingest import DocumentChunk


@dataclass
class RetrievedDocument:
    """A document chunk together with its relevance score."""

    chunk: DocumentChunk
    score: float


class Retriever:
    """Retrieve relevant document chunks."""

    def __init__(
        self,
        chunks: list[DocumentChunk] | None = None,
    ):
        self.chunks = chunks or []

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        """Convert text into normalized tokens."""

        return set(
            re.findall(
                r"[a-zA-Z0-9_]+",
                text.lower(),
            )
        )

    def add_chunks(
        self,
        chunks: list[DocumentChunk],
    ) -> None:
        """Add document chunks to the retrieval index."""

        self.chunks.extend(chunks)

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievedDocument]:
        """
        Retrieve the most relevant chunks for a query.

        Relevance is based on token overlap between the query and
        document chunk.
        """

        if not query.strip():
            return []

        if top_k <= 0:
            return []

        query_tokens = self._tokenize(query)

        if not query_tokens:
            return []

        results: list[RetrievedDocument] = []

        for chunk in self.chunks:
            chunk_tokens = self._tokenize(chunk.text)

            if not chunk_tokens:
                continue

            overlap = query_tokens.intersection(
                chunk_tokens
            )

            if not overlap:
                continue

            score = len(overlap) / len(query_tokens)

            results.append(
                RetrievedDocument(
                    chunk=chunk,
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:top_k]

    def search_text(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[str]:
        """Return only the text of retrieved chunks."""

        results = self.search(
            query=query,
            top_k=top_k,
        )

        return [
            result.chunk.text
            for result in results
        ]