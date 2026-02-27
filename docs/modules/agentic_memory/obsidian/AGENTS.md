# Agent Instructions — Obsidian Vault Integration

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Context

The `obsidian` subpackage provides filesystem-direct and CLI-backed access to Obsidian vaults. It is a 24-file layer within `agentic_memory` with clear mode boundaries — choose the right mode for the task.

## Mode Selection

| Condition | Use |
|-----------|-----|
| Obsidian app unavailable or uncertain | Filesystem mode |
| Need to trigger plugin commands or live sync | CLI mode |
| Batch processing or scripting | Filesystem mode |
| Reading note content | Either (filesystem preferred) |
| Opening/closing notes in the UI | CLI mode |

## Key Import Paths

```python
# Filesystem — all exports from subpackage root
from codomyrmex.agentic_memory.obsidian import (
    ObsidianVault,         # ALWAYS create this first
    Note, Tag, Wikilink,   # data models
    create_note, read_note, update_note, delete_note,  # CRUD
    search_vault, filter_by_tag, search_regex,          # search
    build_link_graph, get_backlinks, find_orphans,      # graph
    create_canvas, parse_canvas, add_canvas_node,       # canvas
)

# CLI
from codomyrmex.agentic_memory.obsidian import (
    ObsidianCLI,
    ObsidianCLIError,
    ObsidianCLINotAvailable,  # raised when CLI binary not found
)

# CLI domain models
from codomyrmex.agentic_memory.obsidian import (
    TaskItem, BookmarkItem, TemplateInfo,
    PluginInfo, SyncStatus, PropertyValue,
)
```

## Agent Operating Contracts

### DO

- **Always** create an `ObsidianVault` instance first and pass it to all filesystem functions
- **Catch** `ObsidianCLINotAvailable` at the call site — never let it propagate silently
- **Prefer** filesystem mode when vault availability is uncertain
- **Use** `crud.py` functions for all note writes — do not write `.md` files directly via `open()`
- **Handle** `KeyError` and `FileNotFoundError` from note reads — notes may not exist

### DO NOT

- **Do not** bypass `crud.py` by writing vault files directly — this skips internal state
- **Do not** call destructive CLI commands (`vault delete`, `note trash`) without user confirmation
- **Do not** store sensitive credentials, API keys, or PII in Obsidian notes via this API
- **Do not** assume CLI mode is available — always check or catch `ObsidianCLINotAvailable`
- **Do not** mix filesystem and CLI writes to the same note in one operation

## Error Handling

| Exception | When Raised | Recovery |
|-----------|-------------|---------|
| `ObsidianCLINotAvailable` | CLI binary not found or Obsidian not running | Fall back to filesystem mode |
| `ObsidianCLIError` | CLI command returned non-zero exit code | Log and surface to caller |
| `FileNotFoundError` | Note path does not exist | Create note or surface to caller |
| `KeyError` | Frontmatter key missing | Use `.get()` or provide default |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
- [Parent AGENTS.md](../AGENTS.md) | [Source](../../../../../src/codomyrmex/agentic_memory/obsidian/)
