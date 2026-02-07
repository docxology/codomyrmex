# Agentic Memory Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `agentic_memory` module provides a long-term memory system for AI agents with retrieval, persistence, and automatic pruning. It supports multiple memory types (episodic, semantic, procedural, working), importance-based ranking, recency-decay scoring, and pluggable storage backends. The module enables agents to maintain stateful, persistent context across interactions through keyword and embedding-based retrieval.


## Installation

```bash
pip install codomyrmex
```

## Key Features

- **Multi-type memory model**: Supports episodic (experiences), semantic (knowledge), procedural (skills), and working (short-term) memory types via `MemoryType` enum
- **Importance-based ranking**: Four-tier importance levels (LOW, MEDIUM, HIGH, CRITICAL) influence retrieval scoring
- **Recency decay scoring**: Memories decay in relevance over time based on last access, using an inverse time-decay function
- **Composite retrieval scoring**: Retrieval combines relevance (0.4), recency (0.3), and importance (0.3) weights for balanced ranking
- **Pluggable storage backends**: Abstract `MemoryStore` base with `InMemoryStore` and `JSONFileStore` implementations
- **Embedding support**: Optional embedding function for cosine-similarity-based semantic retrieval
- **Automatic pruning**: Configurable `max_memories` limit with score-based eviction of lowest-ranked memories
- **Specialized memory subclasses**: `ConversationMemory` for dialog turns and `KnowledgeMemory` for factual knowledge with confidence tracking
- **Thread-safe operations**: All store operations use threading locks for concurrent access safety
- **LLM context generation**: `get_context()` method formats relevant memories for direct injection into LLM prompts


## Key Components

| Component | Description |
|-----------|-------------|
| `MemoryType` | Enum defining memory categories: EPISODIC, SEMANTIC, PROCEDURAL, WORKING |
| `MemoryImportance` | Enum for importance levels: LOW (1), MEDIUM (2), HIGH (3), CRITICAL (4) |
| `Memory` | Core dataclass representing a single memory unit with content, type, importance, embedding, metadata, and access tracking |
| `RetrievalResult` | Dataclass wrapping a Memory with relevance, recency, and importance scores plus a combined ranking score |
| `MemoryStore` | Abstract base class defining the storage interface: save, get, delete, list_all |
| `InMemoryStore` | Thread-safe in-memory dictionary-based storage backend |
| `JSONFileStore` | File-persisted storage backend using JSON serialization |
| `AgentMemory` | Main memory system with remember, recall, forget, get_context, and automatic pruning |
| `ConversationMemory` | Specialized AgentMemory subclass with `add_turn()` for tracking dialog history |
| `KnowledgeMemory` | Specialized AgentMemory subclass with `add_fact()` for storing facts with source and confidence metadata |

## Quick Start

```python
from codomyrmex.agentic_memory import (
    AgentMemory,
    InMemoryStore,
    JSONFileStore,
    MemoryType,
    MemoryImportance,
    ConversationMemory,
    KnowledgeMemory,
)

# Create agent memory with in-memory storage
memory = AgentMemory(store=InMemoryStore())

# Store memories with type and importance
memory.remember(
    "User prefers Python over JavaScript",
    memory_type=MemoryType.SEMANTIC,
    importance=MemoryImportance.HIGH,
)

memory.remember(
    "Deployed auth service to production",
    memory_type=MemoryType.EPISODIC,
    importance=MemoryImportance.MEDIUM,
)

# Retrieve relevant memories
results = memory.recall("programming language preferences", k=5)
for result in results:
    print(f"[{result.memory.memory_type.value}] {result.memory.content} (score: {result.combined_score:.2f})")

# Get formatted context for LLM prompts
context = memory.get_context("What language should I use?")
print(context)

# Persistent storage with JSON file
persistent_memory = AgentMemory(store=JSONFileStore("agent_memories.json"))

# Conversation-specific memory
conv = ConversationMemory()
conv.add_turn("user", "How do I deploy?", turn_number=1)
conv.add_turn("assistant", "Use the deployment module.", turn_number=2)

# Knowledge-specific memory
knowledge = KnowledgeMemory()
knowledge.add_fact(
    "Python 3.12 supports improved error messages",
    source="python.org",
    confidence=0.95,
)
```


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k agentic_memory -v
```

## Related Modules

- [agents](../agents/) - AI agent framework that consumes agentic memory for stateful interactions
- [cerebrum](../cerebrum/) - Higher-level reasoning and memory orchestration
- [llm](../llm/) - LLM providers used for embedding-based retrieval

## Navigation

- **Source**: [src/codomyrmex/agentic_memory/](../../../src/codomyrmex/agentic_memory/)
- **Parent**: [docs/modules/](../README.md)
