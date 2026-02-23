# Agentic Memory Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Agentic Memory module provides persistent, structured memory for AI agents — enabling learning across sessions, context continuity, and experience-based decision making. It supports in-memory and file-backed storage backends, key-value memory operations, search, and user profile tracking.

## Installation

```bash
uv add codomyrmex
```

## Key Exports

### Memory Operations

| Export | Type | Purpose |
|--------|------|---------|
| `memory_get` | Function | Retrieve a stored memory by key |
| `memory_put` | Function | Store a key-value memory entry |
| `memory_search` | Function | Search memories by query pattern |
| `memory_list` | Function | List all stored memory keys |

### Storage Backends

| Export | Type | Purpose |
|--------|------|---------|
| `InMemoryStore` | Class | Session-scoped in-memory storage |
| `JSONFileStore` | Class | Persistent file-backed JSON storage |

### Data Models

| Export | Type | Purpose |
|--------|------|---------|
| `MemoryEntry` | Model | Individual memory record with metadata |
| `MemoryQuery` | Model | Search query specification |
| `UserProfile` | Class | User preference and behavior tracking |

## Quick Start

```python
from codomyrmex.agentic_memory import memory_put, memory_get, memory_search, memory_list

# Store a learning
memory_put(key="pattern_01", value={"type": "refactoring", "outcome": "success"})

# Retrieve
entry = memory_get(key="pattern_01")

# Search
results = memory_search(query="refactoring", limit=10)

# List all keys
all_keys = memory_list()
```

### Using Storage Backends

```python
from codomyrmex.agentic_memory.stores import InMemoryStore, JSONFileStore

# Session-scoped memory
session = InMemoryStore()

# Persistent across sessions
persistent = JSONFileStore(path="~/.codomyrmex/memory/")
```

## Architecture

```
agentic_memory/
├── __init__.py          # Public API (memory_get, memory_put, memory_search, memory_list)
├── memory.py            # Core memory operations
├── models.py            # MemoryEntry, MemoryQuery data models
├── stores.py            # InMemoryStore, JSONFileStore backends
├── user_profile.py      # UserProfile tracking
└── tests/               # Unit tests (Zero-Mock policy)
```

## MCP Integration

Three MCP tools are exposed:

| Tool | MCP Name | Description |
|------|----------|-------------|
| `memory_put` | `store_memory` | Store key-value pair |
| `memory_get` | `recall_memory` | Retrieve value by key |
| `memory_list` | `list_memories` | List all stored keys |

## Navigation

- [SPEC.md](SPEC.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../README.md)
