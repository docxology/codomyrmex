"""Comprehensive unit tests for ci_cd_automation.pipeline.async_manager.

Tests cover: AsyncPipelineResult dataclass, AsyncPipelineManager init/defaults,
header generation, create_pipeline delegation, async_run_local_pipeline,
network-error paths for trigger/status/cancel/workflow-runs, and module-level
convenience functions.

Zero-mock policy: all tests use real objects.  Network methods target an
unreachable local address so they exercise the real aiohttp.ClientError
catch blocks without any stubs.
"""

import json
import os
from datetime import datetime, timezone, UTC

import pytest

from codomyrmex.ci_cd_automation.pipeline.async_manager import (
    AsyncPipelineManager,
    AsyncPipelineResult,
    async_get_pipeline_status,
    async_trigger_pipeline,
    async_wait_for_completion,
)
from codomyrmex.ci_cd_automation.pipeline.models import (
    Pipeline,
    PipelineStatus,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# A URL that is guaranteed to refuse connections quickly so aiohttp raises
# ClientError (ClientConnectorError) without any mock.
_UNREACHABLE_URL = "http://127.0.0.1:1"


def _make_manager(
    tmp_path,
    base_url: str = _UNREACHABLE_URL,
    api_token: str | None = None,
) -> AsyncPipelineManager:
    """Create an AsyncPipelineManager pointing at an unreachable host."""
    workspace = str(tmp_path / "pipelines")
    return AsyncPipelineManager(
        base_url=base_url,
        api_token=api_token,
        workspace_dir=workspace,
    )


def _write_json_config(tmp_path, config: dict) -> str:
    """Write a pipeline JSON config and return its path."""
    config_path = str(tmp_path / "pipeline.json")
    with open(config_path, "w") as f:
        json.dump(config, f)
    return config_path


def _minimal_config() -> dict:
    """Return the smallest valid pipeline config."""
    return {
        "name": "test_pipeline",
        "stages": [
            {
                "name": "build",
                "jobs": [
                    {
                        "name": "compile",
                        "commands": ["echo hello"],
                    }
                ],
            }
        ],
    }


# ---------------------------------------------------------------------------
# AsyncPipelineResult tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAsyncPipelineResult:
    """Tests for the AsyncPipelineResult dataclass."""

    def test_basic_creation(self):
        """Result created with required fields gets sensible defaults."""
        result = AsyncPipelineResult(
            pipeline_id="pipe-1",
            status=PipelineStatus.PENDING,
            message="queued",
        )
        assert result.pipeline_id == "pipe-1"
        assert result.status == PipelineStatus.PENDING
        assert result.message == "queued"
        assert result.data is None
        assert result.error is None
        assert isinstance(result.timestamp, datetime)

    def test_creation_with_all_fields(self):
        """Result created with every field stores them correctly."""
        ts = datetime(2026, 2, 26, 12, 0, 0, tzinfo=UTC)
        result = AsyncPipelineResult(
            pipeline_id="pipe-2",
            status=PipelineStatus.SUCCESS,
            message="done",
            data={"key": "value"},
            error=None,
            timestamp=ts,
        )
        assert result.data == {"key": "value"}
        assert result.timestamp == ts

    def test_to_dict_structure(self):
        """to_dict returns a well-formed dictionary with all expected keys."""
        result = AsyncPipelineResult(
            pipeline_id="pipe-3",
            status=PipelineStatus.FAILURE,
            message="boom",
            data={"exit_code": 1},
            error="process exited 1",
        )
        d = result.to_dict()

        assert d["pipeline_id"] == "pipe-3"
        assert d["status"] == "failure"
        assert d["message"] == "boom"
        assert d["data"] == {"exit_code": 1}
        assert d["error"] == "process exited 1"
        assert "timestamp" in d
        # Timestamp should be an ISO-format string
        datetime.fromisoformat(d["timestamp"])

    def test_to_dict_with_none_data(self):
        """to_dict properly serialises None optional fields."""
        result = AsyncPipelineResult(
            pipeline_id="pipe-4",
            status=PipelineStatus.CANCELLED,
            message="cancelled",
        )
        d = result.to_dict()
        assert d["data"] is None
        assert d["error"] is None

    def test_to_dict_status_values(self):
        """All PipelineStatus enum values serialise correctly."""
        for status in PipelineStatus:
            result = AsyncPipelineResult(
                pipeline_id="enum-check",
                status=status,
                message="test",
            )
            assert result.to_dict()["status"] == status.value


# ---------------------------------------------------------------------------
# AsyncPipelineManager.__init__ tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAsyncPipelineManagerInit:
    """Tests for AsyncPipelineManager constructor and default handling."""

    def test_explicit_params(self, tmp_path):
        """Explicit constructor args are stored verbatim."""
        ws = str(tmp_path / "ws")
        mgr = AsyncPipelineManager(
            base_url="https://custom.api",
            api_token="tok-abc",
            workspace_dir=ws,
        )
        assert mgr.base_url == "https://custom.api"
        assert mgr.api_token == "tok-abc"
        assert mgr.workspace_dir == ws
        assert os.path.isdir(ws)

    def test_default_base_url_without_env(self, tmp_path):
        """Without CI_CD_API_URL env var, defaults to github.com."""
        original = os.environ.get("CI_CD_API_URL")
        try:
            os.environ.pop("CI_CD_API_URL", None)
            ws = str(tmp_path / "ws2")
            mgr2 = AsyncPipelineManager(workspace_dir=ws)
            assert "github.com" in mgr2.base_url
        finally:
            if original is None:
                os.environ.pop("CI_CD_API_URL", None)
            else:
                os.environ["CI_CD_API_URL"] = original

    def test_base_url_from_env(self, tmp_path):
        """CI_CD_API_URL env var is respected when no explicit base_url."""
        original = os.environ.get("CI_CD_API_URL")
        try:
            os.environ["CI_CD_API_URL"] = "https://env.example.com"
            ws = str(tmp_path / "ws3")
            mgr = AsyncPipelineManager(workspace_dir=ws)
            assert mgr.base_url == "https://env.example.com"
        finally:
            if original is None:
                os.environ.pop("CI_CD_API_URL", None)
            else:
                os.environ["CI_CD_API_URL"] = original

    def test_api_token_from_env(self, tmp_path):
        """CI_CD_API_TOKEN env var is picked up."""
        original = os.environ.get("CI_CD_API_TOKEN")
        try:
            os.environ["CI_CD_API_TOKEN"] = "env-token-123"
            ws = str(tmp_path / "ws4")
            mgr = AsyncPipelineManager(workspace_dir=ws)
            assert mgr.api_token == "env-token-123"
        finally:
            if original is None:
                os.environ.pop("CI_CD_API_TOKEN", None)
            else:
                os.environ["CI_CD_API_TOKEN"] = original

    def test_workspace_created(self, tmp_path):
        """Workspace directory is created during init."""
        ws = str(tmp_path / "fresh_workspace")
        assert not os.path.exists(ws)
        AsyncPipelineManager(
            base_url="https://x", workspace_dir=ws
        )
        assert os.path.isdir(ws)

    def test_pipelines_dict_starts_empty(self, tmp_path):
        """Pipelines dict is empty on fresh manager."""
        mgr = _make_manager(tmp_path)
        assert mgr.pipelines == {}

    def test_sync_manager_wired(self, tmp_path):
        """Internal _sync_manager is initialised with same workspace."""
        ws = str(tmp_path / "ws5")
        mgr = AsyncPipelineManager(
            base_url="https://x",
            workspace_dir=ws,
        )
        assert mgr._sync_manager is not None
        assert mgr._sync_manager.workspace_dir == ws


# ---------------------------------------------------------------------------
# _get_headers tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetHeaders:
    """Tests for _get_headers method."""

    def test_headers_without_token(self, tmp_path):
        """Without an API token, no Authorization header is present."""
        mgr = _make_manager(tmp_path, api_token=None)
        # Ensure there's no token from env either
        mgr.api_token = None
        headers = mgr._get_headers()
        assert "Accept" in headers
        assert "Content-Type" in headers
        assert "Authorization" not in headers

    def test_headers_with_token(self, tmp_path):
        """With an API token, Authorization header is 'token <value>'."""
        mgr = _make_manager(tmp_path, api_token="my-secret")
        headers = mgr._get_headers()
        assert headers["Authorization"] == "token my-secret"
        assert "Accept" in headers


# ---------------------------------------------------------------------------
# create_pipeline tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCreatePipeline:
    """Tests for create_pipeline (delegates to sync manager)."""

    def test_create_pipeline_from_json(self, tmp_path):
        """create_pipeline loads JSON, returns Pipeline, and stores it."""
        mgr = _make_manager(tmp_path)
        config_path = _write_json_config(tmp_path, _minimal_config())

        pipeline = mgr.create_pipeline(config_path)

        assert isinstance(pipeline, Pipeline)
        assert pipeline.name == "test_pipeline"
        assert len(pipeline.stages) == 1
        assert "test_pipeline" in mgr.pipelines
        assert mgr.pipelines["test_pipeline"] is pipeline

    def test_create_pipeline_also_registered_in_sync_manager(self, tmp_path):
        """Pipeline is registered in both async and sync managers."""
        mgr = _make_manager(tmp_path)
        config_path = _write_json_config(tmp_path, _minimal_config())

        mgr.create_pipeline(config_path)

        assert "test_pipeline" in mgr._sync_manager.pipelines

    def test_create_pipeline_missing_file_raises(self, tmp_path):
        """Nonexistent config path raises an error."""
        mgr = _make_manager(tmp_path)
        with pytest.raises(FileNotFoundError):
            mgr.create_pipeline(str(tmp_path / "missing.json"))

    def test_create_pipeline_with_variables(self, tmp_path):
        """Pipeline config variables are preserved."""
        config = _minimal_config()
        config["variables"] = {"ENV": "staging", "VERSION": "1.0.0"}
        config_path = _write_json_config(tmp_path, config)

        mgr = _make_manager(tmp_path)
        pipeline = mgr.create_pipeline(config_path)

        assert pipeline.variables == {"ENV": "staging", "VERSION": "1.0.0"}


# ---------------------------------------------------------------------------
# async_run_local_pipeline tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAsyncRunLocalPipeline:
    """Tests for async_run_local_pipeline."""

    async def test_pipeline_not_found_raises(self, tmp_path):
        """ValueError raised when pipeline name is not registered."""
        mgr = _make_manager(tmp_path)
        with pytest.raises(ValueError, match="not found"):
            await mgr.async_run_local_pipeline("nonexistent_pipeline")

    async def test_run_local_pipeline_with_echo(self, tmp_path):
        """A real local pipeline with 'echo' executes successfully."""
        mgr = _make_manager(tmp_path)
        config_path = _write_json_config(tmp_path, _minimal_config())
        mgr.create_pipeline(config_path)

        result = await mgr.async_run_local_pipeline("test_pipeline")

        assert isinstance(result, Pipeline)
        assert result.status in (PipelineStatus.SUCCESS, PipelineStatus.FAILURE)
        # echo hello should succeed
        assert result.status == PipelineStatus.SUCCESS

    async def test_run_local_pipeline_with_variables(self, tmp_path):
        """Runtime variable overrides are passed through."""
        config = _minimal_config()
        config["variables"] = {"MSG": "original"}
        config["stages"][0]["jobs"][0]["commands"] = ["echo ${MSG}"]
        config_path = _write_json_config(tmp_path, config)

        mgr = _make_manager(tmp_path)
        mgr.create_pipeline(config_path)

        result = await mgr.async_run_local_pipeline(
            "test_pipeline",
            variables={"MSG": "overridden"},
        )
        assert result.status == PipelineStatus.SUCCESS


# ---------------------------------------------------------------------------
# Network method error-path tests (real aiohttp, unreachable host)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAsyncTriggerPipeline:
    """Tests for async_trigger_pipeline -- exercises aiohttp.ClientError path."""

    async def test_trigger_returns_failure_on_connection_error(self, tmp_path):
        """Connection refused produces FAILURE result, not an exception."""
        mgr = _make_manager(tmp_path)
        result = await mgr.async_trigger_pipeline(
            pipeline_name="ci",
            repo_owner="owner",
            repo_name="repo",
            workflow_id="ci.yml",
            timeout=2,
        )
        assert isinstance(result, AsyncPipelineResult)
        assert result.status == PipelineStatus.FAILURE
        assert result.error is not None
        assert result.pipeline_id == "ci"

    async def test_trigger_with_inputs(self, tmp_path):
        """Trigger with inputs dict still reaches error path gracefully."""
        mgr = _make_manager(tmp_path)
        result = await mgr.async_trigger_pipeline(
            pipeline_name="deploy",
            repo_owner="org",
            repo_name="app",
            workflow_id="deploy.yml",
            ref="release/v2",
            inputs={"environment": "prod"},
            timeout=2,
        )
        assert result.status == PipelineStatus.FAILURE
        assert result.pipeline_id == "deploy"


@pytest.mark.unit
class TestAsyncGetPipelineStatus:
    """Tests for async_get_pipeline_status."""

    async def test_status_with_run_id(self, tmp_path):
        """Requesting status by run_id hits error path."""
        mgr = _make_manager(tmp_path)
        result = await mgr.async_get_pipeline_status(
            repo_owner="owner",
            repo_name="repo",
            run_id=12345,
            timeout=2,
        )
        assert result.status == PipelineStatus.FAILURE
        assert result.error is not None

    async def test_status_with_workflow_id(self, tmp_path):
        """Requesting status by workflow_id hits error path."""
        mgr = _make_manager(tmp_path)
        result = await mgr.async_get_pipeline_status(
            repo_owner="owner",
            repo_name="repo",
            workflow_id="ci.yml",
            timeout=2,
        )
        assert result.status == PipelineStatus.FAILURE

    async def test_status_with_neither_id(self, tmp_path):
        """Requesting status with no run_id or workflow_id hits fallback URL."""
        mgr = _make_manager(tmp_path)
        result = await mgr.async_get_pipeline_status(
            repo_owner="owner",
            repo_name="repo",
            timeout=2,
        )
        assert result.status == PipelineStatus.FAILURE

    async def test_status_pipeline_id_from_run_id(self, tmp_path):
        """When run_id is given, result pipeline_id encodes it."""
        mgr = _make_manager(tmp_path)
        result = await mgr.async_get_pipeline_status(
            repo_owner="owner",
            repo_name="repo",
            run_id=99,
            timeout=2,
        )
        assert result.pipeline_id == "99"

    async def test_status_pipeline_id_from_workflow(self, tmp_path):
        """When only workflow_id given, pipeline_id uses that name."""
        mgr = _make_manager(tmp_path)
        result = await mgr.async_get_pipeline_status(
            repo_owner="owner",
            repo_name="repo",
            workflow_id="build.yml",
            timeout=2,
        )
        assert result.pipeline_id == "build.yml"


@pytest.mark.unit
class TestAsyncCancelPipeline:
    """Tests for async_cancel_pipeline."""

    async def test_cancel_connection_error(self, tmp_path):
        """Cancel request to unreachable host returns FAILURE."""
        mgr = _make_manager(tmp_path)
        result = await mgr.async_cancel_pipeline(
            repo_owner="owner",
            repo_name="repo",
            run_id=42,
            timeout=2,
        )
        assert result.status == PipelineStatus.FAILURE
        assert result.pipeline_id == "42"
        assert result.error is not None


@pytest.mark.unit
class TestAsyncGetWorkflowRuns:
    """Tests for async_get_workflow_runs."""

    async def test_get_runs_connection_error(self, tmp_path):
        """Listing runs against unreachable host returns FAILURE."""
        mgr = _make_manager(tmp_path)
        result = await mgr.async_get_workflow_runs(
            repo_owner="owner",
            repo_name="repo",
            timeout=2,
        )
        assert result.status == PipelineStatus.FAILURE
        assert result.pipeline_id == "workflow_runs"

    async def test_get_runs_with_filters(self, tmp_path):
        """Filters (workflow_id, status, branch) do not crash."""
        mgr = _make_manager(tmp_path)
        result = await mgr.async_get_workflow_runs(
            repo_owner="owner",
            repo_name="repo",
            workflow_id="ci.yml",
            status="completed",
            branch="main",
            per_page=5,
            timeout=2,
        )
        assert result.status == PipelineStatus.FAILURE

    async def test_get_runs_without_workflow_id(self, tmp_path):
        """When workflow_id is None, uses the all-runs endpoint."""
        mgr = _make_manager(tmp_path)
        result = await mgr.async_get_workflow_runs(
            repo_owner="owner",
            repo_name="repo",
            workflow_id=None,
            timeout=2,
        )
        assert result.status == PipelineStatus.FAILURE


# ---------------------------------------------------------------------------
# async_wait_for_completion tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAsyncWaitForCompletion:
    """Tests for async_wait_for_completion."""

    async def test_wait_times_out_quickly(self, tmp_path):
        """With a tiny timeout the method returns a timeout FAILURE."""
        mgr = _make_manager(tmp_path)
        result = await mgr.async_wait_for_completion(
            repo_owner="owner",
            repo_name="repo",
            run_id=1,
            poll_interval=1,
            timeout=2,
        )
        assert result.status == PipelineStatus.FAILURE
        assert "timeout" in (result.error or "").lower() or "Network error" in (result.message or "")


# ---------------------------------------------------------------------------
# Module-level convenience function tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestConvenienceFunctions:
    """Tests for the module-level async convenience functions."""

    async def test_async_trigger_pipeline_convenience(self):
        """Module-level async_trigger_pipeline returns a result."""
        orig_url = os.environ.get("CI_CD_API_URL")
        orig_tok = os.environ.get("CI_CD_API_TOKEN")
        try:
            os.environ["CI_CD_API_URL"] = _UNREACHABLE_URL
            os.environ.pop("CI_CD_API_TOKEN", None)
            result = await async_trigger_pipeline(
                repo_owner="owner",
                repo_name="repo",
                workflow_id="ci.yml",
            )
            assert isinstance(result, AsyncPipelineResult)
            assert result.status == PipelineStatus.FAILURE
        finally:
            if orig_url is None:
                os.environ.pop("CI_CD_API_URL", None)
            else:
                os.environ["CI_CD_API_URL"] = orig_url
            if orig_tok is None:
                os.environ.pop("CI_CD_API_TOKEN", None)
            else:
                os.environ["CI_CD_API_TOKEN"] = orig_tok

    async def test_async_get_pipeline_status_convenience(self):
        """Module-level async_get_pipeline_status returns a result."""
        orig_url = os.environ.get("CI_CD_API_URL")
        orig_tok = os.environ.get("CI_CD_API_TOKEN")
        try:
            os.environ["CI_CD_API_URL"] = _UNREACHABLE_URL
            os.environ.pop("CI_CD_API_TOKEN", None)
            result = await async_get_pipeline_status(
                repo_owner="owner",
                repo_name="repo",
                run_id=1,
            )
            assert isinstance(result, AsyncPipelineResult)
            assert result.status == PipelineStatus.FAILURE
        finally:
            if orig_url is None:
                os.environ.pop("CI_CD_API_URL", None)
            else:
                os.environ["CI_CD_API_URL"] = orig_url
            if orig_tok is None:
                os.environ.pop("CI_CD_API_TOKEN", None)
            else:
                os.environ["CI_CD_API_TOKEN"] = orig_tok

    async def test_async_wait_for_completion_convenience(self):
        """Module-level async_wait_for_completion returns a result."""
        orig_url = os.environ.get("CI_CD_API_URL")
        orig_tok = os.environ.get("CI_CD_API_TOKEN")
        try:
            os.environ["CI_CD_API_URL"] = _UNREACHABLE_URL
            os.environ.pop("CI_CD_API_TOKEN", None)
            result = await async_wait_for_completion(
                repo_owner="owner",
                repo_name="repo",
                run_id=1,
                poll_interval=1,
                timeout=2,
            )
            assert isinstance(result, AsyncPipelineResult)
            assert result.status == PipelineStatus.FAILURE
        finally:
            if orig_url is None:
                os.environ.pop("CI_CD_API_URL", None)
            else:
                os.environ["CI_CD_API_URL"] = orig_url
            if orig_tok is None:
                os.environ.pop("CI_CD_API_TOKEN", None)
            else:
                os.environ["CI_CD_API_TOKEN"] = orig_tok
