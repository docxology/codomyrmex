"""MCP tools for the free_apis submodule.

Exposes free API discovery and invocation as MCP tools.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool

from .client import FreeAPIClient
from .registry import FreeAPIRegistry

_registry = FreeAPIRegistry()


@mcp_tool(category="api")
def free_api_list_categories() -> dict[str, Any]:
    """list all categories available in the public free APIs registry.

    Fetches the public-apis index (cached for 1 hour) and returns a
    sorted list of unique categories with entry counts.

    Returns:
        Dictionary with ``status``, ``category_count``, and ``categories``
        list of ``{name, count}`` objects.
    """
    try:
        _registry.fetch()
        categories = _registry.get_categories()
        return {
            "status": "success",
            "source": _registry.source.value if _registry.source else "unknown",
            "category_count": len(categories),
            "categories": [c.to_dict() for c in categories],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(category="api")
def free_api_search(
    query: str = "",
    category: str = "",
    auth_type: str = "",
    https_only: bool = False,
) -> dict[str, Any]:
    """Search and filter the free public APIs registry.

    Args:
        query: Substring to match against API name and description.
        category: Restrict results to this category (case-insensitive).
        auth_type: Filter by auth requirement: "", "apiKey", "OAuth", "X-Mashape-Key", etc.
        https_only: When True, return only HTTPS-enabled APIs.

    Returns:
        Dictionary with ``status``, ``count``, and ``entries`` list.
    """
    try:
        _registry.fetch()
        entries = _registry.entries

        if category:
            entries = [e for e in entries if e.category.lower() == category.lower()]
        if auth_type != "":
            entries = [e for e in entries if e.auth == auth_type]
        if https_only:
            entries = [e for e in entries if e.https]
        if query:
            q = query.lower()
            entries = [
                e for e in entries if q in e.name.lower() or q in e.description.lower()
            ]

        return {
            "status": "success",
            "count": len(entries),
            "entries": [e.to_dict() for e in entries],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(category="api")
def free_api_call(
    url: str,
    method: str = "GET",
    params: str = "",
    headers: str = "",
    timeout: int = 10,
) -> dict[str, Any]:
    """Call a free public API endpoint.

    Args:
        url: Full URL of the API endpoint to call.
        method: HTTP method (GET, POST, etc.). Default: ``GET``.
        params: Query parameters as ``key=value`` pairs, comma-separated
                (e.g. ``"limit=10,offset=0"``).
        headers: Extra request headers as ``Key: Value`` pairs, semicolon-separated
                 (e.g. ``"Accept: application/json; X-Custom: foo"``).
        timeout: Request timeout in seconds. Default: 10.

    Returns:
        Dictionary with ``status``, ``status_code``, ``body_text``, and ``headers``.
    """
    try:
        parsed_params = _parse_kv_pairs(params, ",", "=") if params.strip() else None
        parsed_headers = (
            _parse_kv_pairs(headers, ";", ": ") if headers.strip() else None
        )
        client = FreeAPIClient(default_timeout=timeout)
        result = client.call(
            url, method=method, params=parsed_params, headers=parsed_headers
        )
        return {
            "status": "success",
            "status_code": result.status_code,
            "body_text": result.body_text,
            "headers": result.headers,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def _parse_kv_pairs(text: str, pair_sep: str, kv_sep: str) -> dict[str, str]:
    """Parse a separated key-value string into a dict."""
    result: dict[str, str] = {}
    for pair in text.split(pair_sep):
        pair = pair.strip()
        if kv_sep in pair:
            k, v = pair.split(kv_sep, 1)
            result[k.strip()] = v.strip()
    return result


__all__ = [
    "free_api_call",
    "free_api_list_categories",
    "free_api_search",
]
