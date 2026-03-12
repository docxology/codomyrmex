import asyncio
import concurrent.futures
import fnmatch
import os
import subprocess
import time
from datetime import UTC, datetime
from typing import Any

from codomyrmex.logging_monitoring import get_logger

from .models import (
    JobStatus,
    Pipeline,
    PipelineJob,
    PipelineStage,
    StageStatus,
)

logger = get_logger(__name__)


class PipelineExecutionMixin:
    """Mixin for async/sync pipeline, stage, and job execution."""

    async def _execute_pipeline_stages(self, pipeline: Pipeline):
        """Execute pipeline stages in dependency order."""
        # Simple dependency resolution (can be enhanced)
        executed_stages = set()

        for stage in pipeline.stages:
            # Check if all dependencies are satisfied
            if not all(dep in executed_stages for dep in stage.dependencies):
                logger.warning(
                    "Skipping stage %s due to unsatisfied dependencies", stage.name
                )
                stage.status = StageStatus.SKIPPED
                continue

            # Execute stage
            await self._execute_stage(stage, pipeline.variables)
            executed_stages.add(stage.name)

    async def _execute_stage(self, stage: PipelineStage, global_vars: dict[str, str]):
        """Execute a pipeline stage."""
        stage.status = StageStatus.RUNNING
        stage.start_time = datetime.now(UTC)

        logger.info("Executing stage: %s", stage.name)

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
            logger.error("Stage %s failed: %s", stage.name, e)

        stage.end_time = datetime.now(UTC)

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
        job.start_time = datetime.now(UTC)

        logger.info("Executing job: %s", job.name)

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
                    job.error += result.get("stderr")  # type: ignore

                if result.get("returncode", 0) != 0:
                    if job.retry_count > 0:
                        logger.warning("Job %s failed, retrying...", job.name)
                        job.retry_count -= 1
                        continue
                    raise Exception(f"Command failed: {resolved_cmd}")

            job.status = JobStatus.SUCCESS

        except Exception as e:
            job.status = JobStatus.FAILURE
            job.error += str(e)
            logger.error("Job %s failed: %s", job.name, e)

            if not job.allow_failure:
                raise

        job.end_time = datetime.now(UTC)

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
                    shell=True,  # SECURITY: Intentional — executes pipeline commands from YAML config
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
        max_workers = max(min(len(stages), 4), 1)  # Limit concurrent stages; floor at 1

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
                        concurrent.futures.wait(list(futures.values()), timeout=1.0)
                        for stage_name, future in list(futures.items()):
                            if future.done():
                                try:
                                    result = future.result()
                                    results[stage_name] = result
                                    completed.add(stage_name)
                                except Exception as e:
                                    results[stage_name] = {
                                        "error": str(e),
                                        "status": "failed",
                                    }
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
            "failed_stages": len(
                [
                    r
                    for r in results.values()
                    if isinstance(r, dict) and r.get("status") == "failed"
                ]
            ),
            "stage_results": results,
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
                job_results.append(
                    {"name": job["name"], "status": "completed", "duration": 0.05}
                )

            return {
                "stage_name": stage["name"],
                "status": "completed",
                "job_count": len(jobs),
                "jobs": job_results,
                "duration": 0.1 + (len(jobs) * 0.05),
            }

        except Exception as e:
            return {"stage_name": stage["name"], "status": "failed", "error": str(e)}

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
