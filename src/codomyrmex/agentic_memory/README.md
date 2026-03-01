# Agentic Memory Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Agentic Memory module provides persistent, structured memory for AI agents — enabling learning across sessions, context continuity, and experience-based decision making. It supports in-memory and file-backed storage backends, key-value memory operations, search, and user profile tracking.

## Installation

```bash
uv add codomyrmex
```

## Key Exports

| Export | Type | Description |
|--------|------|-------------|
| `AgentMemory` | Class | Primary memory store for AI agents |
| `ConversationMemory` | Class | Conversation history with sliding window |
| `InMemoryStore` | Class | In-process volatile memory backend |
| `JSONFileStore` | Class | JSON file-backed persistent memory |
| `KnowledgeMemory` | Class | Semantic knowledge base with retrieval |
| `Memory` | Class | Base memory abstraction |
| `MemoryImportance` | Enum | Importance levels (LOW/MEDIUM/HIGH/CRITICAL) |
| `MemoryType` | Enum | Memory categories (EPISODIC/SEMANTIC/PROCEDURAL/WORKING) |
| `RetrievalResult` | Class | Memory retrieval result with relevance score |
| `UserProfile` | Class | User-specific memory profile |
| `VectorStoreMemory` | Class | Vector embedding-backed memory store |

## Quick Start

> **MCP Tools vs Python API**: The MCP tools `memory_put`, `memory_get`, and `memory_search`
> are exposed for AI agent use via the MCP bridge (see `mcp_tools.py`). For direct Python
> usage, use the class-based API documented below: `AgentMemory`, `InMemoryStore`,
> `JSONFileStore`, etc.

```python
from codomyrmex.agentic_memory import AgentMemory, InMemoryStore

# Create an in-memory store
store = InMemoryStore()
memory = AgentMemory(store=store)

# Store a memory
memory.store("The user prefers concise responses", importance="high")

# Retrieve relevant memories
results = memory.retrieve("user preferences", top_k=5)
for result in results:
    print(f"[{result.importance}] {result.content}")
```

### Using Storage Backends

```python
from codomyrmex.agentic_memory import InMemoryStore, JSONFileStore

# Session-scoped memory (volatile)
session = InMemoryStore()

# Persistent across sessions (file-backed)
persistent = JSONFileStore(path="~/.codomyrmex/memory/")
```

## Architecture

```
agentic_memory/
├── __init__.py          # Public API (AgentMemory, Memory, stores, enums)
├── memory.py            # Core memory classes (AgentMemory, ConversationMemory, etc.)
├── models.py            # Memory, MemoryType, MemoryImportance, RetrievalResult
├── stores.py            # InMemoryStore, JSONFileStore backends
├── user_profile.py      # UserProfile tracking
├── mcp_tools.py         # MCP tool definitions (memory_put, memory_get, memory_search)
└── tests/               # Unit tests (Zero-Mock policy)
```

## MCP Integration

Three MCP tools are exposed via `mcp_tools.py` (auto-discovered by the MCP bridge):

| MCP Tool | Description |
|----------|-------------|
| `memory_put` | Store a new memory entry with content, type, and importance |
| `memory_get` | Retrieve a memory by its ID |
| `memory_search` | Search memories by text query, returns ranked results |

## Navigation

- **Extended Docs**: [docs/modules/agentic_memory/](../../../docs/modules/agentic_memory/)
- [SPEC.md](SPEC.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../README.md)
