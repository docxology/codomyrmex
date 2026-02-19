# DEPRECATED(v0.2.0): Shim module. Import from codomyrmex.performance.caching.cache_manager instead. Will be removed in v0.3.0.
"""
Backward-compatibility shim.

This module has been moved to codomyrmex.performance.caching.cache_manager.
All imports are re-exported here for backward compatibility.
"""

from codomyrmex.performance.caching.cache_manager import (  # noqa: F401
    CacheManager,
    cached_function,
    clear_cache,
    get_cache_stats,
)
