"""Tests for discovered-skill runner helpers."""

from __future__ import annotations

import pytest

from codomyrmex.skills.discovery import SkillCategory, SkillRegistry, skill
from codomyrmex.skills.skill_runner import list_runnable_skills, run_skill


@pytest.mark.unit
def test_run_skill_raises_on_validation_errors() -> None:
    registry = SkillRegistry()

    @skill(name="needs_value", category=SkillCategory.UTILITY, registry=registry)
    def needs_value(value: str) -> str:
        """Return a required value."""
        return value

    with pytest.raises(ValueError, match="Missing required parameter: value"):
        run_skill(registry, needs_value.metadata.id)


@pytest.mark.unit
def test_list_runnable_skills_uses_discovery_registry_metadata() -> None:
    registry = SkillRegistry()

    @skill(name="echo_value", category=SkillCategory.UTILITY, registry=registry)
    def echo_value(value: str = "ok") -> str:
        """Echo a value."""
        return value

    listed = list_runnable_skills(registry)

    assert listed == [
        {
            "id": echo_value.metadata.id,
            "name": "echo_value",
            "description": "Echo a value.",
            "category": "utility",
            "enabled": True,
        }
    ]
