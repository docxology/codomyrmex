# AGENTS.md — free_apis

AI agent guidance for the `codomyrmex.api.free_apis` submodule.

## Module Purpose

Provides a structured, filterable index of ~1 400 free public APIs (sourced from
[public-apis/public-apis](https://github.com/public-apis/public-apis)) and a
stdlib-only HTTP client to call them.

## Key Files

| File | Role |
|---|---|
| `models.py` | `APIEntry`, `APICategory`, `APICallResult`, `APICallError`, `APISource` |
| `registry.py` | `FreeAPIRegistry` — fetch, cache, filter, search |
| `client.py` | `FreeAPIClient` — make HTTP calls via `urllib.request` |
| `mcp_tools.py` | 3 `@mcp_tool` functions for PAI MCP bridge |

## MCP Tools

| Tool | Category | Description |
|---|---|---|
| `free_api_list_categories` | `api` | List all categories with counts |
| `free_api_search` | `api` | Filter by query/category/auth/https |
| `free_api_call` | `api` | Call any API endpoint |

## Zero-Mock Policy

- All tests in `tests/unit/api/free_apis/` use real logic — no mocks, no stubs.
- Network tests are guarded with `@pytest.mark.skipif(not _NETWORK, ...)`.
- `FreeAPIRegistry.from_entries()` enables fully in-memory testing.

## Conventions

- No external dependencies — only Python stdlib.
- `FreeAPIRegistry` uses TTL-based in-memory caching (default 3 600 s).
- `FreeAPIClient` returns `APICallResult` for HTTP errors (4xx/5xx) instead of raising — only network/timeout failures raise `APICallError`.
- All public classes implement `to_dict()` for JSON serialisation.
