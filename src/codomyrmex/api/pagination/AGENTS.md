# AI Agent Guidelines — api/pagination

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides three pagination strategies (offset, cursor, keyset) through a common `Paginator` interface with factory-based instantiation for consistent API result set traversal.

## Key Components

| Component | Role |
|-----------|------|
| `PaginationStrategy` | Enum: `OFFSET`, `CURSOR`, `KEYSET` |
| `SortDirection` | Enum: `ASC`, `DESC` |
| `PageInfo` | Dataclass with `has_next`, `has_previous`, `total_count`, `start_cursor`, `end_cursor` |
| `PaginatedResponse` | Dataclass wrapping `items`, `page_info`, `page_size`, `current_page` |
| `PaginationRequest` | Dataclass with `page`, `page_size`, `cursor`, `sort_by`, `sort_direction`, `filters` |
| `Paginator` | ABC defining `paginate(items, request) -> PaginatedResponse` |
| `OffsetPaginator` | Classic offset/limit pagination |
| `CursorPaginator` | Base64-encoded cursor pagination with opaque tokens |
| `KeysetPaginator` | Seek-based pagination using sort key comparison |
| `create_paginator` | Factory returning the correct `Paginator` for a given `PaginationStrategy` |

## Operating Contracts

- All paginators implement `Paginator.paginate(items, request) -> PaginatedResponse`.
- `CursorPaginator` encodes/decodes cursors as base64 strings; callers treat cursors as opaque.
- `KeysetPaginator` requires items to be sorted by the keyset field for correct seek behaviour.
- `PaginatedResponse.page_info` always contains navigation metadata.
- `create_paginator(strategy, **kwargs)` selects the implementation by `PaginationStrategy` enum.

## Integration Points

- **Parent**: `api` module uses paginators in REST endpoint handlers.
- **Consumers**: Any list/collection endpoint returning paginated results.
- **Pattern**: `paginator = create_paginator(strategy); response = paginator.paginate(items, request)`.

## Navigation

- **Parent**: [api/README.md](../README.md)
- **Sibling**: [SPEC.md](SPEC.md) | [README.md](README.md)
- **Root**: [../../../../README.md](../../../../README.md)
