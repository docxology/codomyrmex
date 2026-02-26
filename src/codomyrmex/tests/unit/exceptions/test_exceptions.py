"""Comprehensive tests for the Codomyrmex exceptions module.

This module tests all exception classes and utility functions defined in
the exceptions module to ensure proper error handling throughout the package.
"""

from pathlib import Path

import pytest

from codomyrmex.exceptions import (
    AIProviderError,
    CodeExecutionError,
    CodomyrmexError,
    ConfigurationError,
    DependencyError,
    EnvironmentError,
    FileOperationError,
    GitOperationError,
    OrchestrationError,
    StaticAnalysisError,
    TimeoutError,
    VisualizationError,
    create_error_context,
    format_exception_chain,
)


class TestCodomyrmexError:
    """Test the base CodomyrmexError class."""

    def test_basic_error_creation(self):
        """Test creating a basic error."""
        error = CodomyrmexError("Test error message")
        assert str(error) == "[CodomyrmexError] Test error message"
        assert error.message == "Test error message"
        assert error.error_code == "CodomyrmexError"
        assert error.context == {}

    def test_error_with_context(self):
        """Test creating an error with context."""
        context = {"user": "test_user", "operation": "test_op"}
        error = CodomyrmexError("Test error", context=context)

        assert error.context == context
        assert "user=test_user" in str(error)
        assert "operation=test_op" in str(error)

    def test_error_with_custom_code(self):
        """Test creating an error with custom error code."""
        error = CodomyrmexError("Test error", error_code="CUSTOM_001")
        assert error.error_code == "CUSTOM_001"
        assert str(error) == "[CUSTOM_001] Test error"

    def test_error_to_dict(self):
        """Test converting error to dictionary."""
        context = {"key": "value"}
        error = CodomyrmexError("Test error", context=context, error_code="TEST_001")

        error_dict = error.to_dict()
        expected = {
            "error_type": "CodomyrmexError",
            "error_code": "TEST_001",
            "message": "Test error",
            "context": context,
        }
        assert error_dict == expected

    def test_error_inheritance(self):
        """Test that errors inherit from Exception."""
        error = CodomyrmexError("Test error")
        assert isinstance(error, Exception)
        assert isinstance(error, CodomyrmexError)


class TestSpecializedErrors:
    """Test specialized error classes."""

    def test_file_operation_error(self):
        """Test FileOperationError with file path context."""
        file_path = Path("/test/file.txt")
        error = FileOperationError("File not found", file_path=file_path)

        assert error.context["file_path"] == str(file_path)
        assert "file_path=/test/file.txt" in str(error)

    def test_file_operation_error_no_path(self):
        """Test FileOperationError without file path."""
        error = FileOperationError("General file error")
        assert "file_path" not in error.context

    def test_code_execution_error(self):
        """Test CodeExecutionError with execution details."""
        error = CodeExecutionError(
            "Command failed",
            exit_code=1,
            stdout="Output message",
            stderr="Error message"
        )

        assert error.context["exit_code"] == 1
        assert error.context["stdout"] == "Output message"
        assert error.context["stderr"] == "Error message"
        assert "exit_code=1" in str(error)

    def test_code_execution_error_minimal(self):
        """Test CodeExecutionError with minimal information."""
        error = CodeExecutionError("Command failed")
        assert "exit_code" not in error.context
        assert "stdout" not in error.context
        assert "stderr" not in error.context

    def test_git_operation_error(self):
        """Test GitOperationError with git context."""
        repo_path = Path("/test/repo")
        error = GitOperationError(
            "Git command failed",
            git_command="git pull",
            repository_path=repo_path
        )

        assert error.context["git_command"] == "git pull"
        assert error.context["repository_path"] == str(repo_path)

    def test_timeout_error(self):
        """Test TimeoutError with timeout information."""
        error = TimeoutError("Operation timed out", timeout_seconds=30.5)
        assert error.context["timeout_seconds"] == 30.5
        assert "timeout_seconds=30.5" in str(error)

    def test_timeout_error_no_duration(self):
        """Test TimeoutError without timeout duration."""
        error = TimeoutError("Operation timed out")
        assert "timeout_seconds" not in error.context


class TestErrorHierarchy:
    """Test that all error classes inherit from CodomyrmexError."""

    def test_configuration_error_hierarchy(self):
        """Test ConfigurationError inheritance."""
        error = ConfigurationError("Config error")
        assert isinstance(error, CodomyrmexError)
        assert isinstance(error, Exception)

    def test_environment_error_hierarchy(self):
        """Test EnvironmentError inheritance."""
        error = EnvironmentError("Env error")
        assert isinstance(error, CodomyrmexError)

    def test_dependency_error_hierarchy(self):
        """Test DependencyError inheritance."""
        error = DependencyError("Dependency error")
        assert isinstance(error, CodomyrmexError)

    def test_ai_provider_error_hierarchy(self):
        """Test AIProviderError inheritance."""
        error = AIProviderError("AI error")
        assert isinstance(error, CodomyrmexError)

    def test_static_analysis_error_hierarchy(self):
        """Test StaticAnalysisError inheritance."""
        error = StaticAnalysisError("Analysis error")
        assert isinstance(error, CodomyrmexError)

    def test_visualization_error_hierarchy(self):
        """Test VisualizationError inheritance."""
        error = VisualizationError("Viz error")
        assert isinstance(error, CodomyrmexError)

    def test_orchestration_error_hierarchy(self):
        """Test OrchestrationError inheritance."""
        error = OrchestrationError("Orchestration error")
        assert isinstance(error, CodomyrmexError)


class TestUtilityFunctions:
    """Test utility functions for exception handling."""

    def test_create_error_context_basic(self):
        """Test creating error context with basic values."""
        context = create_error_context(user="test_user", operation="test")
        expected = {"user": "test_user", "operation": "test"}
        assert context == expected

    def test_create_error_context_filters_none(self):
        """Test that create_error_context filters out None values."""
        context = create_error_context(
            user="test_user",
            operation=None,
            timestamp="2023-01-01"
        )
        expected = {"user": "test_user", "timestamp": "2023-01-01"}
        assert context == expected

    def test_create_error_context_empty(self):
        """Test creating empty context."""
        context = create_error_context()
        assert context == {}

    def test_format_exception_chain_single(self):
        """Test formatting a single exception."""
        error = CodomyrmexError("Test error")
        formatted = format_exception_chain(error)
        assert formatted == "[CodomyrmexError] Test error"

    def test_format_exception_chain_standard_exception(self):
        """Test formatting a standard Python exception."""
        error = ValueError("Invalid value")
        formatted = format_exception_chain(error)
        assert formatted == "[ValueError] Invalid value"

    def test_format_exception_chain_with_cause(self):
        """Test formatting exception chain with __cause__."""
        cause = CodomyrmexError("Root cause")
        error = ConfigurationError("Config problem")
        error.__cause__ = cause

        formatted = format_exception_chain(error)
        lines = formatted.split('\n')
        assert len(lines) == 2
        assert "[ConfigurationError]" in lines[0]
        assert "[CodomyrmexError]" in lines[1]

    def test_format_exception_chain_with_context(self):
        """Test formatting exception chain with __context__."""
        context_error = ValueError("Context error")
        error = CodomyrmexError("Main error")
        error.__context__ = context_error

        formatted = format_exception_chain(error)
        lines = formatted.split('\n')
        assert len(lines) == 2
        assert "[CodomyrmexError]" in lines[0]
        assert "[ValueError]" in lines[1]


class TestErrorSerialization:
    """Test error serialization and deserialization."""

    def test_error_serialization(self):
        """Test that errors can be serialized to dict."""
        context = {"file": "test.py", "line": 42}
        error = StaticAnalysisError(
            "Syntax error",
            context=context,
            error_code="SYNTAX_001"
        )

        serialized = error.to_dict()
        assert isinstance(serialized, dict)
        assert serialized["error_type"] == "StaticAnalysisError"
        assert serialized["error_code"] == "SYNTAX_001"
        assert serialized["message"] == "Syntax error"
        assert serialized["context"] == context

    def test_error_context_updates(self):
        """Test that error context can be updated after creation."""
        error = CodomyrmexError("Test error")
        assert error.context == {}

        error.context["new_key"] = "new_value"
        assert error.context["new_key"] == "new_value"
        assert "new_key=new_value" in str(error)


class TestErrorUsagePatterns:
    """Test common error usage patterns."""

    def test_raise_and_catch_codomyrmex_error(self):
        """Test raising and catching CodomyrmexError."""
        with pytest.raises(CodomyrmexError) as exc_info:
            raise CodomyrmexError("Test error")

        assert exc_info.value.message == "Test error"

    def test_raise_and_catch_specialized_error(self):
        """Test raising and catching specialized errors."""
        with pytest.raises(FileOperationError) as exc_info:
            raise FileOperationError("File error", file_path="/test/file.txt")

        error = exc_info.value
        assert isinstance(error, CodomyrmexError)
        assert isinstance(error, FileOperationError)
        assert error.context["file_path"] == "/test/file.txt"

    def test_catch_base_error_for_specialized(self):
        """Test that specialized errors can be caught as base error."""
        with pytest.raises(CodomyrmexError):
            raise AIProviderError("API error")

    def test_error_with_exception_chaining(self):
        """Test error chaining with raise ... from ..."""
        original_error = ValueError("Original error")

        with pytest.raises(CodomyrmexError) as exc_info:
            try:
                raise original_error
            except ValueError as e:
                raise CodomyrmexError("Wrapped error") from e

        error = exc_info.value
        assert error.__cause__ is original_error


class TestErrorContextManagement:
    """Test error context management features."""

    def test_context_with_pathlib_path(self):
        """Test context handling with pathlib Path objects."""
        path = Path("/test/directory/file.txt")
        error = FileOperationError("Path error", file_path=path)

        # Should be converted to string
        assert error.context["file_path"] == str(path)
        assert isinstance(error.context["file_path"], str)

    def test_context_with_string_path(self):
        """Test context handling with string paths."""
        path = "/test/directory/file.txt"
        error = FileOperationError("Path error", file_path=path)

        assert error.context["file_path"] == path

    def test_empty_context_string_representation(self):
        """Test string representation with empty context."""
        error = CodomyrmexError("Simple error")
        assert str(error) == "[CodomyrmexError] Simple error"
        assert "(Context:" not in str(error)

    def test_complex_context_string_representation(self):
        """Test string representation with complex context."""
        context = {
            "user": "test_user",
            "operation": "complex_operation",
            "timestamp": "2023-01-01T00:00:00Z",
            "retry_count": 3
        }
        error = CodomyrmexError("Complex error", context=context)

        error_str = str(error)
        assert "[CodomyrmexError] Complex error" in error_str
        assert "(Context:" in error_str
        for key, value in context.items():
            assert f"{key}={value}" in error_str


@pytest.mark.integration
class TestErrorIntegration:
    """Integration tests for error handling."""

    def test_error_logging_compatibility(self):
        """Test that errors work well with logging systems."""
        import logging

        logger = logging.getLogger("test")
        error = CodomyrmexError("Log test error", context={"module": "test"})

        # Should not raise when logging
        logger.error(str(error))
        logger.exception(error)

    def test_error_json_serialization(self):
        """Test that error dictionaries can be JSON serialized."""
        import json

        error = ConfigurationError(
            "JSON test error",
            context={"config_file": "test.yaml", "line": 10},
            error_code="CONFIG_001"
        )

        error_dict = error.to_dict()
        json_str = json.dumps(error_dict)
        parsed = json.loads(json_str)

        assert parsed == error_dict

    def test_error_message_formatting(self):
        """Test error message formatting for user display."""
        error = GitOperationError(
            "Failed to push changes",
            git_command="git push origin main",
            repository_path="/project/repo"
        )

        formatted = format_exception_chain(error)
        assert "Failed to push changes" in formatted
        assert "git_command=git push origin main" in formatted
        assert "repository_path=/project/repo" in formatted


# ==============================================================================
# Specialized Exception Tests
# ==============================================================================


@pytest.mark.unit
class TestSpecializedExceptions:
    """Tests for specialized domain exceptions not yet covered."""

    def test_cerebrum_error_hierarchy(self):
        """CerebrumError inherits from CodomyrmexError."""
        from codomyrmex.exceptions import CerebrumError
        error = CerebrumError("Cerebrum failure")
        assert isinstance(error, CodomyrmexError)
        assert "Cerebrum failure" in str(error)

    def test_case_error_inherits_cerebrum(self):
        """CaseError inherits from CerebrumError."""
        from codomyrmex.exceptions import CaseError, CerebrumError
        error = CaseError("Case problem")
        assert isinstance(error, CerebrumError)
        assert isinstance(error, CodomyrmexError)

    def test_case_not_found_error_chain(self):
        """CaseNotFoundError inherits CaseError -> CerebrumError -> CodomyrmexError."""
        from codomyrmex.exceptions import CaseNotFoundError, CaseError, CerebrumError
        error = CaseNotFoundError("Case 42 missing")
        assert isinstance(error, CaseError)
        assert isinstance(error, CerebrumError)
        assert isinstance(error, CodomyrmexError)

    def test_invalid_case_error_chain(self):
        """InvalidCaseError inherits CaseError."""
        from codomyrmex.exceptions import InvalidCaseError, CaseError
        error = InvalidCaseError("Invalid case data")
        assert isinstance(error, CaseError)

    def test_network_error_with_url_and_status(self):
        """NetworkError stores url and status_code in context."""
        from codomyrmex.exceptions import NetworkError
        error = NetworkError("Connection failed", url="https://api.example.com", status_code=503)
        assert error.context["url"] == "https://api.example.com"
        assert error.context["status_code"] == 503
        assert "url=https://api.example.com" in str(error)

    def test_network_error_without_optional_fields(self):
        """NetworkError without optional fields has minimal context."""
        from codomyrmex.exceptions import NetworkError
        error = NetworkError("Timeout")
        assert "url" not in error.context
        assert "status_code" not in error.context

    def test_validation_error_with_field_and_rule(self):
        """ValidationError stores field_name and validation_rule."""
        from codomyrmex.exceptions import ValidationError
        error = ValidationError(
            "Field invalid", field_name="email", validation_rule="must_contain_at"
        )
        assert error.context["field_name"] == "email"
        assert error.context["validation_rule"] == "must_contain_at"

    def test_simulation_error_inherits_codomyrmex(self):
        """SimulationError inherits from CodomyrmexError."""
        from codomyrmex.exceptions import SimulationError
        error = SimulationError("Simulation crashed")
        assert isinstance(error, CodomyrmexError)

    def test_deployment_error_inherits_codomyrmex(self):
        """DeploymentError inherits from CodomyrmexError."""
        from codomyrmex.exceptions import DeploymentError
        error = DeploymentError("Deploy failed")
        assert isinstance(error, CodomyrmexError)

    def test_compression_error_inherits_codomyrmex(self):
        """CompressionError inherits from CodomyrmexError."""
        from codomyrmex.exceptions import CompressionError
        error = CompressionError("Bad data")
        assert isinstance(error, CodomyrmexError)

    def test_all_exports_are_importable(self):
        """Every name in __all__ is importable from the exceptions package."""
        import codomyrmex.exceptions as exc_mod
        for name in exc_mod.__all__:
            assert hasattr(exc_mod, name), f"{name} listed in __all__ but missing"

    def test_inference_error_deep_chain(self):
        """InferenceError -> BayesianInferenceError -> CerebrumError -> CodomyrmexError."""
        from codomyrmex.exceptions import (
            InferenceError, BayesianInferenceError, CerebrumError,
        )
        error = InferenceError("Inference failed")
        assert isinstance(error, BayesianInferenceError)
        assert isinstance(error, CerebrumError)

    def test_network_structure_error_chain(self):
        """NetworkStructureError -> BayesianInferenceError."""
        from codomyrmex.exceptions import NetworkStructureError, BayesianInferenceError
        error = NetworkStructureError("Bad graph")
        assert isinstance(error, BayesianInferenceError)
