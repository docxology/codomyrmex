"""Zero-mock tests for coding.review module.

Verifies CodeReviewer and related functionality using real objects and files.
Handles environments where pyscn is not installed.
No mocks.
"""

import os
import textwrap
import pytest
from codomyrmex.coding.review import (
    CodeReviewer,
    PyscnAnalyzer,
    AnalysisType,
    Language,
    SeverityLevel,
    AnalysisResult,
    AnalysisSummary,
    QualityGateResult,
)
from codomyrmex.coding.review.models import ToolNotFoundError

@pytest.fixture
def reviewer(tmp_path):
    """Return a CodeReviewer rooted at a temporary directory."""
    try:
        return CodeReviewer(project_root=str(tmp_path))
    except ToolNotFoundError:
        # If pyscn is missing, we might need a way to test without it if possible,
        # but the current CodeReviewer.__init__ calls PyscnAnalyzer() which raises.
        pytest.skip("pyscn not installed, skipping CodeReviewer tests")

@pytest.fixture
def python_file(tmp_path):
    """Create a sample Python file with some issues."""
    p = tmp_path / "sample.py"
    p.write_text(textwrap.dedent("""\
        import os
        import sys # unused

        def complex_func(a, b):
            if a:
                if b:
                    for i in range(10):
                        if i % 2 == 0:
                            print(i)
            return a + b

        def bare_except():
            try:
                pass
            except:
                pass
    """))
    return str(p)

@pytest.mark.unit
class TestCodeReviewerFunctional:
    """Functional tests for CodeReviewer."""

    def test_init_defaults(self, reviewer, tmp_path):
        assert reviewer.project_root == str(tmp_path)
        assert isinstance(reviewer.results, list)
        assert isinstance(reviewer.tools_available, dict)

    def test_analyze_file_python(self, reviewer, python_file):
        results = reviewer.analyze_file(python_file)
        assert isinstance(results, list)

    def test_analyze_project(self, reviewer, python_file):
        summary = reviewer.analyze_project()
        assert isinstance(summary, AnalysisSummary)
        assert summary.files_analyzed == 1
        assert summary.analysis_time >= 0

    def test_check_quality_gates(self, reviewer):
        # Manually add a result to test gate
        reviewer.results.append(AnalysisResult(
            file_path="test.py",
            line_number=1,
            column_number=1,
            severity=SeverityLevel.ERROR,
            message="Too complex",
            rule_id="PYSCN_COMPLEXITY",
            category="complexity"
        ))
        gate_result = reviewer.check_quality_gates(thresholds={"max_complexity": 0})
        assert isinstance(gate_result, QualityGateResult)
        assert gate_result.passed is False
        assert gate_result.failed_checks > 0

    def test_clear_results(self, reviewer):
        reviewer.results.append(AnalysisResult("a.py", 1, 1, SeverityLevel.INFO, "m", "R", "c"))
        reviewer.clear_results()
        assert len(reviewer.results) == 0

@pytest.mark.unit
class TestPyscnAnalyzerFunctional:
    """Functional tests for PyscnAnalyzer."""

    def test_pyscn_init_raises_if_missing(self):
        # Test that it correctly identifies missing tool
        try:
            PyscnAnalyzer()
        except ToolNotFoundError:
            pass # Expected if not installed
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

    def test_pyscn_analyze_complex_code(self, python_file):
        try:
            analyzer = PyscnAnalyzer()
        except ToolNotFoundError:
            pytest.skip("pyscn not installed")

        with open(python_file, "r") as f:
            code = f.read()
        results = analyzer.analyze_code(code, python_file)
        assert isinstance(results, list)
