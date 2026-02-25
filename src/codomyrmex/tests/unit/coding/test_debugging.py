"""Zero-Mock tests for debugging module.

Uses real ErrorAnalyzer, PatchGenerator, and Debugger with real internal
components instead of mocking them.
"""

import textwrap
from pathlib import Path

import pytest

from codomyrmex.coding.debugging import (
    Debugger,
    ErrorAnalyzer,
    ErrorDiagnosis,
    Patch,
    PatchGenerator,
)


@pytest.mark.unit
class TestErrorAnalyzer:
    """Test suite for ErrorAnalyzer."""
    def setup_method(self):
        self.analyzer = ErrorAnalyzer()

    def test_parse_python_syntax_error(self):
        """Test functionality: parse python syntax error."""
        stderr = 'File "test.py", line 1\n    if True\n          ^\nSyntaxError: invalid syntax'
        diagnosis = self.analyzer.analyze("", stderr, 1)
        assert diagnosis is not None
        assert diagnosis.error_type == "SyntaxError"
        assert diagnosis.line_number == 1
        assert diagnosis.file_path == "test.py"

    def test_parse_python_runtime_error(self):
        """Test functionality: parse python runtime error."""
        stderr = 'Traceback (most recent call last):\n  File "main.py", line 10, in <module>\n    print(1/0)\nZeroDivisionError: division by zero'
        diagnosis = self.analyzer.analyze("", stderr, 1)
        assert diagnosis is not None
        assert diagnosis.error_type == "ZeroDivisionError"
        assert diagnosis.line_number == 10
        assert diagnosis.message == "division by zero"

    def test_timeout_error(self):
        """Test functionality: timeout error."""
        diagnosis = self.analyzer.analyze("", "Terminated", 124)
        assert diagnosis is not None
        assert diagnosis.error_type == "TimeoutError"
        assert diagnosis.is_timeout


@pytest.mark.unit
class TestPatchGenerator:
    """Test suite for PatchGenerator."""
    def setup_method(self):
        self.generator = PatchGenerator(llm_client=None)

    def test_generate_no_file_path(self):
        """Test functionality: generate no file path."""
        diagnosis = ErrorDiagnosis("Error", "msg")
        patches = self.generator.generate("code", diagnosis)
        assert patches == []

    def test_generate_returns_list(self):
        """Test functionality: generate returns list."""
        diagnosis = ErrorDiagnosis("Error", "msg", "file.py", 10, "trace")
        patches = self.generator.generate("code", diagnosis)
        assert isinstance(patches, list)


@pytest.mark.unit
class TestDebugger:
    """Test suite for Debugger."""
    def setup_method(self):
        self.debugger = Debugger()

    def test_debug_flow_with_real_components(self):
        """Test the full debug flow with real analyzer, patcher, verifier."""
        # Use a real Python error that the analyzer can parse
        source = 'print(1/0)\n'
        stderr = 'Traceback (most recent call last):\n  File "test.py", line 1, in <module>\n    print(1/0)\nZeroDivisionError: division by zero'

        result = self.debugger.debug(source, "", stderr, 1)
        # The debugger may or may not produce a fix (depends on LLM availability),
        # but it should not crash and should return a result or None
        # With no LLM client, patcher returns empty patches, so result may be None
        assert result is None or isinstance(result, dict)

    def test_debug_flow_no_error(self):
        """Test debug flow when exit code is 0 (no error)."""
        result = self.debugger.debug("print('ok')", "ok", "", 0)
        # Should handle gracefully when there is no error to debug
        assert result is None or isinstance(result, dict)


# From test_coverage_boost_r5.py
class TestAnalysisEnums:
    """Tests for static analysis enums."""

    def test_analysis_type(self):
        from codomyrmex.coding.static_analysis.static_analyzer import AnalysisType

        assert AnalysisType.QUALITY.value == "quality"
        assert AnalysisType.SECURITY.value == "security"

    def test_severity_level(self):
        from codomyrmex.coding.static_analysis.static_analyzer import SeverityLevel

        assert SeverityLevel.INFO.value == "info"
        assert SeverityLevel.CRITICAL.value == "critical"

    def test_language(self):
        from codomyrmex.coding.static_analysis.static_analyzer import Language

        assert Language.PYTHON.value == "python"
        assert Language.JAVASCRIPT.value == "javascript"


# From test_coverage_boost_r5.py
class TestAnalysisResult:
    """Tests for AnalysisResult dataclass."""

    def test_creation(self):
        from codomyrmex.coding.static_analysis.static_analyzer import (
            AnalysisResult, SeverityLevel,
        )

        r = AnalysisResult(
            file_path="test.py",
            line_number=10,
            column_number=5,
            severity=SeverityLevel.WARNING,
            message="Unused variable",
            rule_id="W001",
            category="style",
        )
        assert r.file_path == "test.py"
        assert r.severity == SeverityLevel.WARNING
        assert r.confidence == 1.0


# From test_coverage_boost_r5.py
class TestCodeMetrics:
    """Tests for CodeMetrics dataclass."""

    def test_creation(self):
        from codomyrmex.coding.static_analysis.static_analyzer import CodeMetrics

        m = CodeMetrics(
            lines_of_code=500,
            cyclomatic_complexity=10,
            maintainability_index=85.0,
            technical_debt=2.5,
            code_duplication=3.2,
        )
        assert m.lines_of_code == 500
        assert m.maintainability_index == 85.0


# From test_coverage_boost_r5.py
class TestStaticAnalyzer:
    """Tests for StaticAnalyzer."""

    def test_init(self, tmp_path):
        from codomyrmex.coding.static_analysis.static_analyzer import StaticAnalyzer

        analyzer = StaticAnalyzer(project_root=str(tmp_path))
        assert analyzer is not None

    def test_detect_language(self, tmp_path):
        from codomyrmex.coding.static_analysis.static_analyzer import StaticAnalyzer

        analyzer = StaticAnalyzer(project_root=str(tmp_path))
        py_file = tmp_path / "test.py"
        py_file.write_text("print('hello')")
        lang = analyzer._detect_language(str(py_file))
        assert lang is not None

    def test_analyze_python_file(self, tmp_path):
        from codomyrmex.coding.static_analysis.static_analyzer import StaticAnalyzer

        analyzer = StaticAnalyzer(project_root=str(tmp_path))
        py_file = tmp_path / "sample.py"
        py_file.write_text(textwrap.dedent("""\
            def foo(x):
                y = x + 1
                return y

            def bar():
                pass
        """))
        results = analyzer.analyze_file(str(py_file))
        assert isinstance(results, list)

    def test_clear_results(self, tmp_path):
        from codomyrmex.coding.static_analysis.static_analyzer import StaticAnalyzer

        analyzer = StaticAnalyzer(project_root=str(tmp_path))
        analyzer.clear_results()

    def test_export_results(self, tmp_path):
        from codomyrmex.coding.static_analysis.static_analyzer import StaticAnalyzer

        analyzer = StaticAnalyzer(project_root=str(tmp_path))
        out = str(tmp_path / "results.json")
        analyzer.export_results(out, format="json")
        assert Path(out).exists()
