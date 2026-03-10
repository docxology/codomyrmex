# free_apis

Structured index and HTTP client for the [public-apis](https://github.com/public-apis/public-apis) catalogue — ~1 400 free, publicly accessible APIs organised by category.

## Features

| Capability | Description |
|---|---|
| **Registry** | Fetch, cache, search, and filter all public-apis entries |
| **Client** | Make HTTP calls to any listed (or arbitrary) free API |
| **MCP tools** | 3 PAI-compatible tools: list categories, search, call |
| **Zero deps** | Uses only Python stdlib (`urllib.request`) |

## Installation

No extra packages required. Already part of the `codomyrmex.api` module.

```bash
uv sync   # or: pip install codomyrmex
```

## Quick start

```python
from codomyrmex.api.free_apis import FreeAPIRegistry, FreeAPIClient

# 1. Build the registry (fetches ~1 400 entries, cached 1 hour)
registry = FreeAPIRegistry()
registry.fetch()

# 2. Explore
print(f"Loaded {len(registry.entries)} APIs")
for cat in registry.get_categories()[:5]:
    print(f"  {cat.name}: {cat.count} APIs")

# 3. Search / filter
animals = registry.filter_by_category("Animals")
no_auth  = registry.filter_by_auth("")          # no key required
https    = registry.filter_by_https(https_only=True)
results  = registry.search("weather")

# 4. Call an API
client = FreeAPIClient()
result = client.get("https://dog.ceo/api/breeds/list/all")
print(result.status_code)     # 200
print(result.body_text[:100]) # {"message":{"affenpinscher":[],...

# 5. POST with body
result = client.post("https://httpbin.org/post", body='{"hello":"world"}')
```

## Data source

Data is fetched from:

1. **JSON API** (primary): `https://api.publicapis.org/entries`
2. **GitHub README** (fallback): parses `public-apis/public-apis/README.md`

The registry caches results in memory for `cache_ttl_seconds` (default: 3 600 s).

## MCP Tools

Three tools are auto-discovered by the PAI MCP bridge:

### `free_api_list_categories`

Returns all category names and entry counts from the live registry.

```python
from codomyrmex.api.free_apis.mcp_tools import free_api_list_categories
result = free_api_list_categories()
# {"status": "success", "category_count": 42, "categories": [...]}
```

### `free_api_search`

Filter the registry by query string, category, auth type, and HTTPS flag.

```python
from codomyrmex.api.free_apis.mcp_tools import free_api_search
result = free_api_search(query="dog", category="Animals", https_only=True)
# {"status": "success", "count": 3, "entries": [...]}
```

### `free_api_call`

Call any URL (not limited to listed APIs) with configurable method, params, and headers.

```python
from codomyrmex.api.free_apis.mcp_tools import free_api_call
result = free_api_call(
    url="https://dog.ceo/api/breeds/list/all",
    method="GET",
    timeout=10,
)
# {"status": "success", "status_code": 200, "body_text": "...", "headers": {...}}
```

## API Reference

### `FreeAPIRegistry`

| Method | Description |
|---|---|
| `fetch(force=False)` | Load entries; uses cache unless `force=True` or TTL expired |
| `from_entries(entries)` | Class method — build from a list (no network) |
| `search(query)` | Case-insensitive substring match on name + description |
| `filter_by_category(cat)` | Exact category match (case-insensitive) |
| `filter_by_auth(auth)` | Match auth string exactly (`""`, `"apiKey"`, `"OAuth"`, …) |
| `filter_by_https(https_only)` | Filter by HTTPS flag |
| `get_categories()` | Sorted `APICategory` list with counts |
| `.entries` | All loaded entries (read-only copy) |
| `.source` | `APISource` enum value for last successful fetch |

### `FreeAPIClient`

| Method | Description |
|---|---|
| `call(url, method, headers, params, body, timeout)` | Full HTTP call |
| `get(url, params, timeout)` | Convenience GET |
| `post(url, body, timeout)` | Convenience POST |

### Models

| Class | Key fields |
|---|---|
| `APIEntry` | `name`, `description`, `auth`, `https`, `cors`, `link`, `category` |
| `APICategory` | `name`, `count` |
| `APICallResult` | `url`, `method`, `status_code`, `headers`, `body_text` |
| `APICallError` | `message`, `url` |
| `APISource` | `JSON_API`, `GITHUB_README`, `INLINE` |

## Running tests

```bash
# Unit tests only (no network)
uv run pytest src/codomyrmex/tests/unit/api/free_apis/ -v

# Include network tests
CODOMYRMEX_NETWORK_TESTS=1 uv run pytest src/codomyrmex/tests/unit/api/free_apis/ -v
```
