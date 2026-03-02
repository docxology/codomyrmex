"""Async pipeline manager and convenience functions for non-blocking CI/CD operations."""

import asyncio
import json
import os
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import aiohttp

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from .manager import PipelineManager
from .models import Pipeline, PipelineStatus

logger = get_logger(__name__)


@dataclass
class AsyncPipelineResult:
    """Result of an async pipeline operation."""
    pipeline_id: str
    status: PipelineStatus
    message: str
    data: dict[str, Any] | None = None
    error: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

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

        except TimeoutError:
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
                        await response.text()
                        error_msg = f"Failed to get pipeline status: HTTP {response.status}"
                        logger.error(f"[ASYNC] {error_msg}")
                        return AsyncPipelineResult(
                            pipeline_id=str(run_id) if run_id else (workflow_id or "unknown"),
                            status=PipelineStatus.FAILURE,
                            message="Failed to get status",
                            error=error_msg,
                        )

        except TimeoutError:
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
                        await response.text()
                        error_msg = f"Failed to cancel pipeline: HTTP {response.status}"
                        logger.error(f"[ASYNC] {error_msg}")
                        return AsyncPipelineResult(
                            pipeline_id=str(run_id),
                            status=PipelineStatus.FAILURE,
                            message="Failed to cancel pipeline",
                            error=error_msg,
                        )

        except TimeoutError:
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
                        await response.text()
                        error_msg = f"Failed to get workflow runs: HTTP {response.status}"
                        logger.error(f"[ASYNC] {error_msg}")
                        return AsyncPipelineResult(
                            pipeline_id="workflow_runs",
                            status=PipelineStatus.FAILURE,
                            message="Failed to get workflow runs",
                            error=error_msg,
                        )

        except TimeoutError:
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
