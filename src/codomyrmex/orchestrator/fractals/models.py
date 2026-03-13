"""Data models for the fractals orchestrator."""

from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field


class TaskKind(StrEnum):
    """The kind of a task."""

    ATOMIC = "atomic"
    COMPOSITE = "composite"


class TaskStatus(StrEnum):
    """The execution status of a task."""

    PENDING = "pending"
    DECOMPOSING = "decomposing"
    READY = "ready"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class TaskNode(BaseModel):
    """A node in the recursive task tree."""

    id: str
    description: str
    depth: int = 0
    lineage: list[str] = Field(default_factory=list)

    status: TaskStatus = TaskStatus.PENDING
    kind: Optional[TaskKind] = None
    children: list["TaskNode"] = Field(default_factory=list)

    def is_leaf(self) -> bool:
        """Return True if this task has no children."""
        return len(self.children) == 0

    def get_leaves(self) -> list["TaskNode"]:
        """Collect all leaf tasks in tree order."""
        if self.is_leaf():
            return [self]

        leaves = []
        for child in self.children:
            leaves.extend(child.get_leaves())
        return leaves

    def is_subtree_done(self) -> bool:
        """Check if all leaves under this node are done."""
        if self.is_leaf():
            return self.status == TaskStatus.DONE
        return all(child.is_subtree_done() for child in self.children)


# Needed for self-referential type inference in Pydantic v1,
# harmless in v2 if not needed.
TaskNode.model_rebuild() if hasattr(
    TaskNode, "model_rebuild"
) else TaskNode.update_forward_refs()
