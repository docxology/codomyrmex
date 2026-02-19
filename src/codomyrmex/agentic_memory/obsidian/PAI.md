# Personal AI Infrastructure — Obsidian Vault Module

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Obsidian Vault module is the **agentic memory substrate** for PAI. It gives PAI agents structured read/write access to a personal knowledge base stored as an Obsidian vault — enabling OBSERVE (search/read), BUILD (create/update notes), and VERIFY (graph integrity) operations.

## PAI Capabilities

### OBSERVE Phase — Search and Read

```python
from codomyrmex.agentic_memory.obsidian.vault import ObsidianVault
from codomyrmex.agentic_memory.obsidian.search import (
    search_fulltext, search_by_tag, search_by_frontmatter, search_by_date
)

vault = ObsidianVault()
vault.load("/Users/me/MyVault")

# Find relevant notes
results = search_fulltext(vault, "project alpha deadline")
tagged  = search_by_tag(vault, "meeting")
active  = search_by_frontmatter(vault, "status", "active")

# Read a specific note
note = vault.get_note("Projects/Alpha")
print(note.frontmatter, note.content)
```

### BUILD Phase — Create and Update

```python
from codomyrmex.agentic_memory.obsidian.crud import (
    create_note, update_note, update_frontmatter, rename_note
)

# Record outputs
create_note(vault, "Outputs/Summary.md",
            "# Summary\n\n[[ProjectAlpha]] delivered on time.",
            {"date": "2026-02-18", "tags": ["output"]})

# Update existing knowledge
update_note(vault, "Projects/Alpha.md", new_content)
update_frontmatter(vault, "Projects/Alpha.md", {"status": "complete"})
```

### VERIFY Phase — Graph and Integrity

```python
from codomyrmex.agentic_memory.obsidian.graph import LinkGraph

graph = LinkGraph()
graph.build(vault)

broken  = graph.broken_links()   # Wikilinks with no target note
orphans = graph.orphans()        # Disconnected notes
backs   = graph.backlinks("Projects/Alpha")
```

### Canvas Support

```python
from codomyrmex.agentic_memory.obsidian.canvas import CanvasParser

parser = CanvasParser()
canvas = parser.load("/Users/me/MyVault/Maps/ProjectMap.canvas")
print(canvas.nodes, canvas.edges)
```

## PAI Algorithm Phase Mapping

| Phase | Obsidian Module Contribution |
|-------|------------------------------|
| **OBSERVE** | `search_fulltext`, `search_by_tag`, `search_by_frontmatter`, `vault.get_note`, `vault.list_notes` — read existing knowledge |
| **PLAN** | `graph.backlinks`, `vault.get_metadata`, `search_by_frontmatter` — understand knowledge structure and gaps |
| **BUILD** | `create_note`, `update_note`, `update_frontmatter` — persist agent outputs and discoveries to the vault |
| **EXECUTE** | `rename_note`, `update_frontmatter` — apply knowledge management workflows |
| **VERIFY** | `graph.broken_links`, `graph.orphans` — confirm vault integrity after changes |
| **LEARN** | `search_by_date`, `search_by_tag` — review past notes and identify patterns |

## Key Exports

| Category | Exports |
|----------|---------|
| **Vault** | `ObsidianVault`, `VaultMetadata` |
| **Parser** | `ObsidianParser` |
| **Models** | `Note`, `WikiLink`, `Embed`, `Callout`, `Tag`, `Canvas`, `CanvasNode`, `CanvasEdge`, `SearchResult` |
| **CRUD** | `create_note`, `read_note`, `update_note`, `delete_note`, `rename_note`, `update_frontmatter` |
| **Graph** | `LinkGraph` |
| **Search** | `search_fulltext`, `search_by_tag`, `search_by_frontmatter`, `search_by_date` |
| **Canvas** | `CanvasParser` |
| **MCP** | 8 read tools + 3 write tools via `@mcp_tool` |

## MCP Integration

The 11 MCP tools in `mcp_tools.py` map to PAI phases:

- **Read tools** (OBSERVE/VERIFY): `obsidian_load_vault`, `obsidian_get_note`, `obsidian_list_notes`, `obsidian_search_fulltext`, `obsidian_search_by_tag`, `obsidian_get_backlinks`, `obsidian_get_broken_links`, `obsidian_get_orphans`
- **Write tools** (BUILD) — gated by Trust Gateway: `obsidian_create_note`, `obsidian_update_note`, `obsidian_update_frontmatter`

## Architecture Role

**Service Layer** — sits above Foundation (logging, environment) and is consumed by orchestration and agent modules. The vault acts as persistent agentic memory across PAI sessions.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — agentic_memory PAI map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md) | [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
