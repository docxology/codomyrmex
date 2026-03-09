"""High-level agent memory classes.

``AgentMemory`` wraps an ``InMemoryStore`` with remember/recall/forget.
``VectorStoreMemory`` adds the same API but backed by any store.
``ConversationMemory`` and ``KnowledgeMemory`` are thin specialisations
for turn-based dialogue and factual knowledge respectively.
"""

from __future__ import annotations

import time
import uuid
from typing import TYPE_CHECKING, Any

from codomyrmex.agentic_memory.models import (
    Memory,
    MemoryImportance,
    MemoryType,
    RetrievalResult,
)
from codomyrmex.agentic_memory.sqlite_store import SQLiteStore

if TYPE_CHECKING:
    from codomyrmex.agentic_memory.stores import InMemoryStore
    from codomyrmex.vector_store import VectorStore

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None  # type: ignore

# ── helpers ──────────────────────────────────────────────────────────


def _relevance(query: str, content: str) -> float:
    """Token-overlap relevance scorer (simple but real)."""
    if not query:
        return 0.0
    q_tokens = set(query.lower().split())
    c_tokens = set(content.lower().split())
    if not q_tokens:
        return 0.0
    overlap = q_tokens & c_tokens
    return len(overlap) / len(q_tokens)


def _recency_score(created_at: float, half_life: float = 3600.0) -> float:
    """Exponential-decay recency score."""
    age = max(0.0, time.time() - created_at)
    import math

    return math.exp(-age / half_life)


# ── AgentMemory ──────────────────────────────────────────────────────


class AgentMemory:
    """Agent-level memory with remember / recall / forget / search."""

    def __init__(self, store: Any = None) -> None:
        self.store = store or SQLiteStore()

    @property
    def memory_count(self) -> int:
        return len(self.store.list_all())

    # -- remember / add -----------------------------------------------

    def remember(
        self,
        content: str,
        *,
        memory_type: MemoryType = MemoryType.EPISODIC,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        metadata: dict[str, Any] | None = None,
    ) -> Memory:
        """Create and persist a new memory."""
        mem = Memory(
            id=str(uuid.uuid4()),
            content=content,
            memory_type=memory_type,
            importance=importance,
            metadata=metadata or {},
        )
        self.store.save(mem)
        return mem

    def add(
        self,
        content: str,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
    ) -> Memory:
        """Convenience alias for :meth:`remember`."""
        return self.remember(content, importance=importance)

    # -- recall / search ----------------------------------------------

    def recall(
        self,
        query: str,
        *,
        k: int = 10,
        memory_type: MemoryType | None = None,
        min_importance: MemoryImportance | None = None,
    ) -> list[RetrievalResult]:
        """Return the top-*k* memories matching *query*."""
        return self._search_internal(
            query,
            k=k,
            memory_type=memory_type,
            min_importance=min_importance,
        )

    def search(self, query: str, k: int = 10) -> list[RetrievalResult]:
        """Public search API (matches ``VectorStoreMemory.search``)."""
        return self._search_internal(query, k=k)

    def _search_internal(
        self,
        query: str,
        *,
        k: int = 10,
        memory_type: MemoryType | None = None,
        min_importance: MemoryImportance | None = None,
    ) -> list[RetrievalResult]:
        candidates = self.store.list_all()
        if memory_type is not None:
            candidates = [m for m in candidates if m.memory_type == memory_type]
        if min_importance is not None:
            candidates = [
                m for m in candidates if m.importance.value >= min_importance.value
            ]

        results: list[RetrievalResult] = []
        for mem in candidates:
            rel = _relevance(query, mem.content) if query else 0.0
            rec = _recency_score(mem.created_at)
            imp = mem.importance.value / 4.0
            results.append(
                RetrievalResult(
                    memory=mem,
                    relevance_score=rel,
                    recency_score=rec,
                    importance_score=imp,
                )
            )

        # If no query, return all (filtered). Otherwise sort by score.
        if query:
            results.sort(key=lambda r: r.combined_score, reverse=True)
        return results[:k]

    # -- forget -------------------------------------------------------

    def forget(self, memory_id: str) -> bool:
        """Forget."""
        return self.store.delete(memory_id)

    # -- context ------------------------------------------------------

    def get_context(self, query: str, k: int = 5) -> str:
        """Return a formatted string of relevant memories."""
        results = self.recall(query, k=k)
        if not results:
            return ""
        lines = [f"- {r.memory.content}" for r in results]
        return "\n".join(lines)


# ── VectorStoreMemory ────────────────────────────────────────────────


class VectorStoreMemory:
    """Memory with pluggable store backend and semantic search."""

    def __init__(
        self,
        store: Any = None,
        vector_store: VectorStore | None = None,
        embedding_model: str = "all-MiniLM-L6-v2",
    ) -> None:
        self.store = store or SQLiteStore()
        self._agent = AgentMemory(self.store)

        self.vector_store = vector_store
        if self.vector_store is None:
            from codomyrmex.vector_store import create_vector_store

            try:
                self.vector_store = create_vector_store(
                    backend="chroma", persist_directory="chroma_db"
                )
            except (ValueError, ImportError):
                self.vector_store = create_vector_store(backend="namespaced")

        self._embedder = None
        if self.vector_store is not None:
            if SentenceTransformer is None:
                raise ImportError(
                    "sentence-transformers is required to use VectorStoreMemory "
                    "with a vector_store backend. Please install it."
                )
            self._embedder = SentenceTransformer(embedding_model)

    def remember(
        self,
        content: str,
        *,
        memory_type: MemoryType = MemoryType.EPISODIC,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        metadata: dict[str, Any] | None = None,
    ) -> Memory:
        """Create and persist a new memory, including vector embeddings if configured."""
        mem = self._agent.remember(
            content,
            memory_type=memory_type,
            importance=importance,
            metadata=metadata,
        )

        if self.vector_store and self._embedder:
            embedding = self._embedder.encode(content).tolist()
            if isinstance(embedding, list):
                # Ensure the embedding is indeed a list of floats
                self.vector_store.add(
                    id=mem.id,
                    embedding=embedding,
                    metadata={
                        "importance": importance.value,
                        "type": memory_type.value,
                    },
                )

        return mem

    def add(
        self,
        content: str,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
    ) -> Memory:
        """Convenience alias for :meth:`remember`."""
        return self.remember(content, importance=importance)

    def search(self, query: str, k: int = 10) -> list[RetrievalResult]:
        """Search memory, using semantic vector similarity if a backend is configured."""
        if not self.vector_store or not self._embedder:
            return self._agent.search(query, k=k)

        if not query:
            return self._agent.search(query, k=k)

        query_embedding = self._embedder.encode(query).tolist()
        v_results = self.vector_store.search(query_embedding, k=k * 2)

        results: list[RetrievalResult] = []
        for result in v_results:
            mem = self.store.get(result.id)
            if mem:
                rec = _recency_score(mem.created_at)
                imp = mem.importance.value / 4.0

                results.append(
                    RetrievalResult(
                        memory=mem,
                        relevance_score=result.score,
                        recency_score=rec,
                        importance_score=imp,
                    )
                )

        results.sort(key=lambda r: r.combined_score, reverse=True)
        return results[:k]


# ── ConversationMemory ───────────────────────────────────────────────


class ConversationMemory:
    """Specialised memory for conversation turns."""

    def __init__(self, store: InMemoryStore | None = None) -> None:
        self._agent = AgentMemory(store)

    def add_turn(
        self,
        role: str,
        content: str,
        *,
        turn_number: int = 0,
    ) -> Memory:
        return self._agent.remember(
            content,
            memory_type=MemoryType.EPISODIC,
            metadata={"role": role, "turn": turn_number},
        )


# ── KnowledgeMemory ─────────────────────────────────────────────────


class KnowledgeMemory:
    """Specialised memory for factual knowledge."""

    def __init__(self, store: InMemoryStore | None = None) -> None:
        self._agent = AgentMemory(store)

    def add_fact(
        self,
        fact: str,
        source: str = "",
    ) -> Memory:
        return self._agent.remember(
            fact,
            memory_type=MemoryType.SEMANTIC,
            importance=MemoryImportance.HIGH,
            metadata={"source": source},
        )
