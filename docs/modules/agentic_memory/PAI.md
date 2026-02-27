# Personal AI Infrastructure — Agentic Memory Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Agentic Memory module provides persistent, structured memory for AI agents — enabling learning across sessions, context continuity, and experience-based decision making. It is the primary module for the PAI Algorithm's LEARN phase, capturing work outcomes, state snapshots, and accumulated knowledge.

## PAI Capabilities

### Memory Operations

```python
from codomyrmex.agentic_memory import memory_get, memory_put, memory_search, memory_list

# Store a learning
memory_put(key="refactoring_pattern_01", value={
    "pattern": "extract_method",
    "context": "large_function",
    "outcome": "improved_readability",
    "confidence": 0.92
})

# Retrieve a specific memory
entry = memory_get(key="refactoring_pattern_01")

# Search memories by pattern
results = memory_search(query="refactoring", limit=10)

# List all stored memories
all_keys = memory_list()
```

### Storage Backends

```python
from codomyrmex.agentic_memory.stores import InMemoryStore, JSONFileStore

# In-memory store for session-scoped memory
session_store = InMemoryStore()

# File-backed store for persistent memory across sessions
persistent_store = JSONFileStore(path="~/.codomyrmex/memory/")
```

### User Profile

```python
from codomyrmex.agentic_memory import UserProfile

profile = UserProfile()
# Tracks user preferences, coding style, and interaction patterns
# Informs agent behavior customization
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `memory_get` | Function | Retrieve a stored memory by key |
| `memory_put` | Function | Store a key-value memory entry |
| `memory_search` | Function | Search memories by query pattern |
| `memory_list` | Function | List all stored memory keys |
| `InMemoryStore` | Class | Session-scoped in-memory storage |
| `JSONFileStore` | Class | Persistent file-backed storage |
| `UserProfile` | Class | User preference and behavior tracking |

## PAI Algorithm Phase Mapping

| Phase | Agentic Memory Contribution |
|-------|------------------------------|
| **OBSERVE** | `memory_search` retrieves relevant past experiences for current context |
| **THINK** | Past outcomes inform reasoning about approach selection |
| **EXECUTE** | Session state persisted during long-running agent workflows |
| **LEARN** | `memory_put` captures work outcomes, patterns discovered, and lessons learned |

## MCP Integration

Three MCP tools are exposed for PAI agent consumption:

| Tool | MCP Name | Description |
|------|----------|-------------|
| `memory_put` | `store_memory` | Store key-value pair in memory |
| `memory_get` | `recall_memory` | Retrieve stored value by key |
| `memory_list` | `list_memories` | List all stored memory keys |

## Architecture Role

**Core Layer** — Central memory infrastructure. Consumed by all agent modules. Uses `serialization/` for data persistence and integrates with `logging_monitoring/` for memory operation auditing.

## Obsidian Vault Tools

The `obsidian/` subpackage adds Obsidian-specific capabilities across Algorithm phases:

### Extended PAI Phase Mapping

| Phase | Obsidian Contribution | Key APIs |
|-------|----------------------|----------|
| **OBSERVE** | Search vault for prior notes on the current topic | `ObsidianVault`, `search_vault`, `cli_search` (CLI) |
| **THINK** | Traverse the link graph to surface related concepts | `build_link_graph`, `get_backlinks`, `find_hubs` |
| **BUILD** | Create structured notes for work products and code artefacts | `create_note`, `crud.*`, `ObsidianCLI` |
| **EXECUTE** | Update canvas diagrams as architecture evolves | `create_canvas`, `add_canvas_node`, `connect_nodes` |
| **LEARN** | Capture task outcomes and daily notes | `agentic_memory.obsidian.tasks` (`TaskItem`), `daily_notes` |

### Quick Reference

```python
# OBSERVE — find prior work
from codomyrmex.agentic_memory.obsidian import ObsidianVault, search_vault
vault = ObsidianVault("~/vaults/work")
hits = search_vault(vault, query="authentication refactor", limit=5)

# LEARN — log today's outcome
from codomyrmex.agentic_memory.obsidian.daily_notes import open_or_create_daily_note
note = open_or_create_daily_note(vault)
```

Full reference: [obsidian/PAI.md](obsidian/PAI.md)

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
