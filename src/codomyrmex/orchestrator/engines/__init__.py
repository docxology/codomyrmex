"""Workflow engine implementations."""

from .base import ExecutionEngine
from .models import (
    TaskDefinition,
    TaskResult,
    TaskState,
    WorkflowDefinition,
    WorkflowResult,
)
from .parallel import ParallelEngine
from .sequential import SequentialEngine


def create_engine(engine_type: str = "parallel", **kwargs) -> ExecutionEngine:
    """Factory function for execution engines."""
    engines: dict[str, type[ExecutionEngine]] = {
        "sequential": SequentialEngine,
        "parallel": ParallelEngine,
    }
    engine_class = engines.get(engine_type)
    if not engine_class:
        raise ValueError(f"Unknown engine type: {engine_type}")
    return engine_class(**kwargs)


__all__ = [
    "ExecutionEngine",
    "ParallelEngine",
    "SequentialEngine",
    "TaskDefinition",
    "TaskResult",
    "TaskState",
    "WorkflowDefinition",
    "WorkflowResult",
    "create_engine",
]
