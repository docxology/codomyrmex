"""PipelineManager — synchronous pipeline orchestration and execution."""

import asyncio
import concurrent.futures
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from typing import Any

import yaml

from codomyrmex.logging_monitoring import get_logger

from ._execution import PipelineExecutionMixin
from ._optimization import PipelineOptimizationMixin
from ._validation import PipelineValidationMixin
from .models import (
    Pipeline,
    PipelineJob,
    PipelineStage,
    PipelineStatus,
    StageStatus,
)

logger = get_logger(__name__)


class PipelineManager(
    PipelineExecutionMixin,
    PipelineValidationMixin,
    PipelineOptimizationMixin,
):
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
                if config_path.endswith((".yaml", ".yml")):
                    config = yaml.safe_load(f)
                else:
                    config = json.load(f)

            pipeline = self._parse_pipeline_config(config)
            self.pipelines[pipeline.name] = pipeline

            logger.info("Created pipeline: %s", pipeline.name)
            return pipeline

        except Exception as e:
            logger.error("Failed to create pipeline from %s: %s", config_path, e)
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
        pipeline.started_at = datetime.now(UTC)

        logger.info("Starting pipeline execution: %s", pipeline_name)

        try:
            # Execute stages in dependency order
            await self._execute_pipeline_stages(pipeline)

            # Calculate final status
            pipeline.finished_at = datetime.now(UTC)
            if pipeline.started_at:
                pipeline.duration = (
                    pipeline.finished_at - pipeline.started_at
                ).total_seconds()

            if any(stage.status == StageStatus.FAILURE for stage in pipeline.stages):
                pipeline.status = PipelineStatus.FAILURE
            else:
                pipeline.status = PipelineStatus.SUCCESS

            logger.info(
                "Pipeline %s completed with status: %s",
                pipeline_name,
                pipeline.status.value,
            )

        except Exception as e:
            pipeline.status = PipelineStatus.FAILURE
            pipeline.finished_at = datetime.now(UTC)
            if pipeline.started_at:
                pipeline.duration = (
                    pipeline.finished_at - pipeline.started_at
                ).total_seconds()

            logger.error("Pipeline %s failed: %s", pipeline_name, e)

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

        logger.info("Cancelled pipeline: %s", pipeline_name)
        return True

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
            lines.append(f'    {stage_id}["{stage.name}"]')
            nodes.add(stage_id)

            # Add job nodes within stage
            for job in stage.jobs:
                job_id = f"job_{job.name.replace(' ', '_')}"

                # Add job node
                lines.append(f'    {job_id}["{job.name}"]')
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
            if output_path.endswith((".yaml", ".yml")):
                yaml.dump(config, f, default_flow_style=False)
            else:
                json.dump(config, f, indent=2)

        logger.info("Saved pipeline config to %s", output_path)
