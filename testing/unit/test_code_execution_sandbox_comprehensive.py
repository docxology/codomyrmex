"""Comprehensive unit tests for code_execution_sandbox module."""

import pytest
import sys
import tempfile
import os
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path


class TestCodeExecutionSandboxComprehensive:
    """Comprehensive test cases for code execution sandbox functionality."""

    def test_code_executor_import(self, code_dir):
        """Test that we can import code_executor module."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.code_execution_sandbox import code_executor
            assert code_executor is not None
        except ImportError as e:
            pytest.fail(f"Failed to import code_executor: {e}")

    @patch('subprocess.run')
    def test_check_docker_available_success(self, mock_subprocess, code_dir):
        """Test check_docker_available when Docker is available."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.code_execution_sandbox.code_executor import check_docker_available

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        result = check_docker_available()
        assert result is True
        mock_subprocess.assert_called_once()

    @patch('subprocess.run')
    def test_check_docker_available_failure(self, mock_subprocess, code_dir):
        """Test check_docker_available when Docker is not available."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.code_execution_sandbox.code_executor import check_docker_available

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_subprocess.return_value = mock_result

        result = check_docker_available()
        assert result is False

    def test_validate_language_supported(self, code_dir):
        """Test validate_language with supported languages."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.code_execution_sandbox.code_executor import validate_language

        # Test supported languages
        supported_languages = ['python', 'javascript', 'java', 'cpp', 'c', 'go', 'rust']
        for lang in supported_languages:
            assert validate_language(lang) is True

    def test_validate_language_unsupported(self, code_dir):
        """Test validate_language with unsupported language."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.code_execution_sandbox.code_executor import validate_language

        result = validate_language("unsupported_lang")
        assert result is False

    def test_validate_timeout_valid(self, code_dir):
        """Test validate_timeout with valid values."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.code_execution_sandbox.code_executor import validate_timeout

        assert validate_timeout(10) == 10
        assert validate_timeout(1) == 1
        assert validate_timeout(300) == 300

    def test_validate_timeout_invalid(self, code_dir):
        """Test validate_timeout with invalid values (clamped to valid range)."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.code_execution_sandbox.code_executor import validate_timeout

        # Test that values are clamped to valid range
        assert validate_timeout(0) == 1  # MIN_TIMEOUT
        assert validate_timeout(400) == 300  # MAX_TIMEOUT
        # Note: float values are not converted to int, they are clamped as-is
        assert validate_timeout(10.5) == 10.5

    @patch('builtins.open', new_callable=MagicMock)
    @patch('tempfile.mkdtemp')
    def test_prepare_code_file(self, mock_mkdtemp, mock_open, code_dir):
        """Test prepare_code_file function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.code_execution_sandbox.code_executor import prepare_code_file

        # Mock the temporary directory creation
        mock_mkdtemp.return_value = "/tmp/codomyrmex_sandbox_12345"
        
        # Mock the file opening
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        code = "print('Hello, World!')"
        language = "python"

        file_path, filename = prepare_code_file(code, language)

        # The function creates a file with the language extension
        expected_filename = f"code.py"  # python extension is 'py'
        assert filename == expected_filename
        assert file_path == "/tmp/codomyrmex_sandbox_12345"
        mock_file.write.assert_called_once_with(code)
        mock_mkdtemp.assert_called_once_with(prefix="codomyrmex_sandbox_")

    @patch('subprocess.Popen')
    def test_run_code_in_docker_success(self, mock_popen, code_dir):
        """Test run_code_in_docker successful execution."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.code_execution_sandbox.code_executor import run_code_in_docker

        # Mock subprocess.Popen for successful execution
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("Hello, World!", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        result = run_code_in_docker(
            language="python",
            code_file_path="code.py",
            temp_dir="/tmp",
            stdin_file="stdin.txt",
            timeout=30,
            session_id="test-session-id"
        )

        assert result["stdout"] == "Hello, World!"
        assert result["exit_code"] == 0
        assert "execution_time" in result
        assert result["status"] == "success"

        mock_popen.assert_called_once()

    @patch('codomyrmex.code_execution_sandbox.code_executor.check_docker_available')
    @patch('codomyrmex.code_execution_sandbox.code_executor.validate_language')
    @patch('codomyrmex.code_execution_sandbox.code_executor.validate_timeout')
    @patch('codomyrmex.code_execution_sandbox.code_executor.validate_session_id')
    @patch('codomyrmex.code_execution_sandbox.code_executor.prepare_code_file')
    @patch('codomyrmex.code_execution_sandbox.code_executor.prepare_stdin_file')
    @patch('codomyrmex.code_execution_sandbox.code_executor.run_code_in_docker')
    @patch('codomyrmex.code_execution_sandbox.code_executor.cleanup_temp_files')
    def test_execute_code_success(self, mock_cleanup, mock_run_docker, mock_prepare_stdin,
                                mock_prepare_code, mock_validate_session, mock_validate_timeout,
                                mock_validate_lang, mock_check_docker, code_dir):
        """Test execute_code successful execution."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.code_execution_sandbox.code_executor import execute_code

        # Setup mocks
        mock_check_docker.return_value = True
        mock_validate_lang.return_value = True  # validate_language returns boolean
        mock_validate_timeout.return_value = 30
        mock_validate_session.return_value = "test-session-id"
        mock_prepare_code.return_value = ("/tmp", "code.py")  # Returns (temp_dir, relative_file_path)
        mock_prepare_stdin.return_value = "/tmp/stdin.txt"
        mock_run_docker.return_value = {
            "stdout": "Hello, World!",
            "stderr": "",
            "exit_code": 0,
            "execution_time": 0.5,
            "status": "success"
        }

        result = execute_code(
            language="python",
            code="print('Hello, World!')",
            stdin="test input",
            timeout=30,
            session_id="test-session-id"
        )

        assert result["stdout"] == "Hello, World!"
        assert result["exit_code"] == 0
        assert result["execution_time"] == 0.5
        assert result["status"] == "success"

        # Verify all validation functions were called
        mock_check_docker.assert_called_once()
        mock_validate_lang.assert_called_once_with("python")
        mock_validate_timeout.assert_called_once_with(30)
        mock_validate_session.assert_called_once_with("test-session-id")
        mock_prepare_code.assert_called_once_with("print('Hello, World!')", "python")
        mock_prepare_stdin.assert_called_once_with("test input", "/tmp")
        # run_code_in_docker should be called with the correct parameters
        mock_run_docker.assert_called_once()
        mock_cleanup.assert_called_with("/tmp")

    def test_supported_languages(self, code_dir):
        """Test that all supported languages are properly configured."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.code_execution_sandbox import code_executor

        # Check that language configurations exist
        assert hasattr(code_executor, 'SUPPORTED_LANGUAGES')

        supported_langs = ['python', 'javascript', 'bash']
        for lang in supported_langs:
            assert lang in code_executor.SUPPORTED_LANGUAGES
            config = code_executor.SUPPORTED_LANGUAGES[lang]
            assert 'image' in config
            assert 'extension' in config
            assert 'command' in config
            assert 'timeout_factor' in config

    def test_constants_defined(self, code_dir):
        """Test that all required constants are defined."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.code_execution_sandbox import code_executor

        assert hasattr(code_executor, 'DEFAULT_TIMEOUT')
        assert hasattr(code_executor, 'MAX_TIMEOUT')
        assert hasattr(code_executor, 'MIN_TIMEOUT')

        assert code_executor.DEFAULT_TIMEOUT == 30
        assert code_executor.MAX_TIMEOUT == 300
        assert code_executor.MIN_TIMEOUT == 1
