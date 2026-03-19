"""Hermes CLI skill name normalization for AgentRequest context."""

from __future__ import annotations

from typing import Any

# Session metadata key for Hermes CLI skill preload (list of skill names).
SESSION_METADATA_HERMES_SKILLS_KEY = "hermes_skills"

__all__ = [
    "SESSION_METADATA_HERMES_SKILLS_KEY",
    "agent_context_for_hermes_skills",
    "normalize_hermes_skill_names",
]


def normalize_hermes_skill_names(
    hermes_skill: str | None = None,
    hermes_skills: list[str] | str | None = None,
    *,
    context: dict[str, Any] | None = None,
) -> list[str]:
    """Normalize skill names from MCP/agent context into a deduplicated list."""
    collected: list[str] = []

    def _add_value(value: Any) -> None:
        if value is None:
            return
        if isinstance(value, str):
            for part in value.split(","):
                p = part.strip()
                if p:
                    collected.append(p)
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                if item is not None and str(item).strip():
                    collected.append(str(item).strip())

    if hermes_skill and str(hermes_skill).strip():
        collected.append(str(hermes_skill).strip())
    _add_value(hermes_skills)
    if context:
        cs = context.get("hermes_skill")
        if isinstance(cs, str) and cs.strip():
            collected.append(cs.strip())
        _add_value(context.get("hermes_skills"))

    seen: set[str] = set()
    out: list[str] = []
    for n in collected:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def agent_context_for_hermes_skills(
    hermes_skill: str | None = None,
    hermes_skills: list[str] | str | None = None,
    base: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build an :class:`~codomyrmex.agents.core.AgentRequest` context fragment for CLI skill preload."""
    out = dict(base or {})
    for drop in ("hermes_skill", "hermes_skills"):
        out.pop(drop, None)
    names = normalize_hermes_skill_names(hermes_skill, hermes_skills)
    if names:
        out["hermes_skills"] = names
    return out
