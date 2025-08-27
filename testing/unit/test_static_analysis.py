"""Unit tests for static_analysis module."""

import pytest
import sys
from unittest.mock import patch, MagicMock


class TestStaticAnalysis:
    """Test cases for static analysis functionality."""

    def test_pyrefly_runner_import(self, code_dir):
        """Test that we can import pyrefly_runner module."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from static_analysis import pyrefly_runner
            assert pyrefly_runner is not None
        except ImportError as e:
            pytest.fail(f"Failed to import pyrefly_runner: {e}")

    def test_pyrefly_runner_structure(self, code_dir):
        """Test that pyrefly_runner has expected structure."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from static_analysis import pyrefly_runner

        assert hasattr(pyrefly_runner, '__file__')
        # Add more structural tests based on actual implementation
        # assert hasattr(pyrefly_runner, 'run_pyrefly_analysis')  # Example
        # assert callable(getattr(pyrefly_runner, 'run_pyrefly_analysis', None))  # Example

    @patch('subprocess.run')
    def test_pyrefly_execution_mock(self, mock_subprocess, code_dir):
        """Test pyrefly execution with mocked subprocess."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from static_analysis import pyrefly_runner

        # Mock subprocess.run to return a result
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "No errors found"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        # This is a placeholder test structure
        # Actual test would depend on the specific function signatures
        assert hasattr(pyrefly_runner, '__file__')

    def test_static_analysis_module_imports(self, code_dir):
        """Test that all static analysis modules can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        # Test pyrefly_runner specifically since it's mentioned in the module
        from static_analysis import pyrefly_runner
        assert pyrefly_runner is not None

        # Check that it has expected attributes
        assert hasattr(pyrefly_runner, '__file__')

