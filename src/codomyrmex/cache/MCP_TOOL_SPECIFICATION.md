# Cache - MCP Tool Specification

This document specifies the Model Context Protocol (MCP) tools of the Cache module. They are defined with `@mcp_tool` in `mcp_tools.py` and surfaced by the PAI MCP bridge as `codomyrmex.<name>`.

## General Considerations

- **Backend**: All tools share one module-level `CacheManager` whose caches use the in-memory backend, so entries live only as long as the server process.
- **Named caches**: `cache_name` selects a cache; it is created on first use.
- **Tags and namespaces**: Not supported by the MCP tools. Use the Python `CacheManager` API for other backends.

---

## Tool: `cache_get`

### 1. Tool Purpose and Description

Retrieves a value by key. Returns `null` if the key is missing or has expired.

### 2. Invocation Name

`cache_get`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `key` | `string` | Yes | Cache key to retrieve | `"user:123:profile"` |
| `cache_name` | `string` | No | Named cache (default `"default"`) | `"http_cache"` |

### 4. Output Schema (Return Value)

The cached value itself, or `null` on a miss.

### 5. Error Handling

- Misses are not errors; they return `null`.

### 6. Idempotency

- **Idempotent**: Yes (hit/miss counters change).

### 7. Usage Examples

```json
{
  "tool_name": "cache_get",
  "arguments": {
    "key": "api_response:endpoint1",
    "cache_name": "http_cache"
  }
}
```

### 8. Security Considerations

- **Sensitive Data**: Values are stored unencrypted in process memory.

---

## Tool: `cache_set`

### 1. Tool Purpose and Description

Stores a value under a key with an optional TTL (time-to-live).

### 2. Invocation Name

`cache_set`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `key` | `string` | Yes | Cache key | `"user:123:profile"` |
| `value` | `any` | Yes | Value to cache | `{"name": "John"}` |
| `ttl` | `integer` | No | Time-to-live in seconds; `null` uses the cache default | `3600` |
| `cache_name` | `string` | No | Named cache (default `"default"`) | `"http_cache"` |

### 4. Output Schema (Return Value)

`true` once the value is stored.

### 5. Error Handling

- Backend errors propagate as tool errors.

### 6. Idempotency

- **Idempotent**: Yes (setting the same key and value again leaves the same state).

---

## Tool: `cache_delete`

### 1. Tool Purpose and Description

Removes a key from the cache.

### 2. Invocation Name

`cache_delete`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `key` | `string` | Yes | Cache key to delete | `"user:123:profile"` |
| `cache_name` | `string` | No | Named cache (default `"default"`) | `"http_cache"` |

### 4. Output Schema (Return Value)

`true` if the key was deleted, `false` if it did not exist.

### 5. Error Handling

- A missing key is not an error; it returns `false`.

### 6. Idempotency

- **Idempotent**: Yes (the second call returns `false`).

---

## Tool: `cache_stats`

### 1. Tool Purpose and Description

Returns usage statistics for one named cache.

### 2. Invocation Name

`cache_stats`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `cache_name` | `string` | No | Named cache (default `"default"`) | `"http_cache"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `hits` | `integer` | Lookups that found a value |
| `misses` | `integer` | Lookups that found nothing |
| `total_requests` | `integer` | `hits + misses` |
| `hit_rate` | `number` | Hit ratio between 0 and 1 |
| `size` | `integer` | Current number of entries |
| `max_size` | `integer` | Capacity of the cache |
| `usage_percent` | `number` | `size` as a percentage of `max_size` |
| `evictions` | `integer` | Entries evicted for capacity |
| `writes` | `integer` | Successful `set` calls |
| `deletes` | `integer` | Successful deletions |

### 5. Error Handling

- Unknown cache names are created empty, so the call returns zeroed statistics.

### 6. Idempotency

- **Idempotent**: Yes

---

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->
