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

from codomyrmex.agentic_memory.core.models import (
    Memory,
    MemoryImportance,
    MemoryType,
    RetrievalResult,
)
from codomyrmex.agentic_memory.core.sqlite_store import SQLiteStore

if TYPE_CHECKING:
    from codomyrmex.agentic_memory.core.stores import InMemoryStore
    from codomyrmex.vector_store import VectorStore

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None  # type: ignore

# ── helpers ──────────────────────────────────────────────────────────


def _relevance(query: str, content: str) -> float:
    """Token-overlap relevance scorer (simple but real).

    Computes the fraction of query tokens that also appear in content.
    Returns 0.0 if either string is empty or has no tokenizable words.

    Args:
        query: The search query string.
        content: The memory content to score against.

    Returns:
        A float between 0.0 and 1.0 representing token overlap ratio.
    """
    if not query or not content:
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
        """Return the total number of memories in the store."""
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
        """Delete a memory by its ID. Returns True if the memory existed and was removed."""
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
            if SentenceTransformer is not None:
                self._embedder = SentenceTransformer(embedding_model)
            else:
                # If sentence-transformers is missing, we don't raise error here.
                # Methods like remember() and search() will gracefully degrade
                # to non-vector operations if self._embedder is None.
                self._embedder = None

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
        """Record a conversation turn with the given role and content.

        Args:
            role: Speaker role (e.g. "user", "assistant", "system").
            content: The text content of this turn.
            turn_number: Optional turn index for ordering.

        Returns:
            The persisted Memory object.
        """
        return self._agent.remember(
            content,
            memory_type=MemoryType.EPISODIC,
            metadata={"role": role, "turn": turn_number},
        )


# ── KnowledgeMemory ─────────────────────────────────────────────────


class KnowledgeMemory:
    """Specialised memory for factual knowledge and Knowledge Items (KIs).

    Provides structured storage, ranked recall, and deduplication of
    semantic knowledge items built on top of :class:`AgentMemory`.
    """

    def __init__(self, store: InMemoryStore | None = None) -> None:
        self._agent = AgentMemory(store)

    def add_fact(
        self,
        fact: str,
        source: str = "",
    ) -> Memory:
        """Store a factual knowledge item with high importance.

        Args:
            fact: The factual content to store.
            source: Optional source attribution (e.g. URL, document name).

        Returns:
            The persisted Memory object with SEMANTIC type and HIGH importance.
        """
        return self._agent.remember(
            fact,
            memory_type=MemoryType.SEMANTIC,
            importance=MemoryImportance.HIGH,
            metadata={"source": source},
        )

    def store(
        self,
        title: str,
        body: str,
        *,
        tags: list[str] | None = None,
        source_session_id: str = "",
        source: str = "",
    ) -> Memory:
        """Persist a structured Knowledge Item (KI).

        The combined ``title + body`` text is stored as the memory content
        so that ``recall()`` can rank by token overlap against both fields.

        Args:
            title: Short descriptive title for the KI.
            body: Markdown body of the KI.
            tags: Optional list of topic tags.
            source_session_id: Hermes session ID that generated this KI.
            source: Optional external source attribution.

        Returns:
            The persisted :class:`Memory` object.
        """
        import time as _time

        content = f"{title}\n\n{body}"
        return self._agent.remember(
            content,
            memory_type=MemoryType.SEMANTIC,
            importance=MemoryImportance.HIGH,
            metadata={
                "title": title,
                "tags": tags or [],
                "source_session_id": source_session_id,
                "source": source,
                "ki_stored_at": _time.time(),
            },
        )

    def recall(
        self,
        query: str,
        k: int = 10,
        *,
        use_ollama: bool = True,
        ollama_model: str = "nomic-embed-text",
    ) -> list[RetrievalResult]:
        """Return the top-*k* semantically-ranked KIs matching *query*.

        Filters to ``SEMANTIC`` memory type only so episodic memories
        stored in the same underlying store are excluded.

        When *use_ollama* is ``True``, attempts to re-rank the initial
        token-overlap candidates using cosine similarity over
        ``nomic-embed-text`` embeddings from the local Ollama server
        (``http://localhost:11434``).  If Ollama is unreachable or returns an
        error the method falls back to pure token-overlap ordering silently.

        Args:
            query: Natural language search string.
            k: Maximum results to return.
            use_ollama: Enable Ollama embedding re-ranking (default: True).
            ollama_model: Ollama embedding model name.

        Returns:
            list of :class:`RetrievalResult` sorted by combined score.
        """
        # Phase 1: token-overlap recall (always works, no external deps)
        base_results = self._agent.recall(
            query,
            k=min(k * 3, 30),
            memory_type=MemoryType.SEMANTIC,
        )

        if not use_ollama or not base_results:
            return base_results[:k]

        # Phase 2: Ollama embedding re-rank (best-effort, silently skipped)
        try:
            import json as _json
            import urllib.request as _req

            def _embed(text: str) -> list[float]:
                payload = _json.dumps({"model": ollama_model, "input": text}).encode()
                request = _req.Request(
                    "http://localhost:11434/api/embed",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with _req.urlopen(request, timeout=2.0) as resp:
                    data = _json.loads(resp.read())
                return data["embeddings"][0]

            def _cosine(a: list[float], b: list[float]) -> float:
                dot = sum(x * y for x, y in zip(a, b, strict=True))
                norm_a = sum(x * x for x in a) ** 0.5
                norm_b = sum(x * x for x in b) ** 0.5
                return dot / (norm_a * norm_b + 1e-9)

            q_vec = _embed(query)
            scored: list[tuple[float, RetrievalResult]] = []
            for rr in base_results:
                try:
                    doc_vec = _embed(rr.memory.content[:512])
                    sim = _cosine(q_vec, doc_vec)
                    blended = 0.7 * sim + 0.3 * rr.relevance_score
                    scored.append((blended, rr))
                except Exception:
                    scored.append((rr.relevance_score, rr))

            scored.sort(key=lambda x: x[0], reverse=True)
            return [rr for _, rr in scored[:k]]

        except Exception:
            # Ollama unavailable — fall back to token scoring
            return base_results[:k]

    def merge_duplicates(self, threshold: float = 0.85) -> int:
        """Fold near-duplicate KIs into their older counterpart.

        Uses token-overlap similarity (``_relevance``) to compute pairwise
        cosine-like similarity between all SEMANTIC memories.  When a newer
        memory exceeds *threshold* similarity to an older one, its body is
        appended as a dated ``## Update`` section and the newer record is
        deleted.

        Args:
            threshold: Similarity threshold (0.0–1.0). Default 0.85.

        Returns:
            Number of memories merged (deleted).
        """
        import datetime

        all_memories = self._agent.store.list_all()
        semantic = [m for m in all_memories if m.memory_type == MemoryType.SEMANTIC]
        # Sort oldest first so we always keep the canonical older copy
        semantic.sort(key=lambda m: m.created_at)

        merged = 0
        deleted_ids: set[str] = set()

        for i, base in enumerate(semantic):
            if base.id in deleted_ids:
                continue
            for candidate in semantic[i + 1 :]:
                if candidate.id in deleted_ids:
                    continue
                sim = _relevance(base.content, candidate.content)
                if sim >= threshold:
                    # Append candidate body as an Update section to base
                    now_str = datetime.datetime.fromtimestamp(
                        candidate.created_at
                    ).strftime("%Y-%m-%d")
                    update_text = f"\n\n## Update ({now_str})\n\n{candidate.content}"
                    base.content += update_text
                    self._agent.store.save(base)
                    # Remove the duplicate
                    self._agent.store.delete(candidate.id)
                    deleted_ids.add(candidate.id)
                    merged += 1

        return merged


__all__ = [
    "AgentMemory",
    "ConversationMemory",
    "KnowledgeMemory",
    "VectorStoreMemory",
]
