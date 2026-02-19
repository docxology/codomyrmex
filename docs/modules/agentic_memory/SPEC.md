# Agentic Memory — Functional Specification

**Module**: `codomyrmex.agentic_memory`  
**Version**: v0.1.7  
**Status**: Active

## 1. Overview

Long-term agent memory with retrieval and persistence.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `MemoryType` | Class | Types of agent memory. |
| `MemoryImportance` | Class | Importance levels for memories. |
| `Memory` | Class | A single memory unit. |
| `RetrievalResult` | Class | Result of memory retrieval. |
| `MemoryStore` | Class | Base class for memory storage backends. |
| `InMemoryStore` | Class | In-memory storage for memories. |
| `JSONFileStore` | Class | JSON file storage for memories. |
| `AgentMemory` | Class | Long-term memory system for AI agents. |
| `ConversationMemory` | Class | Memory optimized for conversation history. |
| `KnowledgeMemory` | Class | Memory optimized for knowledge/facts. |
| `age_hours()` | Function | Get memory age in hours. |
| `recency_score()` | Function | Get recency score (decays over time). |
| `access()` | Function | Record an access to this memory. |
| `to_dict()` | Function | Convert to dictionary. |
| `from_dict()` | Function | Create from dictionary. |

## 3. Dependencies

See `src/codomyrmex/agentic_memory/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.agentic_memory import MemoryType, MemoryImportance, Memory, RetrievalResult, MemoryStore
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k agentic_memory -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/agentic_memory/)
