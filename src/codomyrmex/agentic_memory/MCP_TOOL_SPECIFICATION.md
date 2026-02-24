# Agentic Memory Module — MCP Tool Specification

This document describes the 3 MCP tools exposed by `codomyrmex.agentic_memory.mcp_tools`.

> **Note**: The `memory_put`, `memory_get`, and `memory_search` tools use a fresh `InMemoryStore` per invocation. They are designed for single-session in-process use. For persistent memory across invocations, use the Python API with `JSONFileStore` directly.

---

## `memory_put`

Store a new memory entry with content, optional type, and importance.

### Input Schema

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `content` | `str` | Yes | Text content of the memory |
| `memory_type` | `str` | No | One of `"episodic"`, `"semantic"`, `"procedural"` (default `"episodic"`) |
| `importance` | `str` | No | One of `"LOW"`, `"MEDIUM"`, `"HIGH"`, `"CRITICAL"` (default `"medium"`) |

### Output Schema

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "The project deadline is March 1st",
  "memory_type": "episodic",
  "importance": 2,
  "metadata": {},
  "tags": [],
  "created_at": 1740340308.123,
  "access_count": 0,
  "last_accessed": 0.0
}
```

---

## `memory_get`

Retrieve a memory by its ID.

### Input Schema

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `memory_id` | `str` | Yes | UUID of the memory to retrieve |

### Output Schema

Returns the memory dict (same format as `memory_put` output), or `null` if not found.

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "The project deadline is March 1st",
  "memory_type": "episodic",
  "importance": 2,
  "metadata": {},
  "tags": [],
  "created_at": 1740340308.123,
  "access_count": 1,
  "last_accessed": 1740340320.456
}
```

---

## `memory_search`

Search stored memories by a text query and return ranked results.

### Input Schema

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | `str` | Yes | Text query for relevance scoring |
| `k` | `int` | No | Maximum results to return (default 5) |

### Output Schema

```json
[
  {
    "memory": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "content": "The project deadline is March 1st",
      "memory_type": "episodic",
      "importance": 2,
      "metadata": {},
      "tags": [],
      "created_at": 1740340308.123,
      "access_count": 0,
      "last_accessed": 0.0
    },
    "relevance": 0.75,
    "combined_score": 0.52
  }
]
```

Results are sorted by `combined_score` descending (`0.5*relevance + 0.3*recency + 0.2*importance`).
