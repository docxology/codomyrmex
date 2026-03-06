"""Vector store abstractions for RAG retrieval."""

from abc import ABC, abstractmethod

from .models import Chunk, RetrievalResult


class VectorStore(ABC):
    """Base class for vector storage."""

    @abstractmethod
    def add(self, chunks: list[Chunk]) -> None:
        """Add chunks with embeddings."""

    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        k: int = 5,
    ) -> list[RetrievalResult]:
        """Search for similar chunks."""

    @abstractmethod
    def delete(self, document_id: str) -> int:
        """Delete chunks by document ID."""


class InMemoryVectorStore(VectorStore):
    """Simple in-memory vector store."""

    def __init__(self):
        self._chunks: list[Chunk] = []

    def add(self, chunks: list[Chunk]) -> None:
        """Add chunks with embeddings."""
        for chunk in chunks:
            if chunk.embedding is not None:
                self._chunks.append(chunk)

    def search(
        self,
        query_embedding: list[float],
        k: int = 5,
    ) -> list[RetrievalResult]:
        """Search for similar chunks using cosine similarity."""
        results = []

        for chunk in self._chunks:
            if chunk.embedding is None:
                continue

            dot = sum(
                a * b for a, b in zip(query_embedding, chunk.embedding, strict=False)
            )
            mag1 = sum(x * x for x in query_embedding) ** 0.5
            mag2 = sum(x * x for x in chunk.embedding) ** 0.5

            if mag1 > 0 and mag2 > 0:
                score = dot / (mag1 * mag2)
                results.append(RetrievalResult(chunk=chunk, score=score))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:k]

    def delete(self, document_id: str) -> int:
        """Delete chunks by document ID."""
        original = len(self._chunks)
        self._chunks = [c for c in self._chunks if c.document_id != document_id]
        return original - len(self._chunks)

    @property
    def count(self) -> int:
        """Count."""
        return len(self._chunks)
