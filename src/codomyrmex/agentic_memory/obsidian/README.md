# Obsidian

**Version**: v3.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Full-featured Obsidian vault integration for the Codomyrmex ecosystem. Provides **two operational modes**:

1. **Filesystem mode** (no Obsidian app required) — Parse, CRUD, search, graph analysis, and canvas operations directly on vault directories.
2. **CLI mode** (requires Obsidian ≥1.12 with CLI enabled) — Full programmatic access to the Obsidian application via the `obsidian` CLI binary. The app must be running.

## Module Structure

### Filesystem Layer

| File | Purpose |
| ---- | ------- |
| `vault.py` | `ObsidianVault` — load, scan, navigate, list notes/folders, tag queries, alias lookup |
| `parser.py` | Markdown parsing — frontmatter, wikilinks, embeds, tags, callouts, code blocks, math, Dataview fields |
| `models.py` | Core data models (`Note`, `Wikilink`, `Tag`, `CodeBlock`, `MathBlock`, `DataviewField`, `Canvas`, etc.) |
| `crud.py` | Filesystem CRUD — create (with overwrite/template), read, update, append, prepend, move, rename, delete |
| `graph.py` | Link graph — backlinks, forward links, orphans, dead ends, hubs, broken links, shortest path, stats |
| `search.py` | Search — full-text, regex, tag/multi-tag, frontmatter, date, linking-to, embeds filters |
| `canvas.py` | JSON Canvas — parse, create, save, add/remove nodes+edges, factory functions |

### CLI Layer

| File | Purpose |
| ---- | ------- |
| `cli.py` | **Core wrapper** — `ObsidianCLI`, subprocess execution, file/folder operations |
| `cli_search.py` | CLI search — `search`, `search:context`, `search:open` with limit/format/case |
| `daily_notes.py` | Daily notes — open, read, append, prepend with paneType/inline/open |
| `properties.py` | Properties — aliases, get/set/remove with type/sort/format; tags |
| `tasks.py` | Tasks — list with filters (done/todo/daily/status/format), get/toggle/set |
| `plugins.py` | Plugins, themes, CSS snippets — list/enable/disable/install/set |
| `sync.py` | Sync — on/off, status, history, read, restore, deleted; Publish operations |
| `bookmarks.py` | Bookmarks — list, create (file/folder/search/URL) |
| `templates.py` | Templates — list, read (with resolve), insert |
| `workspace.py` | Workspaces — get active, list, save, load, delete; Tabs; Recents |
| `developer.py` | Dev tools — eval JS, screenshot, console, DOM, CSS, CDP, debug, mobile |
| `commands.py` | Commands — palette, hotkeys, diff, history, links, outline, wordcount, random, unique, web |

## Quick Start

### Filesystem mode (no Obsidian app needed)

```python
from codomyrmex.agentic_memory.obsidian import (
    ObsidianVault, create_note, search_vault, find_orphans,
    parse_canvas, create_text_node, connect_nodes,
)

# Load vault
vault = ObsidianVault("/path/to/vault")
print(f"{len(vault)} notes, {vault.metadata.total_words} words")

# CRUD
note = create_note(vault, "New Note", content="# Hello", frontmatter={"tags": ["new"]})
from codomyrmex.agentic_memory.obsidian import append_note, move_note
append_note(vault, "New Note", "\n- [ ] Task 1")
move_note(vault, "New Note", to="projects/")

# Search
results = search_vault(vault, "meeting", case_sensitive=False, folder="work")
from codomyrmex.agentic_memory.obsidian import search_regex, filter_by_tags
regex_results = search_regex(vault, r"\d{4}-\d{2}-\d{2}")
tagged = filter_by_tags(vault, ["project", "active"], match_all=True)

# Graph
orphans = find_orphans(vault)
from codomyrmex.agentic_memory.obsidian import get_shortest_path, find_hubs
path = get_shortest_path(vault, "Note A", "Note B")
hubs = find_hubs(vault, min_links=5)

# Canvas
node1 = create_text_node("Idea", x=0, y=0, color="#50fa7b")
node2 = create_text_node("Implementation", x=300, y=0)
edge = connect_nodes(node1.id, node2.id, label="leads to")
```

### CLI mode (requires Obsidian ≥1.12)

```python
from codomyrmex.agentic_memory.obsidian import ObsidianCLI

cli = ObsidianCLI(vault="MyVault")

# Daily notes
from codomyrmex.agentic_memory.obsidian.daily_notes import read_daily, append_daily
daily = read_daily(cli)
append_daily(cli, "- [ ] Buy groceries", inline=True)

# Tasks
from codomyrmex.agentic_memory.obsidian.tasks import list_tasks, toggle_task
todos = list_tasks(cli, todo=True, daily=True)
toggle_task(cli, ref="todo.md:5")

# Search
from codomyrmex.agentic_memory.obsidian.cli_search import cli_search
results = cli_search(cli, "meeting notes", limit=10, case=True)

# Developer tools
from codomyrmex.agentic_memory.obsidian.developer import eval_js, cdp_command
file_count = eval_js(cli, "app.vault.getFiles().length")
cdp_command(cli, "Page.captureScreenshot")
```

## File Targeting

- `file="note"` — Resolves via wikilink logic (name without path/extension).
- `path="folder/note.md"` — Exact path from vault root.
- Default: Targets the active file.

## Principles

- **Functional Integrity**: All methods are fully operational and production-ready.
- **Zero-Mock Policy**: Tests use real logic; CLI tests skip gracefully when binary unavailable.
- **Dual-Mode**: Filesystem and CLI modes are additive — neither breaks the other.
