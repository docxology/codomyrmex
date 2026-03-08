# Agent Instructions for `codomyrmex.agentic_memory`

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

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

5. **MCP Exposure**: Three MCP tools (`memory_put`, `memory_get`, `memory_search`) are backed by this module via `mcp_tools.py`. Changes to the API surface require updating `mcp_tools.py`.

## Key Files

| File | Purpose |
|------|---------|
| `memory.py` | Core memory operations (get, put, search, list) |
| `models.py` | `MemoryEntry`, `MemoryQuery` data models |
| `stores.py` | `InMemoryStore`, `JSONFileStore` backends |
| `user_profile.py` | User preference tracking |

## MCP Tools Available

All tools are auto-discovered via `@mcp_tool` decorators and exposed through the MCP bridge.

| Tool | Description | Key Parameters | Trust Level |
|------|-------------|----------------|-------------|
| `memory_put` | Store a new memory entry with content, optional type, and importance | `content`, `memory_type` (episodic), `importance` (medium) | Safe |
| `memory_get` | Retrieve a memory by its ID | `memory_id` | Safe |
| `memory_search` | Search memories by a text query; returns ranked results | `query`, `k` (default 5) | Safe |

## Agent Operating Contract

- **DO**: Use `memory_put` to capture learnings after successful operations
- **DO**: Use `memory_search` before starting work to check for relevant past experience
- **DO NOT**: Store sensitive credentials in memory (use `wallet/` or `auth/` instead)
- **DO NOT**: Assume memory persistence — always handle `KeyError` from `memory_get`

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full CRUD | `memory_put`, `memory_get`, `memory_search` | TRUSTED |
| **Architect** | Query-only | `memory_search` | OBSERVED |
| **QATester** | Retrieval + Verification | `memory_search`, `memory_get` | OBSERVED |
| **Researcher** | Read-only | `memory_get`, `memory_search` | OBSERVED |

### Engineer Agent
**Access**: Full — write, read, and search operations on the memory store.
**Use Cases**: Capturing work outcomes in the LEARN phase, storing session state, persisting ISC results and decisions across Algorithm runs.

### Architect Agent
**Access**: Query-only — semantic search for prior architecture decisions.
**Use Cases**: Retrieving precedents for design decisions, querying past problem patterns, informing ISC criteria with prior experience.

### QATester Agent
**Access**: Retrieval + verification — confirm memory round-trips correctly.
**Use Cases**: Verifying that LEARN-phase writes were stored correctly, checking that memory searches return relevant results, testing persistence across sessions.

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md) | [Parent](../AGENTS.md)


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/agentic_memory.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/agentic_memory.cursorrules)
