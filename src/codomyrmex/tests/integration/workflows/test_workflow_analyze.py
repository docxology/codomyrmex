import pytest

from codomyrmex.coding.review.models import AnalysisSummary


def _import_analyze():
    try:
        from codomyrmex.coding import analyze_project

        return analyze_project
    except Exception:
        pytest.skip("analyze_project or its dependency (pyscn) not available")


@pytest.mark.integration
class TestWorkflowAnalyze:
    def test_analyze_utils_module(self, src_codomyrmex):
        analyze_project = _import_analyze()
        target = str(src_codomyrmex / "utils" / "__init__.py")

        try:
            result = analyze_project(target)
        except Exception as exc:
            if "pyscn" in str(exc).lower() or "ToolNotFoundError" in type(exc).__name__:
                pytest.skip(f"External tool unavailable: {exc}")
            raise

        assert isinstance(result, AnalysisSummary), (
            f"Expected summary, got {type(result)}"
        )
        assert result.files_analyzed == 1
        assert result.analysis_time >= 0.0

    def test_analyze_returns_summary(self, src_codomyrmex):
        analyze_project = _import_analyze()
        target = str(src_codomyrmex / "coding" / "review" / "models.py")

        try:
            result = analyze_project(target)
        except Exception as exc:
            if "pyscn" in str(exc).lower() or "ToolNotFoundError" in type(exc).__name__:
                pytest.skip(f"External tool unavailable: {exc}")
            raise

        assert isinstance(result, AnalysisSummary)
        assert result.files_analyzed == 1
        assert isinstance(result.total_issues, int)

    def test_analyze_nonexistent_path(self):
        analyze_project = _import_analyze()

        try:
            result = analyze_project("/nonexistent/path/xyz")
        except Exception as exc:
            if "pyscn" in str(exc).lower() or "ToolNotFoundError" in type(exc).__name__:
                pytest.skip(f"External tool unavailable: {exc}")
            raise

        assert isinstance(result, AnalysisSummary)
        assert result.files_analyzed == 0
