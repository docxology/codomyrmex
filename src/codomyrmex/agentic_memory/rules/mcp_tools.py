"""MCP tools for the rules submodule.

Exposes three safe, auto-discovered tools that allow AI agents to query
the .cursorrules hierarchy programmatically via the PAI MCP bridge.
"""

from __future__ import annotations

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:
    # Fallback decorator preserving _mcp_tool_meta for bridge discovery
    def mcp_tool(**kwargs):  # type: ignore[misc]
        def decorator(fn):
            fn._mcp_tool_meta = kwargs
            return fn
        return decorator


@mcp_tool(
    category="agentic_memory",
    description=(
        "List all Codomyrmex module names that have a defined coding rule. "
        "Returns a sorted list of module names (e.g. 'agentic_memory', 'agents', 'cloud')."
    ),
)
def rules_list_modules() -> list[str]:
    """Return sorted list of all module names with defined .cursorrules files."""
    from .engine import RuleEngine

    return RuleEngine().list_module_names()


@mcp_tool(
    category="agentic_memory",
    description=(
        "Get the full coding rule for a specific Codomyrmex module. "
        "Returns a dict with name, priority, sections, and raw_content, or null if no rule exists."
    ),
)
def rules_get_module_rule(module_name: str) -> dict | None:
    """Return the module-specific Rule as a dict, or None if not found.

    Args:
        module_name: Codomyrmex module name, e.g. ``"agentic_memory"`` or ``"agents"``.
    """
    from .engine import RuleEngine

    rule = RuleEngine().get_module_rule(module_name)
    return rule.to_dict() if rule is not None else None


@mcp_tool(
    category="agentic_memory",
    description=(
        "Get all applicable coding rules for a given file path and/or module name, "
        "ordered highest priority first (FILE_SPECIFIC → MODULE → CROSS_MODULE → GENERAL). "
        "Pass file_path (e.g. 'memory.py') and/or module_name (e.g. 'agentic_memory')."
    ),
)
def rules_get_applicable(file_path: str = "", module_name: str = "") -> list[dict]:
    """Return applicable rules as dicts, sorted FILE_SPECIFIC first.

    Args:
        file_path: File path or filename to determine file-specific rules (optional).
        module_name: Module name to include the module-specific rule (optional).
    """
    from .engine import RuleEngine

    rule_set = RuleEngine().get_applicable_rules(
        file_path=file_path or None,
        module_name=module_name or None,
    )
    return rule_set.to_dict()
