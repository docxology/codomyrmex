"""Skill Runner — execution bridge for discovered skills.

Connects the discovery registry to the execution layer, providing
a single entry point for skill lookup, validation, and execution.
"""

from __future__ import annotations

import logging
from typing import Any

try:
    from codomyrmex.logging_monitoring.core.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

from .discovery import FunctionSkill, Skill, SkillRegistry


def run_skill(
    registry: SkillRegistry,
    skill_id: str,
    **params: Any,
) -> Any:
    """Execute a skill by its unique ID.

    Looks up the skill in the registry, validates the parameters
    against the skill's schema, and executes it.

    Args:
        registry: The SkillRegistry containing registered skills.
        skill_id: Unique skill identifier.
        **params: Keyword arguments forwarded to the skill.

    Returns:
        The skill's return value.

    Raises:
        KeyError: If the skill is not found.
        ValueError: If parameter validation fails.
    """
    skill: Skill | None = registry.get(skill_id)
    if skill is None:
        raise KeyError(f"Skill not found: {skill_id!r}")

    logger.info("Running skill %s with params: %s", skill_id, list(params.keys()))

    # Validate params against the skill's schema
    skill.validate_params(**params)

    result = skill.execute(**params)
    logger.info("Skill %s completed successfully", skill_id)
    return result


def run_skill_by_name(
    registry: SkillRegistry,
    name: str,
    **params: Any,
) -> Any:
    """Execute a skill by its human-readable name.

    Convenience wrapper that looks up by name instead of ID.

    Args:
        registry: The SkillRegistry containing registered skills.
        name: Human-readable skill name.
        **params: Keyword arguments forwarded to the skill.

    Returns:
        The skill's return value.

    Raises:
        KeyError: If no skill with that name is found.
    """
    skill = registry.get_by_name(name)
    if skill is None:
        raise KeyError(f"Skill not found by name: {name!r}")

    return run_skill(registry, skill.metadata.id, **params)


def list_runnable_skills(registry: SkillRegistry) -> list[dict[str, Any]]:
    """List all skills eligible for execution.

    Args:
        registry: The SkillRegistry to query.

    Returns:
        List of dicts with id, name, description, category, and
        enabled status for each registered skill.
    """
    return [
        {
            "id": meta.id,
            "name": meta.name,
            "description": meta.description,
            "category": meta.category.value,
            "enabled": meta.enabled,
        }
        for meta in registry.list_all()
    ]


__all__ = ["run_skill", "run_skill_by_name", "list_runnable_skills"]
