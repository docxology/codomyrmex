"""Unit tests for static_analysis module."""

import pytest
import sys


class TestStaticAnalysis:
    """Test cases for static analysis functionality."""

    def test_pyrefly_runner_import(self, code_dir):
        """Test that we can import pyrefly_runner module."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.static_analysis import pyrefly_runner
            assert pyrefly_runner is not None
        except ImportError as e:
            pytest.fail(f"Failed to import pyrefly_runner: {e}")

    def test_pyrefly_runner_structure(self, code_dir):
        """Test that pyrefly_runner has expected structure and functions."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis import pyrefly_runner

        assert hasattr(pyrefly_runner, '__file__')

        # Test that key functions exist
        assert hasattr(pyrefly_runner, 'parse_pyrefly_output')
        assert callable(pyrefly_runner.parse_pyrefly_output)

        # Test that other expected functions exist if they exist
        # (These may not exist yet, so we test conditionally)
        if hasattr(pyrefly_runner, 'run_pyrefly_analysis'):
            assert callable(getattr(pyrefly_runner, 'run_pyrefly_analysis'))

    def test_parse_pyrefly_output_with_real_data(self, code_dir):
        """Test parse_pyrefly_output with real Pyrefly error data."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.pyrefly_runner import parse_pyrefly_output

        # Test with empty output
        result = parse_pyrefly_output("", "/tmp/project")
        assert result == []

        # Test with real Pyrefly error format
        pyrefly_output = "/path/to/file.py:123:45: error: Undefined name 'undefined_var'"
        project_root = "/path/to"

        result = parse_pyrefly_output(pyrefly_output, project_root)

        assert len(result) == 1
        issue = result[0]
        assert issue["file_path"] == "file.py"
        assert issue["line_number"] == 123
        assert issue["column_number"] == 45
        assert issue["message"] == "Undefined name 'undefined_var'"
        assert issue["severity"] == "error"
        assert issue["code"] == "PYREFLY_ERROR"

    def test_parse_pyrefly_output_multiple_errors(self, code_dir):
        """Test parse_pyrefly_output with multiple real errors."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.pyrefly_runner import parse_pyrefly_output

        pyrefly_output = """/path/to/file1.py:10:5: error: Type mismatch
/path/to/file2.py:25:15: warning: Unused variable
Some non-matching line
/path/to/file3.py:100:20: error: Import error"""

        project_root = "/path/to"
        result = parse_pyrefly_output(pyrefly_output, project_root)

        assert len(result) == 3

        # Check first error
        assert result[0]["file_path"] == "file1.py"
        assert result[0]["line_number"] == 10
        assert result[0]["column_number"] == 5
        assert result[0]["severity"] == "error"

        # Check second error
        assert result[1]["file_path"] == "file2.py"
        assert result[1]["line_number"] == 25
        assert result[1]["column_number"] == 15
        assert result[1]["severity"] == "warning"

        # Check third error
        assert result[2]["file_path"] == "file3.py"
        assert result[2]["line_number"] == 100
        assert result[2]["column_number"] == 20
        assert result[2]["severity"] == "error"

    def test_static_analysis_module_imports(self, code_dir):
        """Test that all static analysis modules can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        # Test pyrefly_runner specifically since it's mentioned in the module
        from codomyrmex.static_analysis import pyrefly_runner
        assert pyrefly_runner is not None

        # Check that it has expected attributes
        assert hasattr(pyrefly_runner, '__file__')

        # Test that parse_pyrefly_output is available and functional
        assert hasattr(pyrefly_runner, 'parse_pyrefly_output')
        assert callable(pyrefly_runner.parse_pyrefly_output)

    def test_code_with_real_issues(self, real_code_samples):
        """Test static analysis with real code samples that have issues."""
        if str(real_code_samples['undefined_var'].parent) not in sys.path:
            sys.path.insert(0, str(real_code_samples['undefined_var'].parent))

        from codomyrmex.static_analysis.pyrefly_runner import parse_pyrefly_output

        # Test with code that has undefined variable
        undefined_var_file = real_code_samples['undefined_var']
        content = undefined_var_file.read_text()

        # Create mock pyrefly output for this file
        # (In real usage, this would come from running pyrefly on the file)
        mock_pyrefly_output = f"{str(undefined_var_file)}:4:10: error: Undefined name 'undefined_variable'"

        result = parse_pyrefly_output(mock_pyrefly_output, str(undefined_var_file.parent))

        assert len(result) == 1
        issue = result[0]
        assert "undefined_variable" in issue["message"]
        assert issue["severity"] == "error"
