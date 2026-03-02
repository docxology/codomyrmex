# Agentic Memory — Specification

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides persistent, structured memory for AI agents with key-value storage, search, and user profiling. Central to the PAI Algorithm's LEARN phase.

## Functional Requirements

### Memory Operations

| Operation | Signature | Description |
|-----------|-----------|-------------|
| **Put** | `memory_put(key: str, value: Any) → None` | Store a key-value pair |
| **Get** | `memory_get(key: str) → Any` | Retrieve value by key; raises `KeyError` if missing |
| **Search** | `memory_search(query: str, limit: int) → list` | Search memories by pattern |
| **List** | `memory_list() → list[str]` | Return all stored keys |

### Storage Backends

| Backend | Persistence | Performance | Thread-Safe |
|---------|-------------|-------------|-------------|
| `InMemoryStore` | Session only | O(1) get/put | Yes |
| `JSONFileStore` | Disk-backed | O(1) get, O(n) search | Yes (file locks) |

### User Profile

| Method | Description |
|--------|-------------|
| `UserProfile()` | Initialize or load user preference tracking |
| Profile fields | Coding style, interaction patterns, preferred models |

## Non-Functional Requirements

- **Latency**: `memory_get` < 1ms (in-memory), < 10ms (file-backed)
- **Capacity**: Up to 100,000 entries per store
- **Durability**: `JSONFileStore` flushes on every write
- **Concurrency**: Thread-safe via locking primitives

## Architecture

- Depends on: `serialization/` (JSON persistence), `logging_monitoring/` (audit logging)
- Consumed by: All agent modules, MCP server (`store_memory`, `recall_memory`, `list_memories`)

## Error Conditions

| Error | Trigger | Resolution |
|-------|---------|------------|
| `KeyError` | `memory_get()` called with a key that does not exist in the store | Call `memory_list()` first to confirm key existence, or use a try/except guard |
| `StorageError` | Disk full or filesystem permissions prevent `JSONFileStore` from writing | Check available disk space; verify write permissions on the store directory |
| `SerializationError` | Value passed to `memory_put()` is not JSON-serializable (e.g., open file handles, lambdas) | Ensure all values are JSON-serializable; convert custom objects to dicts before storing |
| `ValueError` | Empty string passed as `key` to `memory_put()` or `memory_get()` | Validate that keys are non-empty strings before calling |
| `TypeError` | `limit` parameter to `memory_search()` is not an integer | Cast or validate the limit parameter to `int` before calling |
| `RuntimeError` | Backend store failed to initialize (corrupted JSON file, lock contention) | Delete or repair the store file; restart the process to release stale locks |

## Data Contracts

### `memory_put` Input

```python
# Required parameters
{
    "key": str,          # Non-empty string, max 256 characters
    "value": Any,        # Must be JSON-serializable (str, int, float, bool, list, dict, None)
}
```

### `memory_get` Output

```python
# Returns the stored value directly
Any  # Same type that was stored via memory_put
# Raises KeyError if key does not exist
```

### `memory_search` Input/Output

```python
# Input
{
    "query": str,        # Substring to match against keys and string values
    "limit": int,        # Max results to return; default 10, range [1, 1000]
}

# Output
[
    {
        "key": str,              # Matching key
        "value": Any,            # Stored value
        "score": float,          # Relevance score 0.0-1.0 (1.0 = exact match)
        "matched_field": str,    # "key" or "value" indicating where match was found
    },
    ...
]
```

### `memory_list` Output

```python
# Returns list of all keys
list[str]  # e.g., ["user_preference", "session_42", "last_query"]
```

## Performance SLOs

| Operation | Target Latency | Backend | Notes |
|-----------|---------------|---------|-------|
| `memory_get` | < 1ms | `InMemoryStore` | Direct dict lookup, O(1) |
| `memory_get` | < 10ms | `JSONFileStore` | File read with caching; cache TTL 5s |
| `memory_put` | < 1ms | `InMemoryStore` | Direct dict assignment, O(1) |
| `memory_put` | < 20ms | `JSONFileStore` | Atomic write with fsync |
| `memory_search` | < 50ms | `InMemoryStore` | Linear scan, up to 100,000 entries |
| `memory_search` | < 200ms | `JSONFileStore` | Full file load + scan; cached after first call |
| `memory_list` | < 1ms | Both | Key enumeration only |

**Capacity Limits:**
- Maximum entries per store: 100,000
- Maximum key length: 256 characters
- Maximum value size: 1 MB (JSON-serialized)
- Maximum total store size: 500 MB (`JSONFileStore`)

## Design Constraints

1. **Thread Safety**: All store operations are thread-safe. `InMemoryStore` uses `threading.Lock`; `JSONFileStore` uses file-level locking via `fcntl.flock`.
2. **Idempotency**: `memory_put` with the same key overwrites silently. Repeated puts with identical key-value pairs produce no observable side effects.
3. **No Silent Failures**: `memory_get` raises `KeyError` explicitly; `memory_put` raises `StorageError` on write failure. No fallback to in-memory when disk fails.
4. **JSON-Only Values**: All stored values must survive a `json.dumps` / `json.loads` round-trip. Non-serializable values are rejected at put time, not silently coerced.
5. **Search Semantics**: `memory_search` uses case-insensitive substring matching by default. Results are ranked by match quality (exact > prefix > substring).
6. **No TTL by Default**: Entries persist indefinitely. Callers are responsible for cleanup via explicit deletion or store reset.

## PAI Algorithm Integration

| Phase | Usage | Example |
|-------|-------|---------|
| **OBSERVE** | Recall prior context before making decisions | `memory_get("last_session_context")` to resume work |
| **THINK** | Search related memories to inform reasoning | `memory_search("error patterns", limit=5)` for debugging context |
| **LEARN** | Persist new knowledge and outcomes after task completion | `memory_put("sprint_14_outcome", {"status": "success", ...})` |
| **EXECUTE** | Store intermediate results during long-running tasks | `memory_put("build_step_3", partial_result)` for checkpointing |

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../SPEC.md)
