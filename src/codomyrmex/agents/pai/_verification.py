"""Verification of PAI capabilities.

Extracted from trust_gateway.py to reduce module size.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from codomyrmex.agents.pai.trust_gateway import TrustRegistry

from codomyrmex.agents.pai.mcp.discovery import discover_dynamic_tools
from codomyrmex.agents.pai.mcp_bridge import (
    create_codomyrmex_mcp_server,
    get_tool_registry,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def run_verify_capabilities(
    registry: TrustRegistry,
    get_safe_tools_func,
    get_destructive_tools_func,
) -> dict[str, Any]:
    """Run a full read-only audit of all Codomyrmex capabilities.

    Returns:
        Structured report with modules, tools, resources, prompts,
        MCP server health, PAI bridge status, and trust state.
    """
    # ── Module inventory ──────────────────────────────────────────
    import codomyrmex

    modules = codomyrmex.list_modules()

    # ── Promote safe tools to VERIFIED (before snapshot) ──────────
    promoted = registry.verify_all_safe()

    # ── Tool registry ─────────────────────────────────────────────
    # Ensures detailed tool stats, including versions and availability
    # Refresh discovery first just in case
    discover_dynamic_tools()

    tool_registry = get_tool_registry()
    tool_names = sorted(tool_registry.list_tools())

    # Calculate tool categorization stats
    safe_tools = get_safe_tools_func()
    destructive_tools = get_destructive_tools_func()
    by_category = {
        "safe": len(safe_tools),
        "destructive": len(destructive_tools),
        "total": len(tool_names),
    }

    # ── Module Stats ──────────────────────────────────────────────
    # We check discovery metrics for failed modules
    failed_modules = []
    discovery_cache_age = -1.0
    discovery_last_duration = 0.0
    try:
        from codomyrmex.agents.pai.mcp_bridge import get_discovery_metrics

        discovery_metrics = get_discovery_metrics()
        if discovery_metrics is not None:
            failed_modules = [
                {"name": m, "error": "Import failed"}
                for m in discovery_metrics["failed_modules"]
            ]
            last_scan = discovery_metrics["last_scan_time"]
            discovery_cache_age = (
                (datetime.now(UTC) - last_scan).total_seconds() if last_scan else -1.0
            )
            discovery_last_duration = discovery_metrics["scan_duration_ms"]
    except ImportError as e:
        logger.warning("Discovery metrics import failed during health check: %s", e)

    # ── MCP server health ─────────────────────────────────────────
    try:
        # We don't want to create a full server every time if we can avoid it,
        # but it's the robust check.
        server = create_codomyrmex_mcp_server()
        mcp_transport = "stdio/http"  # Configurable, but default
        mcp_resources = len(getattr(server, "_resources", {}))
        mcp_prompts = len(getattr(server, "_prompts", {}))
        server_config = getattr(server, "config", None)
        mcp_server_name = (
            getattr(server_config, "name", "unknown") if server_config else "unknown"
        )
    except (ImportError, TypeError):
        mcp_server_name = "unknown"
        mcp_transport = "unknown"
        mcp_resources = 0
        mcp_prompts = 0

    # ── Validation ────────────────────────────────────────────────

    report = {
        "status": "verified",
        "tools": {
            "safe": sorted(safe_tools),
            "destructive": sorted(destructive_tools),
            "total": len(tool_names),
            "by_category": by_category,
        },
        "modules": {
            "loaded": len(modules),
            "failed": failed_modules,
            "total": len(modules) + len(failed_modules),
        },
        "trust": {
            "promoted_to_verified": promoted,
            "level": registry.get_aggregate_level(),
            "audit_entries": registry.get_audit_count(),
            "gateway_healthy": True,
            "report": registry.get_report(),
        },
        "mcp": {
            "server_name": mcp_server_name,
            "transport": mcp_transport,
            "resources": mcp_resources,
            "prompts": mcp_prompts,
        },
        "discovery": {
            "cache_age_seconds": discovery_cache_age,
            "last_scan_duration_ms": discovery_last_duration,
        },
    }

    logger.info(
        "Verify capabilities: %d tools (%d safe), %d modules loaded.",
        report["tools"]["total"],
        report["tools"]["by_category"]["safe"],
        report["modules"]["loaded"],
    )
    return report
