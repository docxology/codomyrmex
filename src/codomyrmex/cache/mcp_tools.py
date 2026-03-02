"""MCP tools for the cache module.

Exposes get/set/delete/stats operations via the real Cache API.
Uses a module-level CacheManager singleton so data persists across tool calls.
"""

from __future__ import annotations

from typing import Any

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:
    def mcp_tool(**kwargs):
        def decorator(fn):
            fn._mcp_tool_meta = kwargs
            return fn
        return decorator

# Module-level singleton so cache data survives across multiple tool calls.
_manager: Any = None


def _get_manager():
    global _manager
    if _manager is None:
        from codomyrmex.cache import CacheManager
        _manager = CacheManager()
    return _manager


@mcp_tool(
    category="cache",
    description=(
        "Get a value from the named in-memory cache. "
        "Returns the value or None if missing."
    ),
)
def cache_get(key: str, cache_name: str = "default") -> object | None:
    """Retrieve a cached value by key."""
    return _get_manager().get_cache(cache_name).get(key)


@mcp_tool(
    category="cache",
    description=(
        "Store a value in the named in-memory cache with optional TTL (seconds). "
        "Returns True on success."
    ),
)
def cache_set(
    key: str,
    value: object,
    ttl: int | None = None,
    cache_name: str = "default",
) -> bool:
    """Store a value in the cache."""
    _get_manager().get_cache(cache_name).set(key, value, ttl=ttl)
    return True


@mcp_tool(
    category="cache",
    description=(
        "Delete a key from the named in-memory cache. "
        "Returns True if deleted, False if the key did not exist."
    ),
)
def cache_delete(key: str, cache_name: str = "default") -> bool:
    """Delete a key from the cache."""
    return _get_manager().get_cache(cache_name).delete(key)


@mcp_tool(
    category="cache",
    description=(
        "Get hit/miss/eviction statistics for the named in-memory cache. "
        "Returns a dict with hits, misses, hit_rate, size, writes, deletes."
    ),
)
def cache_stats(cache_name: str = "default") -> dict:
    """Return cache statistics as a serializable dict."""
    return _get_manager().get_cache(cache_name).stats.to_dict()
