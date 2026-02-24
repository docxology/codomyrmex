# Technical Specification - Pagination

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.api.pagination`  
**Last Updated**: 2026-01-29

## 1. Purpose

Cursor and offset pagination utilities for API responses

## 2. Architecture

### 2.1 Components

```
pagination/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `api`

## 3. Interfaces

### 3.1 Public API

```python
# Primary exports from codomyrmex.api.pagination
from codomyrmex.api.pagination import (
    # Enums
    PaginationStrategy,    # Enum: OFFSET, CURSOR, KEYSET
    SortDirection,         # Enum: ASC, DESC
    # Dataclasses
    PageInfo,              # Page metadata: has_next_page, has_previous_page, total_items, cursors, etc.
    PaginatedResponse,     # Container: items + page_info
    PaginationRequest,     # Client params: page_size, page, cursor, after_key, sort_field, sort_direction
    # Abstract base
    Paginator,             # ABC with paginate(items, request) -> PaginatedResponse
    # Concrete paginators
    OffsetPaginator,       # Standard page-number pagination (1-based page + page_size)
    CursorPaginator,       # Opaque base64 cursor pagination with encode/decode helpers
    KeysetPaginator,       # Keyset/seek pagination sorted by a configurable field
    # Factory
    create_paginator,      # Factory: create_paginator(PaginationStrategy.CURSOR) -> Paginator
)

# Key class signatures:
class Paginator(ABC):
    def paginate(self, items: list[Any], request: PaginationRequest) -> PaginatedResponse: ...

class CursorPaginator(Paginator):
    @staticmethod
    def encode_cursor(index: int) -> str: ...
    @staticmethod
    def decode_cursor(cursor: str) -> int: ...

class KeysetPaginator(Paginator):
    def __init__(self, sort_field: str = "id"): ...

class PageInfo:
    def to_dict(self) -> dict[str, Any]: ...
    def to_headers(self) -> dict[str, str]: ...  # X-Total-Count, X-Page, X-Per-Page, etc.

def create_paginator(strategy: PaginationStrategy = PaginationStrategy.OFFSET, **kwargs) -> Paginator: ...
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Strategy pattern**: Three pagination strategies (offset, cursor, keyset) share a common `Paginator` ABC, selected via `create_paginator` factory using the `PaginationStrategy` enum.
2. **In-memory pagination**: All paginators operate on in-memory `list[Any]` slicing. This is intentional for composability -- database-level pagination should be done upstream.
3. **HTTP header generation**: `PageInfo.to_headers()` produces standard REST pagination headers (`X-Total-Count`, `X-Page`, `X-Per-Page`, etc.) for direct use in HTTP responses.

### 4.2 Limitations

- All paginators require the full item list in memory; not suitable for very large datasets without upstream query-level pagination
- `CursorPaginator` cursors are base64-encoded indices into the list, so they become invalid if the underlying data changes between requests
- `KeysetPaginator` falls back to original order if the sort field is missing or incomparable across items

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/api/pagination/
```

## 6. Future Considerations

- Database-aware paginator implementations that push LIMIT/OFFSET or WHERE clauses to the query layer
- Link header generation (RFC 8288) for HATEOAS-style pagination navigation
- Async paginator variant for streaming large result sets
