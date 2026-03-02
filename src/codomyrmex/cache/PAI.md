# Personal AI Infrastructure — Cache Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Cache module provides multi-backend caching infrastructure with TTL-based expiration, LRU eviction, distributed caching, and cache warming strategies. It sits in the Foundation Layer of the Codomyrmex architecture, meaning it has no upward dependencies and is consumed by higher-layer modules that need fast repeated access to expensive-to-compute or expensive-to-fetch data. The MCP bridge itself relies on this caching pattern internally, using a 5-minute TTL for auto-discovered tool metadata.

## PAI Capabilities

### In-Memory LRU Cache

The default backend for session-scoped, high-frequency access patterns. Uses an `InMemoryCache` with configurable max size and automatic LRU eviction when capacity is reached.

```python
from codomyrmex.cache import CacheManager

mgr = CacheManager(default_ttl=300)  # 5-minute default TTL
cache = mgr.get_cache("llm_responses", backend="in_memory")

# Store an LLM response to avoid redundant API calls
cache.set("prompt:summarize_module:cache", {
    "response": "The cache module provides multi-backend caching...",
    "model": "claude-3-opus",
    "tokens_used": 142,
}, ttl=600)  # 10-minute TTL for this entry

# Retrieve on subsequent requests — returns None if expired
result = cache.get("prompt:summarize_module:cache")
if result is not None:
    print(f"Cache hit — saved {result['tokens_used']} tokens")
```

### Disk-Backed Cache

Persists cache entries to disk as pickle-serialized files with JSON metadata sidecars. Suitable for expensive computation results that should survive process restarts.

```python
from pathlib import Path
from codomyrmex.cache import CacheManager

mgr = CacheManager()
cache = mgr.get_cache("analysis_results", backend="file_based")

# Cache a static analysis result that took 30 seconds to compute
cache.set("analysis:src/codomyrmex/agents", {
    "issues": 12,
    "complexity_score": 7.3,
    "timestamp": "2026-02-24T10:30:00Z",
}, ttl=3600)  # 1-hour TTL

# On next run, check cache before re-running analysis
cached = cache.get("analysis:src/codomyrmex/agents")
if cached is None:
    # Cache miss or expired — run analysis again
    pass
```

### Distributed Cache (Redis-Compatible)

For multi-agent scenarios where multiple PAI agent instances share state. Falls back to in-memory if Redis is unavailable.

```python
from codomyrmex.cache import CacheManager

mgr = CacheManager()
cache = mgr.get_cache("shared_agent_state", backend="redis")

# Agent A writes a shared result
cache.set("task:review:file_list", [
    "src/codomyrmex/cache/cache.py",
    "src/codomyrmex/cache/cache_manager.py",
], ttl=120)

# Agent B reads the shared result
files = cache.get("task:review:file_list")
```

### Namespaced Cache

Isolate cache entries by module or concern using the `NamespacedCache` wrapper. Prevents key collisions across independent subsystems.

```python
from codomyrmex.cache import get_cache, NamespacedCache

base_cache = get_cache("default", backend="in_memory")

llm_cache = NamespacedCache(base_cache, namespace="llm")
rag_cache = NamespacedCache(base_cache, namespace="rag")

# These keys are independent — stored as "llm:query" and "rag:query"
llm_cache.set("query", {"model": "claude-3-opus"})
rag_cache.set("query", {"chunks": 5, "similarity": 0.87})

# Clear only one namespace without affecting the other
llm_cache.clear()
```

### Cache Warming

Pre-populate caches at startup using the `warmers` sub-module. Supports eager, lazy, scheduled, and adaptive strategies with parallel loading and retry logic.

```python
from codomyrmex.cache.warmers import (
    CacheWarmer,
    StaticKeyProvider,
    CallableValueLoader,
    WarmingConfig,
    WarmingStrategy,
)

# Define what to warm and how to load values
keys = StaticKeyProvider(["config:global", "config:agents", "config:llm"])
loader = CallableValueLoader(lambda k: load_config_from_disk(k))

warmer = CacheWarmer(
    cache=my_cache_dict,
    key_provider=keys,
    value_loader=loader,
    config=WarmingConfig(
        strategy=WarmingStrategy.EAGER,
        batch_size=50,
        max_workers=4,
        retry_on_failure=True,
        max_retries=3,
    ),
)

# Warm synchronously and inspect results
stats = warmer.warm()
print(f"Warmed {stats.keys_warmed} keys in {stats.total_time_ms:.1f}ms")
print(f"Success rate: {stats.success_rate:.1%}")

# Or start scheduled warming (re-warms every 5 minutes)
warmer.start_scheduler()
```

### Cache Statistics

Every cache backend exposes a `CacheStats` object with hit/miss counters, eviction tracking, time-windowed hit rates, and per-key frequency analysis.

```python
cache = mgr.get_cache("sessions", backend="in_memory")

# After some usage...
stats = cache.stats
print(stats.text())
# Output: "Cache: 847/1000 hits (84.7%), 312/1000 entries, 23 evictions"

# Time-windowed hit rate (last 60 seconds)
recent_rate = stats.hit_rate_window(seconds=60.0)

# Find hottest keys for adaptive warming
hot_keys = stats.hottest_keys(n=10)
```

### Async Cache Operations

The `async_ops` sub-module provides non-blocking cache access for use in async PAI workflows. This sub-module exposes async wrappers around the synchronous cache interface.

### TTL Manager

The `TTLManager` runs a background daemon thread that periodically sweeps registered caches and removes expired entries, preventing stale data from consuming memory.

```python
from codomyrmex.cache import TTLManager

ttl_mgr = TTLManager(cleanup_interval=60)  # sweep every 60 seconds
ttl_mgr.register_cache(my_cache)           # auto-starts the daemon
```

## Sub-Modules

| Sub-module | Purpose |
|------------|---------|
| `policies` | Eviction policies (LRU, LFU, TTL-only) |
| `invalidation` | Pattern-based and dependency-graph invalidation |
| `distributed` | Redis-compatible distributed backend |
| `serializers` | JSON, pickle, msgpack serializers |
| `warmers` | Startup preloading strategies with parallel loading |
| `async_ops` | Async get/set/invalidate operations |
| `replication` | Cross-node cache replication |

## MCP Tools

No direct MCP tools via `@mcp_tool` decorators. Access cache functionality programmatically or via the `call_module_function` universal proxy tool:

```json
{
  "tool": "call_module_function",
  "arguments": {
    "module": "cache",
    "function": "get_cache",
    "kwargs": {"name": "llm_responses", "backend": "in_memory"}
  }
}
```

## PAI Algorithm Phase Mapping

| Phase | Cache Contribution |
|-------|-------------------|
| **OBSERVE** | Cache codebase scan results, file trees, and git metadata for repeated access within a session |
| **THINK** | Cache intermediate reasoning artifacts and knowledge graph query results via `graph_rag/` integration |
| **PLAN** | Cache dependency resolution results and workflow template lookups to avoid redundant computation |
| **BUILD** | Cache compiled artifacts, AST parse results, and code generation outputs across incremental builds |
| **EXECUTE** | Cache LLM API responses to reduce cost and latency on repeated or similar prompts |
| **VERIFY** | Cache static analysis and test results so repeated VERIFY cycles skip unchanged modules |
| **LEARN** | Persist frequently accessed data as hot memory via `agentic_memory/` integration; warm caches with learned access patterns |

## PAI Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `CACHE_BACKEND` | `in_memory` | Default backend: `in_memory`, `file_based`, or `redis` |
| `REDIS_URL` | `redis://localhost:6379` | Connection URL for the Redis distributed backend |
| `CACHE_TTL_DEFAULT` | `300` | Default TTL in seconds for cache entries (5 minutes) |
| `CACHE_MAX_SIZE` | `1000` | Maximum entries for in-memory LRU cache |
| `CODOMYRMEX_MCP_CACHE_TTL` | `300` | TTL for MCP bridge auto-discovered tool metadata cache (used by `mcp_bridge.py`) |

## PAI Best Practices

1. **Cache LLM API responses to reduce cost in repeated VERIFY runs.** When PAI re-verifies unchanged code, the same prompts hit the same models. A 10-minute TTL on LLM response caches can eliminate 60-80% of redundant API calls during iterative development cycles.

2. **Match cache TTL to data staleness tolerance.** Git metadata changes on every commit (use 30-60s TTL), while static analysis results are stable until code changes (use 10-30min TTL). The MCP bridge uses 5min TTL for tool discovery because module registration changes infrequently.

3. **Use dependency-graph invalidation when source data changes.** Rather than waiting for TTL expiry, invalidate downstream caches when their source data is modified. For example, when a file is edited during BUILD, invalidate its cached analysis results so the next VERIFY phase recomputes them.

4. **Use namespaced caches to isolate concerns.** Each PAI phase or agent type should use its own namespace to prevent key collisions and enable targeted cache clears without disrupting other subsystems.

5. **Monitor cache statistics to tune performance.** A hit rate below 50% suggests the TTL is too aggressive or the key space is too large. Use `stats.hottest_keys()` to identify candidates for cache warming. Use `hit_rate_window()` to detect performance degradation in real time.

6. **Prefer in-memory for single-agent workflows, Redis for multi-agent.** The in-memory backend has zero serialization overhead and sub-microsecond access. Only use the distributed backend when multiple PAI agent instances need to share state.

## Architecture Role

**Foundation Layer** -- No external module dependencies. The cache module is consumed by:

- `performance/` -- `CacheManager` for benchmark result caching
- `llm/` -- Response caching to reduce redundant API calls
- `graph_rag/` -- Query result caching for knowledge graph lookups
- `agentic_memory/` -- Hot memory tier for frequently accessed context
- `agents/pai/mcp_bridge.py` -- 5-minute TTL cache for auto-discovered MCP tool metadata

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
