"""
Project Orchestration Module for Codomyrmex

This module provides project management and task orchestration capabilities
that integrate Codomyrmex modules into cohesive workflows.

Key Features:
- Task and workflow management
- Inter-module coordination
- Project templates and scaffolding with automatic documentation generation
- Progress tracking and reporting
- Resource management
- Parallel execution support
- Error handling and recovery

Main Components:
- WorkflowManager: Manages workflow definitions and execution
- TaskOrchestrator: Coordinates individual tasks and dependencies
- ProjectManager: High-level project lifecycle management
- ResourceManager: Manages shared resources and dependencies
- DocumentationGenerator: Generates README.md and AGENTS.md files for projects and nested directories

Integration:
- Uses logging_monitoring for all logging
- Integrates with performance monitoring
- Coordinates all other Codomyrmex modules
- Provides MCP tools for AI-driven orchestration
"""

from codomyrmex.exceptions import CodomyrmexError

from .documentation_generator import DocumentationGenerator
from .mcp_tools import execute_mcp_tool, get_mcp_tool_definitions, get_mcp_tools
from .orchestration_engine import (
    OrchestrationEngine,
    OrchestrationSession,
    SessionStatus,
    get_orchestration_engine,
)
from .project_manager import (
    Project,
    ProjectManager,
    ProjectStatus,
    ProjectTemplate,
    ProjectType,
    get_project_manager,
)
from .resource_manager import (
    Resource,
    ResourceAllocation,
    ResourceManager,
    ResourceStatus,
    ResourceType,
    ResourceUsage,
    get_resource_manager,
)
from .task_orchestrator import (
    Task,
    TaskOrchestrator,
    TaskPriority,
    TaskResource,
    TaskResult,
    TaskStatus,
    get_task_orchestrator,
)
from .workflow_manager import (
    WorkflowExecution,
    WorkflowManager,
    WorkflowStatus,
    WorkflowStep,
    get_workflow_manager,
)

__version__ = "0.1.0"

__all__ = [
    "DocumentationGenerator",
    "OrchestrationEngine",
    # Sessions & engine
    "OrchestrationSession",
    "Project",
    "ProjectManager",
    "ProjectTemplate",
    "Resource",
    "ResourceAllocation",
    "ResourceManager",
    "ResourceStatus",
    "ResourceType",
    "ResourceUsage",
    "SessionStatus",
    # Task & scheduling
    "Task",
    "Task",
    "TaskOrchestrator",
    "TaskPriority",
    "TaskResource",
    "TaskResult",
    "TaskResult",
    "TaskStatus",
    "TaskStatus",
    "WorkflowExecution",
    # Core classes
    "WorkflowManager",
    "WorkflowStatus",
    # Data classes
    "WorkflowStep",
    "execute_mcp_tool",
    "get_mcp_tool_definitions",
    # MCP tools
    "get_mcp_tools",
    # Managers
    "get_orchestration_engine",
    "get_project_manager",
    "get_resource_manager",
    "get_task_orchestrator",
    "get_workflow_manager",
]


# Module-level convenience functions
def create_workflow_steps(name: str, steps: list) -> bool:
    """Create a new workflow with steps."""
    wf_manager = get_workflow_manager()
    return wf_manager.create_workflow(name, steps)


def create_task(name: str, module: str, action: str, **kwargs) -> Task:
    """Create a new task instance."""
    return Task(name=name, module=module, action=action, parameters=kwargs)


def create_project(
    name: str, description: str = "", template: str | None = None
) -> Project:
    """Create a new project instance."""
    return Project(name=name, description=description, template=template)





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
