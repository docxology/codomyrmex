"""
Orchestration Engine for Codomyrmex

This is the main orchestration engine that coordinates all project management,
task orchestration, and resource management components. It provides a unified
interface for complex multi-module workflows.
"""

import logging
import threading
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

# Import Codomyrmex modules
try:
    from codomyrmex.logging_monitoring import get_logger

    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

try:
    from codomyrmex.performance import PerformanceMonitor, monitor_performance

    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False

    def monitor_performance(*args, **kwargs):
        """Decorator for performance monitoring (fallback)."""

        def decorator(func):
            return func

        return decorator


import importlib.util as _ilu

MCP_AVAILABLE = _ilu.find_spec("codomyrmex.model_context_protocol") is not None

# Import orchestration components
from .project_manager import (
    ProjectManager,
    ProjectType,
    get_project_manager,
)
from .resource_manager import ResourceManager, get_resource_manager
from .task_orchestrator import Task, TaskOrchestrator, get_task_orchestrator
from .workflow_manager import (
    WorkflowExecution,
    WorkflowManager,
    WorkflowStatus,
    WorkflowStep,
    get_workflow_manager,
)


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
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
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
            except Exception as e:
                logger.warning(
                    "Failed to parse created_at '%s': %s", data["created_at"], e
                )
        if data.get("status"):
            try:
                sess.status = SessionStatus(data["status"])
            except Exception as _exc:
                sess.status = SessionStatus.PENDING
        return sess


def _optional_path(value: Any) -> Path | None:
    return Path(value) if value is not None else None


def _workflow_result(execution: WorkflowExecution) -> dict[str, Any]:
    """Convert a finished workflow execution into the engine's result dict."""
    return {
        "success": execution.success,
        "status": execution.status.value,
        "execution_id": execution.execution_id,
        "result": execution.step_results,
        "error": execution.error,
        "execution_time": execution.duration,
        "steps_executed": sum(
            1
            for step in execution.step_results.values()
            if step.get("start_time") is not None
        ),
    }


class OrchestrationEngine:
    """Main orchestration engine coordinating all components."""

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        *,
        workflow_manager: WorkflowManager | None = None,
        task_orchestrator: TaskOrchestrator | None = None,
        project_manager: ProjectManager | None = None,
        resource_manager: ResourceManager | None = None,
    ):
        """Initialize the orchestration engine.

        Components that are not passed in are created from ``config`` and wired
        together: tasks allocate from the engine's resource manager and
        workflows run on the engine's task orchestrator. :meth:`shutdown` stops
        the task orchestrator only if the engine created it.

        Args:
            config: Optional settings: ``workflows_dir``, ``projects_dir``,
                ``max_workers``.
            workflow_manager: Workflow manager to use.
            task_orchestrator: Task orchestrator to use.
            project_manager: Project manager to use.
            resource_manager: Resource manager to use.
        """
        self.config = config or {}
        self._owns_task_orchestrator = task_orchestrator is None

        # Initialize component managers
        self.resource_manager = (
            resource_manager if resource_manager is not None else ResourceManager()
        )
        self.task_orchestrator = (
            task_orchestrator
            if task_orchestrator is not None
            else TaskOrchestrator(
                max_workers=self.config.get("max_workers", 4),
                resource_manager=self.resource_manager,
            )
        )
        self.workflow_manager = (
            workflow_manager
            if workflow_manager is not None
            else WorkflowManager(
                config_dir=_optional_path(self.config.get("workflows_dir")),
                task_orchestrator=self.task_orchestrator,
            )
        )
        self.project_manager = (
            project_manager
            if project_manager is not None
            else ProjectManager(projects_root=self.config.get("projects_dir"))
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
        self.task_orchestrator.start_processing()

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
                    logger.error("Error in event handler for %s: %s", event, e)

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
        logger.info("Created orchestration session: %s", context.session_id)

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
                context.status = SessionStatus.COMPLETED
                context.completed_at = datetime.now(UTC)

                # Cleanup session resources
                self.resource_manager.deallocate_resources(session_id)

                del self.active_sessions[session_id]

                self.emit_event("session_closed", {"session_id": session_id})
                logger.info("Closed orchestration session: %s", session_id)
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

        context.started_at = datetime.now(UTC)
        context.status = SessionStatus.ACTIVE

        try:
            # Allocate resources if needed
            if context.resource_requirements:
                allocated = self.resource_manager.allocate_resources(
                    session_id, context.resource_requirements, context.timeout_seconds
                )
                if not allocated:
                    context.status = SessionStatus.FAILED
                    context.completed_at = datetime.now(UTC)
                    return {
                        "success": False,
                        "error": "Failed to allocate required resources",
                    }

            # WorkflowManager.execute_workflow is synchronous: it returns once
            # every step has finished.
            try:
                execution = self.workflow_manager.execute_workflow(
                    workflow_name, **params
                )
            except (ValueError, NotImplementedError) as e:
                context.status = SessionStatus.FAILED
                context.completed_at = datetime.now(UTC)
                logger.error("Workflow execution failed: %s", e)
                return {"success": False, "error": f"Workflow execution failed: {e}"}

            result = _workflow_result(execution)

            # Update context
            context.status = (
                SessionStatus.COMPLETED if result["success"] else SessionStatus.FAILED
            )
            context.completed_at = datetime.now(UTC)

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
            context.status = SessionStatus.FAILED
            context.completed_at = datetime.now(UTC)
            logger.error("Workflow execution failed: %s", e)

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

        unknown_deps = [
            dep
            for dep in task.dependencies
            if self.task_orchestrator.get_task(dep) is None
        ]
        if unknown_deps:
            return {
                "success": False,
                "error": f"Task {task.name} depends on unknown task ids {unknown_deps}",
            }

        try:
            # Add task to orchestrator and wait for it to finish
            task_id = self.task_orchestrator.submit_task(task)
            finished = self.task_orchestrator.wait_for_tasks(
                [task_id], timeout=context.timeout_seconds
            )
            if not finished:
                self.task_orchestrator.cancel_task(task_id)
                return {
                    "success": False,
                    "error": (
                        f"Task {task.name} did not finish within "
                        f"{context.timeout_seconds}s and was cancelled"
                    ),
                    "task_id": task_id,
                }

            result = self.task_orchestrator.get_task_result(task_id)

            return {
                "success": result.success if result else False,
                "result": result.to_dict() if result else None,
                "error": result.error if result else "No result recorded",
                "task_id": task_id,
            }

        except Exception as e:
            logger.error("Task execution failed: %s", e)
            return {"success": False, "error": str(e)}

    @monitor_performance(function_name="execute_project_workflow")
    def execute_project_workflow(
        self,
        project_name: str,
        workflow_name: str,
        session_id: str | None = None,
        **params,
    ) -> dict[str, Any]:
        """Execute a workflow for a registered project and record the outcome.

        The workflow runs through :meth:`execute_workflow` (``params`` are passed
        to its steps unchanged). Every run, successful or not, updates the
        project's metrics: ``workflow_executions``,
        ``successful_workflow_executions``, ``last_workflow``,
        ``last_workflow_success`` and ``last_workflow_execution``.
        """
        if not session_id:
            session_id = self.create_session()

        context = self.get_session(session_id)
        if not context:
            return {"success": False, "error": f"Session {session_id} not found"}

        project = self.project_manager.get_project(project_name)
        if project is None:
            return {"success": False, "error": f"Project {project_name} not found"}

        result = self.execute_workflow(workflow_name, session_id=session_id, **params)
        result["project_name"] = project_name

        executions = project.metrics.get("workflow_executions", 0) + 1
        successes = project.metrics.get("successful_workflow_executions", 0) + int(
            result["success"]
        )
        self.project_manager.update_project_metrics(
            project_name,
            {
                "workflow_executions": executions,
                "successful_workflow_executions": successes,
                "last_workflow": workflow_name,
                "last_workflow_success": result["success"],
                "last_workflow_execution": datetime.now(UTC).isoformat(),
            },
        )
        return result

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
            # Parse workflow definition. Dependencies may be given per step
            # ("dependencies" key) and/or in the top-level mapping.
            dependencies = workflow_definition.get("dependencies", {})
            unknown = sorted(
                set(dependencies)
                - {step["name"] for step in workflow_definition.get("steps", [])}
            )
            if unknown:
                raise ValueError(f"Dependencies given for unknown steps: {unknown}")

            steps = []
            for step in workflow_definition.get("steps", []):
                step_deps = list(dependencies.get(step["name"], []))
                step_deps += [
                    dep for dep in step.get("dependencies", []) if dep not in step_deps
                ]
                steps.append(
                    WorkflowStep(
                        name=step["name"],
                        module=step["module"],
                        action=step["action"],
                        parameters=step.get("parameters", {}),
                        dependencies=step_deps,
                    )
                )

            execution = self.workflow_manager.execute_steps(
                workflow_definition.get("name", "complex_workflow"),
                steps,
                timeout=context.timeout_seconds,
            )
        except (KeyError, ValueError, NotImplementedError) as e:
            logger.error("Complex workflow execution failed: %s", e)
            return {"success": False, "error": f"Invalid workflow definition: {e}"}

        result: dict[str, Any] = {
            "success": execution.success,
            "results": execution.step_results,
            "execution_stats": self.task_orchestrator.get_execution_stats(),
        }
        if execution.error:
            result["error"] = execution.error
        return result

    def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status."""
        status = {
            "timestamp": datetime.now(UTC).isoformat(),
            "orchestration_engine": {
                "active_sessions": len(self.active_sessions),
                "event_handlers": {
                    event: len(handlers)
                    for event, handlers in self.event_handlers.items()
                },
            },
            "workflow_manager": {
                "total_workflows": len(self.workflow_manager.workflows),
                "running_workflows": sum(
                    1
                    for execution in self.workflow_manager.executions.values()
                    if execution.status == WorkflowStatus.RUNNING
                ),
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
        description: str = "",
        session_id: str | None = None,
        **params,
    ) -> dict[str, Any]:
        """Create a project and execute a workflow for it.

        Args:
            project_name: Name of the project to create.
            workflow_name: Registered workflow to run for the project.
            template_name: Project template; its name is the
                :class:`ProjectType` value (``ai_analysis``, ``web_application``,
                ``data_pipeline``, ...).
            description: Project description.
            session_id: Optional orchestration session.
            **params: Parameters passed to the workflow's steps.

        Returns:
            ``success`` mirrors the workflow outcome; ``project_created`` and
            ``project`` describe the created project and ``workflow_result``
            holds the :meth:`execute_project_workflow` result. A successful run
            records a ``workflow_<name>_completed`` milestone on the project.
        """
        try:
            project_type = ProjectType(template_name)
        except ValueError:
            return {
                "success": False,
                "project_created": False,
                "error": (
                    f"Unknown project template '{template_name}'; expected one of "
                    f"{[t.value for t in ProjectType]}"
                ),
            }

        project = self.project_manager.create_project(
            name=project_name, type=project_type, description=description
        )
        if project is None:
            return {
                "success": False,
                "project_created": False,
                "error": (
                    f"Project {project_name} could not be created under "
                    f"{self.project_manager.projects_root} (already registered, "
                    "directory exists, or scaffolding failed; see logs)"
                ),
            }

        result = self.execute_project_workflow(
            project_name, workflow_name, session_id=session_id, **params
        )

        if result["success"]:
            self.project_manager.add_project_milestone(
                project_name,
                f"workflow_{workflow_name}_completed",
                {
                    "workflow": workflow_name,
                    "execution_time": result.get("execution_time"),
                    "success": True,
                },
            )

        return {
            "success": result["success"],
            "project_created": True,
            "project": project.to_dict(),
            "workflow_result": result,
            **({"error": result["error"]} if result.get("error") else {}),
        }

    def health_check(self) -> dict[str, Any]:
        """Perform comprehensive health check."""
        health = {
            "overall_status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
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
                        component_status = component.health_check()  # type: ignore
                        component_health["details"] = component_status

                        if component_status.get("overall_status") != "healthy":
                            component_health["status"] = component_status.get(
                                "overall_status", "unhealthy"
                            )
                            health["issues"].extend(component_status.get("issues", []))
                    except Exception as e:
                        component_health["status"] = "error"
                        component_health["error"] = str(e)
                        health["issues"].append(f"{name}: {e!s}")

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
            "timestamp": datetime.now(UTC).isoformat(),
            "sessions": {"total": len(self.active_sessions), "by_status": {}},
            "workflows": {},
            "tasks": {},
            "projects": {},
            "resources": {},
        }

        # Session metrics
        for session in self.active_sessions.values():
            status = session.status.value
            metrics["sessions"]["by_status"][status] = (
                metrics["sessions"]["by_status"].get(status, 0) + 1
            )

        # Component metrics
        metrics["workflows"] = self.workflow_manager.get_performance_summary()
        metrics["tasks"] = self.task_orchestrator.get_execution_stats()
        metrics["projects"] = self.project_manager.get_projects_summary()
        metrics["resources"] = self.resource_manager.get_resource_usage()

        return metrics

    def shutdown(self):
        """Shutdown the orchestration engine."""
        try:
            logger.info("Shutting down OrchestrationEngine...")
        except (ValueError, OSError) as e:
            print(f"Warning: log stream error during shutdown: {e}")
            # stream already closed at interpreter shutdown

        # Close all active sessions
        session_ids = list(self.active_sessions.keys())
        for session_id in session_ids:
            try:
                self.close_session(session_id)
            except (ValueError, OSError) as e:
                print(
                    f"Warning: error closing session {session_id} during shutdown: {e}"
                )

        # Stop components (a shared, injected orchestrator keeps running)
        if self._owns_task_orchestrator:
            self.task_orchestrator.stop_execution()

        # Save state
        if hasattr(self.resource_manager, "save_resources"):
            self.resource_manager.save_resources()  # type: ignore

        try:
            logger.info("OrchestrationEngine shutdown complete")
        except (ValueError, OSError) as e:
            print(f"Warning: log stream error during shutdown: {e}")

    def __del__(self):
        """Cleanup on deletion."""
        previous_raise_exceptions = logging.raiseExceptions
        logging.raiseExceptions = False
        try:
            self.shutdown()
        except (AttributeError, RuntimeError, OSError, ValueError) as e:
            # Ignore errors during cleanup - object may be partially destroyed
            try:
                print(f"Warning: error during OrchestrationEngine cleanup: {e}")
            except (ValueError, OSError):
                pass
        finally:
            logging.raiseExceptions = previous_raise_exceptions


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
    """Get the global orchestration engine instance.

    The global engine is built on the global component singletons
    (``get_workflow_manager()``, ``get_task_orchestrator()``,
    ``get_project_manager()``, ``get_resource_manager()``), so workflows and
    projects registered through those accessors are visible to it.
    """
    global _orchestration_engine
    if _orchestration_engine is None:
        _orchestration_engine = OrchestrationEngine(
            workflow_manager=get_workflow_manager(),
            task_orchestrator=get_task_orchestrator(),
            project_manager=get_project_manager(),
            resource_manager=get_resource_manager(),
        )
    return _orchestration_engine
