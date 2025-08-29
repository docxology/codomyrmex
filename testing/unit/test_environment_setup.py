"""Unit tests for environment_setup module."""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestEnvironmentSetup:
    """Test cases for environment setup functionality."""

    def test_env_checker_import(self, code_dir):
        """Test that we can import the env_checker module."""
        # Add code_dir to path if not already there
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.environment_setup import env_checker
            assert env_checker is not None
        except ImportError as e:
            pytest.fail(f"Failed to import env_checker: {e}")

    def test_ensure_dependencies_installed_success(self, capsys):
        """Test successful dependency check."""
        from codomyrmex.environment_setup.env_checker import ensure_dependencies_installed

        with patch('builtins.__import__') as mock_import:
            # Mock successful imports
            mock_import.side_effect = lambda name, *args, **kwargs: MagicMock()

            # Should not raise SystemExit
            ensure_dependencies_installed()

            # Check output
            captured = capsys.readouterr()
            assert "[INFO] cased/kit library found." in captured.out
            assert "[INFO] python-dotenv library found." in captured.out
            assert "[INFO] Core dependencies (kit, python-dotenv) are installed." in captured.out

    def test_ensure_dependencies_installed_missing_kit(self, capsys):
        """Test dependency check when kit is missing."""
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
            assert "[ERROR] The 'cased/kit' library is not installed" in captured.err
            assert "[INSTRUCTION] Please ensure you have set up the Python environment" in captured.err

    def test_ensure_dependencies_installed_missing_dotenv(self, capsys):
        """Test dependency check when python-dotenv is missing."""
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
            assert "[ERROR] The 'python-dotenv' library is not installed" in captured.err

    def test_check_and_setup_env_vars_file_exists(self, tmp_path, capsys):
        """Test env file check when file exists."""
        from codomyrmex.environment_setup.env_checker import check_and_setup_env_vars

        # Create a dummy .env file
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_KEY=test_value\n")

        check_and_setup_env_vars(str(tmp_path))

        captured = capsys.readouterr()
        assert f"[INFO] .env file found at '{env_file}'." in captured.out
        assert "[INFO] .env file check completed. API keys should now be loaded" not in captured.out

    def test_check_and_setup_env_vars_file_missing(self, tmp_path, capsys):
        """Test env file check when file is missing."""
        from codomyrmex.environment_setup.env_checker import check_and_setup_env_vars

        # Ensure .env file doesn't exist
        env_file = tmp_path / ".env"
        assert not env_file.exists()

        check_and_setup_env_vars(str(tmp_path))

        captured = capsys.readouterr()
        assert f"[WARN] .env file not found at '{env_file}'." in captured.out
        assert "[INSTRUCTION] To use LLM-dependent features (like code summarization and advanced docstring indexing), API keys are recommended." in captured.out
        assert "OPENAI_API_KEY=" in captured.out
        assert "ANTHROPIC_API_KEY=" in captured.out
        assert "GOOGLE_API_KEY=" in captured.out

    @patch('os.path.exists')
    @patch('dotenv.load_dotenv')
    def test_check_and_setup_env_vars_with_mocking(self, mock_load_dotenv, mock_exists, capsys):
        """Test env file check with mocked file operations."""
        from codomyrmex.environment_setup.env_checker import check_and_setup_env_vars

        # Mock file exists
        mock_exists.return_value = True

        check_and_setup_env_vars("/fake/path")

        mock_exists.assert_called_once_with("/fake/path/.env")
        mock_load_dotenv.assert_not_called()  # Since we're not actually loading in the function

        captured = capsys.readouterr()
        assert "[INFO] Checking for .env file at: /fake/path/.env" in captured.out
        assert "[INFO] .env file found at '/fake/path/.env'." in captured.out

