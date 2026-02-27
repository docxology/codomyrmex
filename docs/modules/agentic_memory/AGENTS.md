# Agent Instructions for `codomyrmex.agentic_memory`

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Context

The Agentic Memory module provides persistent key-value memory for AI agents. It is the primary module for the PAI Algorithm's LEARN phase — capturing work outcomes, state snapshots, and accumulated knowledge across sessions.

## Usage Guidelines

1. **Importing**: Always import from the module root.

   ```python
   from codomyrmex.agentic_memory import memory_get, memory_put, memory_search, memory_list
   ```

2. **Storage Selection**: Choose backend based on persistence needs.
   - `InMemoryStore` — session-scoped, fast, ephemeral
   - `JSONFileStore` — persistent across sessions, file-backed

3. **Memory Keys**: Use descriptive, namespaced keys (e.g., `"refactoring:pattern_01"`) to avoid collisions.

4. **Zero-Mock Policy**: Tests must use real `InMemoryStore` or `JSONFileStore` instances — no mocking of storage operations.

5. **MCP Exposure**: Three MCP tools (`store_memory`, `recall_memory`, `list_memories`) are backed by this module. Changes to the API surface require updating `scripts/model_context_protocol/run_mcp_server.py`.

## Key Files

| File | Purpose |
|------|---------|
| `memory.py` | Core memory operations (get, put, search, list) |
| `models.py` | `MemoryEntry`, `MemoryQuery` data models |
| `stores.py` | `InMemoryStore`, `JSONFileStore` backends |
| `user_profile.py` | User preference tracking |

## Agent Operating Contract

- **DO**: Use `memory_put` to capture learnings after successful operations
- **DO**: Use `memory_search` before starting work to check for relevant past experience
- **DO NOT**: Store sensitive credentials in memory (use `wallet/` or `auth/` instead)
- **DO NOT**: Assume memory persistence — always handle `KeyError` from `memory_get`

## Obsidian Subpackage

The `obsidian/` subpackage is a 24-file vault integration layer with two operating modes:

### Mode Selection

| Mode | When to Use | Requirement |
|------|-------------|-------------|
| **Filesystem** | Batch processing, CI/CD, scripting, any Python environment | None — pure Python |
| **CLI** | Live vault interaction, triggering Obsidian plugin actions, sync operations | Obsidian ≥1.12 with CLI enabled |

### Key Import Paths

```python
# Filesystem mode — import from subpackage root
from codomyrmex.agentic_memory.obsidian import (
    ObsidianVault,       # vault root handle
    create_note,         # write a new note
    search_vault,        # full-text search
    build_link_graph,    # wikilink graph analysis
)

# CLI mode
from codomyrmex.agentic_memory.obsidian import ObsidianCLI, ObsidianCLIError
cli = ObsidianCLI()  # raises ObsidianCLINotAvailable if CLI absent
```

### DO / DO NOT Contracts

- **DO**: Use filesystem mode when Obsidian app availability is uncertain
- **DO**: Catch `ObsidianCLINotAvailable` and fall back to filesystem mode when using CLI
- **DO**: Use `ObsidianVault` as the root handle — pass it to all filesystem functions
- **DO NOT**: Write directly to vault files outside of `crud.py` functions — bypass invalidates internal cache
- **DO NOT**: Call CLI commands that modify vault state without explicit user intent
- **DO NOT**: Store secrets or credentials in Obsidian notes via this subpackage

Full reference: [obsidian/AGENTS.md](obsidian/AGENTS.md)

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md) | [Parent](../AGENTS.md)
