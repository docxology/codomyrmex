"""
Unit tests for DataProvider HealthProviderMixin — Zero-Mock compliant.

Tests get_llm_config(), _compute_overall_status(), and get_health_status()
which have zero direct coverage. Pipeline, git_info, and architecture_layers
are already tested in test_data_provider.py.
"""
import pytest

from codomyrmex.website.data_provider import DataProvider

# ── get_llm_config ────────────────────────────────────────────────────

@pytest.mark.unit
class TestGetLlmConfig:
    """Tests for get_llm_config() — LLM configuration loading."""

    def test_returns_dict(self, tmp_path):
        """get_llm_config() returns a dict."""
        provider = DataProvider(tmp_path)
        result = provider.get_llm_config()
        assert isinstance(result, dict)

    def test_has_required_keys(self, tmp_path):
        """Result has default_model, preferred_models, available_models, ollama_host."""
        provider = DataProvider(tmp_path)
        result = provider.get_llm_config()
        for key in ("default_model", "preferred_models", "available_models", "ollama_host"):
            assert key in result, f"Missing key: {key}"

    def test_default_model_is_non_empty_string(self, tmp_path):
        """default_model is a non-empty string."""
        provider = DataProvider(tmp_path)
        result = provider.get_llm_config()
        assert isinstance(result["default_model"], str)
        assert len(result["default_model"]) > 0

    def test_available_models_is_list(self, tmp_path):
        """available_models is a list."""
        provider = DataProvider(tmp_path)
        result = provider.get_llm_config()
        assert isinstance(result["available_models"], list)


# ── _compute_overall_status ───────────────────────────────────────────

@pytest.mark.unit
class TestComputeOverallStatus:
    """Tests for _compute_overall_status() — status + class derivation."""

    def test_no_modules_returns_no_modules_warn(self, tmp_path):
        """Empty module list → ('No Modules', 'warn')."""
        provider = DataProvider(tmp_path)
        status, cls = provider._compute_overall_status([], {})
        assert status == "No Modules"
        assert cls == "warn"

    def test_all_active_with_git_returns_operational(self, tmp_path):
        """All Active modules + clean git → ('Operational', 'ok')."""
        provider = DataProvider(tmp_path)
        modules = [{"status": "Active"}, {"status": "Active"}, {"status": "Active"}]
        git_info = {"branch": "main", "last_commit": "abc123"}
        status, cls = provider._compute_overall_status(modules, git_info)
        assert status == "Operational"
        assert cls == "ok"

    def test_minority_errors_returns_degraded(self, tmp_path):
        """Minority of error modules → ('Degraded', 'warn')."""
        provider = DataProvider(tmp_path)
        modules = [
            {"status": "Active"}, {"status": "Active"}, {"status": "Active"},
            {"status": "SyntaxError"},  # 1/4 = 25%, < 50%
        ]
        git_info = {"branch": "main"}
        status, cls = provider._compute_overall_status(modules, git_info)
        assert status == "Degraded"
        assert cls == "warn"

    def test_majority_errors_returns_error(self, tmp_path):
        """More than 50% error modules → ('Error', 'err')."""
        provider = DataProvider(tmp_path)
        modules = [
            {"status": "SyntaxError"}, {"status": "ImportError"},
            {"status": "Active"},  # 2/3 = 67% errors
        ]
        git_info = {"branch": "main"}
        status, cls = provider._compute_overall_status(modules, git_info)
        assert status == "Error"
        assert cls == "err"

    def test_git_error_key_returns_degraded(self, tmp_path):
        """'error' key in git_info degrades status even if modules healthy."""
        provider = DataProvider(tmp_path)
        modules = [{"status": "Active"}, {"status": "Active"}]
        git_info = {"error": "git not available"}
        status, cls = provider._compute_overall_status(modules, git_info)
        assert status == "Degraded"
        assert cls == "warn"


# ── get_health_status ─────────────────────────────────────────────────

@pytest.mark.unit
class TestGetHealthStatus:
    """Tests for get_health_status() — comprehensive system health aggregation."""

    def test_returns_dict(self, tmp_path):
        """get_health_status() returns a dict."""
        provider = DataProvider(tmp_path)
        result = provider.get_health_status()
        assert isinstance(result, dict)

    def test_has_required_top_level_keys(self, tmp_path):
        """Result includes all required top-level keys."""
        provider = DataProvider(tmp_path)
        result = provider.get_health_status()
        required = {
            "uptime", "uptime_seconds", "status_text", "status_class",
            "python", "git", "modules", "architecture_layers", "llm_config",
        }
        for key in required:
            assert key in result, f"Missing key: {key}"

    def test_uptime_seconds_non_negative(self, tmp_path):
        """uptime_seconds is a non-negative integer."""
        provider = DataProvider(tmp_path)
        result = provider.get_health_status()
        assert isinstance(result["uptime_seconds"], int)
        assert result["uptime_seconds"] >= 0

    def test_python_info_has_required_keys(self, tmp_path):
        """python sub-dict has version, executable, platform."""
        provider = DataProvider(tmp_path)
        result = provider.get_health_status()
        python = result["python"]
        assert isinstance(python, dict)
        for key in ("version", "executable", "platform"):
            assert key in python, f"python missing key: {key}"

    def test_modules_stats_has_required_keys(self, tmp_path):
        """modules sub-dict has total, with_tests, with_api_spec, test_coverage_pct."""
        provider = DataProvider(tmp_path)
        result = provider.get_health_status()
        mods = result["modules"]
        assert isinstance(mods, dict)
        for key in ("total", "with_tests", "with_api_spec", "test_coverage_pct"):
            assert key in mods, f"modules missing key: {key}"
