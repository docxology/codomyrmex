"""Tag lists for MCP tool discovery and PAI skill manifest indexing."""

from __future__ import annotations

__all__ = ["manifest_tags"]


def manifest_tags(*, category: str, explicit: list[str] | None = None) -> list[str]:
    """Return stable tags for manifest and discovery.

    Non-empty explicit ``tags=`` from :func:`decorators.mcp_tool` wins; otherwise
    tags are derived from *category* (e.g. ``hermes`` → agent + MCP routing).
    """
    if explicit is not None and len(explicit) > 0:
        base = list(explicit)
    elif category == "hermes":
        base = ["hermes", "agent", "mcp"]
    elif category not in ("", "general"):
        base = [category, "mcp"]
    else:
        base = ["mcp"]
    seen: set[str] = set()
    out: list[str] = []
    for t in base:
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    if "mcp" not in seen:
        out.append("mcp")
    return out
