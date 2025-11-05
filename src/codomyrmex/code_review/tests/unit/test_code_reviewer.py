"""
Unit tests for CodeReviewer class.

Tests the core functionality of the code review module including
pyscn integration and analysis capabilities.
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

# Add the src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from codomyrmex.code_review import (
    AnalysisResult,
    AnalysisSummary,
    AnalysisType,
    CodeReviewer,
    Language,
    PyscnAnalyzer,
    QualityGateResult,
    SeverityLevel,
    ToolNotFoundError,
)


class TestPyscnAnalyzer(unittest.TestCase):
    """Test cases for PyscnAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = PyscnAnalyzer()

    @patch('glob.glob')
    @patch('os.path.exists')
    @patch('os.path.getmtime')
    def test_analyze_complexity_success(self, mock_getmtime, mock_exists, mock_glob):
        """Test successful complexity analysis."""
        # Mock file system operations
        mock_exists.return_value = True
        mock_glob.return_value = ['/fake/path/report.json']

        # Mock the most recent file
        mock_getmtime.return_value = 1234567890.0

        # Mock JSON content
        mock_json_data = {
            "complexity": {
                "Functions": [
                    {
                        "Name": "test_function",
                        "Metrics": {"Complexity": 15},
                        "StartLine": 10,
                        "FilePath": "test.py",
                        "RiskLevel": "medium"
                    }
                ]
            }
        }

        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            mock_file.return_value.read.return_value = json.dumps(mock_json_data)

            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write('def test_function(): pass\n')
                test_file = f.name

            try:
                results = self.analyzer.analyze_complexity(test_file)
                self.assertEqual(len(results), 1)
                self.assertEqual(results[0]['name'], 'test_function')
                self.assertEqual(results[0]['complexity'], 15)
            finally:
                os.unlink(test_file)

    @patch('glob.glob')
    @patch('os.path.exists')
    def test_analyze_complexity_no_output(self, mock_exists, mock_glob):
        """Test complexity analysis with no output."""
        # Mock no reports directory
        mock_exists.return_value = False

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def test_function(): pass\n')
            test_file = f.name

        try:
            results = self.analyzer.analyze_complexity(test_file)
            self.assertEqual(results, [])
        finally:
            os.unlink(test_file)

    @patch('subprocess.run')
    def test_detect_dead_code(self, mock_run):
        """Test dead code detection."""
        mock_run.return_value.stdout = '''
        {
            "dead_code": {
                "findings": [
                    {
                        "line": 5,
                        "message": "Unreachable code after return"
                    }
                ]
            }
        }
        '''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''
def test_function():
    return 1
    print("unreachable")
''')
            test_file = f.name

        try:
            results = self.analyzer.detect_dead_code(test_file)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['line'], 5)
        finally:
            os.unlink(test_file)


class TestCodeReviewer(unittest.TestCase):
    """Test cases for CodeReviewer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.reviewer = CodeReviewer(project_root=self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test CodeReviewer initialization."""
        self.assertEqual(self.reviewer.project_root, self.temp_dir)
        self.assertIsInstance(self.reviewer.results, list)
        self.assertIsInstance(self.reviewer.metrics, dict)
        self.assertIsInstance(self.reviewer.pyscn_analyzer, PyscnAnalyzer)

    def test_detect_language_python(self):
        """Test language detection for Python files."""
        # This would be a private method, but we can test it indirectly
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('print("hello")')
            test_file = f.name

        try:
            # Access private method for testing
            language = self.reviewer._detect_language(test_file)
            self.assertEqual(language, Language.PYTHON)
        finally:
            os.unlink(test_file)

    def test_detect_language_javascript(self):
        """Test language detection for JavaScript files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write('console.log("hello");')
            test_file = f.name

        try:
            language = self.reviewer._detect_language(test_file)
            self.assertEqual(language, Language.JAVASCRIPT)
        finally:
            os.unlink(test_file)

    def test_should_analyze_file_supported(self):
        """Test file analysis decision for supported files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            test_file = f.name

        try:
            # Access private method for testing
            should_analyze = self.reviewer._should_analyze_file(test_file)
            self.assertTrue(should_analyze)
        finally:
            os.unlink(test_file)

    def test_should_analyze_file_unsupported(self):
        """Test file analysis decision for unsupported files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            test_file = f.name

        try:
            should_analyze = self.reviewer._should_analyze_file(test_file)
            self.assertFalse(should_analyze)
        finally:
            os.unlink(test_file)

    def test_analyze_file_empty_types(self):
        """Test file analysis with no analysis types specified."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def test(): pass')
            test_file = f.name

        try:
            results = self.reviewer.analyze_file(test_file)
            # Should run default analysis types
            self.assertIsInstance(results, list)
        finally:
            os.unlink(test_file)

    def test_analyze_project_empty_directory(self):
        """Test project analysis on empty directory."""
        summary = self.reviewer.analyze_project(target_paths=[self.temp_dir])
        self.assertIsInstance(summary, AnalysisSummary)
        self.assertEqual(summary.files_analyzed, 0)
        self.assertEqual(summary.total_issues, 0)

    @patch('os.walk')
    def test_analyze_project_with_files(self, mock_walk):
        """Test project analysis with Python files."""
        # Mock os.walk to return test files
        mock_walk.return_value = [
            (self.temp_dir, [], ['test1.py', 'test2.py']),
            (os.path.join(self.temp_dir, 'subdir'), [], ['test3.py'])
        ]

        # Mock file reading for _should_analyze_file
        with patch.object(self.reviewer, '_should_analyze_file', return_value=True):
            with patch.object(self.reviewer, 'analyze_file') as mock_analyze:
                mock_analyze.return_value = []

                summary = self.reviewer.analyze_project()
                self.assertIsInstance(summary, AnalysisSummary)

    def test_quality_gates_pass(self):
        """Test quality gates check when all pass."""
        # Create some mock results that would pass
        self.reviewer.results = [
            AnalysisResult(
                file_path="test.py",
                line_number=1,
                column_number=0,
                severity=SeverityLevel.WARNING,
                message="Test warning",
                rule_id="TEST",
                category="test"
            )
        ]

        gates = {"max_issues_per_file": 10}
        result = self.reviewer.check_quality_gates(gates)

        self.assertIsInstance(result, QualityGateResult)
        self.assertTrue(result.passed)

    def test_generate_report_html(self):
        """Test HTML report generation."""
        output_file = os.path.join(self.temp_dir, "report.html")

        success = self.reviewer.generate_report(output_file, format="html")
        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_file))

        # Check file content
        with open(output_file) as f:
            content = f.read()
            self.assertIn("<!DOCTYPE html>", content)
            self.assertIn("Code Review Report", content)

    def test_generate_report_json(self):
        """Test JSON report generation."""
        output_file = os.path.join(self.temp_dir, "report.json")

        success = self.reviewer.generate_report(output_file, format="json")
        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_file))

        # Check file content
        with open(output_file) as f:
            content = f.read()
            self.assertIn('"summary"', content)
            self.assertIn('"results"', content)

    def test_clear_results(self):
        """Test clearing analysis results."""
        # Add some mock results
        self.reviewer.results = [Mock()]
        self.reviewer.metrics = {"test": Mock()}

        self.reviewer.clear_results()

        self.assertEqual(len(self.reviewer.results), 0)
        self.assertEqual(len(self.reviewer.metrics), 0)


class TestEnums(unittest.TestCase):
    """Test cases for enum definitions."""

    def test_analysis_type_enum(self):
        """Test AnalysisType enum values."""
        self.assertEqual(AnalysisType.QUALITY.value, "quality")
        self.assertEqual(AnalysisType.PYSCN.value, "pyscn")

    def test_severity_level_enum(self):
        """Test SeverityLevel enum values."""
        self.assertEqual(SeverityLevel.ERROR.value, "error")
        self.assertEqual(SeverityLevel.CRITICAL.value, "critical")

    def test_language_enum(self):
        """Test Language enum values."""
        self.assertEqual(Language.PYTHON.value, "python")
        self.assertEqual(Language.JAVASCRIPT.value, "javascript")


class TestDataClasses(unittest.TestCase):
    """Test cases for data class definitions."""

    def test_analysis_result_creation(self):
        """Test AnalysisResult data class."""
        result = AnalysisResult(
            file_path="test.py",
            line_number=10,
            column_number=5,
            severity=SeverityLevel.WARNING,
            message="Test message",
            rule_id="TEST001",
            category="test"
        )

        self.assertEqual(result.file_path, "test.py")
        self.assertEqual(result.line_number, 10)
        self.assertEqual(result.severity, SeverityLevel.WARNING)
        self.assertEqual(result.message, "Test message")
        self.assertEqual(result.rule_id, "TEST001")
        self.assertEqual(result.category, "test")

    def test_analysis_summary_creation(self):
        """Test AnalysisSummary data class."""
        summary = AnalysisSummary(
            total_issues=5,
            by_severity={SeverityLevel.ERROR: 2, SeverityLevel.WARNING: 3},
            files_analyzed=3,
            analysis_time=2.5
        )

        self.assertEqual(summary.total_issues, 5)
        self.assertEqual(summary.files_analyzed, 3)
        self.assertEqual(summary.analysis_time, 2.5)

    def test_quality_gate_result_creation(self):
        """Test QualityGateResult data class."""
        result = QualityGateResult(
            passed=True,
            total_checks=3,
            passed_checks=3,
            failed_checks=0
        )

        self.assertTrue(result.passed)
        self.assertEqual(result.total_checks, 3)
        self.assertEqual(result.passed_checks, 3)
        self.assertEqual(result.failed_checks, 0)


class TestErrorClasses(unittest.TestCase):
    """Test cases for custom exception classes."""

    def test_code_review_error(self):
        """Test CodeReviewError exception."""
        error = ToolNotFoundError("Test error")
        self.assertIn("Test error", str(error))

    def test_pyscn_error(self):
        """Test PyscnError exception."""
        from codomyrmex.code_review import PyscnError
        error = PyscnError("Pyscn test error")
        self.assertIn("Pyscn test error", str(error))


if __name__ == '__main__':
    unittest.main()
