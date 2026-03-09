"""Convenience factory functions for building common Workflow patterns."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from .workflow import Workflow


def _make_workflow(name: str) -> Workflow:
    from .workflow import Workflow

    return Workflow(name=name)


def chain(*actions: Callable, names: list[str] | None = None) -> Workflow:
    """Create a linear workflow where each task depends on the previous."""
    workflow = _make_workflow("chain")
    prev_name = None
    for i, action in enumerate(actions):
        name = (
            names[i]
            if names and i < len(names)
            else getattr(action, "__name__", f"task_{i}")
        )
        workflow.add_task(
            name=name, action=action, dependencies=[prev_name] if prev_name else None
        )
        prev_name = name
    return workflow


def parallel(*actions: Callable, names: list[str] | None = None) -> Workflow:
    """Create a workflow where all tasks run in parallel."""
    workflow = _make_workflow("parallel")
    for i, action in enumerate(actions):
        name = (
            names[i]
            if names and i < len(names)
            else getattr(action, "__name__", f"task_{i}")
        )
        workflow.add_task(name=name, action=action)
    return workflow


def fan_out_fan_in(
    initial: Callable,
    parallel_tasks: list[Callable],
    final: Callable,
    initial_name: str = "initial",
    final_name: str = "final",
) -> Workflow:
    """Create a fan-out/fan-in workflow: initial -> [parallel_tasks...] -> final."""
    workflow = _make_workflow("fan_out_fan_in")
    workflow.add_task(name=initial_name, action=initial)
    parallel_names = []
    for i, action in enumerate(parallel_tasks):
        name = getattr(action, "__name__", f"parallel_{i}")
        workflow.add_task(name=name, action=action, dependencies=[initial_name])
        parallel_names.append(name)
    workflow.add_task(name=final_name, action=final, dependencies=parallel_names)
    return workflow
