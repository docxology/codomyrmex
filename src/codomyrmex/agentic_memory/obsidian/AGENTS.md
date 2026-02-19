# Agent Guidelines - Obsidian Vault Module

## Module Overview

Read, search, and mutate an Obsidian vault: notes, frontmatter, wikilinks, tags, the link graph, and JSON Canvas files.

## Key Classes and Functions

- **`ObsidianVault`** — Load and index a vault; always call `load()` before accessing notes
- **`ObsidianParser`** — Parse individual markdown files
- **`LinkGraph`** — Build NetworkX graph; call `build(vault)` after loading
- **`search_fulltext`** / **`search_by_tag`** — Query notes without mutating state
- **`create_note`** / **`update_note`** / **`delete_note`** — Mutating operations

## Agent Instructions

1. **Load before querying** — Always call `vault.load(path)` before any search or CRUD.
2. **Prefer read tools** — Use search and graph tools (OBSERVE) before writing anything.
3. **Check for existing notes** — Use `vault.get_note()` before `create_note()` to avoid duplicates.
4. **Validate wikilinks** — After creating or renaming notes, run `graph.broken_links()` to confirm link integrity.
5. **Frontmatter is structured data** — Use `update_frontmatter()` for metadata; use `update_note()` only for body content.
6. **Respect vault structure** — Create notes in paths that match the vault's existing folder conventions.
7. **Never delete without confirmation** — `delete_note()` is irreversible; verify intent before calling.

## Common Patterns

```python
from codomyrmex.agentic_memory.obsidian.vault import ObsidianVault
from codomyrmex.agentic_memory.obsidian.search import search_fulltext, search_by_tag
from codomyrmex.agentic_memory.obsidian.graph import LinkGraph
from codomyrmex.agentic_memory.obsidian.crud import create_note, update_frontmatter

VAULT_PATH = "/Users/me/MyVault"

# Load
vault = ObsidianVault()
vault.load(VAULT_PATH)

# Observe: search
results = search_fulltext(vault, "project alpha", limit=5)
for r in results:
    print(r.note.title, "|", r.context[:80])

# Observe: tag filter
tagged = search_by_tag(vault, "meeting")

# Observe: graph
graph = LinkGraph()
graph.build(vault)
orphans = graph.orphans()
broken = graph.broken_links()

# Build: create
create_note(vault, "Areas/ProjectAlpha.md", "# Project Alpha\n\n[[Tasks]]", {"status": "active"})

# Build: update metadata
update_frontmatter(vault, "Areas/ProjectAlpha.md", {"priority": "high"})
```

## Testing Patterns

```python
vault = ObsidianVault()
vault.load(VAULT_PATH)
notes = vault.list_notes()
assert len(notes) > 0

graph = LinkGraph()
graph.build(vault)
broken = graph.broken_links()
# broken should be a list (may be empty)
assert isinstance(broken, list)

results = search_fulltext(vault, "test", limit=3)
assert all(hasattr(r, "note") for r in results)
```

## Error Handling

- `vault.get_note()` returns `None` if not found; always check before accessing note attributes.
- `broken_links()` returns link targets that do not resolve; do not assume the source note is broken.
- File write operations may raise `IOError`; wrap in try/except when running in restricted environments.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md) | [API_SPECIFICATION](API_SPECIFICATION.md)
