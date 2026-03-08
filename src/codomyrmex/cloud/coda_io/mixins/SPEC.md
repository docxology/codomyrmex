# Coda API Client Mixins - Specification

> **codomyrmex v1.1.9** | March 2026

## Overview

Technical specification for the Coda.io API client mixin architecture. Each mixin encapsulates a single Coda REST API domain, sharing a common HTTP transport layer provided by `BaseMixin`. The mixins are composed together in the parent `CodaClient` class via multiple inheritance.

## Design Principles

- **Zero-Mock Policy**: Tests against the Coda API use `@pytest.mark.skipif` guards when API keys are unavailable. No mocks or stubs.
- **Explicit Failure**: `BaseMixin._request` raises `CodaAPIError` on non-2xx status codes via `raise_for_status()`. No silent fallbacks.
- **Mixin Composition**: Each mixin is stateless and depends only on `BaseMixin._request`, `_encode_id`, and `self.session`/`self.base_url`/`self.timeout` from the parent client.
- **Typed Responses**: All structured responses are parsed into typed dataclasses from `codomyrmex.cloud.coda_io.models`.

## Architecture

```
cloud/coda_io/mixins/
    base.py              # BaseMixin: _request, _get, _post, _put, _patch, _delete, _encode_id
    access.py            # AccessMixin: 8 methods (sharing, permissions, ACL, publishing)
    analytics.py         # AnalyticsMixin: 3 methods (doc analytics, summary, page analytics)
    docs.py              # DocsMixin: 5 methods (list, create, get, delete, update docs)
    elements.py          # ElementsMixin: 6 methods (buttons, formulas, controls, automations)
    pages.py             # PagesMixin: 7 methods (list, create, get, update, delete, content, export)
    tables.py            # TablesMixin: 10 methods (tables, columns, rows CRUD)
    utils.py             # UtilsMixin: 3 methods (whoami, resolve link, mutation status)
```

## Functional Requirements

### BaseMixin (base.py)

- `_request(method, path, params, json_data, headers) -> dict` - Core HTTP method. Filters `None` from params, calls `raise_for_status` on response.
- `_get`, `_post`, `_put`, `_patch`, `_delete` - Convenience wrappers delegating to `_request`.
- `_encode_id(id_or_name) -> str` - URL-encode identifiers using `urllib.parse.quote(safe="")`.

### DocsMixin (docs.py)

- `list_docs(...) -> DocList` - Paginated listing with owner/published/starred/workspace filters.
- `create_doc(title, source_doc, timezone, folder_id, initial_page) -> Doc` - Requires Doc Maker role.
- `get_doc(doc_id) -> Doc` - Retrieve single doc metadata.
- `delete_doc(doc_id) -> dict` - Delete a document.
- `update_doc(doc_id, title, icon_name) -> dict` - Patch doc metadata.

### TablesMixin (tables.py)

- `list_tables(doc_id, ...) -> TableList` - List tables/views with type filtering.
- `get_table(doc_id, table_id_or_name, ...) -> Table` - Single table metadata.
- `list_columns(doc_id, table_id_or_name, ...) -> ColumnList` - Columns with visibility filter.
- `get_column(...) -> Column` - Single column details.
- `list_rows(doc_id, table_id_or_name, ...) -> RowList` - Rows with query filtering, sync tokens, value formats.
- `insert_rows(doc_id, table_id_or_name, rows, key_columns, ...) -> InsertRowsResult` - Insert or upsert rows.
- `get_row`, `update_row`, `delete_row`, `delete_rows` - Single/batch row operations.

### AccessMixin (access.py)

- `get_sharing_metadata(doc_id) -> SharingMetadata`
- `list_permissions(doc_id, ...) -> PermissionList`
- `add_permission(doc_id, access, principal, suppress_email) -> dict`
- `delete_permission(doc_id, permission_id) -> dict`
- `search_principals(doc_id, query) -> dict`
- `get_acl_settings(doc_id) -> ACLSettings`
- `update_acl_settings(doc_id, ...) -> ACLSettings`
- `publish_doc(doc_id, slug, discoverable, ...) -> dict` / `unpublish_doc(doc_id) -> dict`

### PagesMixin (pages.py)

- `list_pages(doc_id, ...) -> PageList`
- `create_page(doc_id, name, subtitle, ...) -> dict` - Requires Doc Maker role.
- `get_page(doc_id, page_id_or_name) -> Page`
- `update_page(doc_id, page_id_or_name, ...) -> dict`
- `delete_page(doc_id, page_id_or_name) -> dict`
- `list_page_content(doc_id, page_id_or_name, ...) -> dict`
- `export_page(doc_id, page_id_or_name, output_format) -> dict` / `get_page_export_status(...) -> dict`

### AnalyticsMixin (analytics.py)

- `list_doc_analytics(...) -> dict` - Time-series analytics with date/workspace/published filters.
- `get_doc_analytics_summary(...) -> dict` - Aggregate session counts.
- `list_page_analytics(doc_id, ...) -> dict` - Per-page analytics (Enterprise workspaces only).

### ElementsMixin (elements.py)

- `push_button(doc_id, table_id_or_name, row_id_or_name, column_id_or_name) -> dict`
- `list_formulas(doc_id, ...) -> FormulaList` / `get_formula(...) -> Formula`
- `list_controls(doc_id, ...) -> ControlList` / `get_control(...) -> Control`
- `trigger_automation(doc_id, rule_id, payload) -> dict`

### UtilsMixin (utils.py)

- `whoami() -> User` - Current authenticated user info.
- `resolve_browser_link(url, degrade_gracefully) -> dict` - Map browser URL to API resource.
- `get_mutation_status(request_id) -> MutationStatus` - Poll async operation completion.

## Interface Contracts

```python
# BaseMixin._request signature
def _request(
    self,
    method: str,
    path: str,
    params: dict[str, Any] | None = None,
    json_data: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]: ...

# All list methods follow this pagination pattern:
def list_*(self, ..., limit: int = 25, page_token: str | None = None) -> *List: ...
```

## Dependencies

| Dependency | Purpose |
|-----------|---------|
| `codomyrmex.cloud.coda_io.exceptions` | `raise_for_status` for HTTP error handling |
| `codomyrmex.cloud.coda_io.models` | Typed dataclasses (Doc, Page, Table, Row, etc.) |
| `codomyrmex.logging_monitoring` | Structured logging via `get_logger` |
| `urllib.parse` | URL-encoding for path parameters |
| `json` | Response body parsing |

## Constraints

- All API paths are relative (e.g., `/docs`, `/analytics/docs`). The `base_url` is provided by the parent `CodaClient`.
- The `session` object (`requests.Session`) is expected on `self` from the parent client.
- `timeout` is expected on `self` from the parent client.
- Page analytics (`list_page_analytics`) requires an Enterprise workspace.
- Doc creation requires the Doc Maker role in the target workspace.

## Navigation

- Parent: [cloud/coda_io](../README.md)
- Agents: [AGENTS.md](AGENTS.md)
- Module root: [cloud](../../README.md)
