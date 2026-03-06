# Coda API Client Mixins - Agent Coordination

> **codomyrmex v1.1.4** | March 2026

## Overview

Mixin classes that compose the Coda.io API client. Each mixin encapsulates a single Coda API domain and shares a common HTTP request layer via `BaseMixin`. Agents use these mixins indirectly through the parent `CodaClient` to manage Coda documents, pages, tables, permissions, and analytics.

## Key Files

| File | Purpose | Key Classes |
|------|---------|-------------|
| `base.py` | HTTP transport for all Coda API calls | `BaseMixin` |
| `docs.py` | Document CRUD operations | `DocsMixin` |
| `pages.py` | Page management and content export | `PagesMixin` |
| `tables.py` | Table, column, and row operations | `TablesMixin` |
| `access.py` | ACL, permissions, publishing | `AccessMixin` |
| `analytics.py` | Document and page analytics | `AnalyticsMixin` |
| `elements.py` | Formulas, controls, webhook automations | `ElementsMixin` |
| `utils.py` | User identity and async mutation tracking | `UtilsMixin` |

## MCP Tools Available

This subpackage does not expose `@mcp_tool` decorated tools directly. The parent `cloud` module exposes MCP tools (`list_cloud_instances`, `list_s3_buckets`, `upload_file_to_s3`) which are separate from Coda-specific functionality.

## Agent Instructions

1. **Always authenticate first.** The `CodaClient` requires a valid `api_key`. Use `UtilsMixin.whoami()` to verify the token before performing operations.
2. **Use IDs over names.** Table and page lookups accept both IDs and names, but IDs are stable across renames. Prefer IDs for reliability.
3. **Handle pagination.** All list operations return paginated results with a `page_token` field. Iterate until `page_token` is `None` to retrieve all results.
4. **Check mutation status for writes.** Write operations (`insert_rows`, `create_page`, `push_button`) return a `request_id`. Use `get_mutation_status(request_id)` to confirm completion before reading back.
5. **Respect rate limits.** The Coda API enforces rate limits. Space requests appropriately and handle HTTP 429 responses.

## Operating Contracts

- **Authentication**: All requests require a valid Coda API token set on the client session headers.
- **Error handling**: `BaseMixin._request` calls `raise_for_status()` from `codomyrmex.cloud.coda_io.exceptions` on non-2xx responses, raising `CodaAPIError`.
- **Data models**: Response dicts are parsed into typed dataclasses (`Doc`, `Page`, `Table`, `Row`, etc.) from `codomyrmex.cloud.coda_io.models`.
- **Thread safety**: Mixins themselves are stateless. Thread safety depends on the underlying `requests.Session` usage.

## Common Patterns

```python
# Pattern: Paginated listing
all_docs = []
page_token = None
while True:
    result = client.list_docs(limit=100, page_token=page_token)
    all_docs.extend(result.items)
    page_token = result.next_page_token
    if not page_token:
        break

# Pattern: Upsert rows with key columns
client.insert_rows(
    doc_id="AbCdEf",
    table_id_or_name="Inventory",
    rows=[{"cells": [{"column": "SKU", "value": "A100"}, {"column": "Qty", "value": 50}]}],
    key_columns=["SKU"],
)
```

## PAI Agent Role Access Matrix

| Agent Role | Access Level | Typical Operations |
|------------|-------------|-------------------|
| Engineer | Full | Table operations, row upserts, page creation |
| Architect | Read | Doc listing, analytics, ACL inspection |
| QATester | Read | Verify mutation status, validate data integrity |

## Navigation

- Parent: [cloud/coda_io](../README.md)
- Module root: [cloud](../../README.md)
- Spec: [SPEC.md](SPEC.md)
