"""MCP tool definitions for the privacy module.

Exposes CrumbCleaner sanitization and MixnetProxy routing as MCP tools.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_cleaner():
    """Lazy import of CrumbCleaner."""
    from codomyrmex.privacy.crumbs import CrumbCleaner

    return CrumbCleaner()


@mcp_tool(
    category="privacy",
    description=(
        "Scrub tracking metadata (crumbs) from a data structure. "
        "Removes keys like ip_address, device_id, session_id, etc."
    ),
)
def privacy_scrub(data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Remove privacy-sensitive metadata keys from a dictionary.

    Args:
        data: Dictionary to scrub. Nested dicts and lists are handled recursively.

    Returns:
        dict with keys: status, scrubbed (the cleaned data)
    """
    if data is None:
        return {"status": "error", "message": "data is required"}
    try:
        cleaner = _get_cleaner()
        scrubbed = cleaner.scrub(data)
        return {"status": "success", "scrubbed": scrubbed}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="privacy",
    description="List the default blacklisted metadata keys that CrumbCleaner removes.",
)
def privacy_list_blacklist() -> dict[str, Any]:
    """Return the current set of blacklisted metadata key names.

    Returns:
        dict with keys: status, blacklist (sorted list of key names)
    """
    try:
        cleaner = _get_cleaner()
        return {
            "status": "success",
            "blacklist": sorted(cleaner._blacklist),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="privacy",
    description=(
        "Generate cryptographically random noise bytes. "
        "Useful for obscuring activity patterns or padding."
    ),
)
def privacy_generate_noise(size_bytes: int = 64) -> dict[str, Any]:
    """Generate random noise bytes and return as hex string.

    Args:
        size_bytes: Number of random bytes to generate (default: 64).

    Returns:
        dict with keys: status, size_bytes, noise_hex
    """
    if size_bytes <= 0:
        return {"status": "error", "message": "size_bytes must be positive"}
    try:
        cleaner = _get_cleaner()
        noise = cleaner.generate_noise(size_bytes)
        return {
            "status": "success",
            "size_bytes": size_bytes,
            "noise_hex": noise.hex(),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
