"""MCP Tools for the Skills module.

Exposes skill management operations as MCP-discoverable tools.
Each tool wraps a SkillsManager method for agent consumption.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool

logger = get_logger(__name__)


def _get_manager():
    """Lazily obtain a configured SkillsManager."""
    from codomyrmex.skills import get_skills_manager

    mgr = get_skills_manager()
    mgr.initialize()
    return mgr


# ------------------------------------------------------------------
# MCP tools
# ------------------------------------------------------------------


@mcp_tool(
    name="skills_list",
    description="List available skills, optionally filtered by category.",
    category="skills",
    version="1.0",
)
def skills_list(category: str = "") -> list[dict[str, Any]]:
    """List available skills, optionally filtered by category.

    Args:
        category: Optional category filter (empty string for all).

    Returns:
        List of skill information dictionaries with category, name,
        and metadata.
    """
    mgr = _get_manager()
    return mgr.list_skills(category=category or None)


@mcp_tool(
    name="skills_get",
    description="Get a specific skill by category and name.",
    category="skills",
    version="1.0",
)
def skills_get(category: str, name: str) -> dict[str, Any] | None:
    """Get a specific skill by category and name.

    Args:
        category: Skill category.
        name: Skill name.

    Returns:
        Skill data dictionary or None if not found.
    """
    mgr = _get_manager()
    return mgr.get_skill(category, name)


@mcp_tool(
    name="skills_search",
    description="Search skills by query string.",
    category="skills",
    version="1.0",
)
def skills_search(query: str) -> list[dict[str, Any]]:
    """Search skills by query string.

    Args:
        query: Search query.

    Returns:
        List of matching skills with full data and metadata.
    """
    mgr = _get_manager()
    return mgr.search_skills(query)


@mcp_tool(
    name="skills_sync",
    description="Sync with upstream vibeship-spawner-skills repository.",
    category="skills",
    version="1.0",
)
def skills_sync(force: bool = False) -> dict[str, Any]:
    """Sync with upstream vibeship-spawner-skills repository.

    Args:
        force: Force re-clone even if directory exists.

    Returns:
        Success status and sync information.
    """
    mgr = _get_manager()
    success = mgr.sync_upstream(force=force)
    return {
        "success": success,
        "upstream_status": mgr.get_upstream_status(),
    }


@mcp_tool(
    name="skills_add_custom",
    description="Add a custom skill that overrides upstream.",
    category="skills",
    version="1.0",
)
def skills_add_custom(
    category: str, name: str, skill_data: dict[str, Any]
) -> dict[str, Any]:
    """Add a custom skill that overrides upstream.

    Args:
        category: Skill category.
        name: Skill name.
        skill_data: Skill data dictionary.

    Returns:
        Success status dictionary.
    """
    mgr = _get_manager()
    success = mgr.add_custom_skill(category, name, skill_data)
    return {"success": success, "category": category, "name": name}


@mcp_tool(
    name="skills_get_categories",
    description="Get all available skill categories.",
    category="skills",
    version="1.0",
)
def skills_get_categories() -> list[str]:
    """Get all available skill categories.

    Returns:
        List of category names.
    """
    mgr = _get_manager()
    return mgr.get_categories()


@mcp_tool(
    name="skills_get_upstream_status",
    description="Get status of upstream repository.",
    category="skills",
    version="1.0",
)
def skills_get_upstream_status() -> dict[str, Any]:
    """Get status of upstream repository.

    Returns:
        Status dictionary with exists, is_git_repo, branch,
        has_changes, last_commit.
    """
    mgr = _get_manager()
    return mgr.get_upstream_status()


__all__ = [
    "skills_list",
    "skills_get",
    "skills_search",
    "skills_sync",
    "skills_add_custom",
    "skills_get_categories",
    "skills_get_upstream_status",
]
