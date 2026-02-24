# Agentic Memory Module API Specification

**Version**: v0.1.0 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview

The `agentic_memory` module provides persistent and in-process memory for AI agents. It implements remember/recall/forget semantics with token-overlap relevance scoring and exponential-decay recency scoring. Memories are typed (episodic, semantic, procedural) and ranked by importance.

## 2. Core Components

### 2.1 Enumerations (`models.py`)

**`MemoryType`** (enum):
| Value | Meaning |
|-------|---------|
| `EPISODIC` | Event-based memories (conversation turns, actions) |
| `SEMANTIC` | Factual knowledge |
| `PROCEDURAL` | Process or skill-based knowledge |

**`MemoryImportance`** (enum, orderable by `.value`):
| Value | Integer |
|-------|---------|
| `LOW` | 1 |
| `MEDIUM` | 2 |
| `HIGH` | 3 |
| `CRITICAL` | 4 |

### 2.2 Data Models (`models.py`)

**`Memory`** (dataclass): A single memory entry.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | UUID identifier |
| `content` | `str` | Text content of the memory |
| `memory_type` | `MemoryType` | Classification (default: `EPISODIC`) |
| `importance` | `MemoryImportance` | Priority level (default: `MEDIUM`) |
| `metadata` | `dict[str, Any]` | Arbitrary metadata |
| `tags` | `list[str]` | Searchable tags |
| `created_at` | `float` | Unix timestamp of creation |
| `access_count` | `int` | Number of times retrieved |
| `last_accessed` | `float` | Unix timestamp of last access |

Methods: `access() -> None`, `to_dict() -> dict`, `from_dict(data) -> Memory` (classmethod).

**`RetrievalResult`** (dataclass): Output of recall/search operations.

| Field | Type | Description |
|-------|------|-------------|
| `memory` | `Memory` | The matched memory |
| `relevance_score` | `float` | Token-overlap score (0–1) |
| `recency_score` | `float` | Exponential-decay score (0–1) |
| `importance_score` | `float` | Normalized importance (0–1) |
| `combined_score` | `float` (property) | Weighted: `0.5*relevance + 0.3*recency + 0.2*importance` |

### 2.3 Memory Stores (`stores.py`)

**`InMemoryStore`**: In-process dict-backed store. Not persistent across restarts.

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `save` | `(memory: Memory)` | `None` | Upsert a memory entry |
| `get` | `(memory_id: str)` | `Memory \| None` | Fetch by ID; increments `access_count` |
| `delete` | `(memory_id: str)` | `bool` | Remove; returns `True` if existed |
| `list_all` | `()` | `list[Memory]` | Return all stored memories |

**`JSONFileStore`**: Thread-safe file-backed store. Flushes to disk on every write.

| Method | Same as `InMemoryStore` | Extra |
|--------|-------------------------|-------|
| `__init__` | `(path: str)` | Creates parent dirs; loads existing data on init |

### 2.4 High-Level Memory Classes (`memory.py`)

**`AgentMemory`**: Primary agent memory with full remember/recall/forget API.

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `remember` | `(content, *, memory_type, importance, metadata)` | `Memory` | Create and persist a memory |
| `add` | `(content, importance)` | `Memory` | Convenience alias for `remember` |
| `recall` | `(query, *, k, memory_type, min_importance)` | `list[RetrievalResult]` | Top-k memories matching query |
| `search` | `(query, k)` | `list[RetrievalResult]` | Public search API |
| `forget` | `(memory_id: str)` | `bool` | Delete a memory by ID |
| `get_context` | `(query, k)` | `str` | Formatted string of relevant memories |
| `memory_count` | property | `int` | Number of stored memories |

**`VectorStoreMemory`**: Memory with pluggable store backend.

| Method | Signature | Returns |
|--------|-----------|---------|
| `add` | `(content, importance)` | `Memory` |
| `search` | `(query, k)` | `list[RetrievalResult]` |

**`ConversationMemory`**: Specialized for dialogue turn storage.

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `add_turn` | `(role, content, *, turn_number)` | `Memory` | Store a conversation turn with role metadata |

**`KnowledgeMemory`**: Specialized for factual knowledge.

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `add_fact` | `(fact, source="")` | `Memory` | Store a fact with `SEMANTIC` type and `HIGH` importance |

## 3. Usage Example

```python
from codomyrmex.agentic_memory.memory import AgentMemory
from codomyrmex.agentic_memory.models import MemoryType, MemoryImportance

# Basic usage
mem = AgentMemory()
mem.remember("The project deadline is March 1st",
             memory_type=MemoryType.EPISODIC,
             importance=MemoryImportance.HIGH)

results = mem.recall("project deadline", k=5)
for r in results:
    print(f"[{r.combined_score:.2f}] {r.memory.content}")

# Persistent store
from codomyrmex.agentic_memory.stores import JSONFileStore
store = JSONFileStore("/tmp/agent_memories.json")
persistent = AgentMemory(store=store)
persistent.remember("User prefers dark mode", importance=MemoryImportance.MEDIUM)

# Conversation memory
from codomyrmex.agentic_memory.memory import ConversationMemory
conv = ConversationMemory()
conv.add_turn("user", "What is the capital of France?", turn_number=1)
conv.add_turn("assistant", "Paris.", turn_number=2)
```
