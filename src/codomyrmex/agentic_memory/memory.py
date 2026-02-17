"""
Agentic Memory Core

Agent memory systems with retrieval, summarization, and hybrid search.
"""

import threading
import time
from typing import Any
from collections.abc import Callable

from .models import Memory, MemoryImportance, MemoryType, RetrievalResult
from .stores import InMemoryStore, MemoryStore


class AgentMemory:
    """
    Long-term memory system for AI agents.

    Usage:
        memory = AgentMemory(store=InMemoryStore())

        # Add memories
        memory.remember(
            "User prefers Python over JavaScript",
            memory_type=MemoryType.SEMANTIC,
            importance=MemoryImportance.HIGH,
        )

        # Retrieve relevant memories
        results = memory.recall("programming language preferences", k=5)

        # Get context for LLM
        context = memory.get_context("What language should I use?")
    """

    def __init__(
        self,
        store: MemoryStore | None = None,
        embedding_fn: Callable[[str], list[float]] | None = None,
        max_memories: int = 10000,
    ):
        self.store = store or InMemoryStore()
        self.embedding_fn = embedding_fn
        self.max_memories = max_memories
        self._counter = 0
        self._lock = threading.Lock()

    def _generate_id(self) -> str:
        """Generate unique memory ID."""
        with self._lock:
            self._counter += 1
            return f"mem_{self._counter}_{int(time.time())}"

    def _compute_embedding(self, text: str) -> list[float] | None:
        """Compute embedding for text."""
        if self.embedding_fn:
            return self.embedding_fn(text)
        return None

    def remember(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.EPISODIC,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        metadata: dict[str, Any] | None = None,
    ) -> Memory:
        """
        Store a new memory.

        Args:
            content: The memory content
            memory_type: Type of memory
            importance: Importance level
            metadata: Additional metadata

        Returns:
            The created Memory object
        """
        memory = Memory(
            id=self._generate_id(),
            content=content,
            memory_type=memory_type,
            importance=importance,
            metadata=metadata or {},
            embedding=self._compute_embedding(content),
        )

        self.store.save(memory)

        # Prune if over limit
        self._prune_if_needed()

        return memory

    def add(
        self,
        content: str,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        metadata: dict[str, Any] | None = None,
        memory_type: MemoryType = MemoryType.EPISODIC,
    ) -> Memory:
        """Alias for ``remember()`` — provides MCP tool compatibility."""
        return self.remember(
            content=content,
            memory_type=memory_type,
            importance=importance,
            metadata=metadata,
        )

    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[RetrievalResult]:
        """Alias for ``recall()`` — provides MCP tool compatibility."""
        return self.recall(query, k=limit)

    def recall(
        self,
        query: str,
        k: int = 5,
        memory_type: MemoryType | None = None,
        min_importance: MemoryImportance | None = None,
    ) -> list[RetrievalResult]:
        """
        Retrieve relevant memories.

        Args:
            query: Search query
            k: Number of results
            memory_type: Filter by type
            min_importance: Minimum importance

        Returns:
            List of retrieval results ranked by relevance
        """
        all_memories = self.store.list_all()

        # Filter
        if memory_type:
            all_memories = [m for m in all_memories if m.memory_type == memory_type]
        if min_importance:
            all_memories = [m for m in all_memories if m.importance.value >= min_importance.value]

        # Score each memory
        results = []
        query_embedding = self._compute_embedding(query)

        for memory in all_memories:
            # Relevance score (keyword or embedding based)
            if query_embedding and memory.embedding:
                relevance = self._cosine_similarity(query_embedding, memory.embedding)
            else:
                # Simple keyword matching
                query_words = set(query.lower().split())
                content_words = set(memory.content.lower().split())
                overlap = len(query_words & content_words)
                relevance = overlap / max(len(query_words), 1)

            # Importance score (normalized to 0-1)
            importance_score = memory.importance.value / 4.0

            results.append(RetrievalResult(
                memory=memory,
                relevance_score=relevance,
                recency_score=memory.recency_score,
                importance_score=importance_score,
            ))

        # Sort by combined score and take top k
        results.sort(key=lambda r: r.combined_score, reverse=True)
        top_results = results[:k]

        # Mark accessed
        for result in top_results:
            result.memory.access()
            self.store.save(result.memory)

        return top_results

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity."""
        if len(vec1) != len(vec2):
            return 0.0

        dot = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = sum(x * x for x in vec1) ** 0.5
        mag2 = sum(x * x for x in vec2) ** 0.5

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot / (mag1 * mag2)

    def forget(self, memory_id: str) -> bool:
        """Remove a memory."""
        return self.store.delete(memory_id)

    def get_context(
        self,
        query: str,
        k: int = 5,
        format_fn: Callable[[list[Memory]], str] | None = None,
    ) -> str:
        """
        Get formatted context for LLM prompt.

        Args:
            query: The query to find relevant memories for
            k: Number of memories to include
            format_fn: Optional custom formatter

        Returns:
            Formatted string of relevant memories
        """
        results = self.recall(query, k=k)
        memories = [r.memory for r in results]

        if format_fn:
            return format_fn(memories)

        # Default formatting
        lines = ["Relevant memories:"]
        for i, memory in enumerate(memories, 1):
            lines.append(f"{i}. [{memory.memory_type.value}] {memory.content}")

        return "\n".join(lines)

    def _prune_if_needed(self) -> None:
        """Remove old memories if over limit."""
        all_memories = self.store.list_all()
        if len(all_memories) <= self.max_memories:
            return

        # Sort by combined score (lower = more forgettable)
        scored = []
        for memory in all_memories:
            score = (
                memory.recency_score * 0.5 +
                (memory.importance.value / 4.0) * 0.3 +
                (memory.access_count / max(memory.access_count + 1, 1)) * 0.2
            )
            scored.append((memory, score))

        scored.sort(key=lambda x: x[1])

        # Remove lowest scoring
        to_remove = len(all_memories) - self.max_memories
        for memory, _ in scored[:to_remove]:
            self.store.delete(memory.id)

    @property
    def memory_count(self) -> int:
        """Get total number of memories."""
        return len(self.store.list_all())


# Specialized memory types
class ConversationMemory(AgentMemory):
    """Memory optimized for conversation history."""

    def add_turn(
        self,
        role: str,
        content: str,
        turn_number: int = 0,
    ) -> Memory:
        """Add a conversation turn."""
        return self.remember(
            content=content,
            memory_type=MemoryType.EPISODIC,
            importance=MemoryImportance.MEDIUM,
            metadata={"role": role, "turn": turn_number},
        )


class KnowledgeMemory(AgentMemory):
    """Memory optimized for knowledge/facts."""

    def add_fact(
        self,
        fact: str,
        source: str | None = None,
        confidence: float = 1.0,
    ) -> Memory:
        """Add a factual memory."""
        return self.remember(
            content=fact,
            memory_type=MemoryType.SEMANTIC,
            importance=MemoryImportance.HIGH,
            metadata={"source": source, "confidence": confidence},
        )


class VectorStoreMemory(AgentMemory):
    """Memory with integrated vector store for hybrid retrieval."""

    def __init__(
        self,
        store: MemoryStore | None = None,
        vector_store=None,  # VectorStore instance
        embedding_fn: Callable[[str], list[float]] | None = None,
        max_memories: int = 10000,
        hybrid_weight: float = 0.5,  # Balance between vector and keyword
    ):
        super().__init__(store, embedding_fn, max_memories)

        # Auto-create a vector store if none provided
        if vector_store is None:
            try:
                from codomyrmex.vector_store import InMemoryVectorStore as _IMVS
                vector_store = _IMVS()
            except ImportError:
                pass  # vector_store module not available — graceful degradation

        self._vector_store = vector_store
        self.hybrid_weight = hybrid_weight

    @classmethod
    def from_chromadb(
        cls,
        path: str,
        *,
        embedding_fn: Callable[[str], list[float]] | None = None,
        max_memories: int = 10000,
    ) -> "VectorStoreMemory":
        """Create a VectorStoreMemory backed by ChromaDB.

        Args:
            path: Filesystem path for the ChromaDB persistent store.
            embedding_fn: Optional embedding function.
            max_memories: Maximum memories to retain.

        Returns:
            A ``VectorStoreMemory`` with ChromaDB backing.

        Raises:
            ImportError: If ``chromadb`` is not installed.
        """
        try:
            import chromadb  # type: ignore[import-untyped]
        except ImportError:
            raise ImportError(
                "chromadb is required for from_chromadb(). "
                "Install with: pip install chromadb"
            )

        client = chromadb.PersistentClient(path=path)
        collection = client.get_or_create_collection("codomyrmex_memory")

        class _ChromaVectorStore:
            """Adapter wrapping ChromaDB collection as a VectorStore-like object."""

            def add(self, id: str, embedding: list[float], metadata: dict | None = None) -> None:
                collection.add(ids=[id], embeddings=[embedding], metadatas=[metadata or {}])

            def search(self, query: list[float], k: int = 10) -> list:
                results = collection.query(query_embeddings=[query], n_results=k)
                from codomyrmex.vector_store.models import SearchResult
                return [
                    SearchResult(id=rid, score=1.0, embedding=[], metadata=meta or {})
                    for rid, meta in zip(results["ids"][0], results["metadatas"][0])
                ]

            def delete(self, id: str) -> None:
                collection.delete(ids=[id])

        return cls(
            vector_store=_ChromaVectorStore(),
            embedding_fn=embedding_fn,
            max_memories=max_memories,
        )

    def remember(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.EPISODIC,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        metadata: dict[str, Any] | None = None,
    ) -> Memory:
        """Store memory with vector indexing."""
        memory = super().remember(content, memory_type, importance, metadata)

        # Also index in vector store
        if self._vector_store and memory.embedding:
            self._vector_store.add(
                memory.id,
                memory.embedding,
                {"content": content, "type": memory_type.value},
            )

        return memory

    def hybrid_recall(
        self,
        query: str,
        k: int = 5,
        vector_weight: float | None = None,
    ) -> list[RetrievalResult]:
        """Hybrid search using both vector similarity and keyword matching."""
        weight = vector_weight if vector_weight is not None else self.hybrid_weight

        # Get keyword results
        keyword_results = self.recall(query, k=k * 2)
        keyword_scores = {r.memory.id: r.combined_score for r in keyword_results}

        # Get vector results
        vector_scores = {}
        if self._vector_store and self.embedding_fn:
            query_embedding = self.embedding_fn(query)
            vector_results = self._vector_store.search(query_embedding, k=k * 2)
            for vr in vector_results:
                vector_scores[vr.id] = vr.score

        # Combine scores
        all_ids = set(keyword_scores.keys()) | set(vector_scores.keys())
        combined = []

        for mem_id in all_ids:
            memory = self.store.get(mem_id)
            if not memory:
                continue

            kw_score = keyword_scores.get(mem_id, 0)
            vec_score = vector_scores.get(mem_id, 0)
            hybrid_score = (1 - weight) * kw_score + weight * vec_score

            combined.append(RetrievalResult(
                memory=memory,
                relevance_score=hybrid_score,
                recency_score=memory.recency_score,
                importance_score=memory.importance.value / 4.0,
            ))

        combined.sort(key=lambda r: r.combined_score, reverse=True)
        return combined[:k]

    def forget(self, memory_id: str) -> bool:
        """Remove from both stores."""
        if self._vector_store:
            self._vector_store.delete(memory_id)
        return super().forget(memory_id)


class SummaryMemory(AgentMemory):
    """Memory that auto-summarizes old memories."""

    def __init__(
        self,
        store: MemoryStore | None = None,
        embedding_fn: Callable[[str], list[float]] | None = None,
        summarize_fn: Callable[[list[str]], str] | None = None,
        max_memories: int = 1000,
        summarize_threshold: int = 100,
    ):
        super().__init__(store, embedding_fn, max_memories)
        self.summarize_fn = summarize_fn
        self.summarize_threshold = summarize_threshold
        self._summary_count = 0

    def _prune_if_needed(self) -> None:
        """Summarize old memories instead of deleting."""
        all_memories = self.store.list_all()
        if len(all_memories) <= self.summarize_threshold:
            return

        if not self.summarize_fn:
            return super()._prune_if_needed()

        # Get oldest memories
        sorted_mems = sorted(all_memories, key=lambda m: m.created_at)
        to_summarize = sorted_mems[:self.summarize_threshold // 2]

        if len(to_summarize) < 5:
            return

        # Summarize them
        contents = [m.content for m in to_summarize]
        summary = self.summarize_fn(contents)

        # Create summary memory
        self._summary_count += 1
        self.remember(
            content=f"[Summary {self._summary_count}] {summary}",
            memory_type=MemoryType.SEMANTIC,
            importance=MemoryImportance.HIGH,
            metadata={"is_summary": True, "source_count": len(to_summarize)},
        )

        # Delete summarized memories
        for mem in to_summarize:
            self.store.delete(mem.id)
