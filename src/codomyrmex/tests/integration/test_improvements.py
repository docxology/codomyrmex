#!/usr/bin/env python3
"""
Integration tests for the comprehensive improvements made to Codomyrmex.

This test suite validates that all the improvements work together correctly.
"""

import sys
from pathlib import Path

import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.core.logger_config import get_logger, setup_logging


class TestComprehensiveImprovements:
    """Test comprehensive improvements across modules."""

    def test_exception_hierarchy_available(self):
        """Test that the exception hierarchy is properly available."""
        # Test that we can import the base exception
        assert CodomyrmexError

        # Test that we can create and catch the exception
        try:
            raise CodomyrmexError("Test error")
        except CodomyrmexError as e:
            assert str(e) == "[CodomyrmexError] Test error"
            assert e.error_code == "CodomyrmexError"

    def test_logging_infrastructure_available(self):
        """Test that logging infrastructure works."""
        # Setup logging
        setup_logging()

        # Get a logger
        logger = get_logger("test_module")
        assert logger is not None

        # Test that we can log messages
        logger.info("Test log message")
        logger.debug("Debug message")

    def test_module_imports_work(self):
        """Test that key modules can be imported without errors."""
        import_tests = [
            "codomyrmex.exceptions",
            "codomyrmex.logging_monitoring.core.logger_config",
        ]

        for module_name in import_tests:
            try:
                __import__(module_name)
            except ImportError as e:
                pytest.fail(f"Failed to import {module_name}: {e}")

    def test_exception_context_functionality(self):
        """Test that exception context works properly."""
        context = {"operation": "test", "file_path": "/test/path"}

        error = CodomyrmexError(
            "Test error with context",
            context=context
        )

        assert error.context == context
        assert "operation=test" in str(error)
        assert "file_path=/test/path" in str(error)

    def test_exception_serialization(self):
        """Test that exceptions can be serialized to dict."""
        error = CodomyrmexError(
            "Serialization test",
            context={"key": "value"},
            error_code="TEST_ERROR"
        )

        error_dict = error.to_dict()

        assert error_dict["message"] == "Serialization test"
        assert error_dict["context"]["key"] == "value"
        assert error_dict["error_code"] == "TEST_ERROR"

    def test_cross_module_exception_handling(self):
        """Test that exceptions work across module boundaries."""
        from codomyrmex.exceptions import FileOperationError

        # Test specialized exception
        with pytest.raises(FileOperationError) as exc_info:
            raise FileOperationError("File not found", file_path="/test/file.txt")

        error = exc_info.value
        assert isinstance(error, CodomyrmexError)  # Inherits from base
        assert error.context.get("file_path") == "/test/file.txt"

    @pytest.mark.integration
    def test_overall_infrastructure_health(self):
        """High-level test of the overall infrastructure health."""
        # Test that we can:
        # 1. Setup logging
        setup_logging()

        # 2. Get loggers
        logger = get_logger(__name__)

        # 3. Use exceptions with logging
        try:
            raise CodomyrmexError("Integration test error", context={"test": "data"})
        except CodomyrmexError as e:
            logger.error(f"Caught error: {e}")
            # Exception should be serializable for logging
            error_data = e.to_dict()
            assert "message" in error_data
            assert "context" in error_data

        # 4. Verify logger is functional and error serialized correctly
        assert logger is not None
        assert error_data["message"] == "Integration test error"


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
