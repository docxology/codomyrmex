"""Comprehensive unit tests for code.execution and code.sandbox modules."""

import sys

# Removed mock imports to follow TDD principle: no mock methods, always do real data analysis
from pathlib import Path

import pytest


@pytest.mark.unit
class TestCodeExecutionSandboxComprehensive:
    """Comprehensive test cases for code execution sandbox functionality."""

    def test_code_executor_import(self, code_dir):
        """Test that we can import code_executor module."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.coding.execution import executor
            assert executor is not None
        except ImportError as e:
            pytest.fail(f"Failed to import executor: {e}")

    def test_check_docker_available_real(self, code_dir, real_docker_available):
        """Test check_docker_available with real Docker check."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.sandbox.container import check_docker_available

        result = check_docker_available()
        assert isinstance(result, bool)
        # Result should match actual Docker availability
        assert result == real_docker_available

    def test_validate_language_supported(self, code_dir):
        """Test validate_language with supported languages."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.execution.language_support import validate_language

        # Test supported languages
        supported_languages = ['python', 'javascript', 'java', 'cpp', 'c', 'go', 'rust']
        for lang in supported_languages:
            assert validate_language(lang) is True

    def test_validate_language_unsupported(self, code_dir):
        """Test validate_language with unsupported language."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.execution.language_support import validate_language

        result = validate_language("unsupported_lang")
        assert result is False

    def test_validate_timeout_valid(self, code_dir):
        """Test validate_timeout with valid values."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.execution.executor import validate_timeout

        assert validate_timeout(10) == 10
        assert validate_timeout(1) == 1
        assert validate_timeout(300) == 300

    def test_validate_timeout_invalid(self, code_dir):
        """Test validate_timeout with invalid values (clamped to valid range)."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.execution.executor import validate_timeout

        # Test that values are clamped to valid range
        assert validate_timeout(0) == 1  # MIN_TIMEOUT
        assert validate_timeout(400) == 300  # MAX_TIMEOUT
        # Note: float values are not converted to int, they are clamped as-is
        assert validate_timeout(10.5) == 10.5

    def test_prepare_code_file(self, code_dir, tmp_path):
        """Test prepare_code_file function with real file operations."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.execution.executor import prepare_code_file

        code = "print('Hello, World!')"
        language = "python"

        temp_dir, code_file_path = prepare_code_file(code, language)

        # Verify result structure
        assert isinstance(temp_dir, str)
        assert isinstance(code_file_path, str)

        # Verify file was actually created
        file_path = Path(temp_dir) / code_file_path
        assert file_path.exists()
        assert file_path.read_text() == code

    def test_run_code_in_docker_success(self, code_dir, real_docker_available, tmp_path):
        """Test run_code_in_docker successful execution with real Docker."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        if not real_docker_available:
            pytest.skip("Docker not available - install Docker to run this test")

        from codomyrmex.coding.sandbox.container import run_code_in_docker

        # Create real code file
        code_file = tmp_path / "code.py"
        code_file.write_text("print('Hello, World!')")

        # Create a code file in the temp directory
        code_file_rel = "code.py"
        code_file_abs = tmp_path / code_file_rel
        code_file_abs.write_text("print('Hello, World!')")

        result = run_code_in_docker(
            language="python",
            code_file_path=code_file_rel,
            temp_dir=str(tmp_path),
            stdin_file=None,
            timeout=10,  # Short timeout for testing
            session_id="test-session-id"
        )

        assert isinstance(result, dict)
        assert "stdout" in result or "stderr" in result
        assert "exit_code" in result
        assert "execution_time" in result
        assert "status" in result

    def test_execute_code_success(self, code_dir, real_docker_available):
        """Test execute_code successful execution with real implementation."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        if not real_docker_available:
            pytest.skip("Docker not available - install Docker to run this test")

        from codomyrmex.coding.execution.executor import execute_code

        result = execute_code(
            language="python",
            code="print('Hello, World!')",
            stdin=None,
            timeout=10,  # Short timeout for testing
            session_id="test-session-id"
        )

        assert isinstance(result, dict)
        assert "stdout" in result or "stderr" in result
        assert "exit_code" in result
        assert "execution_time" in result
        assert "status" in result

        # If execution succeeded with exit_code 0, verify output
        if result.get("status") == "success" and result.get("exit_code") == 0:
            assert "Hello, World!" in result.get("stdout", "")

    def test_supported_languages(self, code_dir):
        """Test that all supported languages are properly configured."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.execution.language_support import SUPPORTED_LANGUAGES

        # Check that language configurations exist
        assert SUPPORTED_LANGUAGES is not None

        supported_langs = ['python', 'javascript', 'bash']
        for lang in supported_langs:
            assert lang in SUPPORTED_LANGUAGES
            config = SUPPORTED_LANGUAGES[lang]
            assert 'image' in config
            assert 'extension' in config
            assert 'command' in config
            assert 'timeout_factor' in config

    def test_constants_defined(self, code_dir):
        """Test that all required constants are defined."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.execution.executor import (
            DEFAULT_TIMEOUT,
            MAX_TIMEOUT,
            MIN_TIMEOUT,
        )

        assert DEFAULT_TIMEOUT == 30
        assert MAX_TIMEOUT == 300
        assert MIN_TIMEOUT == 1
