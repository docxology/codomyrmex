"""Fractals Submodule for Recursive Agentic Task Orchestration.

This module provides a recursive task decomposition engine that builds a self-similar
tree of executable subtasks, then runs each leaf in isolated git worktrees.
"""

from .executor import execute_leaf_task
from .models import TaskKind, TaskNode, TaskStatus
from .planner import build_tree, find_task, plan, propagate_status
from .workspace import WorkspaceManager

__all__ = [
    "TaskKind",
    "TaskNode",
    "TaskStatus",
    "WorkspaceManager",
    "build_tree",
    "execute_leaf_task",
    "find_task",
    "plan",
    "propagate_status",
]
