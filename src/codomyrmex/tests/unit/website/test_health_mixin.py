"""Zero-mock tests for HealthProviderMixin.

Tests the real project filesystem and git state for health, pipeline,
LLM config, and architecture layer data retrieval.

Zero-Mock policy: every test exercises real production code paths — no
unittest.mock, MagicMock, or @patch usage.
"""

from pathlib import Path

import pytest

from codomyrmex.website.data_provider import DataProvider

# ── Fixtures ────────────────────────────────────────────────────────

_PROJECT_ROOT = Path(__file__).resolve().parents[5]


@pytest.fixture
def provider() -> DataProvider:
    """DataProvider pointed at the real project root."""
    return DataProvider(root_dir=_PROJECT_ROOT)


@pytest.fixture
def tmp_provider(tmp_path: Path) -> DataProvider:
    """DataProvider with a temporary root (no git, no workflows)."""
    return DataProvider(root_dir=tmp_path)


# ── Test: get_pipeline_status ────────────────────────────────────────


class TestGetPipelineStatus:
    """Tests for HealthProviderMixin.get_pipeline_status."""

    def test_returns_list(self, provider: DataProvider) -> None:
        result = provider.get_pipeline_status()
        assert isinstance(result, list)

    def test_workflow_structure(self, provider: DataProvider) -> None:
        """Each workflow entry has expected keys (name, file)."""
        pipelines = provider.get_pipeline_status()
        if not pipelines:
            pytest.skip("No .github/workflows/ found")
        pipeline = pipelines[0]
        for key in ("name", "file"):
            assert key in pipeline, f"Missing key: {key}"

    def test_graceful_on_empty(self, tmp_provider: DataProvider) -> None:
        result = tmp_provider.get_pipeline_status()
        assert isinstance(result, list)


# ── Test: get_health_status ──────────────────────────────────────────


class TestGetHealthStatus:
    """Tests for HealthProviderMixin.get_health_status."""

    def test_returns_dict(self, provider: DataProvider) -> None:
        result = provider.get_health_status()
        assert isinstance(result, dict)

    def test_top_level_keys(self, provider: DataProvider) -> None:
        """Health status has status_text, status_class, modules, python, git."""
        result = provider.get_health_status()
        for key in ("status_text", "status_class", "modules", "python", "git"):
            assert key in result, f"Missing key: {key}"

    def test_status_class_valid(self, provider: DataProvider) -> None:
        result = provider.get_health_status()
        assert result["status_class"] in ("ok", "warn", "err")

    def test_modules_is_dict(self, provider: DataProvider) -> None:
        """modules key contains stats dict (total, with_tests, etc.)."""
        result = provider.get_health_status()
        modules = result["modules"]
        assert isinstance(modules, dict)
        assert "total" in modules

    def test_python_info(self, provider: DataProvider) -> None:
        result = provider.get_health_status()
        assert "version" in result["python"]

    def test_graceful_on_empty(self, tmp_provider: DataProvider) -> None:
        result = tmp_provider.get_health_status()
        assert isinstance(result, dict)
        assert "status_text" in result or "status_class" in result


# ── Test: get_llm_config ─────────────────────────────────────────────


class TestGetLlmConfig:
    """Tests for HealthProviderMixin.get_llm_config."""

    def test_returns_dict(self, provider: DataProvider) -> None:
        result = provider.get_llm_config()
        assert isinstance(result, dict)

    def test_has_model_info(self, provider: DataProvider) -> None:
        """LLM config should contain model info."""
        result = provider.get_llm_config()
        assert len(result) > 0


# ── Test: _get_git_info ──────────────────────────────────────────────


class TestGetGitInfo:
    """Tests for HealthProviderMixin._get_git_info."""

    def test_returns_dict(self, provider: DataProvider) -> None:
        result = provider._get_git_info()
        assert isinstance(result, dict)

    def test_has_branch_or_error(self, provider: DataProvider) -> None:
        result = provider._get_git_info()
        assert "branch" in result or "error" in result

    def test_graceful_on_non_repo(self, tmp_provider: DataProvider) -> None:
        result = tmp_provider._get_git_info()
        assert isinstance(result, dict)


# ── Test: _get_architecture_layers ───────────────────────────────────


class TestGetArchitectureLayers:
    """Tests for HealthProviderMixin._get_architecture_layers.

    Returns a list of layer dicts: [{"name": "...", "modules": [...], "color": "..."}].
    """

    def test_returns_list(self, provider: DataProvider) -> None:
        result = provider._get_architecture_layers()
        assert isinstance(result, list)

    def test_layer_entries_have_keys(self, provider: DataProvider) -> None:
        result = provider._get_architecture_layers()
        if not result:
            pytest.skip("No architecture layers defined")
        for layer in result:
            assert "name" in layer
            assert "modules" in layer
            assert isinstance(layer["modules"], list)


# ── Test: _compute_overall_status ────────────────────────────────────


class TestComputeOverallStatus:
    """Tests for HealthProviderMixin._compute_overall_status."""

    def test_returns_tuple(self, provider: DataProvider) -> None:
        result = provider._compute_overall_status([], {})
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_empty_modules_yields_status(self, provider: DataProvider) -> None:
        status_text, status_class = provider._compute_overall_status([], {})
        assert isinstance(status_text, str)
        assert status_class in ("ok", "warn", "err")

    def test_healthy_modules(self, provider: DataProvider) -> None:
        modules = [{"name": "test", "status": "Active"}]
        git_info = {"branch": "main"}
        status_text, status_class = provider._compute_overall_status(
            modules, git_info
        )
        assert status_class in ("ok", "warn", "err")


# ── Test: run_tests ──────────────────────────────────────────────────


class TestRunTests:
    """Tests for HealthProviderMixin.run_tests (method existence only).

    NOTE: run_tests() spawns a full subprocess pytest invocation, so we
    verify the method is callable rather than invoking it in a unit test
    to avoid multi-minute subprocess execution.
    """

    def test_method_exists(self, provider: DataProvider) -> None:
        """run_tests method is callable."""
        assert callable(getattr(provider, "run_tests", None))
