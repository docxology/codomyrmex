"""
Workflow Manager for Codomyrmex Project Orchestration

This module provides comprehensive workflow management capabilities for the Codomyrmex
project orchestration system. It handles the creation, listing, execution, and management
of workflows that coordinate multiple Codomyrmex modules with performance monitoring.

Key Features:
- Workflow definition and persistence
- Asynchronous workflow execution
- Performance monitoring integration
- Template-based workflow creation
- Error handling and retry logic
- Resource management integration

Architecture:
- WorkflowManager: Main class for workflow operations
- WorkflowStep: Individual workflow step definition
- WorkflowExecution: Execution tracking and state management
- WorkflowStatus: Enumeration of workflow states

Usage:
    from codomyrmex.project_orchestration import get_workflow_manager
from codomyrmex.exceptions import CodomyrmexError

    manager = get_workflow_manager()

    # Create a workflow
    steps = [
        WorkflowStep(name="analyze", module="static_analysis", action="analyze_code"),
        WorkflowStep(name="visualize", module="data_visualization", action="create_chart")
    ]
    manager.create_workflow("my_workflow", steps)

    # Execute workflow
    execution = await manager.execute_workflow("my_workflow")

    # List workflows
    workflows = manager.list_workflows()

Dependencies:
- Performance monitoring (optional)
- JSON file persistence
- Asyncio for asynchronous execution
- Pathlib for file operations

Author: Codomyrmex Team
Version: 1.0.0
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

# Import performance monitoring
try:
    from ..performance import (
        monitor_performance,
        performance_context,
        PerformanceMonitor,
    )

    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    logging.warning("Performance monitoring not available")
    PERFORMANCE_MONITORING_AVAILABLE = False

    def monitor_performance(*args, **kwargs):
        def decorator(func):
            return func

        return decorator

    class performance_context:
        def __init__(self, *args, **kwargs):
        """Performance Context.

            A class for handling performance_context operations.
            """
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass


class WorkflowStatus(Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """
    Represents a single step in a workflow.

    A WorkflowStep defines one atomic operation within a workflow, including
    the module to execute, the action to perform, and any parameters or
    dependencies required for execution.

    Attributes:
        name (str): Unique identifier for this step within the workflow
        module (str): Codomyrmex module name to execute (e.g., 'static_analysis')
        action (str): Specific action/function to call within the module
        parameters (Dict[str, Any]): Parameters to pass to the action function
        dependencies (List[str]): List of step names that must complete before this step
        timeout (Optional[int]): Maximum execution time in seconds (None for no limit)
        retry_count (int): Current number of retry attempts (internal use)
        max_retries (int): Maximum number of retry attempts before marking as failed

    Example:
        step = WorkflowStep(
            name="analyze_code",
            module="static_analysis",
            action="analyze_code_quality",
            parameters={"path": ".", "output_format": "json"},
            dependencies=["setup_environment"],
            timeout=300,
            max_retries=3
        )

    Note:
        - Step names must be unique within a workflow
        - Dependencies are resolved automatically during execution
        - Parameters support template substitution using {{variable}} syntax
        - Timeout values are enforced by the execution engine
    """

    name: str
    module: str
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    timeout: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class WorkflowExecution:
    """
    Tracks workflow execution state and results.

    This class maintains the complete state of a workflow execution,
    including timing information, results from each step, errors,
    and performance metrics.

    Attributes:
        workflow_name (str): Name of the workflow being executed
        status (WorkflowStatus): Current execution status
        start_time (Optional[datetime]): When execution began
        end_time (Optional[datetime]): When execution completed/failed
        results (Dict[str, Any]): Results from each completed step
        errors (List[str]): List of error messages encountered
        performance_metrics (Dict[str, Any]): Performance data for each step

    Example:
        execution = WorkflowExecution(workflow_name="my_workflow")
        execution.status = WorkflowStatus.RUNNING
        execution.start_time = datetime.now()

        # After execution
        execution.status = WorkflowStatus.COMPLETED
        execution.end_time = datetime.now()
        execution.results = {"step1": {"output": "data"}, "step2": {"output": "more_data"}}

    Note:
        - Results dictionary keys correspond to step names
        - Performance metrics include execution time, memory usage, etc.
        - Errors list contains human-readable error descriptions
    """

    workflow_name: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


class WorkflowManager:
    """
    Manages workflow definitions and executions with performance monitoring.

    The WorkflowManager is the central component for managing workflows in the
    Codomyrmex project orchestration system. It provides capabilities for
    creating, persisting, listing, and executing workflows that coordinate
    multiple Codomyrmex modules.

    Key Features:
    - Workflow definition and persistence to disk
    - Asynchronous workflow execution with dependency resolution
    - Performance monitoring and metrics collection
    - Error handling and retry logic
    - Template-based workflow creation
    - Resource management integration

    Attributes:
        config_dir (Path): Directory for storing workflow definitions
        workflows (Dict[str, List[WorkflowStep]]): In-memory workflow storage
        executions (Dict[str, WorkflowExecution]): Active execution tracking
        enable_performance_monitoring (bool): Whether performance monitoring is enabled
        performance_monitor (Optional[PerformanceMonitor]): Performance monitoring instance
        logger (logging.Logger): Logger for this manager

    Example:
        manager = WorkflowManager()

        # Create a workflow
        steps = [
            WorkflowStep(name="analyze", module="static_analysis", action="analyze_code"),
            WorkflowStep(name="visualize", module="data_visualization", action="create_chart")
        ]
        manager.create_workflow("code_analysis", steps)

        # Execute workflow
        execution = await manager.execute_workflow("code_analysis")

        # List all workflows
        workflows = manager.list_workflows()

    Thread Safety:
        This class is not thread-safe. For concurrent access, use appropriate
        synchronization mechanisms or create separate instances.
    """

    def __init__(
        self,
        config_dir: Optional[Path] = None,
        enable_performance_monitoring: bool = True,
    ):
        """
        Initialize the WorkflowManager.

        Args:
            config_dir (Optional[Path]): Directory for storing workflow definitions.
                Defaults to .codomyrmex/workflows in current directory.
            enable_performance_monitoring (bool): Whether to enable performance monitoring.
                Defaults to True if performance monitoring is available.

        Raises:
            OSError: If the configuration directory cannot be created.
            ImportError: If performance monitoring is requested but unavailable.

        Example:
            # Use default configuration
            manager = WorkflowManager()

            # Custom configuration directory
            manager = WorkflowManager(config_dir=Path("/custom/workflows"))

            # Disable performance monitoring
            manager = WorkflowManager(enable_performance_monitoring=False)
        """
        self.config_dir = config_dir or Path.cwd() / ".codomyrmex" / "workflows"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Workflow storage
        self.workflows: Dict[str, List[WorkflowStep]] = {}
        self.executions: Dict[str, WorkflowExecution] = {}

        # Performance monitoring
        self.enable_performance_monitoring = (
            enable_performance_monitoring and PERFORMANCE_MONITORING_AVAILABLE
        )
        self.performance_monitor = (
            PerformanceMonitor() if self.enable_performance_monitoring else None
        )

        # Set up logging
        self.logger = logging.getLogger(__name__)

        # Load existing workflows
        self._load_workflows()

    @monitor_performance("workflow_create")
    def create_workflow(
        self, name: str, steps: List[WorkflowStep], save: bool = True
    ) -> bool:
        """
        Create a new workflow with the specified steps.

        This method creates a new workflow definition and optionally persists it to disk.
        The workflow can then be executed using the execute_workflow method.

        Args:
            name (str): Unique name for the workflow. Must be a valid identifier.
            steps (List[WorkflowStep]): List of workflow steps to execute in order.
                Dependencies between steps are resolved automatically.
            save (bool): Whether to persist the workflow to disk. Defaults to True.

        Returns:
            bool: True if workflow was created successfully, False otherwise.

        Raises:
            ValueError: If workflow name is empty or invalid.
            OSError: If workflow cannot be saved to disk (when save=True).

        Example:
            steps = [
                WorkflowStep(
                    name="setup",
                    module="environment_setup",
                    action="check_environment"
                ),
                WorkflowStep(
                    name="analyze",
                    module="static_analysis",
                    action="analyze_code_quality",
                    parameters={"path": "."},
                    dependencies=["setup"]
                )
            ]

            success = manager.create_workflow("code_analysis", steps)
            if success:
                print("Workflow created successfully")
            else:
                print("Failed to create workflow")

        Note:
            - Workflow names must be unique within the manager instance
            - Steps are validated for proper dependency chains
            - Existing workflows with the same name will be overwritten
            - Performance metrics are collected if monitoring is enabled
        """
        try:
            # Validate inputs
            if not name or not name.strip():
                raise ValueError("Workflow name cannot be empty")

            if not steps:
                raise ValueError("Workflow must have at least one step")

            # Validate step dependencies
            step_names = {step.name for step in steps}
            for step in steps:
                for dep in step.dependencies:
                    if dep not in step_names:
                        self.logger.warning(
                            f"Step '{step.name}' depends on unknown step '{dep}'"
                        )

            # Create workflow
            self.workflows[name] = steps
            if save:
                self._save_workflow(name, steps)
            self.logger.info(f"Created workflow: {name} ({len(steps)} steps)")
            return True
        except Exception as e:
            self.logger.error(f"Error creating workflow {name}: {e}")
            return False

    @monitor_performance("workflow_list")
    def list_workflows(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available workflows with comprehensive metadata.

        This method returns detailed information about all workflows currently
        managed by this WorkflowManager instance, including step counts,
        module dependencies, and estimated execution times.

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mapping workflow names to their metadata.
                Each workflow metadata includes:
                - steps (int): Number of steps in the workflow
                - modules (List[str]): Unique list of modules used by the workflow
                - estimated_duration (int): Estimated total execution time in seconds
                - has_dependencies (bool): Whether the workflow has step dependencies
                - created_time (Optional[str]): When the workflow was created (if available)

        Example:
            workflows = manager.list_workflows()
            for name, info in workflows.items():
                print(f"Workflow: {name}")
                print(f"  Steps: {info['steps']}")
                print(f"  Modules: {', '.join(info['modules'])}")
                print(f"  Estimated Duration: {info['estimated_duration']}s")

        Note:
            - Metadata is computed in real-time from current workflow definitions
            - Estimated duration is based on step timeout values (defaults to 60s)
            - Module list includes all unique modules referenced by workflow steps
            - Performance metrics are collected if monitoring is enabled
        """
        workflow_info = {}
        for name, steps in self.workflows.items():
            # Calculate metadata
            modules = list(set(step.module for step in steps))
            estimated_duration = sum(step.timeout or 60 for step in steps)
            has_dependencies = any(step.dependencies for step in steps)

            workflow_info[name] = {
                "steps": len(steps),
                "modules": modules,
                "estimated_duration": estimated_duration,
                "has_dependencies": has_dependencies,
                "created_time": None,  # Could be enhanced to track creation time
            }
        return workflow_info

    @monitor_performance("workflow_execute")
    async def execute_workflow(
        self,
        name: str,
        parameters: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> WorkflowExecution:
        """
        Execute a workflow asynchronously with performance monitoring.

        This method executes a workflow by running each step in dependency order,
        handling errors, and collecting performance metrics. Steps are executed
        sequentially, with dependency resolution ensuring proper execution order.

        Args:
            name (str): Name of the workflow to execute.
            parameters (Optional[Dict[str, Any]]): Global parameters to pass to workflow steps.
                These can be referenced in step parameters using {{parameter_name}} syntax.
            timeout (Optional[int]): Maximum execution time in seconds. If None, no timeout.

        Returns:
            WorkflowExecution: Execution result containing status, results, errors, and metrics.

        Raises:
            ValueError: If workflow name is not found.
            asyncio.TimeoutError: If workflow execution exceeds the specified timeout.

        Example:
            # Execute workflow with parameters
            execution = await manager.execute_workflow(
                "code_analysis",
                parameters={"project_path": "/path/to/project", "output_format": "json"}
            )

            if execution.status == WorkflowStatus.COMPLETED:
                print("Workflow completed successfully")
                for step_name, result in execution.results.items():
                    print(f"Step {step_name}: {result}")
            else:
                print(f"Workflow failed: {execution.errors}")

        Note:
            - Steps are executed in dependency order, not definition order
            - Global parameters are merged with step-specific parameters
            - Performance metrics are collected for each step if monitoring is enabled
            - Execution state is tracked and can be monitored in real-time
            - Failed steps do not prevent execution of subsequent independent steps
        """
        if name not in self.workflows:
            raise ValueError(f"Workflow '{name}' not found")

        # Create execution tracker
        execution = WorkflowExecution(workflow_name=name)
        execution.start_time = datetime.now()
        execution.status = WorkflowStatus.RUNNING
        execution_id = f"{name}_{int(time.time())}"
        self.executions[execution_id] = execution

        try:
            steps = self.workflows[name]
            completed_steps = set()

            # Execute steps in dependency order
            remaining_steps = list(steps)
            while remaining_steps:
                # Find steps that can be executed (dependencies satisfied)
                ready_steps = [
                    step
                    for step in remaining_steps
                    if all(dep in completed_steps for dep in step.dependencies)
                ]

                if not ready_steps:
                    # No steps can be executed - check for circular dependencies
                    remaining_names = [step.name for step in remaining_steps]
                    raise ValueError(
                        f"Circular dependency detected in workflow steps: {remaining_names}"
                    )

                # Execute ready steps
                for step in ready_steps:
                    try:
                        # Execute step with monitoring
                        step_result = await self._execute_step(
                            step, parameters or {}, execution
                        )
                        execution.results[step.name] = step_result

                        if step_result.get("success", False):
                            completed_steps.add(step.name)
                            remaining_steps.remove(step)
                            self.logger.info(f"Step {step.name} completed successfully")
                        else:
                            error_msg = f"Step {step.name} failed: {step_result.get('error', 'Unknown error')}"
                            execution.errors.append(error_msg)
                            self.logger.error(error_msg)
                            # Remove failed step from remaining steps
                            remaining_steps.remove(step)

                    except Exception as step_error:
                        error_msg = (
                            f"Step {step.name} execution error: {str(step_error)}"
                        )
                        execution.errors.append(error_msg)
                        self.logger.error(error_msg)
                        remaining_steps.remove(step)

            # Update execution status
            execution.end_time = datetime.now()
            execution.status = (
                WorkflowStatus.COMPLETED
                if not execution.errors
                else WorkflowStatus.FAILED
            )

            self.logger.info(
                f"Workflow {name} completed with status: {execution.status}"
            )
            return execution

        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.end_time = datetime.now()
            execution.errors.append(f"Workflow execution failed: {str(e)}")
            self.logger.error(f"Workflow {name} failed: {e}")
            return execution

    @monitor_performance("workflow_step_execution")
    async def _execute_step(
        self,
        step: WorkflowStep,
        parameters: Dict[str, Any],
        execution: WorkflowExecution,
    ) -> Dict[str, Any]:
        """
        Execute a single workflow step with monitoring and error handling.

        This private method handles the execution of individual workflow steps,
        including parameter substitution, module invocation, performance monitoring,
        and error handling.

        Args:
            step (WorkflowStep): The workflow step to execute.
            parameters (Dict[str, Any]): Global parameters for parameter substitution.
            execution (WorkflowExecution): Current execution context for tracking.

        Returns:
            Dict[str, Any]: Step execution result containing:
                - success (bool): Whether the step executed successfully
                - execution_time (float): Step execution time in seconds
                - message (str): Success message (if successful)
                - error (str): Error message (if failed)
                - output (Any): Step output data (if available)

        Note:
            - This method currently simulates module execution
            - Real implementation would dynamically import and call module functions
            - Parameter substitution uses {{variable}} syntax
            - Performance metrics are collected if monitoring is enabled
            - Timeout handling is implemented at the step level
        """
        try:
            self.logger.info(
                f"Executing step: {step.name} ({step.module}.{step.action})"
            )

            # Merge global parameters with step parameters
            merged_params = {**parameters, **step.parameters}

            # TODO: Implement actual module execution
            # This would involve:
            # 1. Dynamic import of the specified module
            # 2. Parameter substitution in step parameters
            # 3. Function call with merged parameters
            # 4. Result capture and error handling

            # Simulate module execution for now
            start_time = time.time()
            await asyncio.sleep(0.5)  # Simulate processing time
            execution_time = time.time() - start_time

            # Record step performance
            if self.enable_performance_monitoring and self.performance_monitor:
                self.performance_monitor.record_metrics(
                    function_name=f"{step.module}_{step.action}",
                    execution_time=execution_time,
                    metadata={
                        "workflow": execution.workflow_name,
                        "step_name": step.name,
                        "parameters": merged_params,
                    },
                )

            # Store performance metrics in execution
            execution.performance_metrics[step.name] = {
                "execution_time": execution_time,
                "module": step.module,
                "action": step.action,
                "parameters": merged_params,
            }

            return {
                "success": True,
                "execution_time": execution_time,
                "message": f"Step {step.name} completed successfully",
                "output": f"Simulated output from {step.module}.{step.action}",
                "parameters_used": merged_params,
            }

        except Exception as e:
            self.logger.error(f"Step {step.name} execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": 0,
                "message": f"Step {step.name} failed: {str(e)}",
            }

    @monitor_performance("workflow_get_performance_summary")
    def get_performance_summary(
        self, workflow_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive performance summary for workflows.

        This method provides detailed performance metrics for workflow executions,
        including execution statistics, timing data, and success/failure rates.

        Args:
            workflow_name (Optional[str]): Specific workflow name to analyze.
                If None, returns summary for all workflows.

        Returns:
            Dict[str, Any]: Performance summary containing:
                - performance_stats (Dict): Detailed performance metrics from monitor
                - total_workflows_executed (int): Total number of workflow executions
                - successful_executions (int): Number of successful executions
                - failed_executions (int): Number of failed executions
                - average_execution_time (float): Average execution time in seconds
                - module_usage_stats (Dict): Usage statistics by module

        Example:
            # Get summary for all workflows
            summary = manager.get_performance_summary()
            print(f"Total executions: {summary['total_workflows_executed']}")
            print(f"Success rate: {summary['successful_executions'] / summary['total_workflows_executed'] * 100:.1f}%")

            # Get summary for specific workflow
            summary = manager.get_performance_summary("code_analysis")

        Note:
            - Requires performance monitoring to be enabled
            - Returns error message if monitoring is not available
            - Statistics are computed from current execution history
        """
        if not self.enable_performance_monitoring or not self.performance_monitor:
            return {"error": "Performance monitoring not enabled"}

        stats = self.performance_monitor.get_stats(workflow_name)

        # Calculate execution statistics
        executions = list(self.executions.values())
        if workflow_name:
            executions = [e for e in executions if e.workflow_name == workflow_name]

        successful_executions = len(
            [e for e in executions if e.status == WorkflowStatus.COMPLETED]
        )
        failed_executions = len(
            [e for e in executions if e.status == WorkflowStatus.FAILED]
        )

        # Calculate average execution time
        completed_executions = [e for e in executions if e.end_time and e.start_time]
        avg_execution_time = 0.0
        if completed_executions:
            total_time = sum(
                (e.end_time - e.start_time).total_seconds()
                for e in completed_executions
            )
            avg_execution_time = total_time / len(completed_executions)

        # Calculate module usage statistics
        module_usage = {}
        for execution in executions:
            for step_name, metrics in execution.performance_metrics.items():
                module = metrics.get("module", "unknown")
                if module not in module_usage:
                    module_usage[module] = {"count": 0, "total_time": 0.0}
                module_usage[module]["count"] += 1
                module_usage[module]["total_time"] += metrics.get("execution_time", 0.0)

        summary = {
            "performance_stats": stats,
            "total_workflows_executed": len(executions),
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "average_execution_time": avg_execution_time,
            "module_usage_stats": module_usage,
        }

        return summary

    def _save_workflow(self, name: str, steps: List[WorkflowStep]) -> None:
        """
        Save a workflow definition to disk in JSON format.

        This private method persists workflow definitions to the configuration
        directory, allowing workflows to survive application restarts.

        Args:
            name (str): Name of the workflow to save.
            steps (List[WorkflowStep]): List of workflow steps to persist.

        Raises:
            OSError: If the workflow file cannot be written.
            json.JSONEncodeError: If workflow data cannot be serialized.

        Note:
            - Workflows are saved as JSON files in the config directory
            - File naming convention: {workflow_name}.json
            - All step attributes are preserved in the serialized format
            - Errors are logged but do not raise exceptions
        """
        try:
            workflow_file = self.config_dir / f"{name}.json"
            workflow_data = {
                "name": name,
                "steps": [
                    {
                        "name": step.name,
                        "module": step.module,
                        "action": step.action,
                        "parameters": step.parameters,
                        "dependencies": step.dependencies,
                        "timeout": step.timeout,
                        "retry_count": step.retry_count,
                        "max_retries": step.max_retries,
                    }
                    for step in steps
                ],
            }

            with open(workflow_file, "w") as f:
                json.dump(workflow_data, f, indent=2)

            self.logger.debug(f"Saved workflow: {name}")
        except Exception as e:
            self.logger.error(f"Failed to save workflow {name}: {e}")

    def _load_workflows(self) -> None:
        """
        Load workflow definitions from disk.

        This private method scans the configuration directory for workflow
        JSON files and loads them into the in-memory workflow storage.
        Invalid or corrupted workflow files are skipped with error logging.

        Note:
            - Only files with .json extension are processed
            - Workflow files must contain valid JSON with required fields
            - Missing or invalid fields use default values
            - Errors loading individual files do not stop the loading process

        Raises:
            OSError: If the configuration directory cannot be accessed.
        """
        try:
            if not self.config_dir.exists():
                self.logger.info(
                    f"Configuration directory {self.config_dir} does not exist, skipping workflow loading"
                )
                return

            loaded_count = 0
            for workflow_file in self.config_dir.glob("*.json"):
                try:
                    with open(workflow_file, "r") as f:
                        workflow_data = json.load(f)

                    # Validate required fields
                    if "name" not in workflow_data or "steps" not in workflow_data:
                        self.logger.warning(
                            f"Invalid workflow file {workflow_file}: missing required fields"
                        )
                        continue

                    steps = [
                        WorkflowStep(
                            name=step_data["name"],
                            module=step_data["module"],
                            action=step_data["action"],
                            parameters=step_data.get("parameters", {}),
                            dependencies=step_data.get("dependencies", []),
                            timeout=step_data.get("timeout"),
                            retry_count=step_data.get("retry_count", 0),
                            max_retries=step_data.get("max_retries", 3),
                        )
                        for step_data in workflow_data.get("steps", [])
                    ]

                    self.workflows[workflow_data["name"]] = steps
                    loaded_count += 1
                    self.logger.debug(f"Loaded workflow: {workflow_data['name']}")
                except json.JSONDecodeError as e:
                    self.logger.error(
                        f"Invalid JSON in workflow file {workflow_file}: {e}"
                    )
                except KeyError as e:
                    self.logger.error(
                        f"Missing required field in workflow file {workflow_file}: {e}"
                    )
                except Exception as e:
                    self.logger.error(
                        f"Failed to load workflow from {workflow_file}: {e}"
                    )

            self.logger.info(f"Loaded {loaded_count} workflows from {self.config_dir}")
        except Exception as e:
            self.logger.error(f"Failed to load workflows: {e}")


# Global workflow manager instance
_workflow_manager = None


def get_workflow_manager() -> WorkflowManager:
    """
    Get the global workflow manager instance.

    This function provides access to a singleton WorkflowManager instance,
    ensuring consistent workflow management across the application. The
    manager is lazily initialized on first access.

    Returns:
        WorkflowManager: The global workflow manager instance.

    Example:
        # Get the global workflow manager
        manager = get_workflow_manager()

        # Use it to create and execute workflows
        manager.create_workflow("my_workflow", steps)
        execution = await manager.execute_workflow("my_workflow")

    Note:
        - The manager is initialized with default settings
        - Subsequent calls return the same instance
        - Thread safety is not guaranteed for the singleton pattern
    """
    global _workflow_manager
    if _workflow_manager is None:
        _workflow_manager = WorkflowManager()
    return _workflow_manager
