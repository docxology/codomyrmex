"""Planning and decomposition logic using LLMs."""

import json

from codomyrmex.agents.core.base import AgentRequest
from codomyrmex.agents.llm_client import get_llm_client

from .models import TaskKind, TaskNode, TaskStatus


def format_lineage(lineage: list[str], current: str) -> str:
    """Format the task lineage into an indented string representation."""
    if not lineage:
        return f"- {current}"

    lines = []
    for i, item in enumerate(lineage):
        indent = "  " * i
        lines.append(f"{indent}- {item}")

    indent = "  " * len(lineage)
    lines.append(f"{indent}- {current} (current)")
    return "\n".join(lines)


def classify(task: str, lineage: list[str]) -> TaskKind:
    """Classify whether a task is atomic or composite."""
    client = get_llm_client("fractals_planner")

    context = format_lineage(lineage, task)
    prompt = f"""Task hierarchy:
{context}

Respond ONLY with valid JSON containing a single key "kind" with value either "atomic" or "composite"."""

    system = """You decide whether a software task is "atomic" or "composite".

- "atomic" = a developer can sit down and implement this directly without needing to plan further.
- "composite" = this clearly contains 2+ independent concerns that should be worked on separately.

Decision heuristics:
- If the task names a single feature, endpoint, component, or module: atomic.
- If the task bundles unrelated concerns: composite.
- When in doubt, choose atomic. Over-decomposition creates more overhead than under-decomposition.

Output strictly JSON: {"kind": "atomic"} or {"kind": "composite"}"""

    req = AgentRequest(prompt=prompt, metadata={"system": system})
    resp = client.execute(req)

    if resp.error:
        raise RuntimeError(f"LLM Classification Error: {resp.error}")

    try:
        # Clean up potential markdown formatting
        content = resp.content.strip()
        content = content.removeprefix("```json")
        content = content.removeprefix("```")
        content = content.removesuffix("```")

        data = json.loads(content.strip())
        return TaskKind(data["kind"])
    except Exception as e:
        # Fallback to atomic if parsing fails
        return TaskKind.ATOMIC


def decompose(task: str, lineage: list[str]) -> list[str]:
    """Decompose a composite task into a list of atomic/smaller subtasks."""
    client = get_llm_client("fractals_planner")

    context = format_lineage(lineage, task)
    prompt = f"""Task hierarchy:
{context}

Respond ONLY with valid JSON containing a single key "subtasks" mapped to an array of strings."""

    system = """You are a pragmatic task decomposition engine for software projects.

Given a composite task, break it into the MINIMUM number of subtasks needed. Use your judgment:
- A simple task might only need 2 subtasks.
- Do NOT pad with extra subtasks to reach a number.
- Each subtask should represent real, distinct work.

Output strictly JSON: {"subtasks": ["subtask 1", "subtask 2"]}"""

    req = AgentRequest(prompt=prompt, metadata={"system": system})
    resp = client.execute(req)

    if resp.error:
        raise RuntimeError(f"LLM Decomposition Error: {resp.error}")

    try:
        content = resp.content.strip()
        content = content.removeprefix("```json")
        content = content.removeprefix("```")
        content = content.removesuffix("```")

        data = json.loads(content.strip())
        return data["subtasks"]
    except Exception as e:
        # If parsing fails, return the original task as a single subtask
        return [task]


def build_tree(description: str) -> TaskNode:
    """Build the root of a task tree."""
    return TaskNode(id="1", description=description, depth=0, lineage=[])


def plan(task: TaskNode, max_depth: int = 5) -> TaskNode:
    """Recursively decompose a task tree (planning phase only -- no execution).

    Classifies each node, then decomposes composites into children.
    Atomic nodes are marked "ready" for later execution.
    """
    if task.depth >= max_depth:
        kind = TaskKind.ATOMIC
    else:
        kind = classify(task.description, task.lineage)

    task.kind = kind

    if kind == TaskKind.ATOMIC:
        task.status = TaskStatus.READY
        return task

    task.status = TaskStatus.DECOMPOSING
    subtask_descriptions = decompose(task.description, task.lineage)

    child_lineage = task.lineage.copy()
    child_lineage.append(task.description)

    task.children = [
        TaskNode(
            id=f"{task.id}.{i + 1}",
            description=desc,
            depth=task.depth + 1,
            lineage=child_lineage,
        )
        for i, desc in enumerate(subtask_descriptions)
    ]

    for child in task.children:
        plan(child, max_depth)

    task.status = TaskStatus.READY
    return task


def find_task(root: TaskNode, task_id: str) -> TaskNode | None:
    """Find a task by ID in the tree."""
    if root.id == task_id:
        return root
    for child in root.children:
        found = find_task(child, task_id)
        if found:
            return found
    return None


def propagate_status(task: TaskNode) -> None:
    """Propagate done status up the tree."""
    if task.is_leaf():
        return
    for child in task.children:
        propagate_status(child)

    if all(c.status == TaskStatus.DONE for c in task.children):
        task.status = TaskStatus.DONE
    elif any(c.status == TaskStatus.FAILED for c in task.children):
        task.status = TaskStatus.FAILED
    elif any(c.status in (TaskStatus.RUNNING, TaskStatus.DONE) for c in task.children):
        task.status = TaskStatus.RUNNING
