"""Unit tests for static_analysis module."""

import sys

import pytest


@pytest.mark.unit
class TestStaticAnalysisComprehensive:
    """Test cases for static analysis functionality."""

    def test_static_analysis_import(self, code_dir):
        """Test that we can import static_analysis module."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.coding.static_analysis import pyrefly_runner
            assert pyrefly_runner is not None
        except ImportError as e:
            pytest.fail(f"Failed to import pyrefly_runner: {e}")
