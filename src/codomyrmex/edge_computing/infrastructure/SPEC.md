# edge_computing/infrastructure — Technical Specification

## Overview

Four modules providing infrastructure services for edge nodes: local caching (`cache.py`), health monitoring (`health.py`), metrics aggregation (`metrics.py`), and state synchronization (`sync.py`).

## Architecture

Each module is self-contained with its own dataclass models. Thread safety is provided via `threading.Lock` in `EdgeCache` and `EdgeSynchronizer`. All modules expose a `summary()` method returning a status dict.

## Key Classes

### EdgeCache (cache.py)

| Method | Signature | Returns |
|--------|-----------|---------|
| `get` | `(key: str)` | `Any \| None` |
| `put` | `(key: str, value: Any, ttl: float \| None)` | None |
| `delete` | `(key: str)` | `bool` |
| `clear` | `()` | `int` (removed count) |
| `purge_expired` | `()` | `int` (expired count) |
| `stats` | `()` | `dict` (size, hits, misses, hit_rate) |

Constructor: `EdgeCache(max_size=1000, default_ttl=300.0)`. Eviction strategy: expired entries first, then least-accessed (`min` by `access_count`).

### HealthMonitor (health.py)

| Method | Signature | Returns |
|--------|-----------|---------|
| `check_node` | `(node: EdgeNode)` | `HealthCheck` |
| `check_cluster` | `(nodes: list[EdgeNode])` | `dict` (cluster health report) |
| `get_history` | `(node_id: str, limit: int)` | `list[HealthCheck]` |
| `detect_flapping` | `(node_id: str, window: int)` | `bool` |

Constructor: `HealthMonitor(heartbeat_timeout_seconds=60.0)`. History capped at 100 entries per node. Flap detection threshold: 3+ transitions in `window` checks.

### EdgeMetrics (metrics.py)

| Method | Signature | Returns |
|--------|-----------|---------|
| `record` | `(record: InvocationRecord)` | None |
| `total_invocations` | `(function_id=None, node_id=None)` | `int` |
| `success_rate` | `(function_id=None)` | `float` (0-100) |
| `avg_latency_ms` | `(function_id=None)` | `float` |
| `error_count` | `(node_id=None)` | `int` |

### EdgeSynchronizer (sync.py)

| Method | Signature | Returns |
|--------|-----------|---------|
| `update_local` | `(data: dict)` | `SyncState` |
| `apply_remote` | `(state: SyncState)` | `bool` (applied?) |
| `get_pending_changes` | `()` | `list[dict]` |
| `confirm_sync` | `(up_to_version: int)` | `int` (removed count) |
| `sync_history` | `(limit: int)` | `list[SyncEvent]` |

Constructor: `EdgeSynchronizer(conflict_strategy=REMOTE_WINS, max_pending=100)`. Properties: `local_version`, `remote_version`, `pending_count`, `is_synced`.

## Dependencies

- `edge_computing.core.models`: `EdgeNode`, `EdgeNodeStatus`, `SyncState`
- Standard library: `threading`, `time`, `datetime`, `enum`, `dataclasses`

## Constraints

- All storage is in-memory; no disk persistence.
- `EdgeCache` eviction is O(n) over stored entries.
- `HealthMonitor` uses naive datetime (no timezone) for heartbeat comparison.
