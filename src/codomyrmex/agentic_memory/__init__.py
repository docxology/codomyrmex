"""
Agentic Memory Module

Long-term agent memory with retrieval and persistence.
"""

__version__ = "0.1.0"

import hashlib
import json
import time
from typing import Optional, List, Dict, Any, Callable, TypeVar
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
import threading


class MemoryType(Enum):
    """Types of agent memory."""
    EPISODIC = "episodic"  # Specific experiences
    SEMANTIC = "semantic"  # General knowledge
    PROCEDURAL = "procedural"  # Skills/procedures
    WORKING = "working"  # Short-term active memory


class MemoryImportance(Enum):
    """Importance levels for memories."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Memory:
    """A single memory unit."""
    id: str
    content: str
    memory_type: MemoryType = MemoryType.EPISODIC
    importance: MemoryImportance = MemoryImportance.MEDIUM
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    
    @property
    def age_hours(self) -> float:
        """Get memory age in hours."""
        return (datetime.now() - self.created_at).total_seconds() / 3600
    
    @property
    def recency_score(self) -> float:
        """Get recency score (decays over time)."""
        hours_since_access = (datetime.now() - self.accessed_at).total_seconds() / 3600
        return 1.0 / (1.0 + hours_since_access)
    
    def access(self) -> None:
        """Record an access to this memory."""
        self.accessed_at = datetime.now()
        self.access_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "importance": self.importance.value,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
            "access_count": self.access_count,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Memory":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            content=data["content"],
            memory_type=MemoryType(data.get("memory_type", "episodic")),
            importance=MemoryImportance(data.get("importance", 2)),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            accessed_at=datetime.fromisoformat(data.get("accessed_at", datetime.now().isoformat())),
            access_count=data.get("access_count", 0),
        )


@dataclass
class RetrievalResult:
    """Result of memory retrieval."""
    memory: Memory
    relevance_score: float
    recency_score: float
    importance_score: float
    
    @property
    def combined_score(self) -> float:
        """Get combined ranking score."""
        return (
            0.4 * self.relevance_score +
            0.3 * self.recency_score +
            0.3 * self.importance_score
        )


class MemoryStore(ABC):
    """Base class for memory storage backends."""
    
    @abstractmethod
    def save(self, memory: Memory) -> None:
        """Save a memory."""
        pass
    
    @abstractmethod
    def get(self, memory_id: str) -> Optional[Memory]:
        """Get a memory by ID."""
        pass
    
    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """Delete a memory."""
        pass
    
    @abstractmethod
    def list_all(self) -> List[Memory]:
        """List all memories."""
        pass


class InMemoryStore(MemoryStore):
    """In-memory storage for memories."""
    
    def __init__(self):
        self._memories: Dict[str, Memory] = {}
        self._lock = threading.Lock()
    
    def save(self, memory: Memory) -> None:
        """Save a memory."""
        with self._lock:
            self._memories[memory.id] = memory
    
    def get(self, memory_id: str) -> Optional[Memory]:
        """Get a memory by ID."""
        return self._memories.get(memory_id)
    
    def delete(self, memory_id: str) -> bool:
        """Delete a memory."""
        with self._lock:
            if memory_id in self._memories:
                del self._memories[memory_id]
                return True
        return False
    
    def list_all(self) -> List[Memory]:
        """List all memories."""
        return list(self._memories.values())


class JSONFileStore(MemoryStore):
    """JSON file storage for memories."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._memories: Dict[str, Memory] = {}
        self._lock = threading.Lock()
        self._load()
    
    def _load(self) -> None:
        """Load memories from file."""
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                for item in data:
                    memory = Memory.from_dict(item)
                    self._memories[memory.id] = memory
        except (FileNotFoundError, json.JSONDecodeError):
            self._memories = {}
    
    def _save_to_file(self) -> None:
        """Save all memories to file."""
        data = [m.to_dict() for m in self._memories.values()]
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def save(self, memory: Memory) -> None:
        """Save a memory."""
        with self._lock:
            self._memories[memory.id] = memory
            self._save_to_file()
    
    def get(self, memory_id: str) -> Optional[Memory]:
        """Get a memory by ID."""
        return self._memories.get(memory_id)
    
    def delete(self, memory_id: str) -> bool:
        """Delete a memory."""
        with self._lock:
            if memory_id in self._memories:
                del self._memories[memory_id]
                self._save_to_file()
                return True
        return False
    
    def list_all(self) -> List[Memory]:
        """List all memories."""
        return list(self._memories.values())


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
        store: Optional[MemoryStore] = None,
        embedding_fn: Optional[Callable[[str], List[float]]] = None,
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
    
    def _compute_embedding(self, text: str) -> Optional[List[float]]:
        """Compute embedding for text."""
        if self.embedding_fn:
            return self.embedding_fn(text)
        return None
    
    def remember(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.EPISODIC,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None,
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
    
    def recall(
        self,
        query: str,
        k: int = 5,
        memory_type: Optional[MemoryType] = None,
        min_importance: Optional[MemoryImportance] = None,
    ) -> List[RetrievalResult]:
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
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
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
        format_fn: Optional[Callable[[List[Memory]], str]] = None,
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
        source: Optional[str] = None,
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
        store: Optional[MemoryStore] = None,
        vector_store=None,  # VectorStore instance
        embedding_fn: Optional[Callable[[str], List[float]]] = None,
        max_memories: int = 10000,
        hybrid_weight: float = 0.5,  # Balance between vector and keyword
    ):
        super().__init__(store, embedding_fn, max_memories)
        self._vector_store = vector_store
        self.hybrid_weight = hybrid_weight
    
    def remember(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.EPISODIC,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None,
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
        vector_weight: Optional[float] = None,
    ) -> List[RetrievalResult]:
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
        store: Optional[MemoryStore] = None,
        embedding_fn: Optional[Callable[[str], List[float]]] = None,
        summarize_fn: Optional[Callable[[List[str]], str]] = None,
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


__all__ = [
    # Enums
    "MemoryType",
    "MemoryImportance",
    # Data classes
    "Memory",
    "RetrievalResult",
    # Stores
    "MemoryStore",
    "InMemoryStore",
    "JSONFileStore",
    # Core
    "AgentMemory",
    "ConversationMemory",
    "KnowledgeMemory",
    # Enhanced
    "VectorStoreMemory",
    "SummaryMemory",
]
