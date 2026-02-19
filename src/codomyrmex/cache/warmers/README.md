# warmers

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Cache pre-population and warming strategies. Provides a `CacheWarmer` that populates a cache dict from pluggable key providers and value loaders, with support for parallel loading, batch loading, scheduled refresh, and async warming. Includes an `AccessTracker` for monitoring cache access patterns and an `AdaptiveKeyProvider` that uses access frequency data to decide which keys to warm.

## Key Exports

- **`WarmingStrategy`** -- Enum of warming strategies (eager, lazy, scheduled, adaptive)
- **`WarmingConfig`** -- Configuration dataclass for warming behavior: strategy, batch size, max workers, refresh interval, timeout, retry settings
- **`WarmingStats`** -- Statistics dataclass tracking keys warmed, keys failed, total time, last warming timestamp, errors, and success rate
- **`KeyProvider`** -- Abstract base class for providing lists of keys to warm
- **`StaticKeyProvider`** -- Key provider that returns a fixed list of keys
- **`CallableKeyProvider`** -- Key provider that invokes a callable to get keys dynamically
- **`AdaptiveKeyProvider`** -- Key provider backed by an `AccessTracker` that returns frequently accessed (hot) keys
- **`ValueLoader`** -- Abstract base class for loading a value given a key
- **`CallableValueLoader`** -- Value loader that delegates to a callable
- **`BatchValueLoader`** -- Value loader optimized for batch operations; accepts a function that maps a list of keys to a dict of results
- **`CacheWarmer`** -- Core warmer class that populates a cache dict using key providers and value loaders with parallel/batch execution, scheduled refresh via a background thread, and async warming via a thread-pool future
- **`AccessTracker`** -- Thread-safe tracker that records per-key access counts and timestamps, supports querying hot keys by frequency threshold and recent keys by time window, with automatic trimming

## Directory Contents

- `__init__.py` - All warming logic: strategies, key providers, value loaders, cache warmer, access tracker
- `README.md` - This file
- `AGENTS.md` - Agent integration notes
- `PAI.md` - PAI-specific documentation
- `SPEC.md` - Module specification
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [cache](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
