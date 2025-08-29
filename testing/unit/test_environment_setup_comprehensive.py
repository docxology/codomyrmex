"""Comprehensive unit tests for environment_setup module."""

import pytest
import sys
import os
import subprocess
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestEnvironmentSetupComprehensive:
    """Comprehensive test cases for environment setup functionality."""

    def test_environment_setup_import(self, code_dir):
        """Test that we can import environment_setup module."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.environment_setup import env_checker
            assert env_checker is not None
        except ImportError as e:
            pytest.fail(f"Failed to import env_checker: {e}")

    @patch('subprocess.run')
    def test_is_uv_available_success(self, mock_subprocess, code_dir):
        """Test is_uv_available when uv is available."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import is_uv_available

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        result = is_uv_available()
        assert result is True
        mock_subprocess.assert_called_once_with(['uv', '--version'], capture_output=True, check=True)

    @patch('subprocess.run')
    def test_is_uv_available_not_found(self, mock_subprocess, code_dir):
        """Test is_uv_available when uv is not found."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import is_uv_available

        mock_subprocess.side_effect = FileNotFoundError("uv command not found")

        result = is_uv_available()
        assert result is False

    @patch('subprocess.run')
    def test_is_uv_available_command_failed(self, mock_subprocess, code_dir):
        """Test is_uv_available when uv command fails."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import is_uv_available

        mock_subprocess.side_effect = subprocess.CalledProcessError(1, 'uv')

        result = is_uv_available()
        assert result is False

    @patch.dict(os.environ, {"UV_ACTIVE": "1"})
    def test_is_uv_environment_active(self, code_dir):
        """Test is_uv_environment when UV_ACTIVE is set."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import is_uv_environment

        result = is_uv_environment()
        assert result is True

    @patch.dict(os.environ, {"VIRTUAL_ENV": "/path/to/uv/env"})
    def test_is_uv_environment_virtual_env_with_uv(self, code_dir):
        """Test is_uv_environment when VIRTUAL_ENV contains 'uv'."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import is_uv_environment

        result = is_uv_environment()
        assert result is True

    @patch.dict(os.environ, {"VIRTUAL_ENV": "/path/to/normal/env"}, clear=True)
    def test_is_uv_environment_normal_virtual_env(self, code_dir):
        """Test is_uv_environment with normal virtual environment."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import is_uv_environment

        result = is_uv_environment()
        assert result is False

    @patch.dict(os.environ, {}, clear=True)
    def test_is_uv_environment_no_env(self, code_dir):
        """Test is_uv_environment with no environment variables."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import is_uv_environment

        result = is_uv_environment()
        assert result is False

    def test_ensure_dependencies_installed_both_available(self, code_dir, capsys):
        """Test ensure_dependencies_installed when both dependencies are available."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import ensure_dependencies_installed

        with patch.dict('sys.modules', {
            'kit': MagicMock(),
            'dotenv': MagicMock()
        }):
            result = ensure_dependencies_installed()

            captured = capsys.readouterr()
            assert "[INFO] cased/kit library found." in captured.out
            assert "[INFO] python-dotenv library found." in captured.out
            assert "[INFO] Core dependencies (kit, python-dotenv) are installed." in captured.out

    def test_ensure_dependencies_installed_kit_missing(self, code_dir, capsys):
        """Test ensure_dependencies_installed when kit is missing."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import ensure_dependencies_installed

        def mock_import(name, *args, **kwargs):
            if name == 'kit':
                raise ImportError("No module named 'kit'")
            return MagicMock()

        with patch('builtins.__import__', side_effect=mock_import):
            with pytest.raises(SystemExit) as exc_info:
                ensure_dependencies_installed()
            
            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "[ERROR] The 'cased/kit' library is not installed or not found." in captured.err

    def test_ensure_dependencies_installed_dotenv_missing(self, code_dir, capsys):
        """Test ensure_dependencies_installed when python-dotenv is missing."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import ensure_dependencies_installed

        def mock_import(name, *args, **kwargs):
            if name == 'dotenv':
                raise ImportError("No module named 'dotenv'")
            return MagicMock()

        with patch('builtins.__import__', side_effect=mock_import):
            with pytest.raises(SystemExit) as exc_info:
                ensure_dependencies_installed()
            
            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "[ERROR] The 'python-dotenv' library is not installed or not found." in captured.err
            assert "This is needed for loading API keys from a .env file." in captured.err

    def test_ensure_dependencies_installed_both_missing(self, code_dir, capsys):
        """Test ensure_dependencies_installed when both dependencies are missing."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import ensure_dependencies_installed

        def mock_import(name, *args, **kwargs):
            if name in ['kit', 'dotenv']:
                raise ImportError(f"No module named '{name}'")
            return MagicMock()

        with patch('builtins.__import__', side_effect=mock_import):
            with pytest.raises(SystemExit) as exc_info:
                ensure_dependencies_installed()
            
            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "[ERROR] The 'cased/kit' library is not installed or not found." in captured.err
            assert "[ERROR] The 'python-dotenv' library is not installed or not found." in captured.err
            assert "[INSTRUCTION] Please ensure you have set up the Python environment" in captured.err

    def test_check_and_setup_env_vars_file_exists(self, code_dir, capsys, tmp_path):
        """Test check_and_setup_env_vars when .env file exists."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import check_and_setup_env_vars

        # Create a dummy .env file
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_KEY=test_value\n")

        check_and_setup_env_vars(str(tmp_path))

        captured = capsys.readouterr()
        assert f"[INFO] Checking for .env file at: {env_file}" in captured.out
        assert f"[INFO] .env file found at '{env_file}'." in captured.out
        assert "Make sure it contains your API keys if you plan to use LLM features" in captured.out

    def test_check_and_setup_env_vars_file_missing(self, code_dir, capsys, tmp_path):
        """Test check_and_setup_env_vars when .env file is missing."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import check_and_setup_env_vars

        # Ensure .env file doesn't exist
        env_file_path = tmp_path / ".env"
        assert not env_file_path.exists()

        check_and_setup_env_vars(str(tmp_path))

        captured = capsys.readouterr()
        assert f"[INFO] Checking for .env file at: {env_file_path}" in captured.out
        assert f"[WARN] .env file not found at '{env_file_path}'." in captured.out
        assert "[INSTRUCTION] To use LLM-dependent features" in captured.out
        assert "OPENAI_API_KEY=" in captured.out
        assert "ANTHROPIC_API_KEY=" in captured.out
        assert "GOOGLE_API_KEY=" in captured.out

    def test_env_checker_module_structure(self, code_dir):
        """Test that env_checker has expected structure."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup import env_checker

        # Check that all expected functions exist
        expected_functions = [
            'is_uv_available',
            'is_uv_environment',
            'ensure_dependencies_installed',
            'check_and_setup_env_vars'
        ]

        for func_name in expected_functions:
            assert hasattr(env_checker, func_name), f"Missing function: {func_name}"
            assert callable(getattr(env_checker, func_name)), f"{func_name} is not callable"

    def test_env_checker_constants(self, code_dir):
        """Test that env_checker has expected constants."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup import env_checker

        # Check that _script_dir is defined
        assert hasattr(env_checker, '_script_dir')
        assert isinstance(env_checker._script_dir, str)

    def test_ensure_dependencies_installed_error_handling(self, code_dir, capsys):
        """Test ensure_dependencies_installed error handling."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import ensure_dependencies_installed

        def mock_import(name, *args, **kwargs):
            if name == 'kit':
                raise Exception("Unexpected error")
            return MagicMock()

        with patch('builtins.__import__', side_effect=mock_import):
            with pytest.raises(SystemExit) as exc_info:
                ensure_dependencies_installed()
            
            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            # Should still check dotenv even if kit fails
            assert "[INFO] python-dotenv library found." in captured.out
            assert "Unexpected error while checking 'cased/kit' library: Unexpected error" in captured.err

    @patch('os.path.exists')
    @patch('os.path.join')
    def test_check_and_setup_env_vars_path_handling(self, mock_join, mock_exists, code_dir, capsys):
        """Test check_and_setup_env_vars path handling."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import check_and_setup_env_vars

        mock_join.return_value = "/mock/path/.env"
        mock_exists.return_value = True

        check_and_setup_env_vars("/mock/repo/root")

        captured = capsys.readouterr()
        assert "[INFO] Checking for .env file at: /mock/path/.env" in captured.out
        assert "[INFO] .env file found at '/mock/path/.env'." in captured.out

    def test_is_uv_available_exception_handling(self, code_dir):
        """Test is_uv_available exception handling."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import is_uv_available

        with patch('subprocess.run', side_effect=Exception("Unexpected error")):
            result = is_uv_available()
            assert result is False

    def test_is_uv_environment_edge_cases(self, code_dir):
        """Test is_uv_environment with edge cases."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import is_uv_environment

        # Test with empty UV_ACTIVE
        with patch.dict(os.environ, {"UV_ACTIVE": ""}):
            result = is_uv_environment()
            assert result is False

        # Test with VIRTUAL_ENV but no 'uv' in path
        with patch.dict(os.environ, {"VIRTUAL_ENV": "/path/to/venv"}):
            result = is_uv_environment()
            assert result is False

    def test_ensure_dependencies_installed_instruction_format(self, code_dir, capsys):
        """Test that ensure_dependencies_installed provides properly formatted instructions."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import ensure_dependencies_installed

        def mock_import(name, *args, **kwargs):
            if name in ['kit', 'dotenv']:
                raise ImportError(f"No module named '{name}'")
            return MagicMock()

        with patch('builtins.__import__', side_effect=mock_import):
            with pytest.raises(SystemExit) as exc_info:
                ensure_dependencies_installed()
            
            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            # Check that instructions include key sections
            assert "[INSTRUCTION] Please ensure you have set up the Python environment" in captured.err
            assert "To set up/update the environment:" in captured.err
            assert "[OPTION 1] Using uv" in captured.err
            assert "[OPTION 2] Using pip" in captured.err

    def test_check_and_setup_env_vars_instruction_format(self, code_dir, capsys, tmp_path):
        """Test that check_and_setup_env_vars provides properly formatted instructions."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import check_and_setup_env_vars

        check_and_setup_env_vars(str(tmp_path))

        captured = capsys.readouterr()
        # Check that instructions include key sections
        assert "[INSTRUCTION] To use LLM-dependent features" in captured.out
        assert "OPENAI_API_KEY=" in captured.out
        assert "ANTHROPIC_API_KEY=" in captured.out
        assert "GOOGLE_API_KEY=" in captured.out
        assert "------------- .env file example -------------" in captured.out

    def test_module_integration_with_logging(self, code_dir):
        """Test that env_checker integrates properly with logging system."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup import env_checker

        # Test that the module can access logging functions
        assert hasattr(env_checker, 'sys')
        assert hasattr(env_checker, 'os')
        assert hasattr(env_checker, 'subprocess')

    def test_env_checker_standalone_execution(self, code_dir, capsys):
        """Test env_checker standalone execution."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        # This would normally be tested by running the module directly,
        # but we can test the functions it calls
        from codomyrmex.environment_setup.env_checker import ensure_dependencies_installed, check_and_setup_env_vars

        # Test that the functions can be called without errors
        ensure_dependencies_installed()
        check_and_setup_env_vars("/tmp")

        captured = capsys.readouterr()
        # Should have some output
        assert len(captured.out) > 0 or len(captured.err) > 0
