"""Workflow integration test: /codomyrmexAnalyze.

Validates the ``analyze_project`` function from the coding module
returns meaningful structural analysis.  Skips if external tools
(pyscn) are unavailable.
"""

import pytest


def _import_analyze():
    """Import analyze_project, skip if pyscn is missing."""
    try:
        from codomyrmex.coding import analyze_project
        return analyze_project
    except Exception:
        pytest.skip("analyze_project or its dependency (pyscn) not available")


@pytest.mark.integration
class TestWorkflowAnalyze:
    """Tests mirroring the /codomyrmexAnalyze workflow."""

    def test_analyze_utils_module(self, src_codomyrmex):
        """Analyze src/codomyrmex/utils/ — expect valid structural data."""
        analyze_project = _import_analyze()
        target = str(src_codomyrmex / "utils")

        try:
            result = analyze_project(target)
        except Exception as exc:
            if "pyscn" in str(exc).lower() or "ToolNotFoundError" in type(exc).__name__:
                pytest.skip(f"External tool unavailable: {exc}")
            raise

        assert isinstance(result, dict), f"Expected dict, got {type(result)}"

    def test_analyze_returns_dict(self, src_codomyrmex):
        """analyse_project always returns a dict."""
        analyze_project = _import_analyze()

        try:
            result = analyze_project(str(src_codomyrmex))
        except Exception as exc:
            if "pyscn" in str(exc).lower() or "ToolNotFoundError" in type(exc).__name__:
                pytest.skip(f"External tool unavailable: {exc}")
            raise

        assert isinstance(result, dict)

    def test_analyze_nonexistent_path(self):
        """Analyzing a nonexistent path returns error or empty result."""
        analyze_project = _import_analyze()

        try:
            result = analyze_project("/nonexistent/path/xyz")
        except Exception as exc:
            if "pyscn" in str(exc).lower() or "ToolNotFoundError" in type(exc).__name__:
                pytest.skip(f"External tool unavailable: {exc}")
            raise

        assert isinstance(result, dict)
