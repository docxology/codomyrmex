"""Unit tests for codomyrmex.coding.static_analysis.static_analyzer.

Tests the StaticAnalyzer class and related data structures using real objects,
real temporary files, and real subprocess calls. Zero mocks per project policy.
"""

import csv
import json
import math
import os
import textwrap

import pytest

from codomyrmex.coding.static_analysis.static_analyzer import (
    AnalysisResult,
    AnalysisSummary,
    AnalysisType,
    CodeMetrics,
    Language,
    SeverityLevel,
    StaticAnalyzer,
    analyze_file as module_analyze_file,
    analyze_project as module_analyze_project,
    get_available_tools,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def analyzer(tmp_path):
    """Return a StaticAnalyzer rooted at a temporary directory."""
    return StaticAnalyzer(project_root=str(tmp_path))


@pytest.fixture
def simple_python_file(tmp_path):
    """Create a simple, valid Python file and return its path."""
    p = tmp_path / "simple.py"
    p.write_text(
        textwrap.dedent("""\
        def hello(name):
            return f"Hello, {name}!"

        if __name__ == "__main__":
            print(hello("world"))
        """),
        encoding="utf-8",
    )
    return str(p)


@pytest.fixture
def complex_python_file(tmp_path):
    """Create a Python file with non-trivial complexity."""
    p = tmp_path / "complex.py"
    p.write_text(
        textwrap.dedent("""\
        def complex_func(a, b, c, d):
            if a > 0:
                for i in range(b):
                    if i % 2 == 0:
                        try:
                            with open("f.txt") as fh:
                                pass
                        except IOError:
                            pass
            elif b > 0:
                while c > 0:
                    c -= 1
            if d or (a and b):
                return True
            return False
        """),
        encoding="utf-8",
    )
    return str(p)


@pytest.fixture
def duplicate_lines_file(tmp_path):
    """Create a Python file with duplicated lines."""
    p = tmp_path / "dupes.py"
    lines = ["x = 1\n"] * 10 + ["y = 2\n"] * 5 + ["z = 3\n"]
    p.write_text("".join(lines), encoding="utf-8")
    return str(p)


@pytest.fixture
def empty_python_file(tmp_path):
    """Create an empty Python file."""
    p = tmp_path / "empty.py"
    p.write_text("", encoding="utf-8")
    return str(p)


@pytest.fixture
def comments_only_file(tmp_path):
    """Create a Python file that is only comments and blank lines."""
    p = tmp_path / "comments.py"
    p.write_text(
        textwrap.dedent("""\
        # This is a comment
        # Another comment

        # End
        """),
        encoding="utf-8",
    )
    return str(p)


@pytest.fixture
def syntax_error_file(tmp_path):
    """Create a Python file with a syntax error."""
    p = tmp_path / "broken.py"
    p.write_text("def foo(:\n    pass\n", encoding="utf-8")
    return str(p)


@pytest.fixture
def project_with_files(tmp_path):
    """Create a small project tree with multiple analysable files."""
    (tmp_path / "main.py").write_text("print('hello')\n", encoding="utf-8")
    sub = tmp_path / "pkg"
    sub.mkdir()
    (sub / "__init__.py").write_text("", encoding="utf-8")
    (sub / "util.py").write_text("x = 1\n", encoding="utf-8")
    # A non-analysable file
    (tmp_path / "readme.txt").write_text("Just a readme.\n", encoding="utf-8")
    # An excluded directory
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    (cache / "junk.py").write_text("pass\n", encoding="utf-8")
    return tmp_path


# ===========================================================================
# Enum and dataclass tests
# ===========================================================================


@pytest.mark.unit
class TestEnums:
    """Tests for AnalysisType, SeverityLevel, and Language enums."""

    def test_analysis_type_values(self):
        assert AnalysisType.QUALITY.value == "quality"
        assert AnalysisType.SECURITY.value == "security"
        assert AnalysisType.PERFORMANCE.value == "performance"
        assert AnalysisType.MAINTAINABILITY.value == "maintainability"
        assert AnalysisType.COMPLEXITY.value == "complexity"
        assert AnalysisType.STYLE.value == "style"
        assert AnalysisType.DOCUMENTATION.value == "documentation"
        assert AnalysisType.TESTING.value == "testing"

    def test_analysis_type_count(self):
        assert len(AnalysisType) == 8

    def test_severity_level_values(self):
        assert SeverityLevel.INFO.value == "info"
        assert SeverityLevel.WARNING.value == "warning"
        assert SeverityLevel.ERROR.value == "error"
        assert SeverityLevel.CRITICAL.value == "critical"

    def test_severity_level_count(self):
        assert len(SeverityLevel) == 4

    def test_language_values(self):
        assert Language.PYTHON.value == "python"
        assert Language.JAVASCRIPT.value == "javascript"
        assert Language.TYPESCRIPT.value == "typescript"
        assert Language.JAVA.value == "java"
        assert Language.CPP.value == "cpp"
        assert Language.CSHARP.value == "csharp"
        assert Language.GO.value == "go"
        assert Language.RUST.value == "rust"
        assert Language.PHP.value == "php"
        assert Language.RUBY.value == "ruby"

    def test_language_count(self):
        assert len(Language) == 10


@pytest.mark.unit
class TestAnalysisResult:
    """Tests for the AnalysisResult dataclass."""

    def test_required_fields(self):
        r = AnalysisResult(
            file_path="test.py",
            line_number=10,
            column_number=5,
            severity=SeverityLevel.WARNING,
            message="unused import",
            rule_id="W001",
            category="quality",
        )
        assert r.file_path == "test.py"
        assert r.line_number == 10
        assert r.column_number == 5
        assert r.severity == SeverityLevel.WARNING
        assert r.message == "unused import"
        assert r.rule_id == "W001"
        assert r.category == "quality"

    def test_optional_defaults(self):
        r = AnalysisResult(
            file_path="a.py",
            line_number=1,
            column_number=0,
            severity=SeverityLevel.INFO,
            message="msg",
            rule_id="R001",
            category="cat",
        )
        assert r.suggestion is None
        assert r.context is None
        assert r.fix_available is False
        assert r.confidence == 1.0

    def test_optional_fields_explicit(self):
        r = AnalysisResult(
            file_path="b.py",
            line_number=2,
            column_number=3,
            severity=SeverityLevel.ERROR,
            message="bad",
            rule_id="E001",
            category="security",
            suggestion="fix it",
            context="some context",
            fix_available=True,
            confidence=0.85,
        )
        assert r.suggestion == "fix it"
        assert r.context == "some context"
        assert r.fix_available is True
        assert r.confidence == 0.85


@pytest.mark.unit
class TestAnalysisSummary:
    """Tests for the AnalysisSummary dataclass."""

    def test_defaults(self):
        s = AnalysisSummary(total_issues=0)
        assert s.total_issues == 0
        assert s.by_severity == {}
        assert s.by_category == {}
        assert s.by_rule == {}
        assert s.files_analyzed == 0
        assert s.analysis_time == 0.0
        assert s.language is None

    def test_with_values(self):
        s = AnalysisSummary(
            total_issues=5,
            by_severity={SeverityLevel.ERROR: 3, SeverityLevel.WARNING: 2},
            by_category={"pylint": 5},
            by_rule={"C0114": 5},
            files_analyzed=2,
            analysis_time=1.23,
            language=Language.PYTHON,
        )
        assert s.total_issues == 5
        assert s.by_severity[SeverityLevel.ERROR] == 3
        assert s.files_analyzed == 2
        assert s.language == Language.PYTHON


@pytest.mark.unit
class TestCodeMetrics:
    """Tests for the CodeMetrics dataclass."""

    def test_required_fields(self):
        m = CodeMetrics(
            lines_of_code=100,
            cyclomatic_complexity=5,
            maintainability_index=80.0,
            technical_debt=1.5,
            code_duplication=3.2,
        )
        assert m.lines_of_code == 100
        assert m.cyclomatic_complexity == 5
        assert m.maintainability_index == 80.0
        assert m.technical_debt == 1.5
        assert m.code_duplication == 3.2

    def test_optional_defaults(self):
        m = CodeMetrics(0, 0, 0.0, 0.0, 0.0)
        assert m.test_coverage is None
        assert m.documentation_coverage is None

    def test_optional_explicit(self):
        m = CodeMetrics(10, 2, 90.0, 0.5, 1.0, test_coverage=95.0, documentation_coverage=80.0)
        assert m.test_coverage == 95.0
        assert m.documentation_coverage == 80.0


# ===========================================================================
# StaticAnalyzer constructor and tool discovery tests
# ===========================================================================


@pytest.mark.unit
class TestStaticAnalyzerInit:
    """Tests for StaticAnalyzer constructor and tool availability checking."""

    def test_default_project_root(self):
        a = StaticAnalyzer()
        assert a.project_root == os.getcwd()

    def test_explicit_project_root(self, tmp_path):
        a = StaticAnalyzer(project_root=str(tmp_path))
        assert a.project_root == str(tmp_path)

    def test_results_initially_empty(self, analyzer):
        assert analyzer.results == []

    def test_metrics_initially_empty(self, analyzer):
        assert analyzer.metrics == {}

    def test_tools_available_is_dict(self, analyzer):
        assert isinstance(analyzer.tools_available, dict)

    def test_tools_available_has_expected_keys(self, analyzer):
        expected_keys = {
            "pylint", "flake8", "mypy", "bandit", "black",
            "isort", "pytest", "coverage", "radon", "vulture",
            "safety", "semgrep", "pyrefly",
        }
        assert set(analyzer.tools_available.keys()) == expected_keys

    def test_tools_available_values_are_bool(self, analyzer):
        for tool_name, available in analyzer.tools_available.items():
            assert isinstance(available, bool), f"{tool_name} should be bool"


# ===========================================================================
# Language detection tests
# ===========================================================================


@pytest.mark.unit
class TestDetectLanguage:
    """Tests for _detect_language method."""

    def test_python_extension(self, analyzer):
        assert analyzer._detect_language("foo.py") == Language.PYTHON

    def test_javascript_extension(self, analyzer):
        assert analyzer._detect_language("app.js") == Language.JAVASCRIPT

    def test_jsx_extension(self, analyzer):
        assert analyzer._detect_language("App.jsx") == Language.JAVASCRIPT

    def test_typescript_extension(self, analyzer):
        assert analyzer._detect_language("main.ts") == Language.TYPESCRIPT

    def test_tsx_extension(self, analyzer):
        assert analyzer._detect_language("Component.tsx") == Language.TYPESCRIPT

    def test_java_extension(self, analyzer):
        assert analyzer._detect_language("Main.java") == Language.JAVA

    def test_cpp_extension(self, analyzer):
        assert analyzer._detect_language("lib.cpp") == Language.CPP

    def test_cc_extension(self, analyzer):
        assert analyzer._detect_language("lib.cc") == Language.CPP

    def test_cxx_extension(self, analyzer):
        assert analyzer._detect_language("lib.cxx") == Language.CPP

    def test_csharp_extension(self, analyzer):
        assert analyzer._detect_language("Program.cs") == Language.CSHARP

    def test_go_extension(self, analyzer):
        assert analyzer._detect_language("main.go") == Language.GO

    def test_rust_extension(self, analyzer):
        assert analyzer._detect_language("lib.rs") == Language.RUST

    def test_php_extension(self, analyzer):
        assert analyzer._detect_language("index.php") == Language.PHP

    def test_ruby_extension(self, analyzer):
        assert analyzer._detect_language("app.rb") == Language.RUBY

    def test_unknown_extension_defaults_to_python(self, analyzer):
        assert analyzer._detect_language("readme.txt") == Language.PYTHON

    def test_no_extension_defaults_to_python(self, analyzer):
        assert analyzer._detect_language("Makefile") == Language.PYTHON

    def test_case_insensitive(self, analyzer):
        assert analyzer._detect_language("script.PY") == Language.PYTHON
        assert analyzer._detect_language("app.JS") == Language.JAVASCRIPT


# ===========================================================================
# _should_analyze_file tests
# ===========================================================================


@pytest.mark.unit
class TestShouldAnalyzeFile:
    """Tests for _should_analyze_file method."""

    def test_python_files_accepted(self, analyzer):
        assert analyzer._should_analyze_file("test.py") is True

    def test_js_files_accepted(self, analyzer):
        assert analyzer._should_analyze_file("app.js") is True

    def test_ts_files_accepted(self, analyzer):
        assert analyzer._should_analyze_file("main.ts") is True

    def test_tsx_files_accepted(self, analyzer):
        assert analyzer._should_analyze_file("Component.tsx") is True

    def test_jsx_files_accepted(self, analyzer):
        assert analyzer._should_analyze_file("App.jsx") is True

    def test_java_files_accepted(self, analyzer):
        assert analyzer._should_analyze_file("Main.java") is True

    def test_cpp_files_accepted(self, analyzer):
        assert analyzer._should_analyze_file("lib.cpp") is True

    def test_cc_files_accepted(self, analyzer):
        assert analyzer._should_analyze_file("lib.cc") is True

    def test_csharp_files_accepted(self, analyzer):
        assert analyzer._should_analyze_file("Program.cs") is True

    def test_go_files_accepted(self, analyzer):
        assert analyzer._should_analyze_file("main.go") is True

    def test_rust_files_accepted(self, analyzer):
        assert analyzer._should_analyze_file("lib.rs") is True

    def test_php_files_accepted(self, analyzer):
        assert analyzer._should_analyze_file("index.php") is True

    def test_ruby_files_accepted(self, analyzer):
        assert analyzer._should_analyze_file("app.rb") is True

    def test_text_file_rejected(self, analyzer):
        assert analyzer._should_analyze_file("readme.txt") is False

    def test_markdown_rejected(self, analyzer):
        assert analyzer._should_analyze_file("README.md") is False

    def test_yaml_rejected(self, analyzer):
        assert analyzer._should_analyze_file("config.yaml") is False

    def test_no_extension_rejected(self, analyzer):
        assert analyzer._should_analyze_file("Makefile") is False


# ===========================================================================
# Cyclomatic complexity calculation tests
# ===========================================================================


@pytest.mark.unit
class TestCyclomaticComplexity:
    """Tests for _calculate_cyclomatic_complexity."""

    def test_empty_content(self, analyzer):
        # Empty string parses to empty module; base complexity = 1
        assert analyzer._calculate_cyclomatic_complexity("") == 1

    def test_simple_function(self, analyzer):
        code = "def foo():\n    return 1\n"
        assert analyzer._calculate_cyclomatic_complexity(code) == 1

    def test_single_if(self, analyzer):
        code = "if x:\n    pass\n"
        assert analyzer._calculate_cyclomatic_complexity(code) == 2

    def test_if_elif_else(self, analyzer):
        code = "if x:\n    pass\nelif y:\n    pass\nelse:\n    pass\n"
        # 1 base + 1 (if) + 1 (elif is another If node) = 3
        assert analyzer._calculate_cyclomatic_complexity(code) == 3

    def test_for_loop(self, analyzer):
        code = "for i in range(10):\n    pass\n"
        assert analyzer._calculate_cyclomatic_complexity(code) == 2

    def test_while_loop(self, analyzer):
        code = "while True:\n    break\n"
        assert analyzer._calculate_cyclomatic_complexity(code) == 2

    def test_try_except(self, analyzer):
        code = "try:\n    pass\nexcept:\n    pass\n"
        assert analyzer._calculate_cyclomatic_complexity(code) == 2

    def test_with_statement(self, analyzer):
        code = "with open('f') as fh:\n    pass\n"
        assert analyzer._calculate_cyclomatic_complexity(code) == 2

    def test_bool_op_and(self, analyzer):
        code = "x = a and b\n"
        assert analyzer._calculate_cyclomatic_complexity(code) == 2

    def test_bool_op_or(self, analyzer):
        code = "x = a or b\n"
        assert analyzer._calculate_cyclomatic_complexity(code) == 2

    def test_bool_op_multiple(self, analyzer):
        # "a and b and c" is a single BoolOp with 3 values -> +2
        code = "x = a and b and c\n"
        assert analyzer._calculate_cyclomatic_complexity(code) == 3

    def test_nested_structures(self, analyzer):
        code = textwrap.dedent("""\
        if a:
            for i in range(10):
                while True:
                    break
        """)
        # 1 base + 1 (if) + 1 (for) + 1 (while) = 4
        assert analyzer._calculate_cyclomatic_complexity(code) == 4

    def test_syntax_error_returns_1(self, analyzer):
        code = "def foo(:\n    pass\n"
        assert analyzer._calculate_cyclomatic_complexity(code) == 1


# ===========================================================================
# Code duplication calculation tests
# ===========================================================================


@pytest.mark.unit
class TestCodeDuplication:
    """Tests for _calculate_code_duplication."""

    def test_no_duplication(self, analyzer):
        code = "a = 1\nb = 2\nc = 3\n"
        result = analyzer._calculate_code_duplication(code)
        assert result == 0.0

    def test_all_duplicate(self, analyzer):
        code = "x = 1\n" * 5
        # 5 lines, all the same. 4 duplicated. 4/5 * 100 = 80.0
        result = analyzer._calculate_code_duplication(code)
        assert result == pytest.approx(80.0)

    def test_empty_content(self, analyzer):
        result = analyzer._calculate_code_duplication("")
        assert result == 0.0

    def test_comments_excluded(self, analyzer):
        code = "# comment\n# comment\na = 1\n"
        # Comments are stripped out. Only "a = 1" remains. No duplication.
        result = analyzer._calculate_code_duplication(code)
        assert result == 0.0

    def test_blank_lines_excluded(self, analyzer):
        code = "\n\n\na = 1\n\n"
        result = analyzer._calculate_code_duplication(code)
        assert result == 0.0

    def test_partial_duplication(self, analyzer):
        code = "a = 1\na = 1\nb = 2\nc = 3\n"
        # 4 non-blank/non-comment lines. "a = 1" appears twice -> 1 duplicate.
        # 1/4 * 100 = 25.0
        result = analyzer._calculate_code_duplication(code)
        assert result == pytest.approx(25.0)


# ===========================================================================
# calculate_metrics tests
# ===========================================================================


@pytest.mark.unit
class TestCalculateMetrics:
    """Tests for calculate_metrics method."""

    def test_simple_file_metrics(self, analyzer, simple_python_file):
        metrics = analyzer.calculate_metrics(simple_python_file)
        assert isinstance(metrics, CodeMetrics)
        assert metrics.lines_of_code > 0
        assert metrics.cyclomatic_complexity >= 1
        assert metrics.maintainability_index >= 0

    def test_metrics_stored_in_dict(self, analyzer, simple_python_file):
        analyzer.calculate_metrics(simple_python_file)
        assert simple_python_file in analyzer.metrics

    def test_complex_file_higher_complexity(self, analyzer, simple_python_file, complex_python_file):
        simple_metrics = analyzer.calculate_metrics(simple_python_file)
        # Reset to avoid cross-contamination from results
        analyzer.results.clear()
        complex_metrics = analyzer.calculate_metrics(complex_python_file)
        assert complex_metrics.cyclomatic_complexity > simple_metrics.cyclomatic_complexity

    def test_duplicate_file_has_duplication(self, analyzer, duplicate_lines_file):
        metrics = analyzer.calculate_metrics(duplicate_lines_file)
        assert metrics.code_duplication > 0.0

    def test_empty_file_metrics(self, analyzer, empty_python_file):
        metrics = analyzer.calculate_metrics(empty_python_file)
        assert metrics.lines_of_code == 0

    def test_comments_only_file(self, analyzer, comments_only_file):
        metrics = analyzer.calculate_metrics(comments_only_file)
        assert metrics.lines_of_code == 0

    def test_nonexistent_file_returns_zero_metrics(self, analyzer):
        metrics = analyzer.calculate_metrics("/nonexistent/path/file.py")
        assert metrics.lines_of_code == 0
        assert metrics.cyclomatic_complexity == 0
        assert metrics.maintainability_index == 0.0

    def test_technical_debt_depends_on_results(self, analyzer, simple_python_file):
        # With no prior results, debt should be 0
        metrics = analyzer.calculate_metrics(simple_python_file)
        assert metrics.technical_debt == 0.0

    def test_technical_debt_with_results(self, analyzer, simple_python_file):
        # Manually add some results to check debt calculation
        for i in range(10):
            analyzer.results.append(
                AnalysisResult(
                    file_path=simple_python_file,
                    line_number=i,
                    column_number=0,
                    severity=SeverityLevel.WARNING,
                    message=f"issue {i}",
                    rule_id="TEST",
                    category="test",
                )
            )
        metrics = analyzer.calculate_metrics(simple_python_file)
        # 10 issues * 0.1 = 1.0
        assert metrics.technical_debt == pytest.approx(1.0)

    def test_syntax_error_file_metrics(self, analyzer, syntax_error_file):
        """Syntax errors should not crash metrics; complexity falls back to 1."""
        metrics = analyzer.calculate_metrics(syntax_error_file)
        assert isinstance(metrics, CodeMetrics)
        assert metrics.cyclomatic_complexity == 1


# ===========================================================================
# analyze_file tests (core dispatch)
# ===========================================================================


@pytest.mark.unit
class TestAnalyzeFile:
    """Tests for analyze_file method (dispatch and result accumulation)."""

    def test_returns_list(self, analyzer, simple_python_file):
        results = analyzer.analyze_file(simple_python_file)
        assert isinstance(results, list)

    def test_results_accumulated(self, analyzer, simple_python_file):
        analyzer.analyze_file(simple_python_file)
        # Results should be appended to self.results
        # (may be empty if no tools are available, but the list should exist)
        assert isinstance(analyzer.results, list)

    def test_default_analysis_types(self, analyzer, simple_python_file):
        """When no analysis_types given, defaults to QUALITY, SECURITY, STYLE."""
        # We just confirm no error is raised with default types
        results = analyzer.analyze_file(simple_python_file)
        assert isinstance(results, list)

    def test_explicit_analysis_types(self, analyzer, simple_python_file):
        results = analyzer.analyze_file(
            simple_python_file,
            analysis_types=[AnalysisType.COMPLEXITY],
        )
        assert isinstance(results, list)

    def test_unsupported_language_file(self, analyzer, tmp_path):
        """A Go file should be logged as unsupported (no Go analyzers configured)."""
        go_file = tmp_path / "main.go"
        go_file.write_text("package main\n", encoding="utf-8")
        results = analyzer.analyze_file(str(go_file))
        # No analyzers for Go, so results should be empty
        assert results == []

    def test_javascript_file_dispatch(self, analyzer, tmp_path):
        js_file = tmp_path / "app.js"
        js_file.write_text("console.log('hi');\n", encoding="utf-8")
        results = analyzer.analyze_file(str(js_file))
        assert isinstance(results, list)

    def test_typescript_file_dispatch(self, analyzer, tmp_path):
        ts_file = tmp_path / "main.ts"
        ts_file.write_text("const x: number = 1;\n", encoding="utf-8")
        results = analyzer.analyze_file(str(ts_file))
        assert isinstance(results, list)

    def test_java_file_dispatch(self, analyzer, tmp_path):
        java_file = tmp_path / "Main.java"
        java_file.write_text("public class Main {}\n", encoding="utf-8")
        results = analyzer.analyze_file(str(java_file))
        assert isinstance(results, list)

    def test_multiple_calls_accumulate(self, analyzer, tmp_path):
        f1 = tmp_path / "a.py"
        f1.write_text("x = 1\n", encoding="utf-8")
        f2 = tmp_path / "b.py"
        f2.write_text("y = 2\n", encoding="utf-8")
        analyzer.analyze_file(str(f1))
        before = len(analyzer.results)
        analyzer.analyze_file(str(f2))
        # results should be >= before (could be equal if no tools found issues)
        assert len(analyzer.results) >= before


# ===========================================================================
# analyze_project tests
# ===========================================================================


@pytest.mark.unit
class TestAnalyzeProject:
    """Tests for analyze_project method."""

    def test_returns_summary(self, project_with_files):
        analyzer = StaticAnalyzer(project_root=str(project_with_files))
        summary = analyzer.analyze_project()
        assert isinstance(summary, AnalysisSummary)

    def test_files_analyzed_count(self, project_with_files):
        analyzer = StaticAnalyzer(project_root=str(project_with_files))
        summary = analyzer.analyze_project()
        # main.py, pkg/__init__.py, pkg/util.py = 3 (cache excluded)
        assert summary.files_analyzed == 3

    def test_excludes_pycache(self, project_with_files):
        analyzer = StaticAnalyzer(project_root=str(project_with_files))
        summary = analyzer.analyze_project()
        # __pycache__/junk.py should be excluded
        analyzed_paths = [r.file_path for r in analyzer.results]
        for p in analyzed_paths:
            assert "__pycache__" not in p

    def test_custom_exclude_patterns(self, project_with_files):
        analyzer = StaticAnalyzer(project_root=str(project_with_files))
        # Exclude "pkg" but keep "__pycache__" excluded too
        summary = analyzer.analyze_project(exclude_patterns=["pkg", "__pycache__"])
        # Only main.py should be analyzed (pkg and __pycache__ excluded)
        assert summary.files_analyzed == 1

    def test_target_paths_single_file(self, project_with_files):
        analyzer = StaticAnalyzer(project_root=str(project_with_files))
        target = str(project_with_files / "main.py")
        summary = analyzer.analyze_project(target_paths=[target])
        assert summary.files_analyzed == 1

    def test_analysis_time_positive(self, project_with_files):
        analyzer = StaticAnalyzer(project_root=str(project_with_files))
        summary = analyzer.analyze_project()
        assert summary.analysis_time >= 0.0

    def test_custom_analysis_types(self, project_with_files):
        analyzer = StaticAnalyzer(project_root=str(project_with_files))
        summary = analyzer.analyze_project(
            analysis_types=[AnalysisType.COMPLEXITY]
        )
        assert isinstance(summary, AnalysisSummary)

    def test_empty_directory(self, tmp_path):
        analyzer = StaticAnalyzer(project_root=str(tmp_path))
        summary = analyzer.analyze_project()
        assert summary.files_analyzed == 0
        assert summary.total_issues == 0


# ===========================================================================
# _generate_summary tests
# ===========================================================================


@pytest.mark.unit
class TestGenerateSummary:
    """Tests for _generate_summary method."""

    def test_empty_results(self, analyzer):
        summary = analyzer._generate_summary(files_analyzed=0, analysis_time=0.5)
        assert summary.total_issues == 0
        assert summary.files_analyzed == 0
        assert summary.analysis_time == 0.5

    def test_with_results(self, analyzer):
        analyzer.results = [
            AnalysisResult("a.py", 1, 0, SeverityLevel.ERROR, "msg1", "R1", "cat1"),
            AnalysisResult("a.py", 2, 0, SeverityLevel.WARNING, "msg2", "R1", "cat1"),
            AnalysisResult("b.py", 1, 0, SeverityLevel.ERROR, "msg3", "R2", "cat2"),
        ]
        summary = analyzer._generate_summary(files_analyzed=2, analysis_time=1.0)
        assert summary.total_issues == 3
        assert summary.by_severity[SeverityLevel.ERROR] == 2
        assert summary.by_severity[SeverityLevel.WARNING] == 1
        assert summary.by_category["cat1"] == 2
        assert summary.by_category["cat2"] == 1
        assert summary.by_rule["R1"] == 2
        assert summary.by_rule["R2"] == 1


# ===========================================================================
# Result filtering tests
# ===========================================================================


@pytest.mark.unit
class TestResultFiltering:
    """Tests for get_results_by_severity, get_results_by_category, get_results_by_file."""

    @pytest.fixture(autouse=True)
    def _populate_results(self, analyzer):
        analyzer.results = [
            AnalysisResult("a.py", 1, 0, SeverityLevel.ERROR, "m1", "R1", "pylint"),
            AnalysisResult("a.py", 2, 0, SeverityLevel.WARNING, "m2", "R2", "flake8"),
            AnalysisResult("b.py", 1, 0, SeverityLevel.ERROR, "m3", "R3", "pylint"),
            AnalysisResult("b.py", 5, 0, SeverityLevel.INFO, "m4", "R4", "security"),
        ]

    def test_by_severity_error(self, analyzer):
        errors = analyzer.get_results_by_severity(SeverityLevel.ERROR)
        assert len(errors) == 2
        assert all(r.severity == SeverityLevel.ERROR for r in errors)

    def test_by_severity_warning(self, analyzer):
        warnings = analyzer.get_results_by_severity(SeverityLevel.WARNING)
        assert len(warnings) == 1

    def test_by_severity_critical_empty(self, analyzer):
        critical = analyzer.get_results_by_severity(SeverityLevel.CRITICAL)
        assert critical == []

    def test_by_category_pylint(self, analyzer):
        pylint_results = analyzer.get_results_by_category("pylint")
        assert len(pylint_results) == 2

    def test_by_category_nonexistent(self, analyzer):
        results = analyzer.get_results_by_category("nonexistent")
        assert results == []

    def test_by_file_a(self, analyzer):
        results = analyzer.get_results_by_file("a.py")
        assert len(results) == 2

    def test_by_file_b(self, analyzer):
        results = analyzer.get_results_by_file("b.py")
        assert len(results) == 2

    def test_by_file_nonexistent(self, analyzer):
        results = analyzer.get_results_by_file("nonexistent.py")
        assert results == []


# ===========================================================================
# export_results tests
# ===========================================================================


@pytest.mark.unit
class TestExportResults:
    """Tests for export_results method."""

    @pytest.fixture(autouse=True)
    def _populate_results(self, analyzer):
        analyzer.results = [
            AnalysisResult("a.py", 1, 0, SeverityLevel.ERROR, "err msg", "E001", "quality", suggestion="fix it"),
            AnalysisResult("b.py", 10, 5, SeverityLevel.WARNING, "warn msg", "W002", "style"),
        ]

    def test_export_json(self, analyzer, tmp_path):
        out = str(tmp_path / "results.json")
        success = analyzer.export_results(out, format="json")
        assert success is True
        with open(out, encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 2
        assert data[0]["file_path"] == "a.py"
        assert data[0]["severity"] == "error"
        assert data[0]["suggestion"] == "fix it"
        assert data[1]["severity"] == "warning"

    def test_export_csv(self, analyzer, tmp_path):
        out = str(tmp_path / "results.csv")
        success = analyzer.export_results(out, format="csv")
        assert success is True
        with open(out, encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
        # Header + 2 data rows
        assert len(rows) == 3
        assert rows[0][0] == "File"
        assert rows[1][0] == "a.py"
        assert rows[2][0] == "b.py"

    def test_export_unsupported_format(self, analyzer, tmp_path):
        out = str(tmp_path / "results.xml")
        success = analyzer.export_results(out, format="xml")
        assert success is False

    def test_export_json_empty_results(self, analyzer, tmp_path):
        analyzer.results = []
        out = str(tmp_path / "empty.json")
        success = analyzer.export_results(out, format="json")
        assert success is True
        with open(out, encoding="utf-8") as f:
            data = json.load(f)
        assert data == []

    def test_export_csv_empty_results(self, analyzer, tmp_path):
        analyzer.results = []
        out = str(tmp_path / "empty.csv")
        success = analyzer.export_results(out, format="csv")
        assert success is True
        with open(out, encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
        # Only header row
        assert len(rows) == 1

    def test_export_invalid_path(self, analyzer):
        success = analyzer.export_results("/nonexistent/dir/results.json", format="json")
        assert success is False

    def test_export_json_field_completeness(self, analyzer, tmp_path):
        """Verify all expected fields are present in JSON export."""
        out = str(tmp_path / "full.json")
        analyzer.export_results(out, format="json")
        with open(out, encoding="utf-8") as f:
            data = json.load(f)
        expected_keys = {
            "file_path", "line_number", "column_number", "severity",
            "message", "rule_id", "category", "suggestion", "context",
            "fix_available", "confidence",
        }
        assert set(data[0].keys()) == expected_keys


# ===========================================================================
# clear_results tests
# ===========================================================================


@pytest.mark.unit
class TestClearResults:
    """Tests for clear_results method."""

    def test_clear_empties_results(self, analyzer, simple_python_file):
        analyzer.results.append(
            AnalysisResult("x.py", 1, 0, SeverityLevel.INFO, "m", "R", "c")
        )
        analyzer.metrics["x.py"] = CodeMetrics(10, 1, 100.0, 0.0, 0.0)
        analyzer.clear_results()
        assert analyzer.results == []
        assert analyzer.metrics == {}

    def test_clear_on_empty(self, analyzer):
        analyzer.clear_results()
        assert analyzer.results == []
        assert analyzer.metrics == {}


# ===========================================================================
# _find_requirements_files tests
# ===========================================================================


@pytest.mark.unit
class TestFindRequirementsFiles:
    """Tests for _find_requirements_files method."""

    def test_finds_requirements_txt(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("flask\n", encoding="utf-8")
        analyzer = StaticAnalyzer(project_root=str(tmp_path))
        found = analyzer._find_requirements_files()
        assert any("requirements.txt" in f for f in found)

    def test_finds_requirements_dev(self, tmp_path):
        (tmp_path / "requirements-dev.txt").write_text("pytest\n", encoding="utf-8")
        analyzer = StaticAnalyzer(project_root=str(tmp_path))
        found = analyzer._find_requirements_files()
        assert any("requirements-dev.txt" in f for f in found)

    def test_finds_pyproject_toml(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
        analyzer = StaticAnalyzer(project_root=str(tmp_path))
        found = analyzer._find_requirements_files()
        assert any("pyproject.toml" in f for f in found)

    def test_empty_directory(self, tmp_path):
        analyzer = StaticAnalyzer(project_root=str(tmp_path))
        found = analyzer._find_requirements_files()
        assert found == []


# ===========================================================================
# Module-level convenience function tests
# ===========================================================================


@pytest.mark.unit
class TestConvenienceFunctions:
    """Tests for module-level analyze_file, analyze_project, get_available_tools."""

    def test_module_analyze_file(self, simple_python_file):
        results = module_analyze_file(simple_python_file)
        assert isinstance(results, list)

    def test_module_analyze_project(self, project_with_files):
        summary = module_analyze_project(str(project_with_files))
        assert isinstance(summary, AnalysisSummary)

    def test_get_available_tools(self):
        tools = get_available_tools()
        assert isinstance(tools, dict)
        assert "pylint" in tools
        assert "mypy" in tools


# ===========================================================================
# _analyze_python_file conditional dispatch tests
# ===========================================================================


@pytest.mark.unit
class TestAnalyzePythonFileDispatch:
    """Test that _analyze_python_file respects tool availability and analysis types."""

    def test_no_tools_returns_empty(self, analyzer, simple_python_file):
        # Force all tools to be unavailable
        for tool in analyzer.tools_available:
            analyzer.tools_available[tool] = False
        results = analyzer._analyze_python_file(
            simple_python_file,
            [AnalysisType.QUALITY, AnalysisType.SECURITY, AnalysisType.STYLE,
             AnalysisType.COMPLEXITY],
        )
        assert results == []

    def test_only_complexity_type(self, analyzer, simple_python_file):
        # Only COMPLEXITY type should only trigger radon
        for tool in analyzer.tools_available:
            analyzer.tools_available[tool] = False
        results = analyzer._analyze_python_file(
            simple_python_file,
            [AnalysisType.COMPLEXITY],
        )
        assert results == []

    def test_style_without_flake8(self, analyzer, simple_python_file):
        for tool in analyzer.tools_available:
            analyzer.tools_available[tool] = False
        results = analyzer._analyze_python_file(
            simple_python_file,
            [AnalysisType.STYLE],
        )
        assert results == []


# ===========================================================================
# _analyze_javascript_file tests
# ===========================================================================


@pytest.mark.unit
class TestAnalyzeJavaScriptFile:
    """Tests for _analyze_javascript_file dispatch."""

    def test_no_eslint_returns_empty(self, analyzer, tmp_path):
        js_file = tmp_path / "app.js"
        js_file.write_text("var x = 1;\n", encoding="utf-8")
        # ESLint is not in the default tools list; ensure it's False
        analyzer.tools_available["eslint"] = False
        results = analyzer._analyze_javascript_file(
            str(js_file), [AnalysisType.QUALITY]
        )
        assert results == []

    def test_typescript_without_tsc(self, analyzer, tmp_path):
        ts_file = tmp_path / "main.ts"
        ts_file.write_text("const x: number = 1;\n", encoding="utf-8")
        # Even without tsc available, the method should return an empty list
        results = analyzer._analyze_javascript_file(
            str(ts_file), [AnalysisType.QUALITY]
        )
        assert isinstance(results, list)


# ===========================================================================
# _analyze_java_file tests
# ===========================================================================


@pytest.mark.unit
class TestAnalyzeJavaFile:
    """Tests for _analyze_java_file dispatch."""

    def test_no_spotbugs_returns_empty(self, analyzer, tmp_path):
        java_file = tmp_path / "Main.java"
        java_file.write_text("public class Main {}\n", encoding="utf-8")
        analyzer.tools_available["spotbugs"] = False
        results = analyzer._analyze_java_file(
            str(java_file), [AnalysisType.QUALITY]
        )
        assert results == []


# ===========================================================================
# Maintainability index formula test
# ===========================================================================


@pytest.mark.unit
class TestMaintainabilityIndex:
    """Verify the maintainability index formula."""

    def test_formula_matches(self, analyzer, tmp_path):
        """Check that the computed maintainability index follows the formula."""
        p = tmp_path / "mi.py"
        # Write code with known structure
        code = textwrap.dedent("""\
        def alpha():
            if True:
                pass

        def beta():
            for i in range(5):
                pass
        """)
        p.write_text(code, encoding="utf-8")
        metrics = analyzer.calculate_metrics(str(p))

        # Recompute expected
        loc = metrics.lines_of_code
        cc = metrics.cyclomatic_complexity
        expected_mi = max(0, 171 - 5.2 * math.log(cc) - 0.23 * loc)
        assert metrics.maintainability_index == pytest.approx(expected_mi, rel=1e-6)
