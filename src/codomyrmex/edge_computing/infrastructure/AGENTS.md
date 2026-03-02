# edge_computing/infrastructure — Agent Coordination

## Purpose

Provides the infrastructure services layer for edge computing: local caching, health monitoring with flap detection, invocation metrics aggregation, and bidirectional edge-cloud state synchronization.

## Key Components

| Component | Role |
|-----------|------|
| `EdgeCache` | Thread-safe LRU cache with TTL expiration, hit/miss tracking, and eviction (least-accessed or expired-first) |
| `CacheEntry` | Single cached value with TTL, creation timestamp, and access counter |
| `HealthMonitor` | Heartbeat-based health checker with per-node history, cluster reports, and flap detection |
| `HealthCheck` | Result of a single health probe: healthy flag, latency, details dict |
| `EdgeMetrics` | Invocation record aggregator: total counts, success rate, average latency, error count with optional function/node filtering |
| `InvocationRecord` | Single invocation record: function_id, node_id, duration_ms, success, error |
| `EdgeSynchronizer` | Bidirectional state sync with configurable conflict resolution, change batching, and sync history |
| `ConflictStrategy` | Enum: `REMOTE_WINS`, `LOCAL_WINS`, `LATEST_WINS` |
| `SyncEvent` | Record of a push/pull sync operation |

## Operating Contracts

- `EdgeCache.get(key)` returns `None` on miss or expiry; auto-deletes expired entries on access. Thread-safe via `threading.Lock`.
- `EdgeCache.put(key, value, ttl)` triggers eviction when `max_size` reached (expired-first, then least-accessed).
- `HealthMonitor.check_node(node)` evaluates health via heartbeat age against configurable timeout. Retains up to 100 checks per node.
- `HealthMonitor.detect_flapping(node_id, window)` returns True if 3+ healthy/unhealthy state transitions within the check window.
- `EdgeMetrics.total_invocations(function_id, node_id)` supports optional filtering by function and/or node.
- `EdgeSynchronizer.apply_remote(state)` uses the configured `ConflictStrategy` to decide whether to accept remote state.
- `EdgeSynchronizer.confirm_sync(version)` removes pending changes up to the given version.

## Integration Points

- **Core models**: Uses `EdgeNode`, `EdgeNodeStatus`, `SyncState` from `edge_computing.core.models`.
- **Runtime**: `InvocationRecord` parallels `InvocationMetrics` from `core.runtime` for cross-node aggregation.
- **Scheduling**: Scheduler jobs can trigger sync or cache operations.

## Navigation

- **Parent**: [edge_computing README](../../edge_computing/README.md)
- **Siblings**: [core](../core/AGENTS.md) | [scheduling](../scheduling/AGENTS.md)
- **Spec**: [SPEC.md](SPEC.md)
