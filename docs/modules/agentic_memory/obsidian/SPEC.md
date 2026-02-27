# Obsidian Vault Integration — Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Provide structured, testable access to Obsidian vault content using dual-mode architecture: pure-Python filesystem operations and CLI-backed live vault commands.

## Architectural Constraints

| Constraint | Rule |
|-----------|------|
| **Mode independence** | Filesystem mode never invokes the CLI; CLI mode never parses files directly |
| **Real execution** | All filesystem ops use `pathlib.Path`; CLI mode wraps the real `obsidian` binary |
| **No silent fallbacks** | `ObsidianCLINotAvailable` is raised explicitly — callers decide fallback strategy |
| **Zero-mock policy** | Tests use real temporary vaults via `tmp_path` pytest fixtures |
| **Frontmatter contract** | YAML frontmatter is preserved exactly; keys not touched by an operation remain unchanged |

## Public API Surface

All exports are available from `codomyrmex.agentic_memory.obsidian`.

### Filesystem Models (`models.py`)

| Class | Key Fields |
|-------|-----------|
| `Note` | `title`, `path`, `frontmatter`, `content`, `tags`, `wikilinks` |
| `Tag` | `name`, `path` |
| `Wikilink` | `target`, `display`, `heading`, `block_id` |
| `Canvas` | `nodes: list[CanvasNode]`, `edges: list[CanvasEdge]` |
| `CanvasNode` | `id`, `type`, `text\|file\|url`, `x`, `y`, `width`, `height` |
| `CanvasEdge` | `id`, `from_node`, `to_node`, `label` |
| `SearchResult` | `note`, `matches: list[str]`, `score: float` |
| `VaultMetadata` | `path`, `note_count`, `tag_count`, `attachment_count` |

### Vault (`vault.py`)

| Method | Signature | Description |
|--------|-----------|-------------|
| `ObsidianVault.__init__` | `(path: str \| Path)` | Open vault at path |
| `list_notes` | `() → list[Path]` | All `.md` file paths |
| `get_metadata` | `() → VaultMetadata` | Aggregate vault stats |

### Parser (`parser.py`)

| Function | Signature | Description |
|----------|-----------|-------------|
| `parse_note` | `(path: Path) → Note` | Parse `.md` to `Note` |
| `serialize_note` | `(note: Note) → str` | Render `Note` to markdown string |
| `parse_frontmatter` | `(content: str) → dict` | Extract YAML frontmatter |
| `extract_wikilinks` | `(content: str) → list[Wikilink]` | All `[[…]]` links |
| `extract_tags` | `(content: str) → list[Tag]` | All `#tag` occurrences |
| `extract_headings` | `(content: str) → list[str]` | All heading strings |
| `extract_code_blocks` | `(content: str) → list[CodeBlock]` | Fenced code blocks |
| `extract_embeds` | `(content: str) → list[Embed]` | `![[…]]` embeds |
| `extract_callouts` | `(content: str) → list[Callout]` | `> [!type]` callouts |
| `extract_math` | `(content: str) → list[MathBlock]` | `$$…$$` math blocks |
| `extract_dataview_fields` | `(content: str) → list[DataviewField]` | `key:: value` fields |

### CRUD (`crud.py`)

| Function | Signature | Description |
|----------|-----------|-------------|
| `create_note` | `(vault, title, content, frontmatter?) → Path` | Create new note |
| `read_note` | `(vault, title \| path) → Note` | Parse and return note |
| `read_note_raw` | `(vault, title \| path) → str` | Return raw markdown string |
| `update_note` | `(vault, title, content) → None` | Overwrite note body |
| `delete_note` | `(vault, title) → None` | Remove note file |
| `move_note` | `(vault, title, new_folder) → Path` | Move to subfolder |
| `rename_note` | `(vault, old_title, new_title) → Path` | Rename file |
| `get_frontmatter` | `(vault, title) → dict` | Read frontmatter dict |
| `set_frontmatter` | `(vault, title, key, value) → None` | Set one frontmatter key |
| `remove_frontmatter_key` | `(vault, title, key) → None` | Remove frontmatter key |
| `append_note` | `(vault, title, content) → None` | Append text to note |
| `prepend_note` | `(vault, title, content) → None` | Prepend text to note |

### Graph (`graph.py`)

| Function | Returns | Description |
|----------|---------|-------------|
| `build_link_graph` | `dict[str, list[str]]` | Full wikilink adjacency map |
| `get_forward_links` | `list[str]` | Notes linked from `title` |
| `get_backlinks` | `list[str]` | Notes that link to `title` |
| `find_orphans` | `list[str]` | Notes with no links |
| `find_hubs` | `list[tuple[str, int]]` | Most-linked notes |
| `find_broken_links` | `list[tuple[str, str]]` | Links to non-existent notes |
| `find_dead_ends` | `list[str]` | Notes with no outgoing links |
| `get_shortest_path` | `list[str] \| None` | BFS path between two notes |
| `get_link_stats` | `dict` | Aggregate link statistics |

### Search (`search.py`)

| Function | Returns | Description |
|----------|---------|-------------|
| `search_vault` | `list[SearchResult]` | Full-text search all notes |
| `search_regex` | `list[SearchResult]` | Regex search across vault |
| `filter_by_tag` | `list[Note]` | Notes matching one tag |
| `filter_by_tags` | `list[Note]` | Notes matching all tags |
| `filter_by_frontmatter` | `list[Note]` | Notes where `key == value` |
| `filter_by_frontmatter_exists` | `list[Note]` | Notes that have `key` |
| `filter_by_date` | `list[Note]` | Notes in date range |
| `find_notes_linking_to` | `list[Note]` | Notes with wikilink to target |
| `find_notes_with_embeds` | `list[Note]` | Notes containing embeds |

### Canvas (`canvas.py`)

| Function | Description |
|----------|-------------|
| `create_canvas` | Create new empty canvas |
| `parse_canvas` | Parse `.canvas` JSON to `Canvas` |
| `save_canvas` | Write `Canvas` to `.canvas` file |
| `canvas_to_dict / canvas_from_dict` | Serialisation helpers |
| `add_canvas_node / remove_canvas_node` | Node management |
| `add_canvas_edge / remove_canvas_edge` | Edge management |
| `connect_nodes` | Add edge between two node IDs |
| `create_text_node / create_file_node / create_link_node` | Typed node factories |

### CLI Core (`cli.py`)

| Symbol | Type | Description |
|--------|------|-------------|
| `ObsidianCLI` | Class | CLI runner; `run(args: list[str]) → CLIResult` |
| `CLIResult` | Dataclass | `stdout`, `stderr`, `returncode` |
| `ObsidianCLIError` | Exception | Non-zero exit code |
| `ObsidianCLINotAvailable` | Exception | CLI binary not found |

## Non-Functional Requirements

- `parse_note` on a 500 KB note: < 50 ms
- `search_vault` on a 1,000-note vault: < 2 s
- `build_link_graph` on a 1,000-note vault: < 1 s
- No external dependencies beyond Python stdlib + `pyyaml`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md)
- [Parent SPEC.md](../SPEC.md) | [Source](../../../../../src/codomyrmex/agentic_memory/obsidian/)
