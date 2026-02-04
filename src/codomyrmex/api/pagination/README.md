# Pagination

Cursor, offset, and keyset pagination utilities for API responses.

## Overview

The `pagination` submodule provides three pagination strategies (offset, cursor, keyset) behind a common `Paginator` interface, along with standard data structures for page metadata and paginated responses.

## Quick Start

```python
from codomyrmex.api.pagination import (
    PaginationStrategy, PaginationRequest, SortDirection,
    OffsetPaginator, CursorPaginator, KeysetPaginator,
    create_paginator,
)

items = list(range(100))

# Offset pagination (page numbers)
paginator = create_paginator(PaginationStrategy.OFFSET)
response = paginator.paginate(items, PaginationRequest(page=2, page_size=10))
# response.items == [10, 11, ..., 19]
# response.page_info.total_pages == 10
# response.page_info.has_next_page == True

# Cursor-based pagination
paginator = create_paginator(PaginationStrategy.CURSOR)
page1 = paginator.paginate(items, PaginationRequest(page_size=10))
page2 = paginator.paginate(items, PaginationRequest(
    page_size=10,
    cursor=page1.page_info.end_cursor,
))

# Keyset pagination (efficient for large datasets)
records = [{"id": i, "name": f"item_{i}"} for i in range(100)]
paginator = create_paginator(PaginationStrategy.KEYSET, sort_field="id")
page = paginator.paginate(records, PaginationRequest(
    page_size=10,
    after_key=42,
    sort_direction=SortDirection.ASC,
))

# Convert to HTTP headers or dict
headers = response.page_info.to_headers()
# {"X-Total-Count": "100", "X-Page": "2", "X-Per-Page": "10", ...}
data = response.to_dict()
# {"items": [...], "page_info": {...}}
```

## Features

- Three pagination strategies: offset, cursor, and keyset
- Common `Paginator` ABC for consistent interface
- `PageInfo` with HTTP header generation (X-Total-Count, X-Page, etc.)
- Opaque base64 cursors for cursor-based pagination
- Keyset pagination with configurable sort field and direction
- Factory function for strategy selection

## API Reference

See [API_SPECIFICATION.md](./API_SPECIFICATION.md) for detailed API documentation.

## Related Modules

- [`api`](../) - Parent module
- [`api.standardization`](../standardization/) - REST API framework
