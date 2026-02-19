# Obsidian Vault Module

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Python interface for Obsidian vaults — parse, index, search, and mutate markdown notes with full support for wikilinks, embeds, callouts, frontmatter, tags, the link graph, and JSON Canvas files. Exposes 11 MCP tools for AI agent use.

## Key Exports

### Data Models (`models.py`)

- **`Note`** — Complete note representation (path, title, frontmatter, content, wikilinks, tags, headings)
- **`WikiLink`** — Parsed `[[target|alias]]` reference
- **`Embed`** — Parsed `![[file]]` embed
- **`Callout`** — Obsidian callout block (`> [!type] title`)
- **`Tag`** — Inline or frontmatter tag
- **`Canvas`** / **`CanvasNode`** / **`CanvasEdge`** — JSON Canvas data model
- **`SearchResult`** — Search hit with note reference and match context
- **`VaultMetadata`** — Vault-level statistics (note count, tag index, etc.)

### Parser (`parser.py`)

- **`ObsidianParser`** — Parses a single markdown file into a `Note` dataclass
  - `parse_file(path)` — Full parse
  - `parse_frontmatter(text)` — YAML frontmatter extraction
  - `parse_wikilinks(text)` — Extract all `[[...]]` links
  - `parse_embeds(text)` — Extract `![[...]]` embeds
  - `parse_callouts(text)` — Extract callout blocks
  - `parse_tags(text)` — Extract inline `#tag` and frontmatter tags
  - `parse_headings(text)` — Extract heading hierarchy

### Vault (`vault.py`)

- **`ObsidianVault`** — Load and index an entire vault from disk
  - `load(vault_path)` — Scan and parse all `.md` files
  - `get_note(title_or_path)` — Retrieve a note by title or relative path
  - `list_notes()` — Return all indexed notes
  - `get_metadata()` — Return `VaultMetadata`

### CRUD (`crud.py`)

- **`create_note(vault, path, content, frontmatter)`** — Create a new note
- **`read_note(vault, path)`** — Read note content
- **`update_note(vault, path, content)`** — Overwrite note content
- **`delete_note(vault, path)`** — Remove note from vault
- **`rename_note(vault, old_path, new_path)`** — Rename and update backlinks
- **`update_frontmatter(vault, path, updates)`** — Merge frontmatter key/value pairs

### Graph (`graph.py`)

- **`LinkGraph`** — NetworkX-backed link graph
  - `build(vault)` — Construct graph from vault index
  - `backlinks(note_title)` — Notes that link to a given note
  - `orphans()` — Notes with no incoming or outgoing links
  - `broken_links()` — Wikilinks that resolve to no existing note
  - `forward_links(note_title)` — Notes linked from a given note

### Search (`search.py`)

- **`search_fulltext(vault, query, limit)`** — Full-text substring/regex search
- **`search_by_tag(vault, tag)`** — Filter notes by tag
- **`search_by_frontmatter(vault, key, value)`** — Filter by frontmatter field
- **`search_by_date(vault, field, start, end)`** — Filter by date range in frontmatter

### Canvas (`canvas.py`)

- **`CanvasParser`** — Parse `.canvas` JSON files into `Canvas` dataclasses
  - `load(path)` — Load canvas from file
  - `save(canvas, path)` — Serialize and write canvas
  - `add_node(canvas, node)` — Add a node to a canvas
  - `add_edge(canvas, edge)` — Add an edge to a canvas

### MCP Tools (`mcp_tools.py`)

11 tools decorated with `@mcp_tool` — see [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md).

## Quick Start

```python
from codomyrmex.agentic_memory.obsidian.vault import ObsidianVault
from codomyrmex.agentic_memory.obsidian.search import search_fulltext
from codomyrmex.agentic_memory.obsidian.graph import LinkGraph

# Load vault
vault = ObsidianVault()
vault.load("/path/to/MyVault")

# Search notes
results = search_fulltext(vault, "machine learning", limit=10)
for r in results:
    print(r.note.title, r.context)

# Explore link graph
graph = LinkGraph()
graph.build(vault)
print("Orphaned notes:", graph.orphans())
print("Broken links:", graph.broken_links())
```

```python
from codomyrmex.agentic_memory.obsidian.crud import create_note, update_frontmatter

# Create a note
create_note(vault, "Projects/NewIdea.md", "# New Idea\n\nDetails here.", {"status": "draft"})

# Tag it
update_frontmatter(vault, "Projects/NewIdea.md", {"status": "active", "tags": ["project"]})
```

## Directory Contents

- `models.py` — Dataclasses for all Obsidian entities
- `parser.py` — Markdown parsing (frontmatter, wikilinks, callouts, tags, headings)
- `vault.py` — Vault loader and in-memory index
- `crud.py` — Note create/read/update/delete/rename
- `graph.py` — Link graph analysis (NetworkX)
- `search.py` — Full-text and filtered search
- `canvas.py` — JSON Canvas parse and creation
- `mcp_tools.py` — 11 MCP tool definitions

## Dependencies

- `python-frontmatter` or `PyYAML` — YAML frontmatter parsing
- `networkx` — Link graph analysis
- Standard library: `pathlib`, `json`, `re`, `datetime`

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/agentic_memory/ -v
```

## Navigation

- **Parent**: [agentic_memory/README.md](../README.md)
- **Project Root**: [README.md](../../../../README.md)
- **Specs**: [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md) | [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
