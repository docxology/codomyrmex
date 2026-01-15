"""
Script Orchestrator Module

This module provides functionality for discovering, configuring, and running
Python scripts within the Codomyrmex project.
"""

from .core import main as run_orchestrator
from .config import load_config, get_script_config
from .workflow import Workflow, Task, TaskStatus, WorkflowError

__all__ = [
    "run_orchestrator",
    "load_config",
    "get_script_config",
    "Workflow",
    "Task",
    "TaskStatus",
    "WorkflowError",
]
