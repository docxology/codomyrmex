"""Unit tests for static_analysis module -- pyrefly_runner, exceptions, init helpers.

Covers areas NOT tested by test_static_analysis_core.py (exports/imports),
test_static_analyzer_core.py (StaticAnalyzer enums/dataclasses),
complexity/test_complexity.py, or linting/test_linting.py.

Focus:
  - PyreflyIssue / PyreflyResult dataclasses
  - PyreflyRunner._parse_output (real JSON strings, no mocks)
  - PyreflyRunner availability detection
  - run_pyrefly / check_pyrefly_available convenience functions
  - Exception hierarchy (exceptions.py)
  - __init__.py: analyze_code_quality, cli_commands
"""

from __future__ import annotations

import json
import shutil

import pytest

from codomyrmex.coding.static_analysis.pyrefly_runner import (
    PyreflyIssue,
    PyreflyResult,
    PyreflyRunner,
    check_pyrefly_available,
    run_pyrefly,
)
from codomyrmex.coding.static_analysis.exceptions import (
    ASTError,
    ComplexityError,
    DependencyAnalysisError,
    LintError,
    MetricsError,
    ParserError,
    SecurityVulnerabilityError,
    TypeCheckError,
)
from codomyrmex.coding.static_analysis import (
    analyze_code_quality,
    cli_commands,
    get_available_tools,
)

pytestmark = pytest.mark.unit

PYREFLY_INSTALLED = shutil.which("pyrefly") is not None


# ===================================================================
# PyreflyIssue dataclass
# ===================================================================


class TestPyreflyIssue:
    """Tests for the PyreflyIssue dataclass."""

    def test_create_with_all_fields(self):
        """All fields including optional rule_id are stored correctly."""
        issue = PyreflyIssue(
            file_path="src/main.py",
            line=42,
            column=8,
            severity="error",
            message="Undefined name 'foo'",
            rule_id="E0001",
        )
        assert issue.file_path == "src/main.py"
        assert issue.line == 42
        assert issue.column == 8
        assert issue.severity == "error"
        assert issue.message == "Undefined name 'foo'"
        assert issue.rule_id == "E0001"

    def test_rule_id_defaults_to_none(self):
        """rule_id defaults to None when not provided."""
        issue = PyreflyIssue(
            file_path="a.py",
            line=1,
            column=0,
            severity="warning",
            message="test",
        )
        assert issue.rule_id is None

    def test_issue_equality(self):
        """Two PyreflyIssues with identical fields are equal (dataclass)."""
        kwargs = dict(
            file_path="x.py", line=10, column=5,
            severity="info", message="msg", rule_id=None,
        )
        assert PyreflyIssue(**kwargs) == PyreflyIssue(**kwargs)


# ===================================================================
# PyreflyResult dataclass
# ===================================================================


class TestPyreflyResult:
    """Tests for the PyreflyResult dataclass."""

    def test_successful_result_defaults(self):
        """A success result has empty issues, no error, 0 files by default."""
        result = PyreflyResult(success=True)
        assert result.success is True
        assert result.issues == []
        assert result.error_message is None
        assert result.files_analyzed == 0

    def test_failed_result_with_error(self):
        """A failure result captures the error message."""
        result = PyreflyResult(success=False, error_message="tool not found")
        assert result.success is False
        assert result.error_message == "tool not found"

    def test_result_with_issues(self):
        """Issues list stores PyreflyIssue instances."""
        issue = PyreflyIssue("f.py", 1, 0, "warning", "unused var")
        result = PyreflyResult(success=True, issues=[issue], files_analyzed=1)
        assert len(result.issues) == 1
        assert result.issues[0].message == "unused var"
        assert result.files_analyzed == 1


# ===================================================================
# PyreflyRunner._parse_output (real JSON, no mocks)
# ===================================================================


class TestPyreflyRunnerParseOutput:
    """Tests for PyreflyRunner._parse_output using real JSON strings."""

    def _make_runner(self) -> PyreflyRunner:
        """Create a runner; pyrefly_available is irrelevant for parse tests."""
        runner = object.__new__(PyreflyRunner)
        runner.config_path = None
        runner.pyrefly_available = False
        return runner

    def test_empty_string_returns_empty_list(self):
        """Empty stdout produces no issues."""
        runner = self._make_runner()
        assert runner._parse_output("") == []

    def test_whitespace_only_returns_empty(self):
        """Whitespace-only stdout produces no issues."""
        runner = self._make_runner()
        assert runner._parse_output("   \n  ") == []

    def test_valid_json_with_issues(self):
        """Valid pyrefly JSON output is parsed into PyreflyIssue objects."""
        runner = self._make_runner()
        data = {
            "issues": [
                {
                    "file": "app.py",
                    "line": 10,
                    "column": 4,
                    "severity": "error",
                    "message": "Type mismatch",
                    "rule_id": "TC001",
                },
                {
                    "file": "lib.py",
                    "line": 5,
                    "column": 0,
                    "severity": "warning",
                    "message": "Unused import",
                },
            ]
        }
        issues = runner._parse_output(json.dumps(data))
        assert len(issues) == 2
        assert issues[0].file_path == "app.py"
        assert issues[0].rule_id == "TC001"
        assert issues[1].severity == "warning"
        assert issues[1].rule_id is None

    def test_json_with_empty_issues_list(self):
        """JSON with an empty issues array produces no issues."""
        runner = self._make_runner()
        issues = runner._parse_output(json.dumps({"issues": []}))
        assert issues == []

    def test_json_missing_issues_key(self):
        """JSON without 'issues' key produces no issues (dict.get fallback)."""
        runner = self._make_runner()
        issues = runner._parse_output(json.dumps({"status": "ok"}))
        assert issues == []

    def test_invalid_json_returns_empty(self):
        """Non-JSON output is handled gracefully, returning empty list."""
        runner = self._make_runner()
        issues = runner._parse_output("this is not json {{[")
        assert issues == []

    def test_partial_issue_fields_use_defaults(self):
        """Issue entries with missing keys fall back to get() defaults."""
        runner = self._make_runner()
        data = {"issues": [{"message": "partial issue"}]}
        issues = runner._parse_output(json.dumps(data))
        assert len(issues) == 1
        assert issues[0].file_path == ""
        assert issues[0].line == 0
        assert issues[0].column == 0
        assert issues[0].severity == "warning"
        assert issues[0].message == "partial issue"
        assert issues[0].rule_id is None


# ===================================================================
# PyreflyRunner -- availability and unavailable-path
# ===================================================================


class TestPyreflyRunnerAvailability:
    """Tests for PyreflyRunner when pyrefly is not installed."""

    @pytest.mark.skipif(PYREFLY_INSTALLED, reason="pyrefly IS installed")
    def test_check_pyrefly_returns_false_when_absent(self):
        """_check_pyrefly returns False when the binary is not on PATH."""
        runner = PyreflyRunner()
        assert runner.pyrefly_available is False

    @pytest.mark.skipif(PYREFLY_INSTALLED, reason="pyrefly IS installed")
    def test_analyze_file_returns_failure_when_unavailable(self, tmp_path):
        """analyze_file returns a failure result when pyrefly is missing."""
        py_file = tmp_path / "sample.py"
        py_file.write_text("x = 1\n", encoding="utf-8")
        runner = PyreflyRunner()
        result = runner.analyze_file(str(py_file))
        assert result.success is False
        assert "not installed" in result.error_message.lower()

    @pytest.mark.skipif(PYREFLY_INSTALLED, reason="pyrefly IS installed")
    def test_analyze_directory_returns_failure_when_unavailable(self, tmp_path):
        """analyze_directory returns a failure result when pyrefly is missing."""
        runner = PyreflyRunner()
        result = runner.analyze_directory(str(tmp_path))
        assert result.success is False
        assert "not installed" in result.error_message.lower()


# ===================================================================
# Convenience functions: run_pyrefly, check_pyrefly_available
# ===================================================================


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    @pytest.mark.skipif(PYREFLY_INSTALLED, reason="pyrefly IS installed")
    def test_check_pyrefly_available_returns_bool(self):
        """check_pyrefly_available returns a boolean."""
        result = check_pyrefly_available()
        assert isinstance(result, bool)
        assert result is False

    @pytest.mark.skipif(PYREFLY_INSTALLED, reason="pyrefly IS installed")
    def test_run_pyrefly_on_file_path(self, tmp_path):
        """run_pyrefly dispatches to analyze_file for a file path."""
        py_file = tmp_path / "test.py"
        py_file.write_text("x = 1\n", encoding="utf-8")
        result = run_pyrefly(str(py_file))
        assert isinstance(result, PyreflyResult)
        assert result.success is False  # pyrefly not installed

    @pytest.mark.skipif(PYREFLY_INSTALLED, reason="pyrefly IS installed")
    def test_run_pyrefly_on_directory_path(self, tmp_path):
        """run_pyrefly dispatches to analyze_directory for a directory path."""
        result = run_pyrefly(str(tmp_path))
        assert isinstance(result, PyreflyResult)
        assert result.success is False  # pyrefly not installed


# ===================================================================
# Exception hierarchy (exceptions.py)
# ===================================================================


class TestExceptionHierarchy:
    """Tests for static analysis exception classes."""

    def test_parser_error_stores_context(self):
        """ParserError stores file_path, line, column in context."""
        err = ParserError("parse failed", file_path="bad.py", line=10, column=5)
        assert "parse failed" in str(err)
        assert err.context["file_path"] == "bad.py"
        assert err.context["line"] == 10
        assert err.context["column"] == 5

    def test_parser_error_without_optional_fields(self):
        """ParserError works with only the message."""
        err = ParserError("just a message")
        assert "file_path" not in err.context

    def test_lint_error_stores_linter_and_rule(self):
        """LintError stores linter name and rule in context."""
        err = LintError("lint fail", linter="ruff", rule="E501")
        assert err.context["linter"] == "ruff"
        assert err.context["rule"] == "E501"

    def test_type_check_error_stores_types(self):
        """TypeCheckError stores expected and actual types."""
        err = TypeCheckError("mismatch", expected_type="int", actual_type="str")
        assert err.context["expected_type"] == "int"
        assert err.context["actual_type"] == "str"

    def test_complexity_error_stores_metric_details(self):
        """ComplexityError stores metric, value, and threshold."""
        err = ComplexityError(
            "too complex", metric="cyclomatic", value=25.0, threshold=10.0
        )
        assert err.context["metric"] == "cyclomatic"
        assert err.context["value"] == 25.0
        assert err.context["threshold"] == 10.0

    def test_dependency_analysis_error_stores_dep_info(self):
        """DependencyAnalysisError stores dependency and version."""
        err = DependencyAnalysisError(
            "dep issue", dependency="numpy", version="1.24"
        )
        assert err.context["dependency"] == "numpy"
        assert err.context["version"] == "1.24"

    def test_security_vulnerability_error_stores_cwe(self):
        """SecurityVulnerabilityError stores vulnerability details."""
        err = SecurityVulnerabilityError(
            "vuln found",
            vulnerability_type="injection",
            severity="critical",
            cwe_id="CWE-89",
        )
        assert err.context["vulnerability_type"] == "injection"
        assert err.context["severity"] == "critical"
        assert err.context["cwe_id"] == "CWE-89"

    def test_ast_error_is_static_analysis_error(self):
        """ASTError inherits from StaticAnalysisError."""
        from codomyrmex.exceptions import StaticAnalysisError
        err = ASTError("ast broke")
        assert isinstance(err, StaticAnalysisError)

    def test_metrics_error_is_static_analysis_error(self):
        """MetricsError inherits from StaticAnalysisError."""
        from codomyrmex.exceptions import StaticAnalysisError
        err = MetricsError("metrics broke")
        assert isinstance(err, StaticAnalysisError)


# ===================================================================
# __init__.py: analyze_code_quality, cli_commands, get_available_tools
# ===================================================================


class TestInitHelpers:
    """Tests for functions exposed by coding.static_analysis.__init__."""

    def test_analyze_code_quality_on_real_directory(self, tmp_path):
        """analyze_code_quality returns a dict with expected keys."""
        py_file = tmp_path / "hello.py"
        py_file.write_text("print('hello')\n", encoding="utf-8")
        result = analyze_code_quality(path=str(tmp_path))
        assert isinstance(result, dict)
        assert "success" in result
        assert "path" in result
        assert result["path"] == str(tmp_path)
        assert "issues_count" in result
        assert "errors" in result
        assert "warnings" in result

    def test_analyze_code_quality_nonexistent_path(self):
        """analyze_code_quality on a bad path returns success=False or handles gracefully."""
        result = analyze_code_quality(path="/nonexistent/path/zzz")
        assert isinstance(result, dict)
        # Either success with 0 issues or failure -- both are valid
        assert "success" in result

    def test_cli_commands_returns_dict_with_callables(self):
        """cli_commands returns a dict whose values are callable."""
        cmds = cli_commands()
        assert isinstance(cmds, dict)
        assert "analyze" in cmds
        assert "tools" in cmds
        assert callable(cmds["analyze"])
        assert callable(cmds["tools"])

    def test_get_available_tools_returns_dict(self):
        """get_available_tools returns a dict mapping tool names to availability."""
        tools = get_available_tools()
        assert isinstance(tools, dict)
        for name, available in tools.items():
            assert isinstance(name, str)
            assert isinstance(available, bool)
