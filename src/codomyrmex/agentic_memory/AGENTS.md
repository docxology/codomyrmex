# Agent Guidelines - Agentic Memory

## Module Overview

Long-term memory for agents with retrieval, persistence, and automatic pruning.

## Key Classes

- **AgentMemory** — Core memory system with remember/recall
- **Memory** — Single memory unit with type, importance, timestamps
- **ConversationMemory** — Optimized for dialogue history
- **KnowledgeMemory** — Fact storage with confidence
- **VectorStoreMemory** — Hybrid keyword + vector search
- **SummaryMemory** — Auto-summarizes old memories

## Agent Instructions

1. **Use appropriate type** — EPISODIC for events, SEMANTIC for facts
2. **Set importance correctly** — HIGH/CRITICAL for critical info
3. **Persist for long-running** — Use `JSONFileStore` for persistence
4. **Retrieve before acting** — Call `recall()` for relevant context
5. **Prune regularly** — Set `max_memories` to avoid unbounded growth

## Common Patterns

```python
from codomyrmex.agentic_memory import AgentMemory, MemoryType, MemoryImportance

memory = AgentMemory(max_memories=1000)

# Remember important context
memory.remember(
    "User is building a Python web application",
    memory_type=MemoryType.SEMANTIC,
    importance=MemoryImportance.HIGH
)

# Get context for LLM
context = memory.get_context("What framework should I use?")

# Use in prompt
prompt = f"{context}\n\nUser: {user_message}"
```

## Testing Patterns

```python
# Verify memory storage and retrieval
memory = AgentMemory()
memory.remember("Python is great")
memory.remember("JavaScript is popular")

results = memory.recall("programming languages")
assert len(results) == 2

# Verify importance ranking
memory.remember("Critical bug found", importance=MemoryImportance.CRITICAL)
results = memory.recall("issues")
assert results[0].memory.importance == MemoryImportance.CRITICAL
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
