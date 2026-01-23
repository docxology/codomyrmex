# Cache - MCP Tool Specification

This document outlines the specification for tools within the Cache module that are intended to be integrated with the Model Context Protocol (MCP).

## General Considerations

- **Tool Integration**: This module provides caching infrastructure for improving performance.
- **Configuration**: Supports multiple backends (memory, file, Redis) with configurable TTLs.

---

## Tool: `cache_get`

### 1. Tool Purpose and Description

Retrieves a value from the cache by its key. Returns null if the key doesn't exist or has expired.

### 2. Invocation Name

`cache_get`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `key` | `string` | Yes | Cache key to retrieve | `"user:123:profile"` |
| `backend` | `string` | No | Specific backend to use (default: configured default) | `"redis"` |
| `namespace` | `string` | No | Namespace prefix for the key | `"myapp"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | "hit", "miss", or "error" | `"hit"` |
| `value` | `any` | The cached value (null if miss) | `{"name": "John"}` |
| `ttl_remaining` | `integer` | Seconds until expiration (null if no TTL) | `3600` |
| `metadata` | `object` | Cache entry metadata | `{"created_at": "..."}` |

### 5. Error Handling

- **Backend Unavailable**: Returns error if cache backend is not accessible
- **Deserialization Error**: Returns error if cached value cannot be deserialized

### 6. Idempotency

- **Idempotent**: Yes

### 7. Usage Examples

```json
{
  "tool_name": "cache_get",
  "arguments": {
    "key": "api_response:endpoint1",
    "namespace": "http_cache"
  }
}
```

### 8. Security Considerations

- **Key Validation**: Keys should be validated to prevent injection
- **Sensitive Data**: Consider encryption for sensitive cached data

---

## Tool: `cache_set`

### 1. Tool Purpose and Description

Stores a value in the cache with an optional TTL (time-to-live).

### 2. Invocation Name

`cache_set`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `key` | `string` | Yes | Cache key | `"user:123:profile"` |
| `value` | `any` | Yes | Value to cache (must be serializable) | `{"name": "John"}` |
| `ttl` | `integer` | No | Time-to-live in seconds (null = no expiration) | `3600` |
| `backend` | `string` | No | Specific backend to use | `"memory"` |
| `namespace` | `string` | No | Namespace prefix for the key | `"myapp"` |
| `tags` | `array[string]` | No | Tags for cache invalidation | `["user", "profile"]` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | "success" or "error" | `"success"` |
| `key` | `string` | Full key that was set | `"myapp:user:123:profile"` |
| `expires_at` | `string` | ISO timestamp of expiration | `"2024-01-01T12:00:00Z"` |

### 5. Error Handling

- **Serialization Error**: Returns error if value cannot be serialized
- **Backend Full**: Returns error if cache storage is exhausted
- **Backend Unavailable**: Returns error if cache backend is not accessible

### 6. Idempotency

- **Idempotent**: Yes

---

## Tool: `cache_delete`

### 1. Tool Purpose and Description

Removes a value from the cache by its key.

### 2. Invocation Name

`cache_delete`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `key` | `string` | Yes | Cache key to delete | `"user:123:profile"` |
| `backend` | `string` | No | Specific backend to use | `"redis"` |
| `namespace` | `string` | No | Namespace prefix | `"myapp"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description |
|:-----------|:-----|:------------|
| `status` | `string` | "deleted", "not_found", or "error" |
| `key` | `string` | Full key that was deleted |

### 5. Error Handling

- **Backend Unavailable**: Returns error if cache backend is not accessible

### 6. Idempotency

- **Idempotent**: Yes

---

## Tool: `cache_invalidate_by_tag`

### 1. Tool Purpose and Description

Invalidates all cache entries with a specific tag or set of tags.

### 2. Invocation Name

`cache_invalidate_by_tag`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `tags` | `array[string]` | Yes | Tags to invalidate | `["user", "123"]` |
| `match_all` | `boolean` | No | If true, entry must have all tags (default: any) | `true` |
| `backend` | `string` | No | Specific backend | `"redis"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description |
|:-----------|:-----|:------------|
| `status` | `string` | "success" or "error" |
| `invalidated_count` | `integer` | Number of entries invalidated |

### 5. Error Handling

- **Backend Unavailable**: Returns error if cache backend is not accessible

### 6. Idempotency

- **Idempotent**: Yes

---

## Tool: `cache_stats`

### 1. Tool Purpose and Description

Returns statistics about cache usage, hit rates, and storage.

### 2. Invocation Name

`cache_stats`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `backend` | `string` | No | Specific backend (default: all) | `"redis"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description |
|:-----------|:-----|:------------|
| `backends` | `object` | Stats per backend |
| `total_entries` | `integer` | Total cached entries |
| `hit_rate` | `number` | Cache hit percentage |
| `memory_usage` | `string` | Approximate memory usage |

### 5. Error Handling

- Returns partial stats if some backends are unavailable

### 6. Idempotency

- **Idempotent**: Yes

---

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
