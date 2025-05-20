"""
Unit tests for the code_executor module.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to the sys.path to allow importing from the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from code_execution_sandbox.code_executor import (
    validate_language,
    validate_timeout,
    validate_session_id,
    check_docker_available,
    execute_code,
    SUPPORTED_LANGUAGES
)

class TestValidators(unittest.TestCase):
    """Tests for validator functions in code_executor.py."""
    
    def test_validate_language(self):
        """Test language validation."""
        # Test valid languages
        for language in SUPPORTED_LANGUAGES.keys():
            self.assertTrue(validate_language(language))
        
        # Test invalid languages
        self.assertFalse(validate_language("unsupported_language"))
        self.assertFalse(validate_language(""))
        self.assertFalse(validate_language(None))
    
    def test_validate_timeout(self):
        """Test timeout validation and normalization."""
        # Test default timeout when None is provided
        self.assertEqual(validate_timeout(None), 30)  # Default timeout
        
        # Test valid timeouts
        self.assertEqual(validate_timeout(10), 10)
        self.assertEqual(validate_timeout(60), 60)
        
        # Test timeout below minimum
        self.assertEqual(validate_timeout(0), 1)  # Should be normalized to MIN_TIMEOUT
        
        # Test timeout above maximum
        self.assertEqual(validate_timeout(1000), 300)  # Should be normalized to MAX_TIMEOUT
    
    def test_validate_session_id(self):
        """Test session ID validation."""
        # Test valid session IDs
        self.assertEqual(validate_session_id("user123"), "user123")
        self.assertEqual(validate_session_id("user-123_session"), "user-123_session")
        
        # Test None session ID
        self.assertIsNone(validate_session_id(None))
        
        # Test invalid session IDs
        self.assertIsNone(validate_session_id(""))
        self.assertIsNone(validate_session_id("invalid/session!id"))
        self.assertIsNone(validate_session_id("a" * 65))  # Too long
        self.assertIsNone(validate_session_id(123))  # Not a string


class TestCheckDockerAvailable(unittest.TestCase):
    """Tests for check_docker_available function."""
    
    @patch('subprocess.run')
    def test_docker_available(self, mock_run):
        """Test when Docker is available."""
        # Mock successful subprocess run
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        self.assertTrue(check_docker_available())
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_docker_not_available(self, mock_run):
        """Test when Docker is not available."""
        # Mock failed subprocess run
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_run.return_value = mock_process
        
        self.assertFalse(check_docker_available())
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_docker_command_error(self, mock_run):
        """Test when Docker command raises an error."""
        # Mock subprocess raising an exception
        mock_run.side_effect = FileNotFoundError("docker command not found")
        
        self.assertFalse(check_docker_available())
        mock_run.assert_called_once()


class TestExecuteCode(unittest.TestCase):
    """Tests for the execute_code function."""
    
    @patch('code_execution_sandbox.code_executor.check_docker_available')
    def test_docker_not_available(self, mock_check_docker):
        """Test execute_code when Docker is not available."""
        mock_check_docker.return_value = False
        
        result = execute_code("python", "print('Hello, World!')")
        
        self.assertEqual(result["status"], "setup_error")
        self.assertEqual(result["exit_code"], -1)
        self.assertIn("Docker is not available", result["error_message"])
        self.assertEqual(result["stdout"], "")
    
    def test_unsupported_language(self):
        """Test execute_code with an unsupported language."""
        result = execute_code("unsupported_language", "print('Hello, World!')")
        
        self.assertEqual(result["status"], "setup_error")
        self.assertEqual(result["exit_code"], -1)
        self.assertIn("not supported", result["error_message"])
        self.assertIn("unsupported_language", result["stderr"])
    
    def test_invalid_code(self):
        """Test execute_code with invalid code."""
        # Empty code
        result = execute_code("python", "")
        self.assertEqual(result["status"], "setup_error")
        self.assertIn("Code must be a non-empty string", result["error_message"])
        
        # None code
        result = execute_code("python", None)
        self.assertEqual(result["status"], "setup_error")
        self.assertIn("Code must be a non-empty string", result["error_message"])
    
    @patch('code_execution_sandbox.code_executor.check_docker_available')
    @patch('code_execution_sandbox.code_executor.prepare_code_file')
    @patch('code_execution_sandbox.code_executor.prepare_stdin_file')
    @patch('code_execution_sandbox.code_executor.run_code_in_docker')
    @patch('code_execution_sandbox.code_executor.cleanup_temp_files')
    def test_successful_execution(self, mock_cleanup, mock_run, mock_stdin, mock_code_file, mock_check_docker):
        """Test successful code execution."""
        # Mock successful Docker check
        mock_check_docker.return_value = True
        
        # Mock file preparation
        mock_code_file.return_value = ("/tmp/test_dir", "code.py")
        mock_stdin.return_value = "/tmp/test_dir/stdin.txt"
        
        # Mock successful execution
        expected_result = {
            "stdout": "Hello, World!",
            "stderr": "",
            "exit_code": 0,
            "execution_time": 0.5,
            "status": "success",
            "error_message": None
        }
        mock_run.return_value = expected_result
        
        # Execute code
        result = execute_code(
            language="python",
            code="print('Hello, World!')",
            stdin="test input",
            timeout=10
        )
        
        # Verify the result
        self.assertEqual(result, expected_result)
        
        # Verify that all the mocked functions were called correctly
        mock_check_docker.assert_called_once()
        mock_code_file.assert_called_once_with("print('Hello, World!')", "python")
        mock_stdin.assert_called_once_with("test input", "/tmp/test_dir")
        mock_run.assert_called_once_with(
            language="python",
            code_file_path="code.py",
            temp_dir="/tmp/test_dir",
            stdin_file="/tmp/test_dir/stdin.txt",
            timeout=10,
            session_id=None
        )
        mock_cleanup.assert_called_once_with("/tmp/test_dir")
    
    @patch('code_execution_sandbox.code_executor.check_docker_available')
    @patch('code_execution_sandbox.code_executor.prepare_code_file')
    @patch('code_execution_sandbox.code_executor.run_code_in_docker')
    @patch('code_execution_sandbox.code_executor.cleanup_temp_files')
    def test_execution_without_stdin(self, mock_cleanup, mock_run, mock_code_file, mock_check_docker):
        """Test code execution without stdin."""
        # Mock successful Docker check
        mock_check_docker.return_value = True
        
        # Mock file preparation
        mock_code_file.return_value = ("/tmp/test_dir", "code.py")
        
        # Mock successful execution
        expected_result = {
            "stdout": "Hello, World!",
            "stderr": "",
            "exit_code": 0,
            "execution_time": 0.5,
            "status": "success",
            "error_message": None
        }
        mock_run.return_value = expected_result
        
        # Execute code without stdin
        result = execute_code(
            language="python",
            code="print('Hello, World!')",
            timeout=10
        )
        
        # Verify the result
        self.assertEqual(result, expected_result)
        
        # Verify that stdin was not prepared
        mock_run.assert_called_once_with(
            language="python",
            code_file_path="code.py",
            temp_dir="/tmp/test_dir",
            stdin_file=None,
            timeout=10,
            session_id=None
        )
    
    @patch('code_execution_sandbox.code_executor.check_docker_available')
    @patch('code_execution_sandbox.code_executor.prepare_code_file')
    @patch('code_execution_sandbox.code_executor.cleanup_temp_files')
    def test_exception_handling(self, mock_cleanup, mock_code_file, mock_check_docker):
        """Test handling of unexpected exceptions during execution."""
        # Mock successful Docker check
        mock_check_docker.return_value = True
        
        # Mock file preparation that raises an exception
        mock_code_file.side_effect = Exception("Test exception")
        
        # Execute code
        result = execute_code(
            language="python",
            code="print('Hello, World!')"
        )
        
        # Verify error result
        self.assertEqual(result["status"], "setup_error")
        self.assertEqual(result["exit_code"], -1)
        self.assertIn("Test exception", result["error_message"])
        self.assertEqual(result["stdout"], "")
        self.assertIn("Internal error", result["stderr"])
        
        # Ensure cleanup was not called (no temp dir created)
        mock_cleanup.assert_not_called()


if __name__ == '__main__':
    unittest.main() 