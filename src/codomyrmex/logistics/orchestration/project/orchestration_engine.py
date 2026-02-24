"""
Orchestration Engine for Codomyrmex

This is the main orchestration engine that coordinates all project management,
task orchestration, and resource management components. It provides a unified
interface for complex multi-module workflows.
"""

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from collections.abc import Callable

# Import Codomyrmex modules
try:
    from codomyrmex.logging_monitoring import get_logger

    logger = get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)

try:
    from codomyrmex.performance import PerformanceMonitor, monitor_performance

    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False

    def monitor_performance(*args, **kwargs):
        """Decorator for performance monitoring (fallback)."""
        def decorator(func):
            """Execute Decorator operations natively."""

            return func

        return decorator


try:
    from codomyrmex.model_context_protocol import MCPErrorDetail, MCPToolResult

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

# Import orchestration components
from .project_manager import ProjectManager
from .resource_manager import ResourceManager
from .task_orchestrator import Task, TaskOrchestrator, TaskStatus
from .workflow_manager import WorkflowManager


class OrchestrationMode(Enum):
    """Orchestration execution modes."""

    SEQUENTIAL = "sequential"  # Execute workflows/tasks one after another
    PARALLEL = "parallel"  # Execute workflows/tasks in parallel when possible
    PRIORITY = "priority"  # Execute based on priority ordering
    RESOURCE_AWARE = "resource_aware"  # Execute based on resource availability


class SessionStatus(Enum):
    """Standard session lifecycle statuses."""

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class OrchestrationSession:
    """Represents an orchestration session (public-facing dataclass used in tests).

    This dataclass mirrors the previous internal context representation but
    provides the `SessionStatus` typed `status` expected by tests and public API.
    """

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    user_id: str = "system"
    mode: OrchestrationMode = OrchestrationMode.RESOURCE_AWARE
    max_parallel_tasks: int = 4
    max_parallel_workflows: int = 2
    timeout_seconds: int | None = None
    resource_requirements: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Execution tracking
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: datetime | None = None
    updated_at: datetime | None = None
    completed_at: datetime | None = None
    status: SessionStatus = SessionStatus.PENDING

    def to_dict(self) -> dict[str, Any]:
        """Convert session to dictionary."""
        data = {
            "session_id": self.session_id,
            "name": self.name,
            "description": self.description,
            "user_id": self.user_id,
            "mode": self.mode.value,
            "max_parallel_tasks": self.max_parallel_tasks,
            "max_parallel_workflows": self.max_parallel_workflows,
            "timeout_seconds": self.timeout_seconds,
            "resource_requirements": self.resource_requirements,
            "metadata": self.metadata,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
        }
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OrchestrationSession":
        """
        Create session from dictionary.

        Args:
            data: Dictionary containing session data.

        Returns:
            New OrchestrationSession instance.
        """
        sess = cls(
            session_id=data.get("session_id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            user_id=data.get("user_id", "system"),
            mode=(
                OrchestrationMode(data.get("mode"))
                if data.get("mode")
                else OrchestrationMode.RESOURCE_AWARE
            ),
            max_parallel_tasks=data.get("max_parallel_tasks", 4),
            max_parallel_workflows=data.get("max_parallel_workflows", 2),
            timeout_seconds=data.get("timeout_seconds"),
            resource_requirements=data.get("resource_requirements", {}),
            metadata=data.get("metadata", {}),
        )
        if data.get("created_at"):
            try:
                sess.created_at = datetime.fromisoformat(data["created_at"])
            except Exception:
                pass
        if data.get("status"):
            try:
                sess.status = SessionStatus(data["status"])
            except Exception:
                sess.status = SessionStatus.PENDING
        return sess




class OrchestrationEngine:
    """Main orchestration engine coordinating all components."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the orchestration engine."""
        self.config = config or {}

        # Initialize component managers
        self.workflow_manager = WorkflowManager(
            config_dir=self.config.get("workflows_dir")
        )
        self.task_orchestrator = TaskOrchestrator(
            max_workers=self.config.get("max_workers", 4)
        )
        self.project_manager = ProjectManager(
            projects_dir=self.config.get("projects_dir"),
            templates_dir=self.config.get("templates_dir"),
        )
        self.resource_manager = ResourceManager(
            config_file=self.config.get("resource_config")
        )

        # Performance monitoring
        self.performance_monitor = (
            PerformanceMonitor() if PERFORMANCE_AVAILABLE else None
        )

        # Active sessions
        self.active_sessions: dict[str, OrchestrationSession] = {}
        self.session_lock = threading.RLock()

        # Event handlers
        self.event_handlers: dict[str, list[Callable]] = {}

        # Start task orchestrator
        self.task_orchestrator.start_execution()

        logger.info("OrchestrationEngine initialized successfully")

    def register_event_handler(self, event: str, handler: Callable):
        """Register an event handler."""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)

    def emit_event(self, event: str, data: dict[str, Any]):
        """Emit an event to registered handlers."""
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    handler(event, data)
                except Exception as e:
                    logger.error(f"Error in event handler for {event}: {e}")

    def create_session(self, user_id: str = "system", **kwargs) -> str:
        """Create a new orchestration session."""
        context = OrchestrationSession(
            user_id=user_id,
            mode=OrchestrationMode(kwargs.get("mode", "resource_aware")),
            max_parallel_tasks=kwargs.get("max_parallel_tasks", 4),
            max_parallel_workflows=kwargs.get("max_parallel_workflows", 2),
            timeout_seconds=kwargs.get("timeout_seconds"),
            resource_requirements=kwargs.get("resource_requirements", {}),
            metadata=kwargs.get("metadata", {}),
        )

        with self.session_lock:
            self.active_sessions[context.session_id] = context

        self.emit_event(
            "session_created", {"session_id": context.session_id, "user_id": user_id}
        )
        logger.info(f"Created orchestration session: {context.session_id}")

        return context.session_id

    def get_session(self, session_id: str) -> OrchestrationSession | None:
        """Get a session by ID."""
        with self.session_lock:
            return self.active_sessions.get(session_id)

    def close_session(self, session_id: str) -> bool:
        """Close an orchestration session."""
        with self.session_lock:
            if session_id in self.active_sessions:
                context = self.active_sessions[session_id]
                context.status = "closed"
                context.completed_at = datetime.now(timezone.utc)

                # Cleanup session resources
                self.resource_manager.deallocate_resources(session_id)

                del self.active_sessions[session_id]

                self.emit_event("session_closed", {"session_id": session_id})
                logger.info(f"Closed orchestration session: {session_id}")
                return True
        return False

    @monitor_performance(function_name="execute_workflow")
    def execute_workflow(
        self, workflow_name: str, session_id: str | None = None, **params
    ) -> dict[str, Any]:
        """Execute a workflow with orchestration."""
        if not session_id:
            session_id = self.create_session()

        context = self.get_session(session_id)
        if not context:
            return {"success": False, "error": f"Session {session_id} not found"}

        context.started_at = datetime.now(timezone.utc)
        context.status = "executing_workflow"

        try:
            # Allocate resources if needed
            if context.resource_requirements:
                allocated = self.resource_manager.allocate_resources(
                    session_id, context.resource_requirements, context.timeout_seconds
                )
                if not allocated:
                    return {
                        "success": False,
                        "error": "Failed to allocate required resources",
                    }

            # Execute workflow (async)
            import asyncio

            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is already running, we need to handle differently
                    # For now, create a new thread with its own event loop
                    import concurrent.futures

                    def run_async():
                        """
                        Run workflow execution in a new event loop.

                        Returns:
                            Result of the workflow execution.
                        """
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        try:
                            return new_loop.run_until_complete(
                                self.workflow_manager.execute_workflow(
                                    workflow_name, **params
                                )
                            )
                        finally:
                            new_loop.close()

                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(run_async)
                        workflow_result = future.result(timeout=300)  # 5 minute timeout
                else:
                    workflow_result = loop.run_until_complete(
                        self.workflow_manager.execute_workflow(workflow_name, **params)
                    )
            except Exception as e:
                logger.error(f"Async workflow execution failed: {e}")
                return {"success": False, "error": f"Workflow execution failed: {e}"}

            # Convert WorkflowExecution to dict format
            result = {
                "success": workflow_result.success,
                "result": workflow_result.result,
                "error": workflow_result.error,
                "execution_time": workflow_result.execution_time,
                "steps_executed": (
                    len(workflow_result.step_results)
                    if workflow_result.step_results
                    else 0
                ),
            }

            # Update context
            context.status = "completed" if result["success"] else "failed"
            context.completed_at = datetime.now(timezone.utc)

            # Emit events
            event_data = {
                "session_id": session_id,
                "workflow_name": workflow_name,
                "success": result["success"],
                "execution_time": (
                    context.completed_at - context.started_at
                ).total_seconds(),
            }
            self.emit_event("workflow_completed", event_data)

            return result

        except Exception as e:
            context.status = "failed"
            context.completed_at = datetime.now(timezone.utc)
            logger.error(f"Workflow execution failed: {e}")

            return {"success": False, "error": str(e)}
        finally:
            # Clean up resources
            self.resource_manager.deallocate_resources(session_id)

    @monitor_performance(function_name="execute_task")
    def execute_task(
        self, task: Task | dict[str, Any], session_id: str | None = None
    ) -> dict[str, Any]:
        """Execute a single task with orchestration."""
        if not session_id:
            session_id = self.create_session()

        context = self.get_session(session_id)
        if not context:
            return {"success": False, "error": f"Session {session_id} not found"}

        # Convert dict to Task if needed
        if isinstance(task, dict):
            task = Task(**task)

        try:
            # Add task to orchestrator
            task_id = self.task_orchestrator.add_task(task)

            # Wait for completion (simplified - in practice might be async)
            import time

            while True:
                task_obj = self.task_orchestrator.get_task(task_id)
                if task_obj and task_obj.status in [
                    TaskStatus.COMPLETED,
                    TaskStatus.FAILED,
                    TaskStatus.CANCELLED,
                ]:
                    break
                time.sleep(0.1)

            result = self.task_orchestrator.get_task_result(task_id)

            return {
                "success": result.success if result else False,
                "result": result.to_dict() if result else None,
                "task_id": task_id,
            }

        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return {"success": False, "error": str(e)}

    @monitor_performance(function_name="execute_project_workflow")
    def execute_project_workflow(
        self,
        project_name: str,
        workflow_name: str,
        session_id: str | None = None,
        **params,
    ) -> dict[str, Any]:
        """Execute a workflow for a specific project."""
        if not session_id:
            session_id = self.create_session()

        context = self.get_session(session_id)
        if not context:
            return {"success": False, "error": f"Session {session_id} not found"}

        try:
            result = self.project_manager.execute_project_workflow(
                project_name, workflow_name, **params
            )

            # Update project metrics
            if result["success"]:
                metrics = {
                    "last_workflow_execution": datetime.now(timezone.utc).isoformat(),
                    "workflow_executions": 1,
                }
                self.project_manager.update_project_metrics(project_name, metrics)

            return result

        except Exception as e:
            logger.error(f"Project workflow execution failed: {e}")
            return {"success": False, "error": str(e)}

    def execute_complex_workflow(
        self, workflow_definition: dict[str, Any], session_id: str | None = None
    ) -> dict[str, Any]:
        """Execute a complex workflow with multiple interdependent steps."""
        if not session_id:
            session_id = self.create_session()

        context = self.get_session(session_id)
        if not context:
            return {"success": False, "error": f"Session {session_id} not found"}

        try:
            # Parse workflow definition
            steps = workflow_definition.get("steps", [])
            dependencies = workflow_definition.get("dependencies", {})
            workflow_definition.get("parallel_groups", [])

            # Create tasks from steps
            tasks = {}
            for step in steps:
                task = Task(
                    name=step["name"],
                    module=step["module"],
                    action=step["action"],
                    parameters=step.get("parameters", {}),
                    dependencies=dependencies.get(step["name"], []),
                )
                task_id = self.task_orchestrator.add_task(task)
                tasks[step["name"]] = task_id

            # Wait for all tasks to complete
            completed = self.task_orchestrator.wait_for_completion(
                timeout=context.timeout_seconds
            )

            if completed:
                # Collect results
                results = {}
                for step_name, task_id in tasks.items():
                    result = self.task_orchestrator.get_task_result(task_id)
                    results[step_name] = result.to_dict() if result else None

                return {
                    "success": True,
                    "results": results,
                    "execution_stats": self.task_orchestrator.get_execution_stats(),
                }
            else:
                return {"success": False, "error": "Workflow execution timed out"}

        except Exception as e:
            logger.error(f"Complex workflow execution failed: {e}")
            return {"success": False, "error": str(e)}

    def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status."""
        status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "orchestration_engine": {
                "active_sessions": len(self.active_sessions),
                "event_handlers": {
                    event: len(handlers)
                    for event, handlers in self.event_handlers.items()
                },
            },
            "workflow_manager": {
                "total_workflows": len(self.workflow_manager.workflows),
                "running_workflows": len(self.workflow_manager.executions),
            },
            "task_orchestrator": self.task_orchestrator.get_execution_stats(),
            "project_manager": self.project_manager.get_projects_summary(),
            "resource_manager": self.resource_manager.get_resource_usage(),
        }

        if self.performance_monitor:
            status["performance"] = self.performance_monitor.get_stats()

        return status

    def create_project_from_workflow(
        self,
        project_name: str,
        workflow_name: str,
        template_name: str = "ai_analysis",
        **kwargs,
    ) -> dict[str, Any]:
        """Create a project and execute a workflow for it."""
        try:
            # Create project
            self.project_manager.create_project(
                name=project_name, template_name=template_name, **kwargs
            )

            # Execute workflow for project
            result = self.execute_project_workflow(project_name, workflow_name)

            if result["success"]:
                # Add completion milestone
                self.project_manager.add_project_milestone(
                    project_name,
                    f"workflow_{workflow_name}_completed",
                    {
                        "workflow": workflow_name,
                        "execution_time": result.get("execution_time", 0),
                        "success": True,
                    },
                )

            return {"success": True, "project_created": True, "workflow_result": result}

        except Exception as e:
            logger.error(f"Failed to create project and execute workflow: {e}")
            return {"success": False, "error": str(e)}

    def health_check(self) -> dict[str, Any]:
        """Perform comprehensive health check."""
        health = {
            "overall_status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {},
            "issues": [],
        }

        try:
            # Check each component
            components = {
                "workflow_manager": self.workflow_manager,
                "task_orchestrator": self.task_orchestrator,
                "project_manager": self.project_manager,
                "resource_manager": self.resource_manager,
            }

            for name, component in components.items():
                component_health = {"status": "healthy", "details": {}}

                if hasattr(component, "health_check"):
                    try:
                        component_status = component.health_check()
                        component_health["details"] = component_status

                        if component_status.get("overall_status") != "healthy":
                            component_health["status"] = component_status.get(
                                "overall_status", "unhealthy"
                            )
                            health["issues"].extend(component_status.get("issues", []))
                    except Exception as e:
                        component_health["status"] = "error"
                        component_health["error"] = str(e)
                        health["issues"].append(f"{name}: {str(e)}")

                health["components"][name] = component_health

            # Determine overall status
            unhealthy_components = [
                name
                for name, comp in health["components"].items()
                if comp["status"] not in ["healthy", "degraded"]
            ]

            if unhealthy_components:
                health["overall_status"] = "unhealthy"
            elif health["issues"]:
                health["overall_status"] = "degraded"

        except Exception as e:
            health["overall_status"] = "error"
            health["error"] = str(e)

        return health

    def get_metrics(self) -> dict[str, Any]:
        """Get comprehensive metrics."""
        metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sessions": {"total": len(self.active_sessions), "by_status": {}},
            "workflows": {},
            "tasks": {},
            "projects": {},
            "resources": {},
        }

        # Session metrics
        for session in self.active_sessions.values():
            status = session.status
            metrics["sessions"]["by_status"][status] = (
                metrics["sessions"]["by_status"].get(status, 0) + 1
            )

        # Component metrics
        if hasattr(self.workflow_manager, "get_metrics"):
            metrics["workflows"] = self.workflow_manager.get_metrics()

        metrics["tasks"] = self.task_orchestrator.get_execution_stats()
        metrics["projects"] = self.project_manager.get_projects_summary()
        metrics["resources"] = self.resource_manager.get_resource_usage()

        return metrics

    def shutdown(self):
        """Shutdown the orchestration engine."""
        logger.info("Shutting down OrchestrationEngine...")

        # Close all active sessions
        session_ids = list(self.active_sessions.keys())
        for session_id in session_ids:
            self.close_session(session_id)

        # Stop components
        self.task_orchestrator.stop_execution()

        # Save state
        if hasattr(self.resource_manager, "save_resources"):
            self.resource_manager.save_resources()

        logger.info("OrchestrationEngine shutdown complete")

    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.shutdown()
        except (AttributeError, RuntimeError, OSError):
            # Ignore errors during cleanup - object may be partially destroyed
            pass


# MCP Tool Integration (if available)
if MCP_AVAILABLE:

    def create_orchestration_mcp_tools():
        """Create MCP tools for orchestration."""
        tools = {}

        # Workflow execution tool
        tools["execute_workflow"] = {
            "name": "execute_workflow",
            "description": "Execute a workflow with the orchestration engine",
            "input_schema": {
                "type": "object",
                "properties": {
                    "workflow_name": {
                        "type": "string",
                        "description": "Name of workflow to execute",
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Workflow parameters",
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Optional session ID",
                    },
                },
                "required": ["workflow_name"],
            },
        }

        # Project creation tool
        tools["create_project"] = {
            "name": "create_project",
            "description": "Create a new project with optional workflow execution",
            "input_schema": {
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "Name of the project",
                    },
                    "template_name": {
                        "type": "string",
                        "description": "Project template to use",
                    },
                    "workflow_name": {
                        "type": "string",
                        "description": "Optional workflow to execute",
                    },
                    "description": {
                        "type": "string",
                        "description": "Project description",
                    },
                },
                "required": ["project_name"],
            },
        }

        # Status check tool
        tools["get_system_status"] = {
            "name": "get_system_status",
            "description": "Get comprehensive system status and metrics",
            "input_schema": {"type": "object", "properties": {}, "required": []},
        }

        return tools


# Global orchestration engine instance
_orchestration_engine = None


def get_orchestration_engine() -> OrchestrationEngine:
    """Get the global orchestration engine instance."""
    global _orchestration_engine
    if _orchestration_engine is None:
        _orchestration_engine = OrchestrationEngine()
    return _orchestration_engine
