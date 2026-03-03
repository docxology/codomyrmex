"""MCP tools for the utils module.

Exposes content hashing, safe JSON parsing, and dict flattening as
auto-discovered MCP tools. Zero external dependencies beyond the
utils module itself.
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


@mcp_tool(
    category="utils",
    description=(
        "Generate a cryptographic hash of text content. "
        "Supports sha256, sha512, and md5 algorithms. "
        "Returns the hex digest string."
    ),
)
def utils_hash_content(content: str, algorithm: str = "sha256") -> str:
    """Hash text content and return the hex digest.

    Args:
        content: Text string to hash.
        algorithm: Hash algorithm (sha256, sha512, md5).

    Returns:
        Hex digest string.
    """
    from codomyrmex.utils import hash_content

    return hash_content(content, algorithm=algorithm)


@mcp_tool(
    category="utils",
    description=(
        "Safely parse a JSON string with a fallback default value. "
        "Returns the parsed Python object, or the default if parsing fails."
    ),
)
def utils_json_loads(text: str, default: Any = None) -> Any:
    """Parse JSON text safely.

    Args:
        text: JSON string to parse.
        default: Fallback value if parsing fails.

    Returns:
        Parsed Python object or default.
    """
    from codomyrmex.utils import safe_json_loads

    return safe_json_loads(text, default=default)


@mcp_tool(
    category="utils",
    description=(
        "Flatten a nested dictionary into a single-level dict with "
        "dot-separated keys (configurable separator)."
    ),
)
def utils_flatten_dict(
    d: dict,
    parent_key: str = "",
    sep: str = ".",
) -> dict:
    """Flatten a nested dictionary.

    Args:
        d: Nested dictionary to flatten.
        parent_key: Prefix for top-level keys.
        sep: Key separator (default '.').

    Returns:
        Flattened dictionary.
    """
    from codomyrmex.utils import flatten_dict

    return flatten_dict(d, parent_key=parent_key, sep=sep)
