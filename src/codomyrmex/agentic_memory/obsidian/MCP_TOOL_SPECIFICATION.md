# Obsidian Vault Module — MCP Tool Specification

This document specifies the 11 MCP tools defined in `mcp_tools.py` using the `@mcp_tool` decorator. Tools 1-8 are read-only; tools 9-11 are write operations gated by the Trust Gateway.

## General Considerations

- **Vault state**: The vault must be loaded (via `obsidian_load_vault`) before most tools operate correctly. Tools cache the loaded vault for the session.
- **Path format**: All `path` parameters are relative to the vault root unless noted.
- **Error format**: All errors return `{"status": "error", "error": "<message>"}`.

---

## Tool 1: `obsidian_load_vault`

### Purpose

Load and index an Obsidian vault from disk. Must be called before search, graph, or CRUD tools.

### Invocation Name

`codomyrmex.obsidian_load_vault`

### Input Schema

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `vault_path` | `string` | Yes | Absolute path to vault root | `"/Users/me/MyVault"` |

### Output Schema

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `note_count` | `integer` | Number of notes indexed | `342` |
| `vault_path` | `string` | Confirmed vault path | `"/Users/me/MyVault"` |

### Idempotency

Yes — reloads and re-indexes on each call.

---

## Tool 2: `obsidian_get_note`

### Purpose

Retrieve a single note by title or relative path.

### Invocation Name

`codomyrmex.obsidian_get_note`

### Input Schema

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `title_or_path` | `string` | Yes | Note title (stem) or relative path | `"Projects/Alpha"` |

### Output Schema

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `found` | `boolean` | Whether note was found | `true` |
| `note` | `object\|null` | Note object (see Note model) | `{...}` |

### Note Object Fields

`path`, `title`, `frontmatter` (object), `content` (string), `tags` (array), `wikilinks` (array), `headings` (array)

### Idempotency

Yes.

---

## Tool 3: `obsidian_list_notes`

### Purpose

List all notes in the loaded vault (titles and paths).

### Invocation Name

`codomyrmex.obsidian_list_notes`

### Input Schema

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `limit` | `integer` | No | Max results (default: 100) | `50` |
| `folder` | `string` | No | Filter by folder prefix | `"Projects/"` |

### Output Schema

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `notes` | `array` | Array of `{title, path}` objects | `[...]` |
| `total` | `integer` | Total notes before limit | `342` |

### Idempotency

Yes.

---

## Tool 4: `obsidian_search_fulltext`

### Purpose

Full-text search across all note titles and content.

### Invocation Name

`codomyrmex.obsidian_search_fulltext`

### Input Schema

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `query` | `string` | Yes | Search query string | `"project alpha deadline"` |
| `limit` | `integer` | No | Max results (default: 20) | `10` |
| `case_sensitive` | `boolean` | No | Case-sensitive match (default: false) | `false` |

### Output Schema

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `results` | `array` | Array of `{title, path, context, score}` | `[...]` |
| `count` | `integer` | Number of results returned | `5` |

### Idempotency

Yes.

---

## Tool 5: `obsidian_search_by_tag`

### Purpose

Return all notes containing a specific tag.

### Invocation Name

`codomyrmex.obsidian_search_by_tag`

### Input Schema

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `tag` | `string` | Yes | Tag name (without `#`) | `"meeting"` |

### Output Schema

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `notes` | `array` | Array of `{title, path}` objects | `[...]` |
| `count` | `integer` | Number of matching notes | `12` |

### Idempotency

Yes.

---

## Tool 6: `obsidian_get_backlinks`

### Purpose

Get all notes that link to a given note.

### Invocation Name

`codomyrmex.obsidian_get_backlinks`

### Input Schema

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `note_title` | `string` | Yes | Note title to find backlinks for | `"Projects/Alpha"` |

### Output Schema

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `backlinks` | `array[string]` | Titles of linking notes | `["Daily/2026-02-01", "MOC/Projects"]` |
| `count` | `integer` | Number of backlinks | `2` |

### Idempotency

Yes.

---

## Tool 7: `obsidian_get_broken_links`

### Purpose

Find all WikiLinks in the vault that point to non-existent notes.

### Invocation Name

`codomyrmex.obsidian_get_broken_links`

### Input Schema

No parameters.

### Output Schema

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `broken_links` | `array` | Array of `{source, target}` pairs | `[{"source": "Home", "target": "MissingNote"}]` |
| `count` | `integer` | Number of broken links | `3` |

### Idempotency

Yes.

---

## Tool 8: `obsidian_get_orphans`

### Purpose

List notes with no incoming or outgoing links (disconnected from graph).

### Invocation Name

`codomyrmex.obsidian_get_orphans`

### Input Schema

No parameters.

### Output Schema

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `orphans` | `array[string]` | Titles of orphaned notes | `["ScratchPad", "OldDraft"]` |
| `count` | `integer` | Number of orphans | `7` |

### Idempotency

Yes.

---

## Tool 9: `obsidian_create_note`

**Write tool — Trust Gateway required.**

### Purpose

Create a new markdown note in the vault.

### Invocation Name

`codomyrmex.obsidian_create_note`

### Input Schema

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `path` | `string` | Yes | Relative path for new note | `"Projects/NewIdea.md"` |
| `content` | `string` | Yes | Markdown body content | `"# New Idea\n\nDetails."` |
| `frontmatter` | `object` | No | YAML frontmatter key/value pairs | `{"status": "draft", "tags": ["idea"]}` |

### Output Schema

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `created` | `boolean` | Whether creation succeeded | `true` |
| `path` | `string` | Confirmed file path | `"Projects/NewIdea.md"` |

### Error Handling

Returns `{"status": "error", "error": "NoteExistsError: ..."}` if file already exists.

### Idempotency

No — fails if note already exists.

---

## Tool 10: `obsidian_update_note`

**Write tool — Trust Gateway required.**

### Purpose

Overwrite the content of an existing note (frontmatter preserved by default).

### Invocation Name

`codomyrmex.obsidian_update_note`

### Input Schema

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `path` | `string` | Yes | Relative path of note to update | `"Projects/Alpha.md"` |
| `content` | `string` | Yes | New markdown body | `"# Alpha\n\nUpdated content."` |
| `preserve_frontmatter` | `boolean` | No | Keep existing frontmatter (default: true) | `true` |

### Output Schema

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `updated` | `boolean` | Whether update succeeded | `true` |
| `path` | `string` | Updated note path | `"Projects/Alpha.md"` |

### Error Handling

Returns error if note does not exist.

### Idempotency

Yes — writing same content twice produces identical result.

---

## Tool 11: `obsidian_update_frontmatter`

**Write tool — Trust Gateway required.**

### Purpose

Merge key/value pairs into a note's frontmatter without touching the body.

### Invocation Name

`codomyrmex.obsidian_update_frontmatter`

### Input Schema

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `path` | `string` | Yes | Relative path of note | `"Projects/Alpha.md"` |
| `updates` | `object` | Yes | Key/value pairs to merge | `{"status": "complete", "priority": "high"}` |

### Output Schema

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `updated` | `boolean` | Whether update succeeded | `true` |
| `frontmatter` | `object` | Full frontmatter after merge | `{...}` |

### Error Handling

Returns error if note does not exist or YAML serialization fails.

### Idempotency

Yes — applying same updates twice produces identical frontmatter.

---

## Security Considerations

- **Trust Gateway**: Tools 9-11 (write operations) require explicit trust grant via `/codomyrmexTrust`.
- **Path validation**: All paths are resolved relative to the loaded vault root; absolute paths and `../` traversal are rejected.
- **No execution**: No code in the note content is executed; content is treated as plain text.

## Navigation

- [README](README.md) | [API_SPECIFICATION](API_SPECIFICATION.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
