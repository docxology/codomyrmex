# Obsidian Vault Integration

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `obsidian` subpackage of `agentic_memory` provides deep Obsidian vault integration using a **dual-mode architecture** — you can work with vault files directly in Python (no Obsidian app required) or drive a live Obsidian instance via its CLI.

## Dual-Mode Architecture

| Mode | Requirement | Best For |
|------|-------------|----------|
| **Filesystem** | None — pure Python, `pathlib` only | CI/CD, batch processing, offline scripting |
| **CLI** | Obsidian ≥1.12 with CLI enabled | Live vault operations, plugin interactions, sync |

Both modes share the same data models (`Note`, `Tag`, `Wikilink`, …). Filesystem mode operates on `.md` and `.canvas` files directly. CLI mode issues commands to the running Obsidian app.

## Filesystem Modules (7)

| Module | Key Exports | Purpose |
|--------|-------------|---------|
| `vault.py` | `ObsidianVault` | Vault root handle, note listing, metadata |
| `models.py` | `Note`, `Tag`, `Wikilink`, `Canvas`, `SearchResult`, … | Shared data models |
| `parser.py` | `parse_note`, `parse_frontmatter`, `extract_*` | Parse `.md` files |
| `crud.py` | `create_note`, `read_note`, `update_note`, `delete_note` | Note lifecycle |
| `graph.py` | `build_link_graph`, `get_backlinks`, `find_orphans` | Wikilink graph analysis |
| `search.py` | `search_vault`, `search_regex`, `filter_by_tag` | Search and filter |
| `canvas.py` | `create_canvas`, `parse_canvas`, `add_canvas_node` | Canvas (`.canvas`) files |

## CLI Modules (12)

| Module | Key Exports | Purpose |
|--------|-------------|---------|
| `cli.py` | `ObsidianCLI`, `CLIResult` | CLI runner and error types |
| `bookmarks.py` | `BookmarkItem` | Read vault bookmarks |
| `commands.py` | `OutlineItem`, `WordCount`, `DiffResult` | Document commands |
| `daily_notes.py` | `open_or_create_daily_note` | Daily note management |
| `developer.py` | `ConsoleEntry` | Developer console access |
| `plugins.py` | `PluginInfo`, `ThemeInfo`, `SnippetInfo` | Plugin and theme state |
| `properties.py` | `PropertyValue` | Vault-level properties |
| `sync.py` | `SyncStatus`, `PublishStatus` | Obsidian Sync status |
| `tasks.py` | `TaskItem` | Obsidian Tasks plugin |
| `templates.py` | `TemplateInfo` | Template listing |
| `workspace.py` | Workspace layout | Active file and panes |
| `cli_search.py` | Live search | CLI-backed vault search |

## Quick Start

```python
# Filesystem mode
from codomyrmex.agentic_memory.obsidian import ObsidianVault, create_note, search_vault

vault = ObsidianVault("/path/to/vault")
results = search_vault(vault, query="meeting notes", limit=10)
create_note(vault, title="2026-02-27 Standup", content="## Agenda\n- Sprint review")

# CLI mode
from codomyrmex.agentic_memory.obsidian import ObsidianCLI, ObsidianCLINotAvailable

try:
    cli = ObsidianCLI()
    result = cli.run(["vault", "open", "My Note"])
except ObsidianCLINotAvailable:
    # Fall back to filesystem mode
    note = read_note(vault, "My Note")
```

## Navigation

- [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
- [Parent README](../README.md) | [Source](../../../../../src/codomyrmex/agentic_memory/obsidian/)
