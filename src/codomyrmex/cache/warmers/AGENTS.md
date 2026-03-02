# Codomyrmex Agents — src/codomyrmex/cache/warmers

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Cache pre-population framework with pluggable key providers, value loaders, parallel and batch warming, scheduled refresh via background thread, and adaptive warming based on access pattern tracking.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `CacheWarmer` (Generic[K, V]) | Orchestrates warming: synchronous, async, batch, parallel, and scheduled modes |
| `__init__.py` | `KeyProvider` (ABC) | Abstract base for providing keys to warm |
| `__init__.py` | `StaticKeyProvider` | Provides a fixed list of keys |
| `__init__.py` | `CallableKeyProvider` | Provides keys from a callable function |
| `__init__.py` | `AdaptiveKeyProvider` | Provides keys from `AccessTracker` hot-key analysis |
| `__init__.py` | `ValueLoader` (ABC) | Abstract base for loading values by key |
| `__init__.py` | `CallableValueLoader` | Loads values using a single-key callable |
| `__init__.py` | `BatchValueLoader` | Loads values in batches via a `dict[K, V]`-returning callable |
| `__init__.py` | `AccessTracker` (Generic[K]) | Tracks access frequency and recency for adaptive warming |
| `__init__.py` | `WarmingConfig` | Configuration dataclass: strategy, batch_size, max_workers, intervals, retries |
| `__init__.py` | `WarmingStats` | Statistics dataclass: keys_warmed, keys_failed, total_time_ms, success_rate |
| `__init__.py` | `WarmingStrategy` | Enum: EAGER, LAZY, SCHEDULED, ADAPTIVE |

## Operating Contracts

- `CacheWarmer.warm()` is idempotent; concurrent calls are serialized via lock.
- Parallel warming uses `ThreadPoolExecutor` with configurable `max_workers` and exponential backoff retries.
- `BatchValueLoader` caches loaded values internally for single-key fallback via `load()`.
- `AccessTracker` trims the oldest half of keys when exceeding `max_keys` capacity.
- `start_scheduler()` runs a daemon thread that calls `warm()` at `refresh_interval_s` intervals.
- Errors must be logged before re-raising.

## Integration Points

- **Depends on**: Standard library only (`concurrent.futures`, `threading`, `time`, `logging`)
- **Used by**: `cache` parent module, application startup, scheduled cache refresh

## Navigation

- **Parent**: [cache](../README.md)
- **Root**: [Root](../../../../README.md)
