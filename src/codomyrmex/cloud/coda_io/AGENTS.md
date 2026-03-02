# Codomyrmex Agents — src/codomyrmex/cloud/coda_io

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides a comprehensive, type-safe Python client for the Coda.io REST API v1. The `CodaClient` class uses a mixin architecture to organize endpoints into logical groups (docs, pages, tables, elements, access, analytics, utilities), while `models.py` defines 30+ dataclasses for deserialization and `exceptions.py` maps HTTP status codes to typed exceptions.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `client.py` | `CodaClient` | Main API client composed of 7 mixins; manages `requests.Session` with Bearer auth |
| `models.py` | `Doc`, `Page`, `Table`, `Row`, `Column`, `Formula`, `Control` | Core resource dataclasses with `from_dict()` deserialization |
| `models.py` | `DocList`, `PageList`, `TableList`, `RowList`, `ColumnList` | Paginated list wrappers with `next_page_token` support |
| `models.py` | `Permission`, `PermissionList`, `ACLSettings`, `SharingMetadata` | Permission and sharing models |
| `models.py` | `MutationStatus`, `InsertRowsResult` | Async mutation result types |
| `models.py` | `TableType`, `PageType`, `ControlType`, `AccessType`, `ValueFormat` | Enums for API field values |
| `exceptions.py` | `CodaAPIError` (base), plus 7 subclasses | Typed exception hierarchy mapping HTTP 400-429 |
| `exceptions.py` | `raise_for_status()` | Dispatcher that maps HTTP status codes to exception classes |
| `mixins/base.py` | `BaseMixin` | Core HTTP methods shared across all endpoint groups |
| `mixins/docs.py` | `DocsMixin` | Doc CRUD, publishing, mutation status |
| `mixins/pages.py` | `PagesMixin` | Page CRUD, content export |
| `mixins/tables.py` | `TablesMixin` | Table, column, and row operations |
| `mixins/elements.py` | `ElementsMixin` | Formulas, controls, automations |
| `mixins/access.py` | `AccessMixin` | Permissions and sharing management |
| `mixins/analytics.py` | `AnalyticsMixin` | Doc, page, and pack analytics |
| `mixins/utils.py` | `UtilsMixin` | `whoami()`, link resolution |

## Operating Contracts

- `CodaClient` requires an API token at init; raises `ImportError` if `requests` is not installed.
- All list endpoints return paginated wrapper objects (`DocList`, `PageList`, etc.) with `next_page_token`.
- Mutations return HTTP 202; callers should poll `get_mutation_status()` for completion.
- HTTP errors are raised as typed exceptions via `raise_for_status()`.
- Rate limits apply: 100 reads/6s, 10 writes/6s, 4 doc-listing/6s.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring` (structured logging), `requests` (HTTP)
- **Used by**: Any agent needing Coda.io document automation or data access

## Navigation

- **Parent**: [cloud](../README.md)
- **Root**: [Root](../../../../README.md)
