from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any, Optional, Tuple, List
import asyncio
import concurrent.futures
import concurrent.futures
import fnmatch
import json
import os
import subprocess
import sys
import time

from dataclasses import dataclass, field
from enum import Enum
import yaml

from codomyrmex.logging_monitoring.logger_config import get_logger




























"""
Pipeline Manager for Codomyrmex CI/CD Automation Module.

Provides comprehensive pipeline orchestration, management, and execution capabilities.
"""



# Add project root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    pass
#     sys.path.insert(0, PROJECT_ROOT)  # Removed sys.path manipulation


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
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
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
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

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
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
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

    def __init__(self, workspace_dir: Optional[str] = None):
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
        self, pipeline_name: str, variables: Optional[dict[str, str]] = None
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
        self, pipeline_name: str, variables: Optional[dict[str, str]] = None
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

    def get_pipeline_status(self, pipeline_name: str) -> Optional[Pipeline]:
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

    def validate_pipeline_config(self, config: dict) -> Tuple[bool, List[str]]:
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

    def _validate_stage_config(self, stage: dict, stage_index: int) -> List[str]:
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

    def _validate_job_config(self, job: dict, stage_index: int, job_index: int) -> List[str]:
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

    def parallel_pipeline_execution(self, stages: List[dict]) -> dict:
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

    def _calculate_execution_levels(self, stages: List, dependencies: dict) -> List[List[str]]:
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

    def get_stage_dependencies(self, stages: List[dict]) -> dict[str, List[str]]:
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

    def validate_stage_dependencies(self, stages: List[dict]) -> Tuple[bool, List[str]]:
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
    config_path: Optional[str] = None,
    variables: Optional[dict[str, str]] = None,
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
