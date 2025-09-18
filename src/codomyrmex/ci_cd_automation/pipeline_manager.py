"""
Pipeline Manager for Codomyrmex CI/CD Automation Module.

Provides comprehensive pipeline orchestration, management, and execution capabilities.
"""

import os
import sys
import json
import yaml
import asyncio
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess

# Add project root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


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
    commands: List[str]
    environment: Dict[str, str] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 3600  # 1 hour
    retry_count: int = 0
    allow_failure: bool = False
    status: JobStatus = JobStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    output: str = ""
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
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
            "error": self.error
        }


@dataclass
class PipelineStage:
    """Pipeline stage containing multiple jobs."""
    name: str
    jobs: List[PipelineJob] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)
    allow_failure: bool = False
    parallel: bool = True
    status: StageStatus = StageStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
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
            "end_time": self.end_time.isoformat() if self.end_time else None
        }


@dataclass
class Pipeline:
    """Complete CI/CD pipeline definition."""
    name: str
    description: str = ""
    stages: List[PipelineStage] = field(default_factory=list)
    variables: Dict[str, str] = field(default_factory=dict)
    triggers: Dict[str, Any] = field(default_factory=dict)
    timeout: int = 7200  # 2 hours
    status: PipelineStatus = PipelineStatus.PENDING
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration: float = 0.0

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
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
            "duration": self.duration
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
        self.pipelines: Dict[str, Pipeline] = {}
        self.active_executions: Dict[str, asyncio.Task] = {}
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
            with open(config_path, 'r') as f:
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
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

    def _parse_pipeline_config(self, config: Dict[str, Any]) -> Pipeline:
        """Parse pipeline configuration into Pipeline object."""
        pipeline = Pipeline(
            name=config.get("name", "unnamed_pipeline"),
            description=config.get("description", ""),
            variables=config.get("variables", {}),
            triggers=config.get("triggers", {}),
            timeout=config.get("timeout", 7200)
        )

        # Parse stages
        for stage_config in config.get("stages", []):
            stage = PipelineStage(
                name=stage_config.get("name", "unnamed_stage"),
                dependencies=stage_config.get("dependencies", []),
                environment=stage_config.get("environment", {}),
                allow_failure=stage_config.get("allow_failure", False),
                parallel=stage_config.get("parallel", True)
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
                    allow_failure=job_config.get("allow_failure", False)
                )
                stage.jobs.append(job)

            pipeline.stages.append(stage)

        return pipeline

    async def run_pipeline_async(self, pipeline_name: str,
                               variables: Optional[Dict[str, str]] = None) -> Pipeline:
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
            pipeline.duration = (pipeline.finished_at - pipeline.started_at).total_seconds()

            if any(stage.status == StageStatus.FAILURE for stage in pipeline.stages):
                pipeline.status = PipelineStatus.FAILURE
            else:
                pipeline.status = PipelineStatus.SUCCESS

            logger.info(f"Pipeline {pipeline_name} completed with status: {pipeline.status.value}")

        except Exception as e:
            pipeline.status = PipelineStatus.FAILURE
            pipeline.finished_at = datetime.now(timezone.utc)
            if pipeline.started_at:
                pipeline.duration = (pipeline.finished_at - pipeline.started_at).total_seconds()

            logger.error(f"Pipeline {pipeline_name} failed: {e}")

        return pipeline

    def run_pipeline(self, pipeline_name: str,
                    variables: Optional[Dict[str, str]] = None) -> Pipeline:
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
                import concurrent.futures

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
                logger.warning(f"Skipping stage {stage.name} due to unsatisfied dependencies")
                stage.status = StageStatus.SKIPPED
                continue

            # Execute stage
            await self._execute_stage(stage, pipeline.variables)
            executed_stages.add(stage.name)

    async def _execute_stage(self, stage: PipelineStage, global_vars: Dict[str, str]):
        """Execute a pipeline stage."""
        stage.status = StageStatus.RUNNING
        stage.start_time = datetime.now(timezone.utc)

        logger.info(f"Executing stage: {stage.name}")

        try:
            if stage.parallel:
                # Execute jobs in parallel
                await self._execute_jobs_parallel(stage.jobs, {**global_vars, **stage.environment})
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

    async def _execute_jobs_parallel(self, jobs: List[PipelineJob], env_vars: Dict[str, str]):
        """Execute jobs in parallel."""
        tasks = []
        for job in jobs:
            task = asyncio.create_task(self._execute_job(job, env_vars))
            tasks.append(task)

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _execute_job(self, job: PipelineJob, env_vars: Dict[str, str]):
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
                result = await self._run_command_async(resolved_cmd, job.timeout, env_vars)

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

    async def _run_command_async(self, command: str, timeout: int,
                               env_vars: Dict[str, str]) -> Dict[str, Any]:
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
                    env=env
                )

                return {
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }

            except subprocess.TimeoutExpired:
                return {
                    "returncode": -1,
                    "stdout": "",
                    "stderr": f"Command timed out after {timeout} seconds"
                }
            except Exception as e:
                return {
                    "returncode": -1,
                    "stdout": "",
                    "stderr": str(e)
                }

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, run_cmd)

    def _substitute_variables(self, text: str, variables: Dict[str, str]) -> str:
        """Substitute variables in text."""
        for key, value in variables.items():
            text = text.replace(f"${{{key}}}", value)
            text = text.replace(f"${key}", value)
        return text

    def get_pipeline_status(self, pipeline_name: str) -> Optional[Pipeline]:
        """Get current status of a pipeline."""
        return self.pipelines.get(pipeline_name)

    def list_pipelines(self) -> List[Pipeline]:
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

    def save_pipeline_config(self, pipeline: Pipeline, output_path: str):
        """Save pipeline configuration to file."""
        config = {
            "name": pipeline.name,
            "description": pipeline.description,
            "variables": pipeline.variables,
            "triggers": pipeline.triggers,
            "timeout": pipeline.timeout,
            "stages": []
        }

        for stage in pipeline.stages:
            stage_config = {
                "name": stage.name,
                "dependencies": stage.dependencies,
                "environment": stage.environment,
                "allow_failure": stage.allow_failure,
                "parallel": stage.parallel,
                "jobs": []
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
                    "allow_failure": job.allow_failure
                }
                stage_config["jobs"].append(job_config)

            config["stages"].append(stage_config)

        # Save to file
        with open(output_path, 'w') as f:
            if output_path.endswith('.yaml') or output_path.endswith('.yml'):
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


def run_pipeline(pipeline_name: str, config_path: Optional[str] = None,
                variables: Optional[Dict[str, str]] = None) -> Pipeline:
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
