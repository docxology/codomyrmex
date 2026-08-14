"""MCP navigation tools for agent and capability operability."""

from typing import Any, cast

from codomyrmex.model_context_protocol.decorators import mcp_tool

from .catalog import CapabilityKind, build_capability_catalog


def _include_tools(kind: str | None, include_tools: bool) -> bool:
    """Include tools automatically when the caller explicitly asks for them."""
    if not isinstance(include_tools, bool):
        raise ValueError("include_tools must be a boolean")
    return include_tools or kind == "tool"


def _invalid_input(exc: ValueError, *, code: str = "INVALID_INPUT") -> dict[str, Any]:
    """Return one stable error shape for malformed navigation requests."""
    return {"status": "error", "error_code": code, "message": str(exc)}


@mcp_tool(category="agents", tags=["navigation", "discovery", "read-only"])
def list_agent_capabilities(
    kind: str | None = None,
    limit: int = 100,
    include_tools: bool = False,
    include_unavailable: bool = False,
) -> dict[str, Any]:
    """List stable agent, module, and optionally MCP tool capability records."""
    try:
        catalog = build_capability_catalog(
            include_tools=_include_tools(kind, include_tools)
        )
        records = catalog.list(
            kind=cast("CapabilityKind | None", kind),
            limit=limit,
            include_unavailable=include_unavailable,
        )
        return {
            "status": "success",
            "capabilities": [record.to_dict() for record in records],
            "count": len(records),
            "summary": catalog.summary(),
        }
    except ValueError as exc:
        code = "INVALID_KIND" if "kind" in str(exc) else "INVALID_INPUT"
        return _invalid_input(exc, code=code)


@mcp_tool(category="agents", tags=["navigation", "search", "read-only"])
def search_agent_capabilities(
    query: str,
    kind: str | None = None,
    limit: int = 20,
    include_tools: bool = False,
    include_unavailable: bool = False,
) -> dict[str, Any]:
    """Search capability names, descriptions, source paths, and tags."""
    try:
        catalog = build_capability_catalog(
            include_tools=_include_tools(kind, include_tools)
        )
        records = catalog.search(
            query,
            kind=cast("CapabilityKind | None", kind),
            limit=limit,
            include_unavailable=include_unavailable,
        )
        return {
            "status": "success",
            "query": query,
            "capabilities": [record.to_dict() for record in records],
            "count": len(records),
            "summary": catalog.summary(),
        }
    except ValueError as exc:
        if "kind" in str(exc):
            code = "INVALID_KIND"
        elif "query" in str(exc):
            code = "INVALID_QUERY"
        else:
            code = "INVALID_INPUT"
        return _invalid_input(exc, code=code)


@mcp_tool(category="agents", tags=["navigation", "discovery", "read-only"])
def get_agent_capability(
    capability_id: str,
    kind: str | None = None,
    include_tools: bool = False,
) -> dict[str, Any]:
    """Return one capability by stable ID such as ``agent:claude``."""
    try:
        wants_tools = isinstance(
            capability_id, str
        ) and capability_id.strip().startswith("tool:")
        catalog = build_capability_catalog(
            include_tools=_include_tools(kind, include_tools) or wants_tools
        )
        matches = catalog.find(capability_id, kind=cast("CapabilityKind | None", kind))
    except ValueError as exc:
        if "kind" in str(exc):
            code = "INVALID_KIND"
        elif "include_tools" in str(exc):
            code = "INVALID_INPUT"
        else:
            code = "INVALID_CAPABILITY_ID"
        return _invalid_input(exc, code=code)
    if len(matches) > 1:
        return {
            "status": "error",
            "error_code": "CAPABILITY_ID_AMBIGUOUS",
            "capability_id": capability_id,
            "candidates": [record.id for record in matches],
            "summary": catalog.summary(),
        }
    record = matches[0] if matches else None
    if record is None:
        return {
            "status": "error",
            "error_code": "CAPABILITY_NOT_FOUND",
            "capability_id": capability_id,
            "summary": catalog.summary(),
        }
    return {"status": "success", "capability": record.to_dict()}


@mcp_tool(category="agents", tags=["operability", "status", "read-only"])
def agent_operability_status(include_tools: bool = False) -> dict[str, Any]:
    """Report catalog health without network probes or agent execution."""
    try:
        catalog = build_capability_catalog(include_tools=include_tools)
        agent_records = catalog.list(kind="agent", limit=500, include_unavailable=True)
    except ValueError as exc:
        return _invalid_input(exc)
    summary = catalog.summary()
    implementation_present_agents = sum(
        record.status == "implementation_present" for record in agent_records
    )
    return {
        "status": ("success" if summary["catalog_state"] == "ready" else "degraded"),
        "probe_policy": "no live probes performed",
        "implementation_present_agents": implementation_present_agents,
        "dispatchability_verified": False,
        "verified_dispatchable_agents": 0,
        "dispatchability_note": (
            "implementation metadata only; configuration, construction, and health "
            "remain unverified"
        ),
        "declared_agents": len(agent_records),
        "summary": summary,
    }


__all__ = [
    "agent_operability_status",
    "get_agent_capability",
    "list_agent_capabilities",
    "search_agent_capabilities",
]
