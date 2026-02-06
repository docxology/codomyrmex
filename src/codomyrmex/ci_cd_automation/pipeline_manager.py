"""
Pipeline Manager for Codomyrmex CI/CD Automation Module.

Provides comprehensive pipeline orchestration, management, and execution capabilities.
"""

import asyncio
import concurrent.futures
import fnmatch
import json
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import aiohttp
import yaml

from codomyrmex.logging_monitoring.logger_config import get_logger

# Add project root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

logger = get_logger(__name__)


class PipelineStatus(Enum):
    """Pipeline execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class StageStatus(Enum):
    """Pipeline stage status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class JobStatus(Enum):
    """Job execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


@dataclass
class PipelineJob:
    """Individual job within a pipeline stage."""

    name: str
    commands: list[str]
    environment: dict[str, str] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    timeout: int = 3600  # 1 hour
    retry_count: int = 0
    allow_failure: bool = False
    status: JobStatus = JobStatus.PENDING
    start_time: datetime | None = None
    end_time: datetime | None = None
    output: str = ""
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert job to dictionary format."""
        return {
            "name": self.name,
            "commands": self.commands,
            "environment": self.environment,
            "artifacts": self.artifacts,
            "dependencies": self.dependencies,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "allow_failure": self.allow_failure,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "output": self.output,
            "error": self.error,
        }


@dataclass
class PipelineStage:
    """Pipeline stage containing multiple jobs."""

    name: str
    jobs: list[PipelineJob] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    environment: dict[str, str] = field(default_factory=dict)
    allow_failure: bool = False
    parallel: bool = True
    status: StageStatus = StageStatus.PENDING
    start_time: datetime | None = None
    end_time: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert stage to dictionary format."""
        return {
            "name": self.name,
            "jobs": [job.to_dict() for job in self.jobs],
            "dependencies": self.dependencies,
            "environment": self.environment,
            "allow_failure": self.allow_failure,
            "parallel": self.parallel,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }


@dataclass
class Pipeline:
    """Complete CI/CD pipeline definition."""

    name: str
    description: str = ""
    stages: list[PipelineStage] = field(default_factory=list)
    variables: dict[str, str] = field(default_factory=dict)
    triggers: dict[str, Any] = field(default_factory=dict)
    timeout: int = 7200  # 2 hours
    status: PipelineStatus = PipelineStatus.PENDING
    created_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration: float = 0.0

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        """Convert pipeline to dictionary format."""
        return {
            "name": self.name,
            "description": self.description,
            "stages": [stage.to_dict() for stage in self.stages],
            "variables": self.variables,
            "triggers": self.triggers,
            "timeout": self.timeout,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration": self.duration,
        }


class PipelineManager:
    """
    Comprehensive pipeline manager for CI/CD orchestration.

    Features:
    - Pipeline creation and configuration
    - Parallel and sequential job execution
    - Dependency resolution
    - Artifact management
    - Failure handling and retries
    - Real-time monitoring
    """

    def __init__(self, workspace_dir: str | None = None):
        """
        Initialize the pipeline manager.

        Args:
            workspace_dir: Directory for pipeline workspaces and artifacts
        """
        self.workspace_dir = workspace_dir or os.path.join(os.getcwd(), ".pipelines")
        self.pipelines: dict[str, Pipeline] = {}
        self.active_executions: dict[str, asyncio.Task] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)

        # Create workspace directory
        os.makedirs(self.workspace_dir, exist_ok=True)
        os.makedirs(os.path.join(self.workspace_dir, "artifacts"), exist_ok=True)

    def create_pipeline(self, config_path: str) -> Pipeline:
        """
        Create a pipeline from configuration file.

        Args:
            config_path: Path to pipeline configuration file (YAML or JSON)

        Returns:
            Pipeline: Created pipeline object
        """
        try:
            with open(config_path) as f:
                if config_path.endswith(".yaml") or config_path.endswith(".yml"):
                    config = yaml.safe_load(f)
                else:
                    config = json.load(f)

            pipeline = self._parse_pipeline_config(config)
            self.pipelines[pipeline.name] = pipeline

            logger.info(f"Created pipeline: {pipeline.name}")
            return pipeline

        except Exception as e:
            logger.error(f"Failed to create pipeline from {config_path}: {e}")
            raise

    def _parse_pipeline_config(self, config: dict[str, Any]) -> Pipeline:
        """Parse pipeline configuration into Pipeline object."""
        pipeline = Pipeline(
            name=config.get("name", "unnamed_pipeline"),
            description=config.get("description", ""),
            variables=config.get("variables", {}),
            triggers=config.get("triggers", {}),
            timeout=config.get("timeout", 7200),
        )

        # Parse stages
        for stage_config in config.get("stages", []):
            stage = PipelineStage(
                name=stage_config.get("name", "unnamed_stage"),
                dependencies=stage_config.get("dependencies", []),
                environment=stage_config.get("environment", {}),
                allow_failure=stage_config.get("allow_failure", False),
                parallel=stage_config.get("parallel", True),
            )

            # Parse jobs
            for job_config in stage_config.get("jobs", []):
                job = PipelineJob(
                    name=job_config.get("name", "unnamed_job"),
                    commands=job_config.get("commands", []),
                    environment=job_config.get("environment", {}),
                    artifacts=job_config.get("artifacts", []),
                    dependencies=job_config.get("dependencies", []),
                    timeout=job_config.get("timeout", 3600),
                    retry_count=job_config.get("retry_count", 0),
                    allow_failure=job_config.get("allow_failure", False),
                )
                stage.jobs.append(job)

            pipeline.stages.append(stage)

        return pipeline

    async def run_pipeline_async(
        self, pipeline_name: str, variables: dict[str, str] | None = None
    ) -> Pipeline:
        """
        Run a pipeline asynchronously.

        Args:
            pipeline_name: Name of the pipeline to run
            variables: Runtime variables to override

        Returns:
            Pipeline: Updated pipeline with execution results
        """
        if pipeline_name not in self.pipelines:
            raise ValueError(f"Pipeline '{pipeline_name}' not found")

        pipeline = self.pipelines[pipeline_name]

        # Override variables if provided
        if variables:
            pipeline.variables.update(variables)

        # Reset pipeline state
        pipeline.status = PipelineStatus.RUNNING
        pipeline.started_at = datetime.now(timezone.utc)

        logger.info(f"Starting pipeline execution: {pipeline_name}")

        try:
            # Execute stages in dependency order
            await self._execute_pipeline_stages(pipeline)

            # Calculate final status
            pipeline.finished_at = datetime.now(timezone.utc)
            if pipeline.started_at:
                pipeline.duration = (
                    pipeline.finished_at - pipeline.started_at
                ).total_seconds()

            if any(stage.status == StageStatus.FAILURE for stage in pipeline.stages):
                pipeline.status = PipelineStatus.FAILURE
            else:
                pipeline.status = PipelineStatus.SUCCESS

            logger.info(
                f"Pipeline {pipeline_name} completed with status: {pipeline.status.value}"
            )

        except Exception as e:
            pipeline.status = PipelineStatus.FAILURE
            pipeline.finished_at = datetime.now(timezone.utc)
            if pipeline.started_at:
                pipeline.duration = (
                    pipeline.finished_at - pipeline.started_at
                ).total_seconds()

            logger.error(f"Pipeline {pipeline_name} failed: {e}")

        return pipeline

    def run_pipeline(
        self, pipeline_name: str, variables: dict[str, str] | None = None
    ) -> Pipeline:
        """
        Run a pipeline synchronously.

        Args:
            pipeline_name: Name of the pipeline to run
            variables: Runtime variables to override

        Returns:
            Pipeline: Updated pipeline with execution results
        """
        # Create event loop if one doesn't exist
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, we need to handle differently

                def run_async():

                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(
                            self.run_pipeline_async(pipeline_name, variables)
                        )
                    finally:
                        new_loop.close()

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_async)
                    return future.result(timeout=7200)  # 2 hour timeout
            else:
                return loop.run_until_complete(
                    self.run_pipeline_async(pipeline_name, variables)
                )
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(self.run_pipeline_async(pipeline_name, variables))

    async def _execute_pipeline_stages(self, pipeline: Pipeline):
        """Execute pipeline stages in dependency order."""
        # Simple dependency resolution (can be enhanced)
        executed_stages = set()

        for stage in pipeline.stages:
            # Check if all dependencies are satisfied
            if not all(dep in executed_stages for dep in stage.dependencies):
                logger.warning(
                    f"Skipping stage {stage.name} due to unsatisfied dependencies"
                )
                stage.status = StageStatus.SKIPPED
                continue

            # Execute stage
            await self._execute_stage(stage, pipeline.variables)
            executed_stages.add(stage.name)

    async def _execute_stage(self, stage: PipelineStage, global_vars: dict[str, str]):
        """Execute a pipeline stage."""
        stage.status = StageStatus.RUNNING
        stage.start_time = datetime.now(timezone.utc)

        logger.info(f"Executing stage: {stage.name}")

        try:
            if stage.parallel:
                # Execute jobs in parallel
                await self._execute_jobs_parallel(
                    stage.jobs, {**global_vars, **stage.environment}
                )
            else:
                # Execute jobs sequentially
                for job in stage.jobs:
                    await self._execute_job(job, {**global_vars, **stage.environment})

            # Determine stage status
            failed_jobs = [job for job in stage.jobs if job.status == JobStatus.FAILURE]
            if failed_jobs and not stage.allow_failure:
                stage.status = StageStatus.FAILURE
            else:
                stage.status = StageStatus.SUCCESS

        except Exception as e:
            stage.status = StageStatus.FAILURE
            logger.error(f"Stage {stage.name} failed: {e}")

        stage.end_time = datetime.now(timezone.utc)

    async def _execute_jobs_parallel(
        self, jobs: list[PipelineJob], env_vars: dict[str, str]
    ):
        """Execute jobs in parallel."""
        tasks = []
        for job in jobs:
            task = asyncio.create_task(self._execute_job(job, env_vars))
            tasks.append(task)

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _execute_job(self, job: PipelineJob, env_vars: dict[str, str]):
        """Execute a single job."""
        job.status = JobStatus.RUNNING
        job.start_time = datetime.now(timezone.utc)

        logger.info(f"Executing job: {job.name}")

        try:
            # Execute commands
            for cmd in job.commands:
                # Substitute variables
                resolved_cmd = self._substitute_variables(cmd, env_vars)

                # Execute command
                result = await self._run_command_async(
                    resolved_cmd, job.timeout, env_vars
                )

                job.output += result.get("stdout", "")
                if result.get("stderr"):
                    job.error += result.get("stderr")

                if result.get("returncode", 0) != 0:
                    if job.retry_count > 0:
                        logger.warning(f"Job {job.name} failed, retrying...")
                        job.retry_count -= 1
                        continue
                    else:
                        raise Exception(f"Command failed: {resolved_cmd}")

            job.status = JobStatus.SUCCESS

        except Exception as e:
            job.status = JobStatus.FAILURE
            job.error += str(e)
            logger.error(f"Job {job.name} failed: {e}")

            if not job.allow_failure:
                raise

        job.end_time = datetime.now(timezone.utc)

    async def _run_command_async(
        self, command: str, timeout: int, env_vars: dict[str, str]
    ) -> dict[str, Any]:
        """Run a command asynchronously."""

        def run_cmd():
            try:
                env = os.environ.copy()
                env.update(env_vars)

                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    env=env,
                )

                return {
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }

            except subprocess.TimeoutExpired:
                return {
                    "returncode": -1,
                    "stdout": "",
                    "stderr": f"Command timed out after {timeout} seconds",
                }
            except Exception as e:
                return {"returncode": -1, "stdout": "", "stderr": str(e)}

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, run_cmd)

    def _substitute_variables(self, text: str, variables: dict[str, str]) -> str:
        """Substitute variables in text."""
        for key, value in variables.items():
            text = text.replace(f"${{{key}}}", value)
            text = text.replace(f"${key}", value)
        return text

    def get_pipeline_status(self, pipeline_name: str) -> Pipeline | None:
        """Get current status of a pipeline."""
        return self.pipelines.get(pipeline_name)

    def list_pipelines(self) -> list[Pipeline]:
        """List all configured pipelines."""
        return list(self.pipelines.values())

    def cancel_pipeline(self, pipeline_name: str) -> bool:
        """
        Cancel a running pipeline.

        Args:
            pipeline_name: Name of the pipeline to cancel

        Returns:
            bool: True if cancellation successful
        """
        if pipeline_name not in self.active_executions:
            return False

        task = self.active_executions[pipeline_name]
        task.cancel()

        if pipeline_name in self.pipelines:
            self.pipelines[pipeline_name].status = PipelineStatus.CANCELLED

        logger.info(f"Cancelled pipeline: {pipeline_name}")
        return True

    def validate_pipeline_config(self, config: dict) -> tuple[bool, list[str]]:
        """
        Validate pipeline configuration with detailed error reporting.

        Args:
            config: Pipeline configuration dictionary

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Validate required fields
        required_fields = ["name", "stages"]
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")

        if "name" in config and not isinstance(config["name"], str):
            errors.append("Pipeline name must be a string")

        if "stages" in config:
            if not isinstance(config["stages"], list):
                errors.append("Stages must be a list")
            else:
                # Validate each stage
                for i, stage in enumerate(config["stages"]):
                    stage_errors = self._validate_stage_config(stage, i)
                    errors.extend(stage_errors)

        # Validate triggers if present
        if "triggers" in config:
            if not isinstance(config["triggers"], list):
                errors.append("Triggers must be a list")
            else:
                valid_triggers = ["push", "pull_request", "manual", "schedule"]
                for trigger in config["triggers"]:
                    if trigger not in valid_triggers:
                        errors.append(f"Invalid trigger: {trigger}. Must be one of {valid_triggers}")

        # Validate timeout if present
        if "timeout" in config:
            if not isinstance(config["timeout"], (int, float)) or config["timeout"] <= 0:
                errors.append("Timeout must be a positive number")

        return len(errors) == 0, errors

    def _validate_stage_config(self, stage: dict, stage_index: int) -> list[str]:
        """Validate a single stage configuration."""
        errors = []
        prefix = f"Stage {stage_index}"

        # Validate required stage fields
        if "name" not in stage:
            errors.append(f"{prefix}: Missing required field 'name'")
        elif not isinstance(stage["name"], str):
            errors.append(f"{prefix}: Stage name must be a string")

        if "jobs" not in stage:
            errors.append(f"{prefix}: Missing required field 'jobs'")
        elif not isinstance(stage["jobs"], list):
            errors.append(f"{prefix}: Jobs must be a list")
        else:
            # Validate each job
            for j, job in enumerate(stage["jobs"]):
                job_errors = self._validate_job_config(job, stage_index, j)
                errors.extend(job_errors)

        # Validate dependencies if present
        if "dependencies" in stage:
            if not isinstance(stage["dependencies"], list):
                errors.append(f"{prefix}: Dependencies must be a list")

        return errors

    def _validate_job_config(self, job: dict, stage_index: int, job_index: int) -> list[str]:
        """Validate a single job configuration."""
        errors = []
        prefix = f"Stage {stage_index}, Job {job_index}"

        # Validate required job fields
        if "name" not in job:
            errors.append(f"{prefix}: Missing required field 'name'")
        elif not isinstance(job["name"], str):
            errors.append(f"{prefix}: Job name must be a string")

        if "commands" not in job:
            errors.append(f"{prefix}: Missing required field 'commands'")
        elif not isinstance(job["commands"], list):
            errors.append(f"{prefix}: Commands must be a list")
        elif len(job["commands"]) == 0:
            errors.append(f"{prefix}: Commands list cannot be empty")

        # Validate optional fields
        if "timeout" in job and (not isinstance(job["timeout"], (int, float)) or job["timeout"] <= 0):
            errors.append(f"{prefix}: Timeout must be a positive number")

        if "retry_count" in job and (not isinstance(job["retry_count"], int) or job["retry_count"] < 0):
            errors.append(f"{prefix}: Retry count must be a non-negative integer")

        return errors

    def generate_pipeline_visualization(self, pipeline: Pipeline) -> str:
        """
        Generate a Mermaid diagram for pipeline visualization.

        Args:
            pipeline: Pipeline object to visualize

        Returns:
            Mermaid diagram as string
        """
        lines = ["graph TD"]

        # Track all nodes and edges
        nodes = set()
        edges = set()

        for stage in pipeline.stages:
            stage_id = f"stage_{stage.name.replace(' ', '_')}"

            # Add stage node
            lines.append(f"    {stage_id}[\"{stage.name}\"]")
            nodes.add(stage_id)

            # Add job nodes within stage
            for job in stage.jobs:
                job_id = f"job_{job.name.replace(' ', '_')}"

                # Add job node
                lines.append(f"    {job_id}[\"{job.name}\"]")
                nodes.add(job_id)

                # Connect stage to job
                edge = f"    {stage_id} --> {job_id}"
                if edge not in edges:
                    lines.append(edge)
                    edges.add(edge)

                # Add job dependencies
                for dep in job.dependencies:
                    dep_id = f"job_{dep.replace(' ', '_')}"
                    edge = f"    {dep_id} --> {job_id}"
                    if edge not in edges:
                        lines.append(edge)
                        edges.add(edge)

            # Add stage dependencies
            for dep in stage.dependencies:
                dep_id = f"stage_{dep.replace(' ', '_')}"
                edge = f"    {dep_id} --> {stage_id}"
                if edge not in edges:
                    lines.append(edge)
                    edges.add(edge)

        return "\\n".join(lines)

    def parallel_pipeline_execution(self, stages: list[dict]) -> dict:
        """
        Execute pipeline stages in parallel where possible.

        Args:
            stages: List of stage dictionaries with dependencies

        Returns:
            Dictionary with execution results
        """

        # Build dependency graph
        stage_deps = {}
        for stage in stages:
            stage_name = stage["name"]
            deps = stage.get("dependencies", [])
            stage_deps[stage_name] = deps

        # Execute stages respecting dependencies
        completed = set()
        results = {}
        max_workers = min(len(stages), 4)  # Limit concurrent stages

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}

            while len(completed) < len(stages):
                # Find stages ready to execute
                ready_stages = []
                for stage in stages:
                    stage_name = stage["name"]
                    if stage_name in completed or stage_name in futures:
                        continue

                    deps = stage_deps.get(stage_name, [])
                    if all(dep in completed for dep in deps):
                        ready_stages.append(stage)

                if not ready_stages:
                    # Wait for running stages to complete
                    if futures:
                        concurrent.futures.wait(futures, timeout=1.0)
                        for stage_name, future in list(futures.items()):
                            if future.done():
                                try:
                                    result = future.result()
                                    results[stage_name] = result
                                    completed.add(stage_name)
                                except Exception as e:
                                    results[stage_name] = {"error": str(e), "status": "failed"}
                                    completed.add(stage_name)
                                del futures[stage_name]
                    else:
                        break  # No more work to do
                    continue

                # Submit ready stages for execution
                for stage in ready_stages:
                    stage_name = stage["name"]
                    future = executor.submit(self._execute_stage_parallel, stage)
                    futures[stage_name] = future

        # Collect final results
        summary = {
            "total_stages": len(stages),
            "completed_stages": len(completed),
            "failed_stages": len([r for r in results.values() if isinstance(r, dict) and r.get("status") == "failed"]),
            "stage_results": results
        }

        return summary

    def _execute_stage_parallel(self, stage: dict) -> dict:
        """
        Execute a single stage (simplified for parallel execution).

        Args:
            stage: Stage dictionary

        Returns:
            Execution result
        """
        try:
            # Simulate stage execution
            time.sleep(0.1)  # Simulate work

            jobs = stage.get("jobs", [])
            job_results = []

            for job in jobs:
                # Simulate job execution
                time.sleep(0.05)
                job_results.append({
                    "name": job["name"],
                    "status": "completed",
                    "duration": 0.05
                })

            return {
                "stage_name": stage["name"],
                "status": "completed",
                "job_count": len(jobs),
                "jobs": job_results,
                "duration": 0.1 + (len(jobs) * 0.05)
            }

        except Exception as e:
            return {
                "stage_name": stage["name"],
                "status": "failed",
                "error": str(e)
            }

    def conditional_stage_execution(self, stage: dict, conditions: dict) -> bool:
        """
        Evaluate conditions for stage execution.

        Args:
            stage: Stage dictionary
            conditions: Global condition variables

        Returns:
            True if stage should execute
        """
        # Check if stage has conditions
        if "conditions" not in stage:
            return True  # No conditions means always execute

        stage_conditions = stage["conditions"]

        # Evaluate branch conditions
        if "branch" in stage_conditions:
            branch_pattern = stage_conditions["branch"]
            current_branch = conditions.get("branch", "")
            if not self._matches_pattern(current_branch, branch_pattern):
                return False

        # Evaluate environment conditions
        if "environment" in stage_conditions:
            env_conditions = stage_conditions["environment"]
            for env_var, expected_value in env_conditions.items():
                actual_value = conditions.get(f"env_{env_var}")
                if actual_value != expected_value:
                    return False

        # Evaluate custom conditions
        if "custom" in stage_conditions:
            custom_condition = stage_conditions["custom"]
            # Simple evaluation (could be extended with a proper expression evaluator)
            if isinstance(custom_condition, str):
                # Very basic condition evaluation
                if "failure" in custom_condition.lower():
                    has_failures = conditions.get("has_previous_failures", False)
                    if has_failures:
                        return True
                elif "success" in custom_condition.lower():
                    has_failures = conditions.get("has_previous_failures", False)
                    if not has_failures:
                        return True

        return True

    def _matches_pattern(self, value: str, pattern: str) -> bool:
        """Simple pattern matching for conditions."""
        return fnmatch.fnmatch(value, pattern)

    def optimize_pipeline_schedule(self, pipeline: Pipeline) -> dict:
        """
        Optimize pipeline execution schedule for parallelism.

        Args:
            pipeline: Pipeline to optimize

        Returns:
            Optimized pipeline configuration
        """
        # Analyze stage dependencies
        stage_deps = {}
        for stage in pipeline.stages:
            stage_deps[stage.name] = stage.dependencies

        # Calculate parallelism opportunities
        independent_stages = []
        sequential_stages = []

        for stage_name, deps in stage_deps.items():
            if not deps:
                independent_stages.append(stage_name)
            else:
                sequential_stages.append((stage_name, deps))

        # Group stages by dependency levels
        execution_levels = self._calculate_execution_levels(pipeline.stages, stage_deps)

        optimization = {
            "parallel_stages": len(independent_stages),
            "sequential_chains": len(sequential_stages),
            "execution_levels": execution_levels,
            "estimated_parallelism": len(execution_levels[0]) if execution_levels else 0,
            "optimization_suggestions": []
        }

        # Add optimization suggestions
        if len(independent_stages) > 1:
            optimization["optimization_suggestions"].append(
                f"Consider running {len(independent_stages)} independent stages in parallel"
            )

        max_level_size = max(len(level) for level in execution_levels) if execution_levels else 0
        if max_level_size > 1:
            optimization["optimization_suggestions"].append(
                f"Maximum parallelism: {max_level_size} stages can run concurrently"
            )

        return optimization

    def _calculate_execution_levels(self, stages: list, dependencies: dict) -> list[list[str]]:
        """Calculate execution levels for optimal parallelism."""
        # Kahn's algorithm for topological levels
        in_degree = {stage.name: len(stage.dependencies) for stage in stages}
        queue = [stage.name for stage in stages if in_degree[stage.name] == 0]
        levels = []

        while queue:
            level = []
            next_queue = []

            for stage_name in queue:
                level.append(stage_name)

                # Find stages that depend on this one
                for other_stage in stages:
                    if stage_name in other_stage.dependencies:
                        in_degree[other_stage.name] -= 1
                        if in_degree[other_stage.name] == 0:
                            next_queue.append(other_stage.name)

            if level:
                levels.append(sorted(level))
            queue = next_queue

        return levels

    def get_stage_dependencies(self, stages: list[dict]) -> dict[str, list[str]]:
        """
        Extract stage dependencies from stage list.

        Args:
            stages: List of stage dictionaries

        Returns:
            Dictionary mapping stage names to dependency lists
        """
        dependencies = {}
        for stage in stages:
            stage_name = stage["name"]
            deps = stage.get("dependencies", [])
            dependencies[stage_name] = deps

        return dependencies

    def validate_stage_dependencies(self, stages: list[dict]) -> tuple[bool, list[str]]:
        """
        Validate stage dependency graph.

        Args:
            stages: List of stage dictionaries

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        stage_names = {stage["name"] for stage in stages}
        dependencies = self.get_stage_dependencies(stages)

        # Check for missing dependencies
        for stage_name, deps in dependencies.items():
            for dep in deps:
                if dep not in stage_names:
                    errors.append(f"Stage '{stage_name}' depends on missing stage '{dep}'")

        # Check for self-dependencies
        for stage_name, deps in dependencies.items():
            if stage_name in deps:
                errors.append(f"Stage '{stage_name}' cannot depend on itself")

        # Check for cycles (simplified check)
        visited = set()
        rec_stack = set()

        def has_cycle(node: str) -> bool:

            visited.add(node)
            rec_stack.add(node)

            for neighbor in dependencies.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for stage_name in stage_names:
            if stage_name not in visited:
                if has_cycle(stage_name):
                    errors.append(f"Cycle detected involving stage '{stage_name}'")
                    break  # Only report first cycle

        return len(errors) == 0, errors

    def save_pipeline_config(self, pipeline: Pipeline, output_path: str):
        """Save pipeline configuration to file."""
        config = {
            "name": pipeline.name,
            "description": pipeline.description,
            "variables": pipeline.variables,
            "triggers": pipeline.triggers,
            "timeout": pipeline.timeout,
            "stages": [],
        }

        for stage in pipeline.stages:
            stage_config = {
                "name": stage.name,
                "dependencies": stage.dependencies,
                "environment": stage.environment,
                "allow_failure": stage.allow_failure,
                "parallel": stage.parallel,
                "jobs": [],
            }

            for job in stage.jobs:
                job_config = {
                    "name": job.name,
                    "commands": job.commands,
                    "environment": job.environment,
                    "artifacts": job.artifacts,
                    "dependencies": job.dependencies,
                    "timeout": job.timeout,
                    "retry_count": job.retry_count,
                    "allow_failure": job.allow_failure,
                }
                stage_config["jobs"].append(job_config)

            config["stages"].append(stage_config)

        # Save to file
        with open(output_path, "w") as f:
            if output_path.endswith(".yaml") or output_path.endswith(".yml"):
                yaml.dump(config, f, default_flow_style=False)
            else:
                json.dump(config, f, indent=2)

        logger.info(f"Saved pipeline config to {output_path}")


# Convenience functions
def create_pipeline(config_path: str) -> Pipeline:
    """
    Convenience function to create a pipeline from configuration.

    Args:
        config_path: Path to pipeline configuration file

    Returns:
        Pipeline: Created pipeline
    """
    manager = PipelineManager()
    return manager.create_pipeline(config_path)


def run_pipeline(
    pipeline_name: str,
    config_path: str | None = None,
    variables: dict[str, str] | None = None,
) -> Pipeline:
    """
    Convenience function to run a pipeline.

    Args:
        pipeline_name: Name of the pipeline to run
        config_path: Path to pipeline config (if not already loaded)
        variables: Runtime variables

    Returns:
        Pipeline: Pipeline execution results
    """
    manager = PipelineManager()

    if config_path:
        manager.create_pipeline(config_path)

    return manager.run_pipeline(pipeline_name, variables)


# =============================================================================
# ASYNC PIPELINE OPERATIONS
# =============================================================================


@dataclass
class AsyncPipelineResult:
    """Result of an async pipeline operation."""
    pipeline_id: str
    status: PipelineStatus
    message: str
    data: dict[str, Any] | None = None
    error: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary format."""
        return {
            "pipeline_id": self.pipeline_id,
            "status": self.status.value,
            "message": self.message,
            "data": self.data,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
        }


class AsyncPipelineManager:
    """
    Async pipeline manager for non-blocking CI/CD operations.

    Provides async variants of pipeline operations using aiohttp for
    external CI/CD service integrations (GitHub Actions, GitLab CI, etc.).
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_token: str | None = None,
        workspace_dir: str | None = None,
    ):
        """
        Initialize the async pipeline manager.

        Args:
            base_url: Base URL for CI/CD API (e.g., GitHub Actions API)
            api_token: API authentication token
            workspace_dir: Directory for pipeline workspaces and artifacts
        """
        self.base_url = base_url or os.environ.get(
            "CI_CD_API_URL", "https://api.github.com"
        )
        self.api_token = api_token or os.environ.get("CI_CD_API_TOKEN")
        self.workspace_dir = workspace_dir or os.path.join(os.getcwd(), ".pipelines")
        self.pipelines: dict[str, Pipeline] = {}
        self._sync_manager = PipelineManager(workspace_dir)

        # Create workspace directory
        os.makedirs(self.workspace_dir, exist_ok=True)

    def _get_headers(self) -> dict[str, str]:
        """Get API request headers."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        }
        if self.api_token:
            headers["Authorization"] = f"token {self.api_token}"
        return headers

    async def async_trigger_pipeline(
        self,
        pipeline_name: str,
        repo_owner: str,
        repo_name: str,
        workflow_id: str,
        ref: str = "main",
        inputs: dict[str, str] | None = None,
        timeout: int = 30,
    ) -> AsyncPipelineResult:
        """
        Trigger a CI/CD pipeline asynchronously.

        This method triggers a workflow dispatch event on GitHub Actions
        or similar CI/CD platform.

        Args:
            pipeline_name: Name identifier for tracking
            repo_owner: Repository owner
            repo_name: Repository name
            workflow_id: Workflow file name or ID (e.g., "ci.yml")
            ref: Git reference (branch/tag) to run the workflow on
            inputs: Workflow input parameters
            timeout: Request timeout in seconds

        Returns:
            AsyncPipelineResult with trigger status
        """
        logger.info(
            f"[ASYNC] Triggering pipeline {pipeline_name} for {repo_owner}/{repo_name}"
        )

        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/actions/workflows/{workflow_id}/dispatches"

        payload: dict[str, Any] = {"ref": ref}
        if inputs:
            payload["inputs"] = inputs

        try:
            timeout_config = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(timeout=timeout_config) as session:
                async with session.post(
                    url,
                    headers=self._get_headers(),
                    json=payload,
                ) as response:
                    if response.status == 204:
                        logger.info(
                            f"[ASYNC] Pipeline {pipeline_name} triggered successfully"
                        )
                        return AsyncPipelineResult(
                            pipeline_id=pipeline_name,
                            status=PipelineStatus.PENDING,
                            message="Pipeline triggered successfully",
                            data={
                                "repo": f"{repo_owner}/{repo_name}",
                                "workflow_id": workflow_id,
                                "ref": ref,
                                "inputs": inputs,
                            },
                        )
                    else:
                        error_text = await response.text()
                        error_msg = f"Failed to trigger pipeline: HTTP {response.status}"
                        try:
                            error_data = json.loads(error_text)
                            error_msg += f" - {error_data.get('message', error_text)}"
                        except json.JSONDecodeError:
                            error_msg += f" - {error_text}"

                        logger.error(f"[ASYNC] {error_msg}")
                        return AsyncPipelineResult(
                            pipeline_id=pipeline_name,
                            status=PipelineStatus.FAILURE,
                            message="Failed to trigger pipeline",
                            error=error_msg,
                        )

        except asyncio.TimeoutError:
            error_msg = "Pipeline trigger request timed out"
            logger.error(f"[ASYNC] {error_msg}")
            return AsyncPipelineResult(
                pipeline_id=pipeline_name,
                status=PipelineStatus.FAILURE,
                message=error_msg,
                error=error_msg,
            )
        except aiohttp.ClientError as e:
            error_msg = f"Network error triggering pipeline: {e}"
            logger.error(f"[ASYNC] {error_msg}")
            return AsyncPipelineResult(
                pipeline_id=pipeline_name,
                status=PipelineStatus.FAILURE,
                message="Network error",
                error=error_msg,
            )

    async def async_get_pipeline_status(
        self,
        repo_owner: str,
        repo_name: str,
        run_id: int | None = None,
        workflow_id: str | None = None,
        timeout: int = 30,
    ) -> AsyncPipelineResult:
        """
        Get the status of a pipeline/workflow run asynchronously.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            run_id: Specific workflow run ID to check
            workflow_id: Workflow file name to get latest run status
            timeout: Request timeout in seconds

        Returns:
            AsyncPipelineResult with pipeline status details
        """
        logger.info(
            f"[ASYNC] Getting pipeline status for {repo_owner}/{repo_name}"
        )

        if run_id:
            url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/actions/runs/{run_id}"
        elif workflow_id:
            url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/actions/workflows/{workflow_id}/runs?per_page=1"
        else:
            url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/actions/runs?per_page=1"

        try:
            timeout_config = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(timeout=timeout_config) as session:
                async with session.get(
                    url,
                    headers=self._get_headers(),
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Handle single run vs. list of runs
                        if "workflow_runs" in data:
                            if not data["workflow_runs"]:
                                return AsyncPipelineResult(
                                    pipeline_id=workflow_id or "unknown",
                                    status=PipelineStatus.PENDING,
                                    message="No workflow runs found",
                                    data={"total_count": 0},
                                )
                            run_data = data["workflow_runs"][0]
                        else:
                            run_data = data

                        # Map GitHub Actions status to PipelineStatus
                        gh_status = run_data.get("status", "")
                        gh_conclusion = run_data.get("conclusion")

                        if gh_status == "completed":
                            if gh_conclusion == "success":
                                status = PipelineStatus.SUCCESS
                            elif gh_conclusion == "failure":
                                status = PipelineStatus.FAILURE
                            elif gh_conclusion == "cancelled":
                                status = PipelineStatus.CANCELLED
                            else:
                                status = PipelineStatus.FAILURE
                        elif gh_status == "in_progress":
                            status = PipelineStatus.RUNNING
                        elif gh_status == "queued":
                            status = PipelineStatus.PENDING
                        else:
                            status = PipelineStatus.PENDING

                        logger.info(
                            f"[ASYNC] Pipeline status: {status.value} (GitHub: {gh_status}/{gh_conclusion})"
                        )

                        return AsyncPipelineResult(
                            pipeline_id=str(run_data.get("id", "unknown")),
                            status=status,
                            message=f"Pipeline {gh_status}" + (f" ({gh_conclusion})" if gh_conclusion else ""),
                            data={
                                "run_id": run_data.get("id"),
                                "name": run_data.get("name"),
                                "head_branch": run_data.get("head_branch"),
                                "head_sha": run_data.get("head_sha"),
                                "status": gh_status,
                                "conclusion": gh_conclusion,
                                "html_url": run_data.get("html_url"),
                                "created_at": run_data.get("created_at"),
                                "updated_at": run_data.get("updated_at"),
                                "run_started_at": run_data.get("run_started_at"),
                            },
                        )
                    else:
                        error_text = await response.text()
                        error_msg = f"Failed to get pipeline status: HTTP {response.status}"
                        logger.error(f"[ASYNC] {error_msg}")
                        return AsyncPipelineResult(
                            pipeline_id=str(run_id) if run_id else (workflow_id or "unknown"),
                            status=PipelineStatus.FAILURE,
                            message="Failed to get status",
                            error=error_msg,
                        )

        except asyncio.TimeoutError:
            error_msg = "Pipeline status request timed out"
            logger.error(f"[ASYNC] {error_msg}")
            return AsyncPipelineResult(
                pipeline_id=str(run_id) if run_id else (workflow_id or "unknown"),
                status=PipelineStatus.FAILURE,
                message=error_msg,
                error=error_msg,
            )
        except aiohttp.ClientError as e:
            error_msg = f"Network error getting pipeline status: {e}"
            logger.error(f"[ASYNC] {error_msg}")
            return AsyncPipelineResult(
                pipeline_id=str(run_id) if run_id else (workflow_id or "unknown"),
                status=PipelineStatus.FAILURE,
                message="Network error",
                error=error_msg,
            )

    async def async_wait_for_completion(
        self,
        repo_owner: str,
        repo_name: str,
        run_id: int,
        poll_interval: int = 30,
        timeout: int = 3600,
    ) -> AsyncPipelineResult:
        """
        Wait for a pipeline run to complete asynchronously.

        Polls the pipeline status at regular intervals until completion
        or timeout.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            run_id: Workflow run ID to monitor
            poll_interval: Seconds between status checks
            timeout: Maximum time to wait in seconds

        Returns:
            AsyncPipelineResult with final pipeline status
        """
        logger.info(
            f"[ASYNC] Waiting for pipeline {run_id} to complete (timeout: {timeout}s)"
        )

        start_time = time.time()
        last_status = None

        while (time.time() - start_time) < timeout:
            result = await self.async_get_pipeline_status(
                repo_owner=repo_owner,
                repo_name=repo_name,
                run_id=run_id,
            )

            if result.error:
                logger.warning(f"[ASYNC] Error checking status: {result.error}")
                # Continue polling despite transient errors
                await asyncio.sleep(poll_interval)
                continue

            current_status = result.status

            # Log status changes
            if current_status != last_status:
                logger.info(f"[ASYNC] Pipeline {run_id} status: {current_status.value}")
                last_status = current_status

            # Check for terminal states
            if current_status in (
                PipelineStatus.SUCCESS,
                PipelineStatus.FAILURE,
                PipelineStatus.CANCELLED,
            ):
                elapsed = time.time() - start_time
                logger.info(
                    f"[ASYNC] Pipeline {run_id} completed with status {current_status.value} "
                    f"after {elapsed:.1f}s"
                )
                return result

            await asyncio.sleep(poll_interval)

        # Timeout reached
        elapsed = time.time() - start_time
        logger.warning(
            f"[ASYNC] Pipeline {run_id} did not complete within {timeout}s (waited {elapsed:.1f}s)"
        )
        return AsyncPipelineResult(
            pipeline_id=str(run_id),
            status=PipelineStatus.FAILURE,
            message=f"Pipeline did not complete within {timeout}s timeout",
            error="Timeout waiting for pipeline completion",
            data={"last_known_status": last_status.value if last_status else "unknown"},
        )

    async def async_cancel_pipeline(
        self,
        repo_owner: str,
        repo_name: str,
        run_id: int,
        timeout: int = 30,
    ) -> AsyncPipelineResult:
        """
        Cancel a running pipeline asynchronously.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            run_id: Workflow run ID to cancel
            timeout: Request timeout in seconds

        Returns:
            AsyncPipelineResult with cancellation status
        """
        logger.info(
            f"[ASYNC] Cancelling pipeline {run_id} for {repo_owner}/{repo_name}"
        )

        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/actions/runs/{run_id}/cancel"

        try:
            timeout_config = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(timeout=timeout_config) as session:
                async with session.post(
                    url,
                    headers=self._get_headers(),
                ) as response:
                    if response.status == 202:
                        logger.info(f"[ASYNC] Pipeline {run_id} cancel request accepted")
                        return AsyncPipelineResult(
                            pipeline_id=str(run_id),
                            status=PipelineStatus.CANCELLED,
                            message="Pipeline cancellation requested",
                            data={"run_id": run_id},
                        )
                    else:
                        error_text = await response.text()
                        error_msg = f"Failed to cancel pipeline: HTTP {response.status}"
                        logger.error(f"[ASYNC] {error_msg}")
                        return AsyncPipelineResult(
                            pipeline_id=str(run_id),
                            status=PipelineStatus.FAILURE,
                            message="Failed to cancel pipeline",
                            error=error_msg,
                        )

        except asyncio.TimeoutError:
            error_msg = "Pipeline cancel request timed out"
            logger.error(f"[ASYNC] {error_msg}")
            return AsyncPipelineResult(
                pipeline_id=str(run_id),
                status=PipelineStatus.FAILURE,
                message=error_msg,
                error=error_msg,
            )
        except aiohttp.ClientError as e:
            error_msg = f"Network error cancelling pipeline: {e}"
            logger.error(f"[ASYNC] {error_msg}")
            return AsyncPipelineResult(
                pipeline_id=str(run_id),
                status=PipelineStatus.FAILURE,
                message="Network error",
                error=error_msg,
            )

    async def async_get_workflow_runs(
        self,
        repo_owner: str,
        repo_name: str,
        workflow_id: str | None = None,
        status: str | None = None,
        branch: str | None = None,
        per_page: int = 10,
        timeout: int = 30,
    ) -> AsyncPipelineResult:
        """
        List workflow runs asynchronously.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            workflow_id: Filter by workflow file name
            status: Filter by status (queued, in_progress, completed)
            branch: Filter by branch name
            per_page: Number of results per page
            timeout: Request timeout in seconds

        Returns:
            AsyncPipelineResult with list of workflow runs
        """
        logger.info(
            f"[ASYNC] Getting workflow runs for {repo_owner}/{repo_name}"
        )

        if workflow_id:
            url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/actions/workflows/{workflow_id}/runs"
        else:
            url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/actions/runs"

        params: dict[str, Any] = {"per_page": per_page}
        if status:
            params["status"] = status
        if branch:
            params["branch"] = branch

        try:
            timeout_config = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(timeout=timeout_config) as session:
                async with session.get(
                    url,
                    headers=self._get_headers(),
                    params=params,
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        runs = data.get("workflow_runs", [])

                        logger.info(
                            f"[ASYNC] Found {len(runs)} workflow runs"
                        )

                        return AsyncPipelineResult(
                            pipeline_id="workflow_runs",
                            status=PipelineStatus.SUCCESS,
                            message=f"Found {len(runs)} workflow runs",
                            data={
                                "total_count": data.get("total_count", len(runs)),
                                "runs": [
                                    {
                                        "id": run.get("id"),
                                        "name": run.get("name"),
                                        "status": run.get("status"),
                                        "conclusion": run.get("conclusion"),
                                        "head_branch": run.get("head_branch"),
                                        "html_url": run.get("html_url"),
                                        "created_at": run.get("created_at"),
                                    }
                                    for run in runs
                                ],
                            },
                        )
                    else:
                        error_text = await response.text()
                        error_msg = f"Failed to get workflow runs: HTTP {response.status}"
                        logger.error(f"[ASYNC] {error_msg}")
                        return AsyncPipelineResult(
                            pipeline_id="workflow_runs",
                            status=PipelineStatus.FAILURE,
                            message="Failed to get workflow runs",
                            error=error_msg,
                        )

        except asyncio.TimeoutError:
            error_msg = "Workflow runs request timed out"
            logger.error(f"[ASYNC] {error_msg}")
            return AsyncPipelineResult(
                pipeline_id="workflow_runs",
                status=PipelineStatus.FAILURE,
                message=error_msg,
                error=error_msg,
            )
        except aiohttp.ClientError as e:
            error_msg = f"Network error getting workflow runs: {e}"
            logger.error(f"[ASYNC] {error_msg}")
            return AsyncPipelineResult(
                pipeline_id="workflow_runs",
                status=PipelineStatus.FAILURE,
                message="Network error",
                error=error_msg,
            )

    async def async_run_local_pipeline(
        self,
        pipeline_name: str,
        variables: dict[str, str] | None = None,
    ) -> Pipeline:
        """
        Run a locally configured pipeline asynchronously.

        This uses the synchronous PipelineManager for local execution
        but wraps it in an async context.

        Args:
            pipeline_name: Name of the pipeline to run
            variables: Runtime variables to override

        Returns:
            Pipeline object with execution results
        """
        if pipeline_name not in self._sync_manager.pipelines:
            raise ValueError(f"Pipeline '{pipeline_name}' not found")

        logger.info(f"[ASYNC] Running local pipeline: {pipeline_name}")

        # Run the pipeline in the async context
        return await self._sync_manager.run_pipeline_async(pipeline_name, variables)

    def create_pipeline(self, config_path: str) -> Pipeline:
        """
        Create a pipeline from configuration file.

        Delegates to the synchronous manager.

        Args:
            config_path: Path to pipeline configuration file

        Returns:
            Pipeline: Created pipeline object
        """
        pipeline = self._sync_manager.create_pipeline(config_path)
        self.pipelines[pipeline.name] = pipeline
        return pipeline


# Convenience async functions


async def async_trigger_pipeline(
    repo_owner: str,
    repo_name: str,
    workflow_id: str,
    ref: str = "main",
    inputs: dict[str, str] | None = None,
    api_token: str | None = None,
) -> AsyncPipelineResult:
    """
    Convenience function to trigger a pipeline asynchronously.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        workflow_id: Workflow file name or ID
        ref: Git reference to run on
        inputs: Workflow input parameters
        api_token: API authentication token

    Returns:
        AsyncPipelineResult with trigger status
    """
    manager = AsyncPipelineManager(api_token=api_token)
    return await manager.async_trigger_pipeline(
        pipeline_name=f"{repo_owner}/{repo_name}/{workflow_id}",
        repo_owner=repo_owner,
        repo_name=repo_name,
        workflow_id=workflow_id,
        ref=ref,
        inputs=inputs,
    )


async def async_get_pipeline_status(
    repo_owner: str,
    repo_name: str,
    run_id: int | None = None,
    workflow_id: str | None = None,
    api_token: str | None = None,
) -> AsyncPipelineResult:
    """
    Convenience function to get pipeline status asynchronously.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        run_id: Specific workflow run ID
        workflow_id: Workflow file name
        api_token: API authentication token

    Returns:
        AsyncPipelineResult with pipeline status
    """
    manager = AsyncPipelineManager(api_token=api_token)
    return await manager.async_get_pipeline_status(
        repo_owner=repo_owner,
        repo_name=repo_name,
        run_id=run_id,
        workflow_id=workflow_id,
    )


async def async_wait_for_completion(
    repo_owner: str,
    repo_name: str,
    run_id: int,
    poll_interval: int = 30,
    timeout: int = 3600,
    api_token: str | None = None,
) -> AsyncPipelineResult:
    """
    Convenience function to wait for pipeline completion asynchronously.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        run_id: Workflow run ID to monitor
        poll_interval: Seconds between status checks
        timeout: Maximum time to wait
        api_token: API authentication token

    Returns:
        AsyncPipelineResult with final status
    """
    manager = AsyncPipelineManager(api_token=api_token)
    return await manager.async_wait_for_completion(
        repo_owner=repo_owner,
        repo_name=repo_name,
        run_id=run_id,
        poll_interval=poll_interval,
        timeout=timeout,
    )
