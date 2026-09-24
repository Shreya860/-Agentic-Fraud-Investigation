"""
Document ingestion utilities for the Fraud Investigation RAG system.

Responsible for:
- discovering supported documents
- reading text
- cleaning text
- splitting documents into chunks

This module does not perform retrieval or graph operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
}


@dataclass
class DocumentChunk:
    """A chunk of source document text."""

    chunk_id: str
    source: str
    text: str


class DocumentIngester:
    """Load and split RAG documents into manageable chunks."""

    def __init__(
        self,
        documents_dir: str | Path = "rag/documents",
        chunk_size: int = 1000,
        chunk_overlap: int = 150,
    ):
        self.documents_dir = Path(documents_dir)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )

    def discover_documents(self) -> list[Path]:
        """Return all supported documents recursively."""

        if not self.documents_dir.exists():
            return []

        documents = []

        for path in self.documents_dir.rglob("*"):
            if (
                path.is_file()
                and path.suffix.lower() in SUPPORTED_EXTENSIONS
            ):
                documents.append(path)

        return sorted(documents)

    def read_document(self, path: Path) -> str:
        """Read a document as UTF-8 text."""

        return path.read_text(
            encoding="utf-8",
            errors="replace",
        )

    @staticmethod
    def clean_text(text: str) -> str:
        """Normalize whitespace while preserving the actual content."""

        lines = [
            line.strip()
            for line in text.splitlines()
        ]

        lines = [
            line
            for line in lines
            if line
        ]

        return "\n".join(lines).strip()

    def chunk_text(
        self,
        text: str,
        source: str,
    ) -> list[DocumentChunk]:
        """Split text into overlapping chunks."""

        text = self.clean_text(text)

        if not text:
            return []

        chunks = []
        start = 0
        chunk_number = 0

        while start < len(text):
            end = min(
                start + self.chunk_size,
                len(text),
            )

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{Path(source).stem}-{chunk_number}",
                        source=source,
                        text=chunk,
                    )
                )

            if end >= len(text):
                break

            start = end - self.chunk_overlap
            chunk_number += 1

        return chunks

    def ingest(self) -> list[DocumentChunk]:
        """Discover, read, clean, and chunk all documents."""

        all_chunks: list[DocumentChunk] = []

        for path in self.discover_documents():
            text = self.read_document(path)

            chunks = self.chunk_text(
                text=text,
                source=str(path),
            )

            all_chunks.extend(chunks)

        return all_chunks