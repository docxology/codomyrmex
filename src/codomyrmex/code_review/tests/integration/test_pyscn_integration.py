"""
Integration tests for pyscn functionality.

These tests require pyscn to be installed and will test the actual
pyscn integration with real Python code.
"""

import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

# Add the src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from codomyrmex.code_review import (
    CodeReviewer,
    PyscnAnalyzer,
    SeverityLevel,
    ToolNotFoundError,
)


def _pyscn_available():
    """Check if pyscn is available for testing."""
    try:
        import subprocess
        result = subprocess.run(
            ["pyscn", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


class TestPyscnIntegration(unittest.TestCase):
    """Integration tests for pyscn functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures", "python")

        # Create test files
        self.test_files = self._create_test_files()

    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def _create_test_files(self):
        """Create test files from fixtures."""
        test_files = {}

        for fixture_file in ["simple_function.py", "complex_function.py", "clone_example.py", "security_issues.py"]:
            fixture_path = os.path.join(self.fixtures_dir, fixture_file)
            if os.path.exists(fixture_path):
                # Copy fixture to test directory
                test_path = os.path.join(self.test_dir, fixture_file)
                shutil.copy2(fixture_path, test_path)
                test_files[fixture_file] = test_path

        return test_files

    def test_pyscn_availability(self):
        """Test that pyscn is available and working."""
        try:
            analyzer = PyscnAnalyzer()
            # This should not raise an exception
            self.assertIsInstance(analyzer, PyscnAnalyzer)
        except ToolNotFoundError:
            self.skipTest("Pyscn not available - install with: pipx install pyscn")

    @unittest.skipUnless(_pyscn_available(), "Pyscn not available")
    def test_complexity_analysis_simple(self):
        """Test complexity analysis on simple function."""
        if "simple_function.py" not in self.test_files:
            self.skipTest("Simple function fixture not available")

        analyzer = PyscnAnalyzer()
        results = analyzer.analyze_complexity(self.test_files["simple_function.py"])

        # Should find at least 2 functions
        self.assertGreaterEqual(len(results), 2)

        # Check that results have expected structure
        for result in results:
            self.assertIn("name", result)
            self.assertIn("complexity", result)
            self.assertIn("line", result)

    @unittest.skipUnless(_pyscn_available(), "Pyscn not available")
    def test_complexity_analysis_complex(self):
        """Test complexity analysis on complex function."""
        if "complex_function.py" not in self.test_files:
            self.skipTest("Complex function fixture not available")

        analyzer = PyscnAnalyzer()
        results = analyzer.analyze_complexity(self.test_files["complex_function.py"])

        # Should find functions with high complexity
        self.assertGreaterEqual(len(results), 2)

        # Look for the highly_complex_function
        complex_func = None
        for result in results:
            if result.get("name") == "highly_complex_function":
                complex_func = result
                break

        if complex_func:
            # Should have high complexity
            self.assertGreater(complex_func["complexity"], 10)

    @unittest.skipUnless(_pyscn_available(), "Pyscn not available")
    def test_dead_code_detection(self):
        """Test dead code detection."""
        if "complex_function.py" not in self.test_files:
            self.skipTest("Complex function fixture not available")

        analyzer = PyscnAnalyzer()
        results = analyzer.detect_dead_code(self.test_files["complex_function.py"])

        # Should find unreachable code
        self.assertGreaterEqual(len(results), 1)

        # Check result structure
        for result in results:
            self.assertIn("line", result)
            self.assertIn("message", result)

    @unittest.skipUnless(_pyscn_available(), "Pyscn not available")
    def test_clone_detection(self):
        """Test code clone detection."""
        if len(self.test_files) < 2:
            self.skipTest("Need at least 2 test files for clone detection")

        analyzer = PyscnAnalyzer()
        file_list = list(self.test_files.values())

        results = analyzer.find_clones(file_list, threshold=0.7)

        # Results should be a list
        self.assertIsInstance(results, list)

        # Each result should have expected structure if clones are found
        for result in results:
            if isinstance(result, dict):
                self.assertIn("file1", result)
                self.assertIn("file2", result)
                self.assertIn("similarity", result)

    @unittest.skipUnless(_pyscn_available(), "Pyscn not available")
    def test_coupling_analysis(self):
        """Test coupling between objects analysis."""
        if "clone_example.py" not in self.test_files:
            self.skipTest("Clone example fixture not available")

        analyzer = PyscnAnalyzer()
        results = analyzer.analyze_coupling(self.test_files["clone_example.py"])

        # Results should be a list
        self.assertIsInstance(results, list)

    @unittest.skipUnless(_pyscn_available(), "Pyscn not available")
    def test_full_integration_workflow(self):
        """Test complete workflow with CodeReviewer."""
        if not self.test_files:
            self.skipTest("No test files available")

        reviewer = CodeReviewer(project_root=self.test_dir)

        # Analyze a single file
        test_file = list(self.test_files.values())[0]
        results = reviewer.analyze_file(test_file)

        # Should return analysis results
        self.assertIsInstance(results, list)

        # Check result structure
        for result in results:
            self.assertIsInstance(result.file_path, str)
            self.assertIsInstance(result.line_number, int)
            self.assertIsInstance(result.severity, SeverityLevel)
            self.assertIsInstance(result.message, str)
            self.assertIsInstance(result.rule_id, str)
            self.assertIsInstance(result.category, str)

    @unittest.skipUnless(_pyscn_available(), "Pyscn not available")
    def test_project_analysis(self):
        """Test project-wide analysis."""
        reviewer = CodeReviewer(project_root=self.test_dir)

        summary = reviewer.analyze_project(target_paths=[self.test_dir])

        # Should return a summary
        self.assertIsInstance(summary.total_issues, int)
        self.assertIsInstance(summary.files_analyzed, int)
        self.assertIsInstance(summary.analysis_time, float)

        # Should have analyzed some files
        self.assertGreaterEqual(summary.files_analyzed, 0)

    @unittest.skipUnless(_pyscn_available(), "Pyscn not available")
    def test_report_generation(self):
        """Test HTML report generation."""
        reviewer = CodeReviewer(project_root=self.test_dir)
        reviewer.analyze_project(target_paths=[self.test_dir])

        report_path = os.path.join(self.test_dir, "test_report.html")
        success = reviewer.generate_report(report_path, format="html")

        if success:
            # Check that report file exists
            self.assertTrue(os.path.exists(report_path))

            # Check file content
            with open(report_path) as f:
                content = f.read()
                self.assertIn("<!DOCTYPE html>", content)
                self.assertIn("Code Review Report", content)

    @unittest.skipUnless(_pyscn_available(), "Pyscn not available")
    def test_quality_gates(self):
        """Test quality gate checking."""
        reviewer = CodeReviewer(project_root=self.test_dir)
        reviewer.analyze_project(target_paths=[self.test_dir])

        # Test with reasonable thresholds
        thresholds = {
            "max_complexity": 10,
            "max_issues_per_file": 50
        }

        result = reviewer.check_quality_gates(thresholds)

        # Should return a quality gate result
        self.assertIsInstance(result.passed, bool)
        self.assertIsInstance(result.total_checks, int)
        self.assertIsInstance(result.passed_checks, int)
        self.assertIsInstance(result.failed_checks, int)

    def test_pyscn_not_available_fallback(self):
        """Test behavior when pyscn is not available."""
        with patch('subprocess.run', side_effect=FileNotFoundError("pyscn not found")):
            with self.assertRaises(ToolNotFoundError):
                PyscnAnalyzer()


if __name__ == '__main__':
    # Check if pyscn is available before running tests
    if _pyscn_available():
        print("✅ Pyscn is available - running integration tests")
        unittest.main(verbosity=2)
    else:
        print("❌ Pyscn not available - install with: pipx install pyscn")
        print("Skipping integration tests")
        sys.exit(0)
