# Obsidian Vault Module — Technical Specification

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Provide a programmatic Python interface for Obsidian vaults, enabling AI agents to read, search, analyze, and mutate personal knowledge bases stored as Obsidian markdown.

## Architecture

```
obsidian/
  models.py      — Immutable dataclasses (Note, WikiLink, Embed, Callout, Tag,
                   Canvas, CanvasNode, CanvasEdge, SearchResult, VaultMetadata)
  parser.py      — Stateless parsing functions (ObsidianParser class)
  vault.py       — In-memory index (ObsidianVault class)
  crud.py        — Filesystem mutations (read/write/delete/rename)
  graph.py       — NetworkX link graph (LinkGraph class)
  search.py      — Search functions operating on vault index
  canvas.py      — JSON Canvas parser and builder (CanvasParser class)
  mcp_tools.py   — @mcp_tool decorated functions (11 tools)
```

## Data Model

### `Note`
```
path: str               # Relative path within vault (e.g., "Projects/Alpha.md")
title: str              # H1 heading or filename stem
frontmatter: dict       # Parsed YAML frontmatter
content: str            # Raw markdown body (after frontmatter)
wikilinks: list[WikiLink]
embeds: list[Embed]
callouts: list[Callout]
tags: list[Tag]
headings: list[tuple[int, str]]   # (level, text)
```

### `WikiLink`
```
target: str    # Link target (e.g., "ProjectAlpha")
alias: str     # Display alias (empty string if absent)
anchor: str    # Heading anchor (empty string if absent)
```

### `Embed`
```
target: str    # Embedded file path
anchor: str    # Optional block/heading anchor
```

### `Callout`
```
type: str      # e.g., "note", "warning", "info"
title: str     # Optional callout title
content: str   # Body text
```

### `Tag`
```
name: str      # Tag text without leading `#`
source: str    # "inline" or "frontmatter"
```

### `Canvas` / `CanvasNode` / `CanvasEdge`
Mirrors the Obsidian JSON Canvas spec (v1.0).

### `SearchResult`
```
note: Note
context: str   # Snippet of matching text
score: float   # Relevance score (1.0 for exact match)
```

### `VaultMetadata`
```
vault_path: str
note_count: int
tag_index: dict[str, list[str]]     # tag -> [note_paths]
link_index: dict[str, list[str]]    # note -> [link targets]
last_indexed: datetime
```

## Component Specifications

### ObsidianParser

- Stateless — no instance state between calls.
- Frontmatter: standard YAML block fenced by `---` / `---`.
- Wikilinks: regex `\[\[([^\]|#]+)(?:#([^\]|]+))?(?:\|([^\]]+))?\]\]`.
- Embeds: same pattern prefixed with `!`.
- Callouts: line pattern `^> \[!(\w+)\](.*)`.
- Tags: inline `#[\w/]+` not inside code blocks or frontmatter; also reads `tags:` and `tag:` frontmatter keys.
- Headings: ATX style (`#` through `######`).

### ObsidianVault

- Scans recursively for `*.md` files (excludes `.obsidian/` and `.trash/`).
- Builds two indexes on load: `title_index` (stem -> Note), `path_index` (relative path -> Note).
- Re-index triggered manually via `reload()`.

### LinkGraph

- Nodes: note titles (string).
- Edges: directed, source -> target for each WikiLink.
- `broken_links()`: edges where target node has no corresponding note in vault.
- `orphans()`: nodes with in-degree == 0 AND out-degree == 0.
- Built on `networkx.DiGraph`.

### Search

- `search_fulltext`: case-insensitive substring match across `content` + `title`. Returns `list[SearchResult]` sorted by score, limited to `limit`.
- `search_by_tag`: exact match on `tag.name` (case-insensitive).
- `search_by_frontmatter`: key existence and optional value equality.
- `search_by_date`: parses frontmatter date fields with `dateutil.parser.parse`; filters by inclusive range.

### CRUD

- All mutations operate on the filesystem immediately; vault index is updated in-memory after each operation.
- `rename_note`: updates all WikiLink targets across the vault (in-memory and on-disk rewrite of affected files).
- `update_frontmatter`: round-trips YAML; preserves unknown keys.

### Canvas

- Follows the [Obsidian JSON Canvas spec](https://jsoncanvas.org/).
- Node types: `text`, `file`, `link`, `group`.
- Serializes with `json.dumps(indent=2)`.

## MCP Tools

11 tools in `mcp_tools.py`:

| # | Name | Type | Backing function |
|---|------|------|-----------------|
| 1 | `obsidian_load_vault` | read | `ObsidianVault.load` |
| 2 | `obsidian_get_note` | read | `vault.get_note` |
| 3 | `obsidian_list_notes` | read | `vault.list_notes` |
| 4 | `obsidian_search_fulltext` | read | `search_fulltext` |
| 5 | `obsidian_search_by_tag` | read | `search_by_tag` |
| 6 | `obsidian_get_backlinks` | read | `graph.backlinks` |
| 7 | `obsidian_get_broken_links` | read | `graph.broken_links` |
| 8 | `obsidian_get_orphans` | read | `graph.orphans` |
| 9 | `obsidian_create_note` | write | `create_note` |
| 10 | `obsidian_update_note` | write | `update_note` |
| 11 | `obsidian_update_frontmatter` | write | `update_frontmatter` |

## Error Handling

- File not found: raises `NoteNotFoundError(path)`.
- Duplicate on create: raises `NoteExistsError(path)`.
- Invalid frontmatter YAML: logs warning, stores raw string under `_raw_frontmatter`.
- NetworkX unavailable: `graph.py` raises `ImportError` with install hint.

## Layer Position

**Service Layer** — Depends on `logging_monitoring` (Foundation). Used by agent orchestration modules.

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md) | [API_SPECIFICATION](API_SPECIFICATION.md) | [MCP_TOOL_SPECIFICATION](MCP_TOOL_SPECIFICATION.md)
