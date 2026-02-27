# Obsidian Agentic Context

**Version**: v3.0.0 | **Status**: Active | **Last Updated**: February 2026

## Agent Overview

This module gives agents full Obsidian vault access via two modes:

1. **Filesystem mode** — Direct file operations for parsing, CRUD, search, graph analysis, and canvas. No external dependencies.
2. **CLI mode** — Subprocess wrapper for the `obsidian` binary (≥1.12). The Obsidian app must be running.

## Operational Directives

1. **Mode Selection**: Use filesystem mode for offline/CI/batch. Use CLI mode for live Obsidian interaction.
2. **CLI Availability**: Check `ObsidianCLI.is_available()` or handle `ObsidianCLINotAvailable`.
3. **Vault Targeting**: CLI defaults to CWD vault. Use `vault=` to target specific vaults.
4. **File Targeting**: Use `file=` (wikilink resolution) or `path=` (exact path). Omit both for active file.
5. **Flat Imports**: All models and functions are exported from `__init__.py` for convenience.
6. **Documentation Sync**: Keep `AGENTS.md`, `README.md`, `SPEC.md` synchronized.

## Key Entry Points

### Filesystem Operations

| Task | Import | Example |
| ---- | ------ | ------- |
| Load vault | `ObsidianVault` | `vault = ObsidianVault(path)` |
| Check note | `ObsidianVault` | `vault.has_note("name")` or `"name" in vault` |
| List notes | `ObsidianVault` | `vault.list_notes(folder="sub")` |
| Create note | `create_note` | `create_note(vault, "n", content="...", template="T")` |
| Append/Prepend | `append_note`, `prepend_note` | `append_note(vault, "n", "text")` |
| Move/Rename | `move_note`, `rename_note` | `move_note(vault, "n", to="folder/")` |
| Raw read | `read_note_raw` | `text = read_note_raw(vault, "n")` |
| Full-text search | `search_vault` | `search_vault(vault, "q", folder="x")` |
| Regex search | `search_regex` | `search_regex(vault, r"\d+")` |
| Multi-tag filter | `filter_by_tags` | `filter_by_tags(vault, ["a","b"], match_all=True)` |
| Notes with key | `filter_by_frontmatter_exists` | `filter_by_frontmatter_exists(vault, "status")` |
| Notes linking to | `find_notes_linking_to` | `find_notes_linking_to(vault, "Target")` |
| Orphans | `find_orphans` | `find_orphans(vault)` |
| Dead ends | `find_dead_ends` | `find_dead_ends(vault)` |
| Hub notes | `find_hubs` | `find_hubs(vault, min_links=5)` |
| Shortest path | `get_shortest_path` | `get_shortest_path(vault, "A", "B")` |
| Graph stats | `get_link_stats` | Stats with orphan/dead_end counts |
| Parse canvas | `parse_canvas` | `canvas = parse_canvas("f.canvas")` |
| Create nodes | `create_text_node` | `node = create_text_node("Hi", color="#ff0")` |
| Connect nodes | `connect_nodes` | `edge = connect_nodes(n1.id, n2.id)` |
| Extract code | `extract_code_blocks` | From parsed `note.code_blocks` |
| Extract math | `extract_math` | From parsed `note.math_blocks` |
| Dataview fields | `extract_dataview_fields` | From parsed `note.dataview_fields` |

### CLI Operations

| Task | Module | Example |
| ---- | ------ | ------- |
| Search (CLI) | `cli_search.py` | `cli_search(cli, query, limit=10)` |
| Daily notes | `daily_notes.py` | `read_daily(cli)`, `append_daily(cli, text)` |
| Tasks | `tasks.py` | `list_tasks(cli, todo=True)` |
| Properties | `properties.py` | `set_property(cli, "title", "val")` |
| Plugins | `plugins.py` | `list_plugins(cli)`, `reload_plugin(cli, id)` |
| Themes | `plugins.py` | `set_theme(cli, name)`, `install_theme(cli, name)` |
| Sync/Publish | `sync.py` | `sync_status(cli)`, `publish_add(cli, file="n")` |
| Bookmarks | `bookmarks.py` | `bookmark_file(cli, file="note")` |
| Templates | `templates.py` | `read_template(cli, file="t", resolve=True)` |
| Workspaces | `workspace.py` | `save_workspace(cli, name)`, `list_tabs(cli)` |
| Dev tools | `developer.py` | `eval_js(cli, code)`, `cdp_command(cli, method)` |
| Links | `commands.py` | `get_orphans(cli)`, `get_deadends(cli)` |
| History | `commands.py` | `list_history(cli, file="n")`, `restore_history(cli)` |
| Random/Web | `commands.py` | `open_random(cli)`, `open_web(cli, url)` |
