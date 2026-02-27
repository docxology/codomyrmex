# Agentic Memory — Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Provides persistent, structured memory for AI agents with key-value storage, search, and user profiling. Central to the PAI Algorithm's LEARN phase.

## Functional Requirements

### Memory Operations

| Operation | Signature | Description |
|-----------|-----------|-------------|
| **Put** | `memory_put(key: str, value: Any) → None` | Store a key-value pair |
| **Get** | `memory_get(key: str) → Any` | Retrieve value by key; raises `KeyError` if missing |
| **Search** | `memory_search(query: str, limit: int) → list` | Search memories by pattern |
| **List** | `memory_list() → list[str]` | Return all stored keys |

### Storage Backends

| Backend | Persistence | Performance | Thread-Safe |
|---------|-------------|-------------|-------------|
| `InMemoryStore` | Session only | O(1) get/put | Yes |
| `JSONFileStore` | Disk-backed | O(1) get, O(n) search | Yes (file locks) |

### User Profile

| Method | Description |
|--------|-------------|
| `UserProfile()` | Initialize or load user preference tracking |
| Profile fields | Coding style, interaction patterns, preferred models |

## Non-Functional Requirements

- **Latency**: `memory_get` < 1ms (in-memory), < 10ms (file-backed)
- **Capacity**: Up to 100,000 entries per store
- **Durability**: `JSONFileStore` flushes on every write
- **Concurrency**: Thread-safe via locking primitives

## Architecture

- Depends on: `serialization/` (JSON persistence), `logging_monitoring/` (audit logging)
- Consumed by: All agent modules, MCP server (`store_memory`, `recall_memory`, `list_memories`)

## Obsidian Integration

The `obsidian/` subpackage extends agentic memory with Obsidian vault integration.

### Architectural Constraints

- **Dual-mode**: Filesystem and CLI modes are independent; filesystem never invokes CLI
- **Real execution**: No stubs — filesystem operations use actual `pathlib.Path`; CLI wraps real `obsidian` binary
- **Graceful degradation**: `ObsidianCLINotAvailable` is raised (not suppressed) when CLI is absent; callers decide whether to fall back to filesystem mode
- **Zero-mock policy**: Tests use real temporary vaults via `tmp_path` fixtures

### Public API Surface (from `obsidian/__init__.py`)

**Filesystem core:**
- `ObsidianVault` — vault root; `Note`, `Tag`, `Wikilink`, `Canvas`, `CanvasNode`, `CanvasEdge`, `SearchResult`, `VaultMetadata` models
- `parse_note`, `serialize_note`, `parse_frontmatter` — note serialisation
- `create_note`, `read_note`, `update_note`, `delete_note`, `move_note`, `rename_note` — CRUD
- `build_link_graph`, `get_backlinks`, `get_forward_links`, `find_orphans`, `find_hubs` — graph analysis
- `search_vault`, `search_regex`, `filter_by_tag`, `filter_by_frontmatter` — search

**Canvas:**
- `create_canvas`, `parse_canvas`, `save_canvas`, `add_canvas_node`, `add_canvas_edge`, `connect_nodes`

**CLI core:**
- `ObsidianCLI`, `CLIResult`, `ObsidianCLIError`, `ObsidianCLINotAvailable`

**CLI domain models:**
- `BookmarkItem`, `TaskItem`, `TemplateInfo`, `PluginInfo`, `ThemeInfo`, `SnippetInfo`
- `PropertyValue`, `SyncStatus`, `SyncHistoryEntry`, `PublishStatus`
- `OutlineItem`, `WordCount`, `DiffResult`, `HistoryEntry`, `ConsoleEntry`

Full reference: [obsidian/SPEC.md](obsidian/SPEC.md)

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../SPEC.md)
