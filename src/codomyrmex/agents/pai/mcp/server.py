"""MCP server setup and execution."""

import json
import time
from typing import Any

from codomyrmex.logging_monitoring import get_logger

from .definitions import _PROMPT_DEFINITIONS, _RESOURCE_DEFINITIONS, _TOOL_DEFINITIONS
from .discovery import _discover_dynamic_tools
from .proxy_tools import _get_package_version, _tool_pai_status

logger = get_logger(__name__)


class _ToolRegistry:
    """Lightweight in-process tool registry (replaces MCPToolRegistry from mcp SDK)."""

    def __init__(self) -> None:
        self._tools: dict[str, dict[str, Any]] = {}

    def register(self, *, tool_name: str, schema: dict[str, Any], handler: Any) -> None:
        self._tools[tool_name] = {"schema": schema, "handler": handler, "name": tool_name}

    def list_tools(self) -> list[str]:
        return sorted(self._tools)

    def get(self, name: str) -> dict[str, Any] | None:
        return self._tools.get(name)

    def get_tool(self, name: str) -> dict[str, Any] | None:
        return self._tools.get(name)


def get_tool_registry() -> _ToolRegistry:
    """Build a registry populated with all Codomyrmex tools (static + dynamic).

    Returns:
        A :class:`_ToolRegistry` with core static tools + dynamically discovered module tools.
    """
    registry = _ToolRegistry()

    # 1. Register Core Static Tools
    for name, description, handler, input_schema in _TOOL_DEFINITIONS:
        registry.register(
            tool_name=name,
            schema={
                "name": name,
                "description": description,
                "inputSchema": input_schema,
            },
            handler=handler,
        )

    # 2. Register Dynamic Module Tools
    dynamic_tools = _discover_dynamic_tools()
    for name, description, handler, input_schema in dynamic_tools:
        registry.register(
            tool_name=name,
            schema={
                "name": name,
                "description": description,
                "inputSchema": input_schema,
            },
            handler=handler,
        )

    return registry

def create_codomyrmex_mcp_server(
    *,
    name: str = "codomyrmex-mcp-server",
    transport: str = "stdio",
):
    """Create a fully-configured MCP server with all Codomyrmex capabilities.

    Args:
        name: Server identity name.
        transport: ``"stdio"`` or ``"http"``.

    Returns:
        An MCPServer ready to ``run()``.
    """
    from codomyrmex.model_context_protocol.transport.server import (  # noqa: PLC0415 — lazy import
        MCPServer,
        MCPServerConfig,
    )
    config = MCPServerConfig(name=name, transport=transport)
    server = MCPServer(config=config)

    # ── Warm-up: eagerly populate discovery cache ─────────────────
    if config.warm_up:
        t0 = time.monotonic()
        _discover_dynamic_tools()
        warm_ms = (time.monotonic() - t0) * 1000
        logger.info("Discovery warm-up completed in %.0fms", warm_ms)

    # ── Register tools (Static + Dynamic) ──────────────────────────
    registry = get_tool_registry()
    # The server uses its own internal registry, so we copy over
    # (or ideally server accepts a pre-built registry, but standard pattern confirms manual reg)

    for tool_name in registry.list_tools():
        tool = registry.get_tool(tool_name)
        if tool:
            server.register_tool(
                name=tool_name,
                schema=tool["schema"],
                handler=tool["handler"],
            )

    # ── Register resources ────────────────────────────────────────
    for uri, res_name, res_desc, mime in _RESOURCE_DEFINITIONS:
        if uri == "codomyrmex://modules":
            def _modules_provider() -> str:
                import codomyrmex
                return json.dumps({"modules": codomyrmex.list_modules()})
            provider = _modules_provider
        elif uri == "codomyrmex://status":
            def _status_provider() -> str:
                return json.dumps(_tool_pai_status())
            provider = _status_provider
        else:
            provider = None

        server.register_resource(
            uri=uri,
            name=res_name,
            description=res_desc,
            mime_type=mime,
            content_provider=provider,
        )

    # ── Register prompts ──────────────────────────────────────────
    for prompt_name, prompt_desc, prompt_args, template in _PROMPT_DEFINITIONS:
        server.register_prompt(
            name=prompt_name,
            description=prompt_desc,
            arguments=prompt_args,
            template=template,
        )

    # ── Register discovery metrics resource ────────────────────────
    def _discovery_metrics_provider() -> str:
        from codomyrmex.model_context_protocol.discovery import MCPDiscovery as _Disc
        disc = _Disc()
        m = disc.get_metrics()
        return json.dumps({
            "total_tools": m.total_tools,
            "scan_duration_ms": m.scan_duration_ms,
            "failed_modules": m.failed_modules,
            "modules_scanned": m.modules_scanned,
            "cache_hits": m.cache_hits,
            "last_scan_time": m.last_scan_time.isoformat() if m.last_scan_time else None,
        })

    server.register_resource(
        uri="codomyrmex://discovery/metrics",
        name="Discovery Metrics",
        description="Runtime metrics from MCP tool discovery (scan time, failures, cache hits).",
        mime_type="application/json",
        content_provider=_discovery_metrics_provider,
    )

    logger.info(
        "Codomyrmex MCP server created: %d tools, %d resources, %d prompts",
        len(server._tool_registry.list_tools()),
        len(server._resources),
        len(server._prompts),
    )
    return server

def call_tool(name: str, **kwargs: Any) -> dict[str, Any]:
    """Call a Codomyrmex MCP tool directly (no MCP protocol overhead).

    This is the fastest way to invoke tools from Python code.
    Supports both static core tools and dynamically discovered module tools.

    Delegates to ``trust_gateway.trusted_call_tool`` to ensure:
    1. Authorization policies are enforced.
    2. Audit logs are recorded.
    3. Destructive actions are confirmed.

    Args:
        name: Tool name (e.g. ``"codomyrmex.list_modules"``).
        **kwargs: Tool arguments.

    Returns:
        Tool result dictionary.  On error, returns a dict with
        ``"error"`` key containing a structured :class:`MCPToolError` dict.

    Raises:
        KeyError: If the tool name is not registered.
    """
    from codomyrmex.agents.pai.trust_gateway import SecurityError, trusted_call_tool
    from codomyrmex.logging_monitoring.core.correlation import with_correlation
    from codomyrmex.model_context_protocol.errors import (
        MCPErrorCode,
        MCPToolError,
        execution_error,
    )

    # Check if tool is known first to match original behavior's KeyError
    # (trusted_call_tool will also check, but let's be explicit about "registration" vs "trust")
    # Actually trusted_call_tool handles this via get_tool_registry() lookup.

    with with_correlation():
        try:
            return trusted_call_tool(name, **kwargs)
        except KeyError:
            # Re-raise KeyError to maintain contract if tool not found
            all_static = sorted(t[0] for t in _TOOL_DEFINITIONS)
            raise KeyError(f"Unknown tool: {name!r}. Available (static): {all_static}") from None
        except SecurityError as exc:
            return {"error": MCPToolError(
                code=MCPErrorCode.ACCESS_DENIED,
                message=str(exc),
                tool_name=name
            ).to_dict()}
        except ValueError as exc:
            from codomyrmex.model_context_protocol.errors import validation_error
            return {"error": validation_error(
                tool_name=name,
                message=str(exc)
            ).to_dict()}
        except TimeoutError as exc:
            return {"error": MCPToolError(
                code=MCPErrorCode.TIMEOUT,
                message=str(exc),
                tool_name=name,
            ).to_dict()}
        except Exception as exc:
            # Wrap other execution errors
            module_hint = name.split(".")[1] if "." in name else name
            return {"error": execution_error(
                name, exc, module=module_hint
            ).to_dict()}

def get_skill_manifest() -> dict[str, Any]:
    """Return a PAI-compatible skill manifest for Codomyrmex.

    This can be consumed by PAI's skill routing system to understand
    what capabilities Codomyrmex provides.

    Returns:
        Dictionary with skill metadata, tools, workflows, and knowledge scope.
    """
    # Start with static schema
    static_tools = [
        {
            "name": t[0],
            "description": t[1],
            "category": t[0].split(".")[1] if "." in t[0] else "general",
            "input_schema": t[3],
        }
        for t in _TOOL_DEFINITIONS
    ]

    # Merge dynamic tools
    dynamic_list = _discover_dynamic_tools()
    dynamic_tools = []
    for t in dynamic_list:
        name, description, handler, input_schema = t
        # Extract category from @mcp_tool metadata on the handler
        category = "general"
        if handler and hasattr(handler, "_mcp_tool_meta"):
            category = handler._mcp_tool_meta.get("category", "general")
        if category == "general" and "." in name:
            # Fallback: derive from dotted tool name prefix
            category = name.split(".")[1]
        dynamic_tools.append({
            "name": name,
            "description": description,
            "category": category,
            "input_schema": input_schema,
        })

    # Deduplicate: dynamic tools override static when names collide
    seen: dict[str, dict[str, Any]] = {}
    for t in static_tools:
        seen[t["name"]] = t
    for t in dynamic_tools:
        seen[t["name"]] = t  # dynamic wins
    all_tools = sorted(seen.values(), key=lambda t: t["name"])

    return {
        "name": "Codomyrmex",
        "version": _get_package_version(),
        "description": (
            "Modular coding workspace exposing 100+ modules for AI-assisted "
            "development, code analysis, testing, documentation, and automation."
        ),
        "upstream": "https://github.com/docxology/codomyrmex",
        "mcp_server": "codomyrmex-mcp-server",
        "tools": all_tools,
        "resources": [
            {"uri": r[0], "name": r[1], "description": r[2]}
            for r in _RESOURCE_DEFINITIONS
        ],
        "prompts": [
            {"name": p[0], "description": p[1]}
            for p in _PROMPT_DEFINITIONS
        ],
        "workflows": [
            {
                "name": "codomyrmexVerify",
                "steps": [
                    "codomyrmex.pai_status",
                    "verify_capabilities()",
                ],
                "description": "Verify all Codomyrmex capabilities",
            },
            {
                "name": "codomyrmexTrust",
                "steps": [
                    "trust_all()",
                ],
                "description": "Trust Codomyrmex tools for full execution",
            },
            {
                "name": "analyze_and_test",
                "steps": [
                    "codomyrmex.list_modules",
                    "codomyrmex.module_info",
                    "codomyrmex.analyze_python",
                    "codomyrmex.run_tests",
                ],
                "description": "Discover → Analyze → Test a module",
            },
            {
                "name": "code_review",
                "steps": [
                    "codomyrmex.git_status",
                    "codomyrmex.git_diff",
                    "codomyrmex.search_codebase",
                    "codomyrmex.analyze_python",
                ],
                "description": "Review changes via git status → diff → search → analysis",
            },
            {
                "name": "pai_health_check",
                "steps": [
                    "codomyrmex.pai_status",
                    "codomyrmex.pai_awareness",
                    "codomyrmex.list_modules",
                ],
                "description": "Full PAI + Codomyrmex health assessment",
            },
        ],
        "algorithm_mapping": {
            "OBSERVE": ["codomyrmex.list_modules", "codomyrmex.module_info", "codomyrmex.list_directory"],
            "THINK": ["codomyrmex.analyze_python", "codomyrmex.search_codebase"],
            "PLAN": ["codomyrmex.read_file", "codomyrmex.json_query"],
            "BUILD": ["codomyrmex.write_file"],
            "EXECUTE": ["codomyrmex.run_command", "codomyrmex.run_tests"],
            "VERIFY": ["codomyrmex.git_status", "codomyrmex.git_diff", "codomyrmex.checksum_file"],
            "LEARN": ["codomyrmex.pai_awareness", "codomyrmex.pai_status"],
        },
        "knowledge_scope": {
            "core_infrastructure": [
                "logging_monitoring", "config_management", "environment_setup",
                "events", "exceptions", "utils", "schemas", "concurrency",
                "compression", "serialization", "streaming",
            ],
            "ai_and_agents": [
                "agents", "llm", "model_context_protocol", "orchestrator",
                "prompt_engineering", "cerebrum", "agentic_memory",
                "inference_optimization", "model_ops", "model_registry",
                "model_evaluation", "prompt_testing",
            ],
            "code_and_analysis": [
                "coding", "static_analysis", "tree_sitter", "documentation",
                "git_operations", "build_synthesis", "testing", "validation",
                "pattern_matching", "dependency_injection",
            ],
            "data_and_processing": [
                "database_management", "vector_store", "cache", "data_lineage",
                "data_visualization", "graph_rag", "feature_store",
                "feature_flags", "search", "documents", "fpf", "scrape",
            ],
            "security_and_identity": [
                "security", "auth", "encryption", "privacy", "defense",
                "identity", "wallet", "governance",
            ],
            "infrastructure_and_ops": [
                "cloud", "containerization", "deployment", "ci_cd_automation",
                "networking", "telemetry", "performance", "metrics",
                "edge_computing", "service_mesh", "scheduler", "rate_limiting",
                "cost_management", "chaos_engineering", "migration",
                "observability_dashboard",
            ],
            "ui_and_interface": [
                "cli", "website", "terminal_interface", "ide", "visualization",
                "video", "audio", "multimodal", "accessibility", "i18n",
                "templating", "notification",
            ],
            "domain_and_simulation": [
                "bio_simulation", "finance", "logistics", "spatial", "education",
                "meme", "embodiment", "evolutionary_ai", "quantum",
                "smart_contracts", "market", "dark", "physical_management",
                "relations", "collaboration",
            ],
            "system_and_meta": [
                "system_discovery", "plugin_system", "skills", "tool_use",
                "tools", "module_template", "examples", "tests",
                "workflow_testing", "api",
            ],
        },
    }

def get_total_tool_count() -> int:
    """Get the total number of registered tools (static + dynamic)."""
    return len(get_tool_registry().list_tools())

