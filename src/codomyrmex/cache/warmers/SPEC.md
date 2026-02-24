# Technical Specification - Warmers

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.cache.warmers`  
**Last Updated**: 2026-01-29

## 1. Purpose

Cache pre-population and predictive caching strategies

## 2. Architecture

### 2.1 Components

```
warmers/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `cache`

## 3. Interfaces

### 3.1 Public API

```python
# Primary exports from codomyrmex.cache.warmers
from codomyrmex.cache.warmers import (
    WarmingStrategy,       # Enum: EAGER, LAZY, SCHEDULED, ADAPTIVE
    WarmingConfig,         # Dataclass for warming configuration (batch_size, workers, intervals)
    WarmingStats,          # Dataclass for warming statistics (keys_warmed, success_rate)
    KeyProvider,           # ABC for providing keys to warm
    StaticKeyProvider,     # Provide a static list of keys
    CallableKeyProvider,   # Provide keys from a callable
    AdaptiveKeyProvider,   # Provide keys based on access patterns via AccessTracker
    ValueLoader,           # ABC for loading values by key
    CallableValueLoader,   # Load values using a callable
    BatchValueLoader,      # Load values in batches for efficiency
    CacheWarmer,           # Main warmer: orchestrates key providers, loaders, and caching
    AccessTracker,         # Track cache access patterns for adaptive warming
)

# Key class signatures:
class WarmingConfig:
    strategy: WarmingStrategy       # Default: LAZY
    batch_size: int                 # Default: 100
    max_workers: int                # Default: 4
    refresh_interval_s: float       # Default: 300.0
    warmup_timeout_s: float         # Default: 60.0
    retry_on_failure: bool          # Default: True
    max_retries: int                # Default: 3

class CacheWarmer(Generic[K, V]):
    def __init__(self, cache: dict[K, V], key_provider: KeyProvider[K],
                 value_loader: ValueLoader[K, V], config: WarmingConfig | None = None): ...
    def warm(self, keys: list[K] | None = None) -> WarmingStats: ...
    def warm_async(self, keys: list[K] | None = None) -> concurrent.futures.Future: ...
    def warm_key(self, key: K) -> bool: ...
    def start_scheduler(self) -> None: ...
    def stop_scheduler(self) -> None: ...

class AccessTracker(Generic[K]):
    def __init__(self, max_keys: int = 10000): ...
    def record_access(self, key: K) -> None: ...
    def get_access_count(self, key: K) -> int: ...
    def get_hot_keys(self, threshold: int = 5, limit: int = 100) -> list[K]: ...
    def get_recent_keys(self, seconds: float = 300.0, limit: int = 100) -> list[K]: ...
    def clear(self) -> None: ...
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Strategy pattern for key providers and value loaders**: Abstract base classes (`KeyProvider`, `ValueLoader`) allow pluggable data sources without modifying the core `CacheWarmer`.
2. **Parallel warming with thread pool**: Uses `concurrent.futures.ThreadPoolExecutor` with configurable worker count and exponential backoff retries.
3. **Adaptive warming via AccessTracker**: Tracks access frequency and recency to automatically determine which keys to pre-warm, avoiding unnecessary cache population.

### 4.2 Limitations

- Known limitation 1
- Known limitation 2

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/cache/warmers/
```

## 6. Future Considerations

- Add priority-weighted warming to bias towards high-value keys
- Implement warming progress callbacks and cancellation support
- Add TTL-aware warming that pre-warms keys before their cache entries expire
