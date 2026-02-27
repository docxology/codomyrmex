# Personal AI Infrastructure — Obsidian Vault Integration

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `obsidian` subpackage extends `agentic_memory` with structured Obsidian vault access. It maps naturally to the PAI Algorithm phases — vault search for OBSERVE, note creation for BUILD, task tracking for LEARN.

## PAI Algorithm Phase Mapping

| Phase | Capability | Key API |
|-------|-----------|---------|
| **OBSERVE** | Search vault for prior work on the current topic | `search_vault(vault, query, limit)` |
| **OBSERVE** | Full-text and regex search | `search_regex(vault, pattern)` |
| **OBSERVE** | Live vault search via CLI | `ObsidianCLI.run(["search", …])` |
| **OBSERVE** | List notes with a specific tag | `filter_by_tag(vault, "#project")` |
| **THINK** | Traverse link graph to surface related concepts | `build_link_graph(vault)`, `get_backlinks(vault, title)` |
| **THINK** | Find knowledge hubs and central notes | `find_hubs(vault, top_n=10)` |
| **PLAN** | Read canvas diagrams for architecture context | `parse_canvas(vault, "Architecture.canvas")` |
| **BUILD** | Create structured notes for work products | `create_note(vault, title, content, frontmatter)` |
| **BUILD** | Update existing notes with new content | `update_note(vault, title, content)` |
| **BUILD** | Build CLI-driven commands via `ObsidianCLI` | `ObsidianCLI().run([…])` |
| **EXECUTE** | Evolve canvas diagrams as architecture changes | `add_canvas_node`, `connect_nodes`, `save_canvas` |
| **EXECUTE** | Move and rename notes during restructuring | `move_note`, `rename_note` |
| **VERIFY** | Validate link graph integrity | `find_broken_links(vault)`, `find_orphans(vault)` |
| **LEARN** | Capture task outcomes via Tasks plugin | `TaskItem` from `obsidian.tasks` |
| **LEARN** | Log work in today's daily note | `open_or_create_daily_note(vault)` |
| **LEARN** | Tag and frontmatter management for note lifecycle | `set_frontmatter`, `filter_by_frontmatter` |

## Quick Reference

```python
# OBSERVE — find prior work
from codomyrmex.agentic_memory.obsidian import ObsidianVault, search_vault
vault = ObsidianVault("~/vaults/work")
hits = search_vault(vault, query="authentication refactor", limit=5)

# THINK — map knowledge graph
from codomyrmex.agentic_memory.obsidian import build_link_graph, find_hubs
graph = build_link_graph(vault)
hubs = find_hubs(vault, top_n=5)

# BUILD — create work notes
from codomyrmex.agentic_memory.obsidian import create_note
create_note(vault, title="Sprint 10 Plan", content="## Goals\n- …", frontmatter={"status": "active"})

# LEARN — daily note capture
from codomyrmex.agentic_memory.obsidian.daily_notes import open_or_create_daily_note
daily = open_or_create_daily_note(vault)

# CLI mode — live vault
from codomyrmex.agentic_memory.obsidian import ObsidianCLI, ObsidianCLINotAvailable
try:
    cli = ObsidianCLI()
    result = cli.run(["note", "open", "Sprint 10 Plan"])
except ObsidianCLINotAvailable:
    pass  # Obsidian not running; filesystem mode already handled above
```

## Mode Selection for PAI Agents

| Scenario | Mode | Rationale |
|----------|------|-----------|
| PAI running in CI/CD, no Obsidian app | Filesystem | No app dependency |
| PAI driving Obsidian UI for user review | CLI | Triggers actual Obsidian UI |
| Bulk note ingestion during OBSERVE | Filesystem | Speed; no app overhead |
| Creating daily note during LEARN | Either | CLI opens note in UI if available |

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
- [Parent PAI.md](../PAI.md) | [Source](../../../../../src/codomyrmex/agentic_memory/obsidian/)
