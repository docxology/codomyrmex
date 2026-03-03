# Coda API Client Mixins

> **codomyrmex v1.0.8** | March 2026

## Overview

Mixin classes that compose the Coda.io API client. Each mixin encapsulates a single Coda API domain (docs, pages, tables, access control, analytics, elements, utilities) and relies on a shared `BaseMixin._request` HTTP layer for authenticated requests. The parent `CodaClient` inherits all mixins to form the full client surface.

## PAI Integration

| PAI Phase | Relevance | Usage |
|-----------|-----------|-------|
| EXECUTE | Primary | Agents use the Coda client to read/write docs, tables, and pages |
| OBSERVE | Secondary | `AnalyticsMixin` retrieves doc and page analytics |
| VERIFY | Supporting | `UtilsMixin.whoami()` confirms authentication; `get_mutation_status()` checks async write completion |

## Key Exports

| File | Class/Function | Purpose |
|------|---------------|---------|
| `base.py` | `BaseMixin` | HTTP request layer (`_get`, `_post`, `_put`, `_patch`, `_delete`, `_encode_id`) |
| `docs.py` | `DocsMixin` | CRUD for Coda docs (`list_docs`, `create_doc`, `get_doc`, `delete_doc`, `update_doc`) |
| `pages.py` | `PagesMixin` | Page management (`list_pages`, `create_page`, `get_page`, `update_page`, `delete_page`, `export_page`) |
| `tables.py` | `TablesMixin` | Table and row operations (`list_tables`, `list_columns`, `list_rows`, `insert_rows`, `get_row`, `update_row`, `delete_row`) |
| `access.py` | `AccessMixin` | ACL and sharing (`get_sharing_metadata`, `list_permissions`, `add_permission`, `delete_permission`, `get_acl_settings`, `update_acl_settings`, `publish_doc`) |
| `analytics.py` | `AnalyticsMixin` | Doc/page analytics (`list_doc_analytics`, `get_doc_analytics_summary`, `list_page_analytics`) |
| `elements.py` | `ElementsMixin` | Formulas, controls, automations (`push_button`, `list_formulas`, `get_formula`, `list_controls`, `get_control`, `trigger_automation`) |
| `utils.py` | `UtilsMixin` | User identity and mutation status (`whoami`, `resolve_browser_link`, `get_mutation_status`) |

## Quick Start

```python
from codomyrmex.cloud.coda_io.client import CodaClient

client = CodaClient(api_key="coda-api-key-here")

# List all accessible docs
docs = client.list_docs(is_owner=True, limit=10)
for doc in docs.items:
    print(doc.name)

# Get rows from a table
rows = client.list_rows(doc_id="AbCdEf", table_id_or_name="Tasks")
for row in rows.items:
    print(row.values)

# Check sharing permissions
metadata = client.get_sharing_metadata(doc_id="AbCdEf")
print(metadata)
```

## Architecture

```
cloud/coda_io/mixins/
    __init__.py          # Package init
    base.py              # BaseMixin - HTTP request layer
    access.py            # AccessMixin - ACL, permissions, publishing
    analytics.py         # AnalyticsMixin - doc and page analytics
    docs.py              # DocsMixin - document CRUD
    elements.py          # ElementsMixin - formulas, controls, automations
    pages.py             # PagesMixin - page CRUD and export
    tables.py            # TablesMixin - tables, columns, rows
    utils.py             # UtilsMixin - whoami, mutation status
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/cloud/ -v
```

## Navigation

- Parent: [cloud/coda_io](../README.md)
- Module root: [cloud](../../README.md)
- Project root: [codomyrmex](../../../../../README.md)
