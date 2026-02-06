# Agentic Memory Module

**Version**: v0.1.0 | **Status**: Active

Long-term agent memory with retrieval, persistence, and automatic pruning.

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

## Exports

| Class | Description |
|-------|-------------|
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

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
