# Personal AI Infrastructure — Agentic Memory Module

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Agentic Memory module provides persistent, structured memory for AI agents — enabling learning across sessions, context continuity, and experience-based decision making. It is the primary module for the PAI Algorithm's LEARN phase, capturing work outcomes, state snapshots, and accumulated knowledge.

## PAI Capabilities

### Memory Operations

```python
from codomyrmex.agentic_memory import AgentMemory, JSONFileStore, MemoryImportance, MemoryType

memory = AgentMemory(store=JSONFileStore("memories.json"))

# Store a learning
mem = memory.remember(
    "extract_method on a large function improved readability",
    memory_type=MemoryType.PROCEDURAL,
    importance=MemoryImportance.HIGH,
    metadata={"pattern": "extract_method", "confidence": 0.92},
)

# Retrieve a specific memory
entry = memory.store.get(mem.id)

# Search memories (relevance, recency, and importance scoring)
results = memory.recall("refactoring", k=10)

# List all stored memories
all_memories = memory.store.list_all()
```

The same operations are exposed as MCP tools in `codomyrmex.agentic_memory.mcp_tools`: `memory_put(content, memory_type, importance)`, `memory_get(memory_id)`, and `memory_search(query, k)`.

### Storage Backends

```python
from codomyrmex.agentic_memory.stores import InMemoryStore, JSONFileStore

# In-memory store for session-scoped memory
session_store = InMemoryStore()

# File-backed store for persistent memory across sessions
persistent_store = JSONFileStore(path="memories.json")
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
| --- | --- | --- |
| `AgentMemory` | Class | `remember`, `recall`, `search`, `forget`, and `get_context` over a store |
| `MemoryType` / `MemoryImportance` | Enum | Episodic, semantic, procedural, knowledge; low to critical |
| `mcp_tools.memory_put` / `memory_get` / `memory_search` | MCP tool | Store, fetch by ID, and semantically search memories |
| `InMemoryStore` | Class | Session-scoped in-memory storage |
| `JSONFileStore` | Class | Persistent file-backed storage |
| `UserProfile` | Class | User preference and behavior tracking |

## PAI Algorithm Phase Mapping

| Phase | Agentic Memory Contribution |
| --- | --- |
| **OBSERVE** | `AgentMemory.recall` / `memory_search` retrieve relevant past experiences for current context |
| **THINK** | Past outcomes inform reasoning about approach selection |
| **EXECUTE** | Session state persisted during long-running agent workflows |
| **LEARN** | `AgentMemory.remember` / `memory_put` capture work outcomes, patterns discovered, and lessons learned |

## MCP Integration

Four MCP tools are exposed for PAI agent consumption:

| Tool | MCP Name | Description |
| --- | --- | --- |
| `memory_put` | `codomyrmex.memory_put` | Store a memory (content, type, importance) |
| `memory_get` | `codomyrmex.memory_get` | Retrieve a stored memory by ID |
| `memory_search` | `codomyrmex.memory_search` | Semantic search over stored memories |
| `obsidian_sync` | `codomyrmex.obsidian_sync` | Synchronize an Obsidian vault with agentic memory |

## Architecture Role

**Core Layer** — Central memory infrastructure. Consumed by all agent modules. Uses `serialization/` for data persistence and integrates with `logging_monitoring/` for memory operation auditing.

## Obsidian Vault Tools

The `obsidian/` subpackage adds Obsidian-specific capabilities across Algorithm phases:

### Extended PAI Phase Mapping

| Phase | Obsidian Contribution | Key APIs |
| --- | --- | --- |
| **OBSERVE** | Search vault for prior notes on the current topic | `ObsidianVault`, `search_vault`, `cli_search` (CLI) |
| **THINK** | Traverse the link graph to surface related concepts | `build_link_graph`, `get_backlinks`, `find_hubs` |
| **BUILD** | Create structured notes for work products and code artefacts | `create_note`, `crud.*`, `ObsidianCLI` |
| **EXECUTE** | Update canvas diagrams as architecture evolves | `create_canvas`, `add_canvas_node`, `connect_nodes` |
| **LEARN** | Capture task outcomes and daily notes | `agentic_memory.obsidian.tasks` (`TaskItem`), `daily_notes` |

### Quick Reference

```python
# OBSERVE — find prior work
from pathlib import Path

from codomyrmex.agentic_memory.obsidian import ObsidianVault, search_vault
vault = ObsidianVault(Path("~/vaults/work").expanduser())
hits = search_vault(vault, query="authentication refactor", limit=5)

# LEARN — log today's outcome (daily notes go through the Obsidian CLI)
from codomyrmex.agentic_memory.obsidian import ObsidianCLI
from codomyrmex.agentic_memory.obsidian.daily_notes import append_daily
append_daily(ObsidianCLI(), "- Finished the authentication refactor")
```

Full reference: [obsidian/PAI.md](obsidian/PAI.md)

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](../../../src/codomyrmex/agentic_memory/API_SPECIFICATION.md)
