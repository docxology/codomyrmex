"""
Comprehensive tests for static analysis functionality.

This module tests all static analysis functions including file analysis,
project analysis, metrics calculation, and result processing.
"""

import pytest
import os
import sys
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

# Add project root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from static_analysis.static_analyzer import (
    StaticAnalyzer,
    analyze_file,
    analyze_project,
    get_available_tools,
    AnalysisResult,
    AnalysisSummary,
    CodeMetrics,
    AnalysisType,
    SeverityLevel,
    Language,
)


class TestEnums:
    """Test enum classes."""

    def test_analysis_type_enum(self):
        """Test AnalysisType enum values."""
        assert AnalysisType.QUALITY.value == "quality"
        assert AnalysisType.SECURITY.value == "security"
        assert AnalysisType.PERFORMANCE.value == "performance"
        assert AnalysisType.MAINTAINABILITY.value == "maintainability"
        assert AnalysisType.COMPLEXITY.value == "complexity"
        assert AnalysisType.STYLE.value == "style"
        assert AnalysisType.DOCUMENTATION.value == "documentation"
        assert AnalysisType.TESTING.value == "testing"

    def test_severity_level_enum(self):
        """Test SeverityLevel enum values."""
        assert SeverityLevel.INFO.value == "info"
        assert SeverityLevel.WARNING.value == "warning"
        assert SeverityLevel.ERROR.value == "error"
        assert SeverityLevel.CRITICAL.value == "critical"

    def test_language_enum(self):
        """Test Language enum values."""
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


class TestDataStructures:
    """Test data structure classes."""

    def test_analysis_result(self):
        """Test AnalysisResult creation."""
        result = AnalysisResult(
            file_path="test.py",
            line_number=10,
            column_number=5,
            severity=SeverityLevel.WARNING,
            message="Test warning",
            rule_id="E001",
            category="pylint",
        )

        assert result.file_path == "test.py"
        assert result.line_number == 10
        assert result.column_number == 5
        assert result.severity == SeverityLevel.WARNING
        assert result.message == "Test warning"
        assert result.rule_id == "E001"
        assert result.category == "pylint"
        assert result.suggestion is None
        assert result.context is None
        assert result.fix_available is False
        assert result.confidence == 1.0

    def test_analysis_summary(self):
        """Test AnalysisSummary creation."""
        summary = AnalysisSummary(total_issues=5, files_analyzed=2, analysis_time=1.5)

        assert summary.total_issues == 5
        assert summary.files_analyzed == 2
        assert summary.analysis_time == 1.5
        assert summary.by_severity == {}
        assert summary.by_category == {}
        assert summary.by_rule == {}
        assert summary.language is None

    def test_code_metrics(self):
        """Test CodeMetrics creation."""
        metrics = CodeMetrics(
            lines_of_code=100,
            cyclomatic_complexity=5,
            maintainability_index=80.0,
            technical_debt=2.5,
            code_duplication=10.0,
        )

        assert metrics.lines_of_code == 100
        assert metrics.cyclomatic_complexity == 5
        assert metrics.maintainability_index == 80.0
        assert metrics.technical_debt == 2.5
        assert metrics.code_duplication == 10.0
        assert metrics.test_coverage is None
        assert metrics.documentation_coverage is None


class TestStaticAnalyzer:
    """Test StaticAnalyzer class."""

    def test_initialization(self):
        """Test StaticAnalyzer initialization."""
        analyzer = StaticAnalyzer("/test/project")

        assert analyzer.project_root == "/test/project"
        assert analyzer.results == []
        assert analyzer.metrics == {}
        assert isinstance(analyzer.tools_available, dict)

    def test_initialization_default_project_root(self):
        """Test StaticAnalyzer initialization with default project root."""
        analyzer = StaticAnalyzer()

        assert analyzer.project_root == os.getcwd()
        assert analyzer.results == []
        assert analyzer.metrics == {}

    def test_detect_language(self):
        """Test language detection."""
        analyzer = StaticAnalyzer()

        assert analyzer._detect_language("test.py") == Language.PYTHON
        assert analyzer._detect_language("test.js") == Language.JAVASCRIPT
        assert analyzer._detect_language("test.ts") == Language.TYPESCRIPT
        assert analyzer._detect_language("test.java") == Language.JAVA
        assert analyzer._detect_language("test.cpp") == Language.CPP
        assert analyzer._detect_language("test.cs") == Language.CSHARP
        assert analyzer._detect_language("test.go") == Language.GO
        assert analyzer._detect_language("test.rs") == Language.RUST
        assert analyzer._detect_language("test.php") == Language.PHP
        assert analyzer._detect_language("test.rb") == Language.RUBY
        assert analyzer._detect_language("test.unknown") == Language.PYTHON  # Default

    def test_should_analyze_file(self):
        """Test file analysis eligibility."""
        analyzer = StaticAnalyzer()

        assert analyzer._should_analyze_file("test.py") is True
        assert analyzer._should_analyze_file("test.js") is True
        assert analyzer._should_analyze_file("test.ts") is True
        assert analyzer._should_analyze_file("test.java") is True
        assert analyzer._should_analyze_file("test.cpp") is True
        assert analyzer._should_analyze_file("test.txt") is False
        assert analyzer._should_analyze_file("test.md") is False
        assert analyzer._should_analyze_file("test.log") is False

    def test_find_requirements_files(self):
        """Test finding requirements files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = StaticAnalyzer(temp_dir)

            # Create test requirements files
            os.makedirs(os.path.join(temp_dir, "subdir"))

            with open(os.path.join(temp_dir, "requirements.txt"), "w") as f:
                f.write("pytest==6.0.0")

            with open(os.path.join(temp_dir, "requirements-dev.txt"), "w") as f:
                f.write("black==21.0.0")

            with open(os.path.join(temp_dir, "subdir", "requirements.txt"), "w") as f:
                f.write("requests==2.25.0")

            req_files = analyzer._find_requirements_files()

            assert len(req_files) >= 2
            assert any("requirements.txt" in f for f in req_files)
            assert any("requirements-dev.txt" in f for f in req_files)

    def test_calculate_cyclomatic_complexity(self):
        """Test cyclomatic complexity calculation."""
        analyzer = StaticAnalyzer()

        # Simple function
        simple_code = "def func(): return 1"
        assert analyzer._calculate_cyclomatic_complexity(simple_code) == 1

        # Function with if statement
        if_code = "def func(x):\n    if x > 0:\n        return 1\n    return 0"
        assert analyzer._calculate_cyclomatic_complexity(if_code) == 2

        # Function with loop
        loop_code = "def func(items):\n    for item in items:\n        if item > 0:\n            print(item)"
        assert analyzer._calculate_cyclomatic_complexity(loop_code) == 3

        # Invalid syntax
        invalid_code = "def func(:\n    return 1"
        assert analyzer._calculate_cyclomatic_complexity(invalid_code) == 1

    def test_calculate_code_duplication(self):
        """Test code duplication calculation."""
        analyzer = StaticAnalyzer()

        # No duplication
        no_dup_code = "def func1():\n    return 1\n\ndef func2():\n    return 2"
        assert analyzer._calculate_code_duplication(no_dup_code) == 0.0

        # Some duplication
        dup_code = "def func1():\n    return 1\n\ndef func2():\n    return 1"
        assert analyzer._calculate_code_duplication(dup_code) > 0.0

        # Empty code
        empty_code = ""
        assert analyzer._calculate_code_duplication(empty_code) == 0.0

        # Only comments
        comment_code = "# This is a comment\n# Another comment"
        assert analyzer._calculate_code_duplication(comment_code) == 0.0


class TestFileAnalysis:
    """Test file analysis functionality."""

    def test_analyze_file_python(self):
        """Test Python file analysis."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def test_func():\n    print('hello')\n    return 1")
            temp_file = f.name

        try:
            analyzer = StaticAnalyzer()

            with patch.object(analyzer, "_analyze_python_file") as mock_analyze:
                mock_results = [
                    AnalysisResult(
                        file_path=temp_file,
                        line_number=1,
                        column_number=0,
                        severity=SeverityLevel.INFO,
                        message="Test message",
                        rule_id="E001",
                        category="pylint",
                    )
                ]
                mock_analyze.return_value = mock_results

                results = analyzer.analyze_file(temp_file)

                assert len(results) == 1
                assert results[0].file_path == temp_file
                mock_analyze.assert_called_once()

        finally:
            os.unlink(temp_file)

    def test_analyze_file_javascript(self):
        """Test JavaScript file analysis."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write("function test() {\n    console.log('hello');\n}")
            temp_file = f.name

        try:
            analyzer = StaticAnalyzer()

            with patch.object(analyzer, "_analyze_javascript_file") as mock_analyze:
                mock_results = [
                    AnalysisResult(
                        file_path=temp_file,
                        line_number=1,
                        column_number=0,
                        severity=SeverityLevel.WARNING,
                        message="Test warning",
                        rule_id="ESLINT001",
                        category="eslint",
                    )
                ]
                mock_analyze.return_value = mock_results

                results = analyzer.analyze_file(temp_file)

                assert len(results) == 1
                assert results[0].file_path == temp_file
                mock_analyze.assert_called_once()

        finally:
            os.unlink(temp_file)

    def test_analyze_file_unsupported_language(self):
        """Test analysis of unsupported language file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".unknown", delete=False
        ) as f:
            f.write("some content")
            temp_file = f.name

        try:
            analyzer = StaticAnalyzer()
            results = analyzer.analyze_file(temp_file)

            assert results == []

        finally:
            os.unlink(temp_file)


class TestProjectAnalysis:
    """Test project analysis functionality."""

    def test_analyze_project(self):
        """Test project analysis."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            with open(os.path.join(temp_dir, "test1.py"), "w") as f:
                f.write("def func1():\n    return 1")

            with open(os.path.join(temp_dir, "test2.py"), "w") as f:
                f.write("def func2():\n    return 2")

            with open(os.path.join(temp_dir, "test.txt"), "w") as f:
                f.write("This is not code")

            analyzer = StaticAnalyzer(temp_dir)

            with patch.object(analyzer, "analyze_file") as mock_analyze:
                mock_analyze.return_value = []

                summary = analyzer.analyze_project()

                assert summary.files_analyzed == 2  # Only .py files
                assert summary.total_issues == 0
                assert summary.analysis_time > 0
                assert mock_analyze.call_count == 2

    def test_analyze_project_with_exclude_patterns(self):
        """Test project analysis with exclude patterns."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            with open(os.path.join(temp_dir, "test.py"), "w") as f:
                f.write("def func():\n    return 1")

            # Create excluded directory
            os.makedirs(os.path.join(temp_dir, "__pycache__"))
            with open(os.path.join(temp_dir, "__pycache__", "test.pyc"), "w") as f:
                f.write("compiled code")

            analyzer = StaticAnalyzer(temp_dir)

            with patch.object(analyzer, "analyze_file") as mock_analyze:
                mock_analyze.return_value = []

                summary = analyzer.analyze_project(exclude_patterns=["__pycache__"])

                assert summary.files_analyzed == 1  # Only the .py file, not .pyc
                assert mock_analyze.call_count == 1

    def test_analyze_project_specific_paths(self):
        """Test project analysis with specific target paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            with open(os.path.join(temp_dir, "test1.py"), "w") as f:
                f.write("def func1():\n    return 1")

            with open(os.path.join(temp_dir, "test2.py"), "w") as f:
                f.write("def func2():\n    return 2")

            analyzer = StaticAnalyzer(temp_dir)

            with patch.object(analyzer, "analyze_file") as mock_analyze:
                mock_analyze.return_value = []

                summary = analyzer.analyze_project(
                    target_paths=[os.path.join(temp_dir, "test1.py")]
                )

                assert summary.files_analyzed == 1
                assert mock_analyze.call_count == 1


class TestToolIntegration:
    """Test integration with analysis tools."""

    def test_run_pylint_success(self):
        """Test successful pylint execution."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def test_func():\n    print('hello')\n    return 1")
            temp_file = f.name

        try:
            analyzer = StaticAnalyzer()

            with patch("subprocess.run") as mock_run:
                mock_result = Mock()
                mock_result.returncode = 1
                mock_result.stdout = json.dumps(
                    [
                        {
                            "path": temp_file,
                            "line": 1,
                            "column": 0,
                            "type": "warning",
                            "message": "Test warning",
                            "message-id": "W0001",
                        }
                    ]
                )
                mock_run.return_value = mock_result

                results = analyzer._run_pylint(temp_file)

                assert len(results) == 1
                assert results[0].message == "Test warning"
                assert results[0].severity == SeverityLevel.WARNING
                assert results[0].rule_id == "W0001"
                assert results[0].category == "pylint"

        finally:
            os.unlink(temp_file)

    def test_run_pylint_timeout(self):
        """Test pylint execution timeout."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def test_func():\n    print('hello')\n    return 1")
            temp_file = f.name

        try:
            analyzer = StaticAnalyzer()

            with patch(
                "subprocess.run", side_effect=subprocess.TimeoutExpired("pylint", 30)
            ):
                results = analyzer._run_pylint(temp_file)

                assert results == []

        finally:
            os.unlink(temp_file)

    def test_run_flake8_success(self):
        """Test successful flake8 execution."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def test_func():\n    print('hello')\n    return 1")
            temp_file = f.name

        try:
            analyzer = StaticAnalyzer()

            with patch("subprocess.run") as mock_run:
                mock_result = Mock()
                mock_result.returncode = 1
                mock_result.stdout = f"{temp_file}:1:1: E001 test error"
                mock_run.return_value = mock_result

                results = analyzer._run_flake8(temp_file)

                assert len(results) == 1
                assert results[0].message == "E001 test error"
                assert results[0].severity == SeverityLevel.ERROR
                assert results[0].rule_id == "E001"
                assert results[0].category == "flake8"

        finally:
            os.unlink(temp_file)

    def test_run_bandit_success(self):
        """Test successful bandit execution."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("import os\nos.system('ls')")
            temp_file = f.name

        try:
            analyzer = StaticAnalyzer()

            with patch("subprocess.run") as mock_run:
                mock_result = Mock()
                mock_result.returncode = 1
                mock_result.stdout = json.dumps(
                    {
                        "results": [
                            {
                                "filename": temp_file,
                                "line_number": 2,
                                "issue_severity": "HIGH",
                                "issue_text": "Test security issue",
                                "test_id": "B001",
                            }
                        ]
                    }
                )
                mock_run.return_value = mock_result

                results = analyzer._run_bandit(temp_file)

                assert len(results) == 1
                assert results[0].message == "Test security issue"
                assert results[0].severity == SeverityLevel.ERROR
                assert results[0].rule_id == "B001"
                assert results[0].category == "security"

        finally:
            os.unlink(temp_file)


class TestMetricsCalculation:
    """Test code metrics calculation."""

    def test_calculate_metrics(self):
        """Test metrics calculation for a file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def func1():\n    return 1\n\ndef func2():\n    return 2")
            temp_file = f.name

        try:
            analyzer = StaticAnalyzer()

            # Add some mock results
            analyzer.results = [
                AnalysisResult(
                    file_path=temp_file,
                    line_number=1,
                    column_number=0,
                    severity=SeverityLevel.WARNING,
                    message="Test warning",
                    rule_id="E001",
                    category="pylint",
                )
            ]

            metrics = analyzer.calculate_metrics(temp_file)

            assert metrics.lines_of_code > 0
            assert metrics.cyclomatic_complexity >= 1
            assert metrics.maintainability_index >= 0
            assert metrics.technical_debt >= 0
            assert metrics.code_duplication >= 0
            assert temp_file in analyzer.metrics

        finally:
            os.unlink(temp_file)

    def test_calculate_metrics_invalid_file(self):
        """Test metrics calculation for invalid file."""
        analyzer = StaticAnalyzer()

        metrics = analyzer.calculate_metrics("/nonexistent/file.py")

        assert metrics.lines_of_code == 0
        assert metrics.cyclomatic_complexity == 0
        assert metrics.maintainability_index == 0
        assert metrics.technical_debt == 0
        assert metrics.code_duplication == 0


class TestResultFiltering:
    """Test result filtering functionality."""

    def test_get_results_by_severity(self):
        """Test filtering results by severity."""
        analyzer = StaticAnalyzer()

        # Add test results
        analyzer.results = [
            AnalysisResult(
                "file1.py", 1, 0, SeverityLevel.INFO, "Info", "I001", "test"
            ),
            AnalysisResult(
                "file2.py", 2, 0, SeverityLevel.WARNING, "Warning", "W001", "test"
            ),
            AnalysisResult(
                "file3.py", 3, 0, SeverityLevel.ERROR, "Error", "E001", "test"
            ),
        ]

        info_results = analyzer.get_results_by_severity(SeverityLevel.INFO)
        warning_results = analyzer.get_results_by_severity(SeverityLevel.WARNING)
        error_results = analyzer.get_results_by_severity(SeverityLevel.ERROR)

        assert len(info_results) == 1
        assert len(warning_results) == 1
        assert len(error_results) == 1
        assert info_results[0].message == "Info"
        assert warning_results[0].message == "Warning"
        assert error_results[0].message == "Error"

    def test_get_results_by_category(self):
        """Test filtering results by category."""
        analyzer = StaticAnalyzer()

        # Add test results
        analyzer.results = [
            AnalysisResult(
                "file1.py", 1, 0, SeverityLevel.INFO, "Info", "I001", "pylint"
            ),
            AnalysisResult(
                "file2.py", 2, 0, SeverityLevel.WARNING, "Warning", "W001", "flake8"
            ),
            AnalysisResult(
                "file3.py", 3, 0, SeverityLevel.ERROR, "Error", "E001", "pylint"
            ),
        ]

        pylint_results = analyzer.get_results_by_category("pylint")
        flake8_results = analyzer.get_results_by_category("flake8")

        assert len(pylint_results) == 2
        assert len(flake8_results) == 1
        assert all(r.category == "pylint" for r in pylint_results)
        assert all(r.category == "flake8" for r in flake8_results)

    def test_get_results_by_file(self):
        """Test filtering results by file."""
        analyzer = StaticAnalyzer()

        # Add test results
        analyzer.results = [
            AnalysisResult(
                "file1.py", 1, 0, SeverityLevel.INFO, "Info", "I001", "test"
            ),
            AnalysisResult(
                "file2.py", 2, 0, SeverityLevel.WARNING, "Warning", "W001", "test"
            ),
            AnalysisResult(
                "file1.py", 3, 0, SeverityLevel.ERROR, "Error", "E001", "test"
            ),
        ]

        file1_results = analyzer.get_results_by_file("file1.py")
        file2_results = analyzer.get_results_by_file("file2.py")

        assert len(file1_results) == 2
        assert len(file2_results) == 1
        assert all(r.file_path == "file1.py" for r in file1_results)
        assert all(r.file_path == "file2.py" for r in file2_results)


class TestExportFunctionality:
    """Test result export functionality."""

    def test_export_results_json(self):
        """Test exporting results to JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_file = f.name

        try:
            analyzer = StaticAnalyzer()

            # Add test results
            analyzer.results = [
                AnalysisResult(
                    "file1.py", 1, 0, SeverityLevel.INFO, "Info", "I001", "test"
                ),
                AnalysisResult(
                    "file2.py", 2, 0, SeverityLevel.WARNING, "Warning", "W001", "test"
                ),
            ]

            success = analyzer.export_results(temp_file, "json")

            assert success is True
            assert os.path.exists(temp_file)

            # Verify JSON content
            with open(temp_file, "r") as f:
                data = json.load(f)

            assert len(data) == 2
            assert data[0]["file_path"] == "file1.py"
            assert data[0]["severity"] == "info"
            assert data[1]["file_path"] == "file2.py"
            assert data[1]["severity"] == "warning"

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_export_results_csv(self):
        """Test exporting results to CSV."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_file = f.name

        try:
            analyzer = StaticAnalyzer()

            # Add test results
            analyzer.results = [
                AnalysisResult(
                    "file1.py", 1, 0, SeverityLevel.INFO, "Info", "I001", "test"
                ),
            ]

            success = analyzer.export_results(temp_file, "csv")

            assert success is True
            assert os.path.exists(temp_file)

            # Verify CSV content
            with open(temp_file, "r") as f:
                content = f.read()

            assert "file1.py" in content
            assert "Info" in content
            assert "I001" in content

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_export_results_unsupported_format(self):
        """Test exporting results with unsupported format."""
        analyzer = StaticAnalyzer()

        success = analyzer.export_results("test.xml", "xml")

        assert success is False

    def test_clear_results(self):
        """Test clearing results."""
        analyzer = StaticAnalyzer()

        # Add some results and metrics
        analyzer.results = [
            AnalysisResult("file1.py", 1, 0, SeverityLevel.INFO, "Info", "I001", "test")
        ]
        analyzer.metrics["file1.py"] = CodeMetrics(10, 1, 80.0, 0.1, 0.0)

        analyzer.clear_results()

        assert analyzer.results == []
        assert analyzer.metrics == {}


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_analyze_file_function(self):
        """Test analyze_file convenience function."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def test_func():\n    return 1")
            temp_file = f.name

        try:
            with patch(
                "static_analysis.static_analyzer.StaticAnalyzer.analyze_file"
            ) as mock_analyze:
                mock_results = [
                    AnalysisResult(
                        "test.py", 1, 0, SeverityLevel.INFO, "Test", "T001", "test"
                    )
                ]
                mock_analyze.return_value = mock_results

                results = analyze_file(temp_file)

                assert len(results) == 1
                mock_analyze.assert_called_once()

        finally:
            os.unlink(temp_file)

    def test_analyze_project_function(self):
        """Test analyze_project convenience function."""
        with patch(
            "static_analysis.static_analyzer.StaticAnalyzer.analyze_project"
        ) as mock_analyze:
            mock_summary = AnalysisSummary(5, 2, 1.0)
            mock_analyze.return_value = mock_summary

            summary = analyze_project("/test/project")

            assert summary.total_issues == 5
            assert summary.files_analyzed == 2
            mock_analyze.assert_called_once()

    def test_get_available_tools_function(self):
        """Test get_available_tools convenience function."""
        tools = get_available_tools()

        assert isinstance(tools, dict)
        assert "pylint" in tools
        assert "flake8" in tools
        assert "mypy" in tools
        assert "bandit" in tools


class TestIntegration:
    """Integration tests."""

    def test_full_analysis_workflow(self):
        """Test complete analysis workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test Python file
            test_file = os.path.join(temp_dir, "test.py")
            with open(test_file, "w") as f:
                f.write(
                    """
def complex_function(x, y):
    if x > 0:
        if y > 0:
            for i in range(x):
                if i % 2 == 0:
                    print(i)
                else:
                    print(i * 2)
        else:
            return 0
    else:
        return -1
    return x + y
"""
                )

            analyzer = StaticAnalyzer(temp_dir)

            # Analyze the file
            results = analyzer.analyze_file(test_file)

            # Calculate metrics
            metrics = analyzer.calculate_metrics(test_file)

            # Get summary
            summary = analyzer.analyze_project()

            # Verify results
            assert isinstance(results, list)
            assert isinstance(metrics, CodeMetrics)
            assert isinstance(summary, AnalysisSummary)
            assert summary.files_analyzed >= 1

            # Test filtering
            error_results = analyzer.get_results_by_severity(SeverityLevel.ERROR)
            warning_results = analyzer.get_results_by_severity(SeverityLevel.WARNING)

            assert isinstance(error_results, list)
            assert isinstance(warning_results, list)


if __name__ == "__main__":
    pytest.main([__file__])
