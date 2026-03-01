"""Task decomposition and planning for agenticSeek.

Mirrors the ``PlannerAgent`` logic from the upstream project, providing
JSON plan parsing, dependency validation, and topological execution
ordering—all without requiring an LLM call.

Reference: https://github.com/Fosowl/agenticSeek/blob/main/sources/agents/planner_agent.py
"""

from __future__ import annotations

import json
import logging
import re
from collections import deque
from typing import Any

logger = logging.getLogger(__name__)

from codomyrmex.agents.agentic_seek.agent_types import (
    AgenticSeekAgentType,
    AgenticSeekTaskStep,
)


# ---------------------------------------------------------------------------
# Task-name extraction (mirrors PlannerAgent.get_task_names)
# ---------------------------------------------------------------------------

def extract_task_names(text: str) -> list[str]:
    """Extract task headings from a planner's textual output.

    Recognises lines that start with ``##`` or a digit, matching the
    upstream ``PlannerAgent.get_task_names`` heuristic.

    Args:
        text: Multi-line planner output.

    Returns:
        Ordered list of extracted task names.
    """
    names: list[str] = []
    for raw_line in text.strip().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("##") or (line and line[0].isdigit()):
            names.append(line)
    return names


# ---------------------------------------------------------------------------
# JSON plan parsing (mirrors PlannerAgent.parse_agent_tasks)
# ---------------------------------------------------------------------------

_JSON_BLOCK_PATTERN = re.compile(r"```(?:json)?\s*\n(.*?)```", re.DOTALL)


def _extract_json_from_text(text: str) -> list[dict[str, Any]]:
    """Pull JSON objects out of markdown-fenced or raw JSON text."""
    results: list[dict[str, Any]] = []

    # Try fenced blocks first
    for match in _JSON_BLOCK_PATTERN.finditer(text):
        try:
            parsed = json.loads(match.group(1))
            if isinstance(parsed, dict):
                results.append(parsed)
            elif isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, dict):
                        results.append(item)
        except json.JSONDecodeError:
            continue

    # If no fenced blocks, try whole text as JSON
    if not results:
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                results.append(parsed)
        except json.JSONDecodeError as e:
            logger.debug("Skipping non-JSON chunk in task plan response: %s", e)
            pass

    return results


def parse_plan_json(text: str) -> list[AgenticSeekTaskStep]:
    """Parse a JSON execution plan into ``AgenticSeekTaskStep`` objects.

    Expects JSON with a ``"plan"`` key containing a list of task
    objects, each with ``"agent"``, ``"id"``, ``"task"``, and
    optionally ``"need"`` (dependency list) keys.

    Example JSON::

        {
          "plan": [
            {"agent": "coder", "id": 1, "task": "Write script"},
            {"agent": "web",   "id": 2, "task": "Search docs", "need": [1]}
          ]
        }

    Args:
        text: LLM response containing a JSON plan.

    Returns:
        Ordered list of ``AgenticSeekTaskStep``.

    Raises:
        ValueError: On missing required fields or unknown agent types.
    """
    json_blocks = _extract_json_from_text(text)
    steps: list[AgenticSeekTaskStep] = []

    for block in json_blocks:
        plan_items = block.get("plan", [])
        if not isinstance(plan_items, list):
            continue
        for item in plan_items:
            # Validate required fields
            missing = [k for k in ("agent", "id", "task") if k not in item]
            if missing:
                raise ValueError(
                    f"Plan step missing required fields: {missing}. "
                    f"Got: {item}"
                )

            # Map "web" → BROWSER (upstream convention)
            agent_str = item["agent"].lower()
            if agent_str == "web":
                agent_str = "browser"

            try:
                agent_type = AgenticSeekAgentType.from_string(agent_str)
            except ValueError:
                raise ValueError(
                    f"Unknown agent type {item['agent']!r} in plan step "
                    f"{item['id']}."
                )

            deps = item.get("need", [])
            if isinstance(deps, int):
                deps = [deps]

            steps.append(
                AgenticSeekTaskStep(
                    agent_type=agent_type,
                    task_id=int(item["id"]),
                    description=str(item["task"]),
                    dependencies=[int(d) for d in deps],
                )
            )

    return steps


# ---------------------------------------------------------------------------
# Plan validation
# ---------------------------------------------------------------------------

def validate_plan(
    steps: list[AgenticSeekTaskStep],
    available_agents: set[AgenticSeekAgentType] | None = None,
) -> list[str]:
    """Validate a parsed plan for structural problems.

    Checks performed:

    1. All referenced agents are available.
    2. All dependency IDs reference existing steps.
    3. No circular dependencies.
    4. Task IDs are unique.

    Args:
        steps: The parsed plan steps.
        available_agents: Set of agent types that are actually available.
            If ``None``, all types are considered available.

    Returns:
        List of human-readable error strings (empty if valid).
    """
    if available_agents is None:
        available_agents = set(AgenticSeekAgentType)

    errors: list[str] = []
    step_ids = {s.task_id for s in steps}

    # Check uniqueness
    if len(step_ids) != len(steps):
        errors.append("Duplicate task IDs detected.")

    for step in steps:
        # Agent availability
        if step.agent_type not in available_agents:
            errors.append(
                f"Step {step.task_id}: agent type "
                f"{step.agent_type.value!r} not available."
            )
        # Dependency existence
        for dep_id in step.dependencies:
            if dep_id not in step_ids:
                errors.append(
                    f"Step {step.task_id}: dependency {dep_id} "
                    f"does not exist."
                )

    # Circular dependency detection (Kahn's algorithm)
    if not errors:
        cycle_errors = _detect_cycles(steps)
        errors.extend(cycle_errors)

    return errors


def _detect_cycles(steps: list[AgenticSeekTaskStep]) -> list[str]:
    """Detect circular dependencies using Kahn's topological sort."""
    in_degree: dict[int, int] = {s.task_id: 0 for s in steps}
    adjacency: dict[int, list[int]] = {s.task_id: [] for s in steps}

    for step in steps:
        for dep_id in step.dependencies:
            if dep_id in adjacency:
                adjacency[dep_id].append(step.task_id)
                in_degree[step.task_id] += 1

    queue: deque[int] = deque(
        tid for tid, deg in in_degree.items() if deg == 0
    )
    visited = 0
    while queue:
        node = queue.popleft()
        visited += 1
        for neighbour in adjacency.get(node, []):
            in_degree[neighbour] -= 1
            if in_degree[neighbour] == 0:
                queue.append(neighbour)

    if visited != len(steps):
        return ["Circular dependency detected in plan."]
    return []


# ---------------------------------------------------------------------------
# Execution ordering
# ---------------------------------------------------------------------------

def get_execution_order(
    steps: list[AgenticSeekTaskStep],
) -> list[AgenticSeekTaskStep]:
    """Return steps in a valid execution order (topological sort).

    Steps with no dependencies come first, followed by steps whose
    dependencies have already been listed.

    Args:
        steps: Plan steps (assumed to be cycle-free).

    Returns:
        Topologically sorted list of steps.

    Raises:
        ValueError: If a cycle is detected.
    """
    id_to_step = {s.task_id: s for s in steps}
    in_degree: dict[int, int] = {s.task_id: 0 for s in steps}
    adjacency: dict[int, list[int]] = {s.task_id: [] for s in steps}

    for step in steps:
        for dep_id in step.dependencies:
            if dep_id in adjacency:
                adjacency[dep_id].append(step.task_id)
                in_degree[step.task_id] += 1

    queue: deque[int] = deque(
        tid for tid, deg in in_degree.items() if deg == 0
    )
    ordered: list[AgenticSeekTaskStep] = []

    while queue:
        node = queue.popleft()
        ordered.append(id_to_step[node])
        for neighbour in adjacency.get(node, []):
            in_degree[neighbour] -= 1
            if in_degree[neighbour] == 0:
                queue.append(neighbour)

    if len(ordered) != len(steps):
        raise ValueError("Circular dependency detected—cannot determine execution order.")

    return ordered


# ---------------------------------------------------------------------------
# Convenience facade
# ---------------------------------------------------------------------------

class AgenticSeekTaskPlanner:
    """High-level facade for plan parsing, validation, and ordering.

    Example::

        planner = AgenticSeekTaskPlanner()
        steps = planner.parse(llm_response)
        errors = planner.validate(steps)
        if not errors:
            ordered = planner.execution_order(steps)
    """

    def parse(self, text: str) -> list[AgenticSeekTaskStep]:
        """Parse a JSON plan from LLM text."""
        return parse_plan_json(text)

    def validate(
        self,
        steps: list[AgenticSeekTaskStep],
        available_agents: set[AgenticSeekAgentType] | None = None,
    ) -> list[str]:
        """Validate a parsed plan."""
        return validate_plan(steps, available_agents)

    def execution_order(
        self,
        steps: list[AgenticSeekTaskStep],
    ) -> list[AgenticSeekTaskStep]:
        """Return steps in topological (dependency-respecting) order."""
        return get_execution_order(steps)

    def extract_names(self, text: str) -> list[str]:
        """Extract task name headings from planner output."""
        return extract_task_names(text)
