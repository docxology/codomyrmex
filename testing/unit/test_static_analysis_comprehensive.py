"""Comprehensive unit tests for static_analysis module."""

import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestStaticAnalysisComprehensive:
    """Comprehensive test cases for static analysis functionality."""

    def test_static_analysis_import(self, code_dir):
        """Test that we can import static_analysis module."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from static_analysis import pyrefly_runner
            assert pyrefly_runner is not None
        except ImportError as e:
            pytest.fail(f"Failed to import pyrefly_runner: {e}")

    def test_parse_pyrefly_output_no_output(self, code_dir):
        """Test parse_pyrefly_output with empty output."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from static_analysis.pyrefly_runner import parse_pyrefly_output

        result = parse_pyrefly_output("", "/tmp/project")
        assert result == []

    def test_parse_pyrefly_output_valid_error(self, code_dir):
        """Test parse_pyrefly_output with valid Pyrefly error format."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from static_analysis.pyrefly_runner import parse_pyrefly_output

        # Mock output with typical Pyrefly error format
        output = "/path/to/file.py:123:45: error: Undefined name 'undefined_var'"
        project_root = "/path/to"

        result = parse_pyrefly_output(output, project_root)

        assert len(result) == 1
        issue = result[0]
        assert issue["file_path"] == "file.py"  # Should be relative to project_root
        assert issue["line_number"] == 123
        assert issue["column_number"] == 45
        assert issue["message"] == "error: Undefined name 'undefined_var'"
        assert issue["severity"] == "error"
        assert issue["code"] == "PYREFLY_ERROR"

    def test_parse_pyrefly_output_multiple_errors(self, code_dir):
        """Test parse_pyrefly_output with multiple errors."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from static_analysis.pyrefly_runner import parse_pyrefly_output

        output = """/path/to/file1.py:10:5: error: Type mismatch
/path/to/file2.py:25:15: warning: Unused variable
Some non-matching line
/path/to/file3.py:100:20: error: Import error"""

        project_root = "/path/to"
        result = parse_pyrefly_output(output, project_root)

        assert len(result) == 3

        # Check first error
        assert result[0]["file_path"] == "file1.py"
        assert result[0]["line_number"] == 10
        assert result[0]["column_number"] == 5

        # Check second error
        assert result[1]["file_path"] == "file2.py"
        assert result[1]["line_number"] == 25
        assert result[1]["column_number"] == 15

        # Check third error
        assert result[2]["file_path"] == "file3.py"
        assert result[2]["line_number"] == 100
        assert result[2]["column_number"] == 20

    def test_parse_pyrefly_output_malformed_line(self, code_dir):
        """Test parse_pyrefly_output with malformed lines."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from static_analysis.pyrefly_runner import parse_pyrefly_output

        output = """This is not an error line
incomplete:123
/path/to/file.py:abc:def: error: Invalid line number
Valid error: /path/to/file.py:123:45: error: Real error"""

        project_root = "/path/to"
        result = parse_pyrefly_output(output, project_root)

        # Should only parse the valid error line
        assert len(result) == 1
        assert result[0]["file_path"] == "file.py"
        assert result[0]["line_number"] == 123
        assert result[0]["column_number"] == 45

    def test_parse_pyrefly_output_absolute_path_handling(self, code_dir):
        """Test parse_pyrefly_output with absolute paths."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from static_analysis.pyrefly_runner import parse_pyrefly_output

        output = "/absolute/path/to/file.py:50:10: error: Absolute path error"
        project_root = "/absolute/path"

        result = parse_pyrefly_output(output, project_root)

        assert len(result) == 1
        assert result[0]["file_path"] == "to/file.py"  # Should be relative to project_root

    def test_parse_pyrefly_output_empty_message(self, code_dir):
        """Test parse_pyrefly_output with empty error message."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from static_analysis.pyrefly_runner import parse_pyrefly_output

        output = "/path/to/file.py:1:1:"
        project_root = "/path/to"

        result = parse_pyrefly_output(output, project_root)

        assert len(result) == 1
        assert result[0]["message"] == ""

    @patch('subprocess.run')
    def test_run_pyrefly_analysis_success(self, mock_subprocess, code_dir):
        """Test run_pyrefly_analysis successful execution."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from static_analysis.pyrefly_runner import run_pyrefly_analysis

        # Mock successful subprocess execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "/path/to/file.py:10:5: error: Test error"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        target_paths = ["file1.py", "file2.py"]
        project_root = "/path/to"

        result = run_pyrefly_analysis(target_paths, project_root)

        assert result["tool_name"] == "pyrefly"
        assert result["issue_count"] == 1
        assert len(result["issues"]) == 1
        assert result["error"] is None
        assert result["raw_output"] != ""

        # Check that subprocess was called correctly
        mock_subprocess.assert_called_once_with(
            ["pyrefly", "check", "file1.py", "file2.py"],
            capture_output=True,
            text=True,
            cwd="/path/to",
            check=False
        )

    @patch('subprocess.run')
    def test_run_pyrefly_analysis_no_targets(self, mock_subprocess, code_dir):
        """Test run_pyrefly_analysis with no target paths."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from static_analysis.pyrefly_runner import run_pyrefly_analysis

        result = run_pyrefly_analysis([], "/path/to/project")

        assert result["tool_name"] == "pyrefly"
        assert result["issue_count"] == 0
        assert result["error"] == "No target paths provided for Pyrefly analysis."
        assert len(result["issues"]) == 0

        # subprocess should not be called
        mock_subprocess.assert_not_called()

    @patch('subprocess.run')
    def test_run_pyrefly_analysis_with_stderr(self, mock_subprocess, code_dir):
        """Test run_pyrefly_analysis when Pyrefly outputs to stderr."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from static_analysis.pyrefly_runner import run_pyrefly_analysis

        # Mock subprocess with stderr output
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "/path/to/file.py:20:10: error: Error in stderr"
        mock_subprocess.return_value = mock_result

        target_paths = ["test.py"]
        project_root = "/path/to"

        result = run_pyrefly_analysis(target_paths, project_root)

        assert result["tool_name"] == "pyrefly"
        assert result["issue_count"] == 1
        assert len(result["issues"]) == 1
        assert "Error in stderr" in result["issues"][0]["message"]
        assert "Pyrefly command failed with exit code 1" in result["error"]

    @patch('subprocess.run')
    def test_run_pyrefly_analysis_both_stdout_stderr(self, mock_subprocess, code_dir):
        """Test run_pyrefly_analysis with both stdout and stderr."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from static_analysis.pyrefly_runner import run_pyrefly_analysis

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "/path/to/file1.py:10:5: error: Stdout error"
        mock_result.stderr = "/path/to/file2.py:20:10: error: Stderr error"
        mock_subprocess.return_value = mock_result

        target_paths = ["test.py"]
        project_root = "/path/to"

        result = run_pyrefly_analysis(target_paths, project_root)

        assert result["tool_name"] == "pyrefly"
        assert result["issue_count"] == 2
        assert len(result["issues"]) == 2
        assert "Stdout error" in result["issues"][0]["message"]
        assert "Stderr error" in result["issues"][1]["message"]
        assert "--- Pyrefly STDOUT ---" in result["raw_output"]
        assert "--- Pyrefly STDERR ---" in result["raw_output"]

    @patch('subprocess.run')
    def test_run_pyrefly_analysis_subprocess_error(self, mock_subprocess, code_dir):
        """Test run_pyrefly_analysis when subprocess raises exception."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from static_analysis.pyrefly_runner import run_pyrefly_analysis

        # Mock subprocess to raise FileNotFoundError
        mock_subprocess.side_effect = FileNotFoundError("pyrefly command not found")

        target_paths = ["test.py"]
        project_root = "/path/to"

        result = run_pyrefly_analysis(target_paths, project_root)

        assert result["tool_name"] == "pyrefly"
        assert result["issue_count"] == 0
        assert "Failed to run Pyrefly" in result["error"]
        assert "pyrefly command not found" in result["error"]

    @patch('subprocess.run')
    def test_run_pyrefly_analysis_no_errors_found(self, mock_subprocess, code_dir):
        """Test run_pyrefly_analysis when no errors are found."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from static_analysis.pyrefly_runner import run_pyrefly_analysis

        # Mock successful execution with no errors
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        target_paths = ["test.py"]
        project_root = "/path/to"

        result = run_pyrefly_analysis(target_paths, project_root)

        assert result["tool_name"] == "pyrefly"
        assert result["issue_count"] == 0
        assert len(result["issues"]) == 0
        assert result["error"] is None

    def test_pyrefly_error_pattern_compilation(self, code_dir):
        """Test that PYREFLY_ERROR_PATTERN is properly compiled."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from static_analysis import pyrefly_runner

        # Check that the pattern exists and is compiled
        assert hasattr(pyrefly_runner, 'PYREFLY_ERROR_PATTERN')
        assert hasattr(pyrefly_runner.PYREFLY_ERROR_PATTERN, 'match')

    def test_parse_pyrefly_output_with_project_root_variations(self, code_dir):
        """Test parse_pyrefly_output with different project root scenarios."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from static_analysis.pyrefly_runner import parse_pyrefly_output

        # Test with relative paths
        output = "src/main.py:15:8: error: Type error"
        project_root = "/home/user/project"

        result = parse_pyrefly_output(output, project_root)

        assert len(result) == 1
        assert result[0]["file_path"] == "src/main.py"

    def test_run_pyrefly_analysis_result_structure(self, code_dir):
        """Test that run_pyrefly_analysis returns properly structured results."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from static_analysis.pyrefly_runner import run_pyrefly_analysis

        # Test with empty target paths (should return error structure)
        result = run_pyrefly_analysis([], "/tmp")

        required_keys = ["tool_name", "issue_count", "issues", "raw_output", "error", "report_path"]
        for key in required_keys:
            assert key in result

        assert result["tool_name"] == "pyrefly"
        assert isinstance(result["issues"], list)
        assert isinstance(result["issue_count"], int)

    @patch('subprocess.run')
    def test_run_pyrefly_analysis_command_construction(self, mock_subprocess, code_dir):
        """Test that run_pyrefly_analysis constructs command correctly."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from static_analysis.pyrefly_runner import run_pyrefly_analysis

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        target_paths = ["file1.py", "dir/", "file2.py"]
        project_root = "/home/user/project"

        run_pyrefly_analysis(target_paths, project_root)

        # Verify the command was constructed correctly
        expected_command = ["pyrefly", "check", "file1.py", "dir/", "file2.py"]
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args
        assert call_args[1]["args"] == expected_command
        assert call_args[1]["cwd"] == project_root
        assert call_args[1]["capture_output"] is True
        assert call_args[1]["text"] is True
        assert call_args[1]["check"] is False

    def test_parse_pyrefly_output_preserves_message_formatting(self, code_dir):
        """Test that parse_pyrefly_output preserves original message formatting."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from static_analysis.pyrefly_runner import parse_pyrefly_output

        output = "/path/to/file.py:1:1: error: Complex error message with    multiple   spaces   and   special:characters"
        project_root = "/path/to"

        result = parse_pyrefly_output(output, project_root)

        assert len(result) == 1
        assert result[0]["message"] == "error: Complex error message with    multiple   spaces   and   special:characters"

    def test_module_constants(self, code_dir):
        """Test that static analysis module has expected constants."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from static_analysis import pyrefly_runner

        # Check that PYREFLY_ERROR_PATTERN exists
        assert hasattr(pyrefly_runner, 'PYREFLY_ERROR_PATTERN')

        # Check that logger is defined
        assert hasattr(pyrefly_runner, 'logger')

    def test_parse_pyrefly_output_empty_lines(self, code_dir):
        """Test parse_pyrefly_output handles empty lines correctly."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from static_analysis.pyrefly_runner import parse_pyrefly_output

        output = """
/path/to/file.py:10:5: error: First error

/path/to/file.py:20:15: error: Second error
"""

        project_root = "/path/to"
        result = parse_pyrefly_output(output, project_root)

        assert len(result) == 2
        assert result[0]["line_number"] == 10
        assert result[1]["line_number"] == 20
