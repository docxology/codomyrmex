"""Hermes-local capability dispatch helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping


def filter_agent_names(
    all_agents: list[str],
    profile: Mapping[str, list[str]],
    role: str,
) -> list[str]:
    """Filter agent names by the role's allowed prefixes."""
    allowed = profile.get(role)
    if allowed is None:
        return all_agents
    return [
        name
        for name in all_agents
        if any(name.startswith(prefix) for prefix in allowed)
    ]


def spawn_agent(
    role: str,
    task: str,
    *,
    agents: Mapping[str, Callable[..., Any]],
    capability_profile: Mapping[str, list[str]] | None = None,
    extra_kwargs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Synchronously dispatch a task to a matching Hermes-local agent."""
    profile = capability_profile or {}
    allowed_agents = filter_agent_names(list(agents), profile, role)
    agent_name = next(
        (name for name in allowed_agents if name in agents),
        next(iter(agents), None),
    )

    if agent_name is None:
        return {
            "status": "error",
            "role": role,
            "task": task,
            "error": f"No agents registered for role '{role}'.",
        }

    try:
        result = agents[agent_name](task, **(extra_kwargs or {}))
        return {
            "status": "success",
            "role": role,
            "agent": agent_name,
            "result": result,
        }
    except Exception as exc:
        return {
            "status": "error",
            "role": role,
            "agent": agent_name,
            "error": str(exc),
        }


__all__ = ["filter_agent_names", "spawn_agent"]
