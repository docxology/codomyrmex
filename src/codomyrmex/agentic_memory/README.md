# Agentic Memory Module

**Version**: v0.1.0 | **Status**: Active

Long-term agent memory with retrieval, persistence, and automatic pruning.

## Key Exports

### Classes

- **`MemoryType`** — Types of agent memory.
- **`MemoryImportance`** — Importance levels for memories.
- **`Memory`** — A single memory unit.
- **`RetrievalResult`** — Result of memory retrieval.
- **`MemoryStore`** — Base class for memory storage backends.
- **`InMemoryStore`** — In-memory storage for memories.
- **`JSONFileStore`** — JSON file storage for memories.
- **`AgentMemory`** — Long-term memory system for AI agents.

## Quick Start

```python
from codomyrmex.agentic_memory import (
    AgentMemory, Memory, MemoryType, MemoryImportance,
    InMemoryStore, JSONFileStore
)

# Create memory system
memory = AgentMemory()

# Store memories
memory.remember(
    "User prefers Python over JavaScript",
    memory_type=MemoryType.SEMANTIC,
    importance=MemoryImportance.HIGH
)

memory.remember(
    "Project uses FastAPI for backend",
    memory_type=MemoryType.SEMANTIC
)

# Retrieve relevant memories
results = memory.recall("What language should I use?", k=5)
for r in results:
    print(f"{r.combined_score:.2f}: {r.memory.content}")

# Get context for LLM prompt
context = memory.get_context("programming preferences")
print(context)
```

## Specialized Memory Types

```python
from codomyrmex.agentic_memory import (
    ConversationMemory, KnowledgeMemory, VectorStoreMemory, SummaryMemory
)

# Conversation history
conv = ConversationMemory()
conv.add_turn("user", "How do I install Python?")
conv.add_turn("assistant", "Run `brew install python`")

# Knowledge base
kb = KnowledgeMemory()
kb.add_fact("Earth orbits the Sun", source="Wikipedia", confidence=1.0)

# Vector-enhanced retrieval
vec_mem = VectorStoreMemory(embedding_fn=get_embeddings)
vec_mem.remember("Important fact...")
results = vec_mem.hybrid_recall("query", vector_weight=0.7)

# Auto-summarizing memory
summary_mem = SummaryMemory(summarize_fn=llm_summarize)
```

## Directory Structure

- `models.py` — Data models (`Memory`, `MemoryType`, `RetrievalResult`)
- `stores.py` — Storage backends (`MemoryStore`, `InMemoryStore`, `JSONFileStore`)
- `memory.py` — Core logic (`AgentMemory`, specialized memory types)
- `__init__.py` — Public API re-exports

## Exports

| Class | Description |
| :--- | :--- |
| `AgentMemory` | Core memory system |
| `Memory` | Single memory unit |
| `MemoryType` | Enum: episodic, semantic, procedural, working |
| `MemoryImportance` | Enum: low, medium, high, critical |
| `InMemoryStore` | In-memory storage |
| `JSONFileStore` | File-based persistence |
| `ConversationMemory` | Conversation history |
| `KnowledgeMemory` | Fact storage |
| `VectorStoreMemory` | Vector-enhanced retrieval |
| `SummaryMemory` | Auto-summarizing memory |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k agentic_memory -v
```

## Documentation

- [Module Documentation](../../../docs/modules/agentic_memory/README.md)
- [Agent Guide](../../../docs/modules/agentic_memory/AGENTS.md)
- [Specification](../../../docs/modules/agentic_memory/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
