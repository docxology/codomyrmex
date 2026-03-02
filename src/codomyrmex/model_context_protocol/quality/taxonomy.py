"""MCP Tool Category Taxonomy.

Auto-classifies MCP tools into semantic categories for filtering,
documentation, and access-control purposes.

Categories::

    analysis   — Read-only inspection (code review, static analysis)
    generation — Creates new content (diagrams, docs, charts)
    execution  — Runs code or commands (side-effects)
    query      — Retrieves data without side-effects
    mutation   — Modifies persistent state (files, git, notes)
"""

from __future__ import annotations

import enum
import re
from dataclasses import dataclass, field
from typing import Any
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class ToolCategory(enum.Enum):
    """Semantic category for an MCP tool."""

    ANALYSIS = "analysis"
    GENERATION = "generation"
    EXECUTION = "execution"
    QUERY = "query"
    MUTATION = "mutation"


# ── Pattern-Based Auto-Classification ────────────────────────────────

# Each tuple: (compiled regex on tool name, category).
# Order matters — first match wins.
_CATEGORY_RULES: list[tuple[re.Pattern[str], ToolCategory]] = [
    # Mutations (state-changing operations).
    (re.compile(r"git_(commit|push|pull|init|create_branch|switch_branch|clone)$"), ToolCategory.MUTATION),
    (re.compile(r"write_file$"), ToolCategory.MUTATION),
    (re.compile(r"obsidian_(create|update|delete)_note$"), ToolCategory.MUTATION),
    (re.compile(r"invalidate_cache$"), ToolCategory.MUTATION),

    # Execution (runs code/commands with side-effects).
    (re.compile(r"(execute_code|code_execute|run_command|run_tests|call_module_function)$"), ToolCategory.EXECUTION),
    (re.compile(r"code_debug$"), ToolCategory.EXECUTION),

    # Generation (creates new artifacts/content).
    (re.compile(r"create_(bar_chart|line_plot|pie_chart|ascii_art)$"), ToolCategory.GENERATION),
    (re.compile(r"create_(commit_timeline|git_branch|git_workflow|repository_structure)_diagram$"), ToolCategory.GENERATION),
    (re.compile(r"generate_documentation$"), ToolCategory.GENERATION),

    # Analysis (read-only inspection).
    (re.compile(r"(analyze_file|analyze_project|analyze_python)$"), ToolCategory.ANALYSIS),
    (re.compile(r"code_review_(file|project)$"), ToolCategory.ANALYSIS),
    (re.compile(r"checksum_file$"), ToolCategory.ANALYSIS),
    (re.compile(r"obsidian_find_broken_links$"), ToolCategory.ANALYSIS),
    (re.compile(r"obsidian_vault_stats$"), ToolCategory.ANALYSIS),

    # Query (data retrieval, no side-effects).
    (re.compile(r"(list_|get_|search_|read_|module_info|pai_|json_query|code_list)"), ToolCategory.QUERY),
    (re.compile(r"obsidian_(load_vault|read_|search|list_tags|get_backlinks)"), ToolCategory.QUERY),
    (re.compile(r"git_(diff|log|status|repo_status|is_repo|check_availability|current_branch)$"), ToolCategory.QUERY),
]


def categorize_tool(tool_name: str) -> ToolCategory:
    """Classify a single tool by name using pattern rules.

    Args:
        tool_name: Fully-qualified tool name (e.g. ``codomyrmex.analyze_file``).

    Returns:
        The best-matching ``ToolCategory``.  Defaults to ``QUERY`` if no
        pattern matches (conservative: assume read-only).
    """
    # Strip common prefix for matching.
    short = tool_name.split(".")[-1] if "." in tool_name else tool_name

    for pattern, category in _CATEGORY_RULES:
        if pattern.search(short):
            return category

    logger.debug(f"No category rule matched for '{tool_name}', defaulting to QUERY")
    return ToolCategory.QUERY


def categorize_all_tools(tool_names: list[str]) -> dict[str, ToolCategory]:
    """Classify all tools, returning a name→category mapping.

    Args:
        tool_names: List of fully-qualified tool names.

    Returns:
        Dict mapping each tool name to its ``ToolCategory``.
    """
    return {name: categorize_tool(name) for name in tool_names}


@dataclass
class TaxonomyReport:
    """Summary of tool categorization."""

    total: int = 0
    by_category: dict[str, int] = field(default_factory=dict)
    tools: dict[str, str] = field(default_factory=dict)

    def summary(self) -> dict[str, Any]:
        """Return a serializable summary."""
        return {
            "total": self.total,
            "by_category": self.by_category,
            "coverage": f"{sum(self.by_category.values())}/{self.total}",
        }


def generate_taxonomy_report(tool_names: list[str]) -> TaxonomyReport:
    """Generate a full taxonomy report for a set of tools.

    Args:
        tool_names: List of tool names to classify.

    Returns:
        A ``TaxonomyReport`` with per-category counts and tool assignments.
    """
    mapping = categorize_all_tools(tool_names)

    by_category: dict[str, int] = {}
    tools: dict[str, str] = {}
    for name, cat in mapping.items():
        cat_val = cat.value
        by_category[cat_val] = by_category.get(cat_val, 0) + 1
        tools[name] = cat_val

    return TaxonomyReport(
        total=len(tool_names),
        by_category=by_category,
        tools=tools,
    )
