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


@mcp_tool(
    category="agentic_memory",
    description=(
        "Get a specific numbered section (0–7) from a module's coding rule. "
        "Returns a dict with number, title, and content, or null if not found."
    ),
)
def rules_get_section(module_name: str, section_number: int) -> dict | None:
    """Return one section from a module rule as a dict, or None if not found.

    Args:
        module_name: Codomyrmex module name, e.g. ``"agentic_memory"``.
        section_number: Section number 0–7 (§0 Preamble through §7 Final Check).
    """
    from .engine import RuleEngine

    rule = RuleEngine().get_module_rule(module_name)
    if rule is None:
        return None
    section = rule.get_section(section_number)
    return section.to_dict() if section is not None else None


@mcp_tool(
    category="agentic_memory",
    description=(
        "Search all 75 .cursorrules files for a text query (case-insensitive). "
        "Returns a list of matching rules with name, priority, and file path."
    ),
)
def rules_search(query: str) -> list[dict]:
    """Return all rules whose raw content contains *query* (case-insensitive).

    Args:
        query: Text to search for, e.g. ``"Zero-Mock"`` or ``"pytest"``.
    """
    from .engine import RuleEngine

    query_lower = query.lower()
    return [
        {
            "name": r.name,
            "priority": r.priority.name,
            "file_path": str(r.file_path),
        }
        for r in RuleEngine().list_all_rules()
        if query_lower in r.raw_content.lower()
    ]


@mcp_tool(
    category="agentic_memory",
    description="List all cross-module rule names (8 rules governing inter-module concerns).",
)
def rules_list_cross_module() -> list[str]:
    """Return sorted list of all cross-module rule names."""
    from .engine import RuleEngine

    return RuleEngine().list_cross_module_names()


@mcp_tool(
    category="agentic_memory",
    description=(
        "List all file-specific rule names (6 rules for file types: .py, .yaml, .json, etc.)."
    ),
)
def rules_list_file_specific() -> list[str]:
    """Return sorted list of all file-specific rule names."""
    from .engine import RuleEngine

    return RuleEngine().list_file_rule_names()


@mcp_tool(
    category="agentic_memory",
    description=(
        "List all 75 rules across all categories as summary dicts, sorted by priority. "
        "FILE_SPECIFIC rules come first, GENERAL last."
    ),
)
def rules_list_all() -> list[dict]:
    """Return all rules as summary dicts sorted FILE_SPECIFIC first.

    Each dict contains ``name``, ``priority``, and ``file_path``.
    """
    from .engine import RuleEngine

    return [
        {
            "name": r.name,
            "priority": r.priority.name,
            "file_path": str(r.file_path),
        }
        for r in RuleEngine().list_all_rules()
    ]
