# Obsidian Specification

**Version**: v3.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Defines the architecture, interfaces, and behavioral contracts for the Obsidian module's dual-mode vault integration: filesystem-direct and CLI-backed.

## Architectural Constraints

- **Modularity**: Each command group lives in its own module with dedicated models.
- **Real Execution**: All functions execute real subprocess calls or filesystem operations.
- **Data Integrity**: Input/output uses typed dataclasses with strict validation.
- **Graceful Degradation**: CLI functions raise `ObsidianCLINotAvailable` when binary missing.

## Filesystem Layer

### Vault (`vault.py`) — `ObsidianVault`

| Method | Description |
| ------ | ----------- |
| `__init__(path)` | Load vault, validate directory exists |
| `notes` | Lazy-loaded `{relative_path: Note}` dict |
| `get_note(name)` | Lookup by path, filename, title, or alias |
| `has_note(name)` | Boolean existence check |
| `list_notes(folder=)` | List relative paths, optionally within folder |
| `list_folders()` | Unique folder paths |
| `get_notes_by_tag(tag)` | Notes matching tag (including nested) |
| `get_all_tags()` | Set of unique tag names |
| `metadata` | `VaultMetadata(note_count, tag_count, link_count, total_words, folder_count)` |
| `get_config()` | Read `.obsidian/*.json` into dict |
| `get_daily_notes_config()` | Daily-notes plugin config |
| `refresh()` | Re-scan vault |
| `__len__`, `__contains__`, `__iter__`, `__repr__` | Pythonic vault access |

### Parser (`parser.py`)

| Function | Returns |
| -------- | ------- |
| `parse_note(path, raw=)` | `Note` with all parsed fields |
| `parse_frontmatter(raw)` | `(dict, body_str)` |
| `extract_wikilinks(content)` | `list[Wikilink]` (target, alias, heading, block) |
| `extract_embeds(content)` | `list[Embed]` (target, width, height) |
| `extract_tags(content, fm=)` | `list[Tag]` from content + frontmatter |
| `extract_headings(content)` | `list[(level, text)]` |
| `extract_callouts(content)` | `list[Callout]` |
| `extract_code_blocks(content)` | `list[CodeBlock]` (language, content, line_start) |
| `extract_math(content)` | `list[MathBlock]` (display + inline) |
| `extract_dataview_fields(content)` | `list[DataviewField]` (key:: value) |
| `serialize_note(note)` | Markdown string |

### CRUD (`crud.py`)

| Function | Description |
| -------- | ----------- |
| `create_note(vault, name, content=, frontmatter=, overwrite=, template=)` | Create with optional template/overwrite |
| `read_note(vault, name)` | Parse and return `Note` |
| `read_note_raw(vault, name)` | Raw text, no parsing |
| `update_note(vault, name, content=, frontmatter=)` | Update content/frontmatter |
| `append_note(vault, name, content, newline=)` | Append text |
| `prepend_note(vault, name, content, after_frontmatter=)` | Prepend (FM-aware) |
| `delete_note(vault, name)` | Delete, returns `bool` |
| `rename_note(vault, old, new)` | Rename + update wikilinks |
| `move_note(vault, name, to=)` | Move to folder/path + update links |
| `get_frontmatter`, `set_frontmatter`, `remove_frontmatter_key` | FM manipulation |

### Graph (`graph.py`)

| Function | Description |
| -------- | ----------- |
| `build_link_graph(vault)` | Directed graph with `in_degree/out_degree/degree/has_node/has_edge` |
| `get_backlinks(vault, title)` | Notes linking TO title |
| `get_forward_links(vault, title)` | Notes linked FROM title |
| `find_orphans(vault)` | No in/out links |
| `find_dead_ends(vault)` | In links but no out links |
| `find_hubs(vault, min_links=)` | Heavily-linked notes, sorted |
| `find_broken_links(vault)` | `(note, wikilink)` pairs to missing targets |
| `get_link_stats(vault)` | `{node_count, edge_count, density, components, orphan_count, dead_end_count}` |
| `get_shortest_path(vault, src, tgt)` | BFS undirected path or `None` |

### Search (`search.py`)

| Function | Description |
| -------- | ----------- |
| `search_vault(vault, query, limit=, case_sensitive=, folder=)` | Full-text with title boost |
| `search_regex(vault, pattern, limit=, flags=)` | Regex content search |
| `filter_by_tag(vault, tag, include_nested=)` | Single tag filter |
| `filter_by_tags(vault, tags, match_all=)` | Multi-tag AND/OR |
| `filter_by_frontmatter(vault, key, value=)` | FM key/value filter |
| `filter_by_frontmatter_exists(vault, *keys)` | Must have ALL keys |
| `filter_by_date(vault, after=, before=, date_field=)` | Date range |
| `find_notes_linking_to(vault, target)` | Notes with wikilink to target |
| `find_notes_with_embeds(vault, target=)` | Notes embedding files |

### Canvas (`canvas.py`)

| Function | Description |
| -------- | ----------- |
| `parse_canvas(path)` | Read `.canvas` → `Canvas` |
| `create_canvas(path, nodes=, edges=)` | Create + write |
| `save_canvas(canvas, path=)` | Write to disk |
| `canvas_to_dict/from_dict` | Serialization |
| `add_canvas_node/edge` | Append (mutate) |
| `remove_canvas_node(canvas, id)` | Remove + cascade edges |
| `remove_canvas_edge(canvas, id)` | Remove edge |
| `create_text_node/file_node/link_node` | Factories with auto-ID |
| `connect_nodes(from_id, to_id, ...)` | Edge factory |

---

## CLI Layer

### Core (`cli.py`)

| Method | Description |
| ------ | ----------- |
| `ObsidianCLI(binary=, vault=, timeout=)` | Configure CLI wrapper |
| `run(args)` | Execute command, return `CLIResult` |
| `is_available()` | Check binary on PATH |
| `list_files/folders()`, `file_info/folder_info()` | File system queries |
| `open_file/read_file/create_file/append_file/prepend_file/move_file/rename_file/delete_file` | File operations |

### Domain Modules

| Module | Key Functions |
| ------ | ------------- |
| `daily_notes.py` | `open_daily`, `get_daily_path`, `read_daily`, `append_daily`, `prepend_daily` |
| `cli_search.py` | `cli_search`, `cli_search_context`, `cli_search_open` |
| `properties.py` | `get_aliases`, `get_properties`, `read/set/remove_property`, `get_tags` |
| `tasks.py` | `list_tasks`, `get_task`, `toggle_task`, `set_task_status` |
| `plugins.py` | `list_plugins/enabled`, `enable/disable/install/uninstall/reload_plugin`, themes, snippets |
| `sync.py` | `sync_toggle/status/history/read/restore/open/deleted`, `publish_site/list/status/add/remove/open` |
| `bookmarks.py` | `list_bookmarks`, `bookmark_file/folder/search/url` |
| `templates.py` | `list_templates`, `read_template(resolve=)`, `insert_template` |
| `workspace.py` | `get_active_workspace`, `list/save/load/delete_workspace`, `list_tabs`, `open_tab`, `list_recents` |
| `developer.py` | `toggle_devtools`, `eval_js`, `screenshot`, `get_console_log/errors`, `get_dom/css`, `debug_toggle`, `cdp_command`, `mobile_toggle` |
| `commands.py` | `list_commands/hotkeys`, `run_command`, `get_hotkey`, `get_diff`, history ops, link ops, `get_outline/wordcount`, `open_random/read_random`, `generate_unique_id`, `open_web`, `get_version`, `reload_vault`, `restart_app` |

---

## Error Hierarchy

```text
RuntimeError
├── ObsidianCLINotAvailable   # Binary not found on PATH
└── ObsidianCLIError          # Non-zero exit code (stores returncode, stderr, cmd)
```

## Testing

Tests in `tests/unit/agentic_memory/obsidian/` (18 files, 413 tests). CLI integration tests skipped via `pytest.mark.skipif` when `obsidian` binary not on PATH.
