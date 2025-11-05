"""
Project Orchestration Module for Codomyrmex

This module provides comprehensive project management and task orchestration
capabilities that integrate all other Codomyrmex modules into cohesive workflows.

Key Features:
- Task and workflow management
- Inter-module coordination
- Project templates and scaffolding
- Progress tracking and reporting
- Resource management
- Parallel execution support
- Error handling and recovery

Main Components:
- WorkflowManager: Manages workflow definitions and execution
- TaskOrchestrator: Coordinates individual tasks and dependencies
- ProjectManager: High-level project lifecycle management
- ResourceManager: Manages shared resources and dependencies

Integration:
- Uses logging_monitoring for all logging
- Integrates with performance monitoring
- Coordinates all other Codomyrmex modules
- Provides MCP tools for AI-driven orchestration
"""

from codomyrmex.exceptions import CodomyrmexError

from .mcp_tools import execute_mcp_tool, get_mcp_tool_definitions, get_mcp_tools
from .orchestration_engine import (
    OrchestrationContext,
    OrchestrationEngine,
    OrchestrationSession,
    SessionStatus,
)
from .project_manager import (
    Project,
    ProjectManager,
    ProjectStatus,
    ProjectTemplate,
    ProjectType,
)
from .resource_manager import (
    Resource,
    ResourceAllocation,
    ResourceManager,
    ResourceStatus,
    ResourceType,
    ResourceUsage,
)
from .task_orchestrator import (
    Task,
    TaskOrchestrator,
    TaskPriority,
    TaskResource,
    TaskResult,
    TaskStatus,
)
from .workflow_manager import (
    WorkflowExecution,
    WorkflowManager,
    WorkflowStatus,
    WorkflowStep,
)

__version__ = "0.1.0"

__all__ = [
    # Core classes
    "WorkflowManager",
    "TaskOrchestrator",
    "ProjectManager",
    "ResourceManager",
    "OrchestrationEngine",
    # Data classes
    "WorkflowStep",
    "WorkflowStatus",
    "WorkflowExecution",
    # Task & scheduling
    "Task",
    "TaskStatus",
    "TaskPriority",
    "TaskResult",
    "TaskResource",
    "Task",
    "TaskStatus",
    "TaskResult",
    "Project",
    "ProjectTemplate",
    "Resource",
    "ResourceType",
    "ResourceStatus",
    "ResourceAllocation",
    "ResourceUsage",
    # Sessions & engine
    "OrchestrationSession",
    "SessionStatus",
    "OrchestrationContext",
    # MCP tools
    "get_mcp_tools",
    "get_mcp_tool_definitions",
    "execute_mcp_tool",
]


# Module-level convenience functions
def create_workflow_steps(name: str, steps: list) -> bool:
    """Create a new workflow with steps."""
    wf_manager = get_workflow_manager()
    return wf_manager.create_workflow(name, steps)


def create_task(name: str, module: str, action: str, **kwargs) -> Task:
    """Create a new task instance."""
    return Task(name=name, module=module, action=action, parameters=kwargs)


def create_project(name: str, description: str = "", template: str = None) -> Project:
    """Create a new project instance."""
    return Project(name=name, description=description, template=template)


# Initialize default managers (lazy initialization)
_workflow_manager = None
_task_orchestrator = None
_project_manager = None
_resource_manager = None
_orchestration_engine = None


def get_workflow_manager() -> WorkflowManager:
    """Get the default workflow manager instance."""
    global _workflow_manager
    if _workflow_manager is None:
        _workflow_manager = WorkflowManager()
    return _workflow_manager


def get_task_orchestrator() -> TaskOrchestrator:
    """Get the default task orchestrator instance."""
    global _task_orchestrator
    if _task_orchestrator is None:
        _task_orchestrator = TaskOrchestrator()
    return _task_orchestrator


def get_project_manager() -> ProjectManager:
    """Get the default project manager instance."""
    global _project_manager
    if _project_manager is None:
        _project_manager = ProjectManager()
    return _project_manager


def get_resource_manager() -> ResourceManager:
    """Get the default resource manager instance."""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager


def get_orchestration_engine() -> OrchestrationEngine:
    """Get the default orchestration engine instance."""
    global _orchestration_engine
    if _orchestration_engine is None:
        _orchestration_engine = OrchestrationEngine()
    return _orchestration_engine


# Quick workflow execution function
def execute_workflow(name: str, **params):
    """Execute a workflow with given parameters."""
    manager = get_workflow_manager()
    return manager.execute_workflow(name, **params)


# Quick task execution function
def execute_task(task: Task):
    """Execute a single task."""
    orchestrator = get_task_orchestrator()
    return orchestrator.execute_task(task)
