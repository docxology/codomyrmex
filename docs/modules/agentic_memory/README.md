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

## Obsidian Vault Integration

The `obsidian` subpackage provides deep integration with [Obsidian](https://obsidian.md) vaults using a dual-mode architecture:

- **Filesystem mode** — Pure Python, no Obsidian app required. Parses and writes `.md` files and `.canvas` files directly.
- **CLI mode** — Wraps the Obsidian CLI (requires Obsidian ≥1.12 with CLI enabled) for live-vault operations.

### Filesystem Modules (7)

| Module | Purpose |
|--------|---------|
| `vault.py` | `ObsidianVault` — vault root, note listing, metadata |
| `models.py` | `Note`, `Tag`, `Wikilink`, `Canvas`, `SearchResult`, … |
| `parser.py` | Frontmatter, wikilinks, tags, code blocks, headings |
| `crud.py` | Create / read / update / delete / move / rename notes |
| `graph.py` | Link graph, backlinks, orphans, hubs, shortest path |
| `search.py` | Full-text, regex, tag, frontmatter, and date filtering |
| `canvas.py` | Parse, build, and save `.canvas` JSON files |

### CLI Modules (12)

| Module | Purpose |
|--------|---------|
| `cli.py` | `ObsidianCLI` — command runner, `CLIResult` |
| `bookmarks.py` | `BookmarkItem` — read bookmark lists |
| `commands.py` | `OutlineItem`, `WordCount`, `DiffResult`, `HistoryEntry` |
| `daily_notes.py` | Create / open daily notes |
| `developer.py` | `ConsoleEntry` — developer console access |
| `plugins.py` | `PluginInfo`, `ThemeInfo`, `SnippetInfo` |
| `properties.py` | `PropertyValue` — vault property store |
| `sync.py` | `SyncStatus`, `SyncHistoryEntry`, `PublishStatus` |
| `tasks.py` | `TaskItem` — Obsidian Tasks plugin integration |
| `templates.py` | `TemplateInfo` — template listing |
| `workspace.py` | Workspace layouts and active file |
| `cli_search.py` | Live vault search via CLI |

### Quick Start

```python
# Filesystem mode (no Obsidian app needed)
from codomyrmex.agentic_memory.obsidian import ObsidianVault, create_note, search_vault

vault = ObsidianVault("/path/to/vault")
results = search_vault(vault, query="meeting notes", limit=10)
create_note(vault, title="2026-02-27 Standup", content="## Agenda\n- Sprint review")

# CLI mode (requires Obsidian ≥1.12 with CLI enabled)
from codomyrmex.agentic_memory.obsidian import ObsidianCLI

cli = ObsidianCLI()
result = cli.run(["vault", "open", "My Note"])
```

Full reference: [obsidian/README.md](obsidian/README.md)

## Navigation

- [SPEC.md](SPEC.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../README.md)
