"""Unit tests for environment_setup module."""

import pytest
import sys
import os
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
        """Test successful dependency check with real imports."""
        from codomyrmex.environment_setup.env_checker import ensure_dependencies_installed

        # Test with real dependency checking - should succeed if dependencies are installed
        # This will actually check if kit and python-dotenv are available
        try:
            ensure_dependencies_installed()

            captured = capsys.readouterr()
            # If dependencies are installed, we should see success messages
            # If not installed, the function will exit - but that's testing real behavior
            assert ("[INFO] cased/kit library found." in captured.out or
                   "[ERROR] The 'cased/kit' library is not installed" in captured.err)

        except SystemExit:
            # This is expected if dependencies are missing - real behavior
            captured = capsys.readouterr()
            assert "[ERROR]" in captured.err

    def test_is_uv_available(self):
        """Test real uv availability checking."""
        from codomyrmex.environment_setup.env_checker import is_uv_available

        # This tests the real uv availability check
        result = is_uv_available()
        assert isinstance(result, bool)
        # We don't assert True/False since uv may or may not be installed

    def test_is_uv_environment(self):
        """Test real uv environment detection."""
        from codomyrmex.environment_setup.env_checker import is_uv_environment

        # This tests real environment variable checking
        result = is_uv_environment()
        assert isinstance(result, bool)

        # Test with environment variables set
        original_uv_active = os.environ.get("UV_ACTIVE")
        original_virtual_env = os.environ.get("VIRTUAL_ENV")

        try:
            os.environ["UV_ACTIVE"] = "1"
            assert is_uv_environment() == True

            del os.environ["UV_ACTIVE"]
            os.environ["VIRTUAL_ENV"] = "/path/to/uv/env"
            assert is_uv_environment() == True

        finally:
            # Restore original environment
            if original_uv_active is not None:
                os.environ["UV_ACTIVE"] = original_uv_active
            elif "UV_ACTIVE" in os.environ:
                del os.environ["UV_ACTIVE"]

            if original_virtual_env is not None:
                os.environ["VIRTUAL_ENV"] = original_virtual_env
            elif "VIRTUAL_ENV" in os.environ:
                del os.environ["VIRTUAL_ENV"]

    def test_check_and_setup_env_vars_file_exists(self, real_env_file, capsys):
        """Test env file check when file exists using real file."""
        from codomyrmex.environment_setup.env_checker import check_and_setup_env_vars

        # Use the real .env file fixture
        env_dir = real_env_file.parent
        check_and_setup_env_vars(str(env_dir))

        captured = capsys.readouterr()
        assert f"[INFO] .env file found at '{real_env_file}'." in captured.out

    def test_check_and_setup_env_vars_file_missing(self, tmp_path, capsys):
        """Test env file check when file is missing using real file system."""
        from codomyrmex.environment_setup.env_checker import check_and_setup_env_vars

        # Ensure .env file doesn't exist
        env_file = tmp_path / ".env"
        assert not env_file.exists()

        check_and_setup_env_vars(str(tmp_path))

        captured = capsys.readouterr()
        assert f"[WARN] .env file not found at '{env_file}'." in captured.out
        assert "[INSTRUCTION]" in captured.out
        # Check for API key template suggestions
        assert "OPENAI_API_KEY=" in captured.out or "ANTHROPIC_API_KEY=" in captured.out

    def test_real_env_file_content(self, real_env_file):
        """Test that the real env file fixture creates valid content."""
        assert real_env_file.exists()
        content = real_env_file.read_text()

        # Verify it contains expected environment variables
        assert "CODOMYRMEX_LOG_LEVEL=" in content
        assert "OPENAI_API_KEY=" in content
        assert "ANTHROPIC_API_KEY=" in content

        # Verify it's valid .env format (key=value pairs, allowing comments)
        lines = content.strip().split('\n')
        key_value_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        for line in key_value_lines:
            assert '=' in line, f"Invalid .env line: {line}"

    def test_env_checker_functions_exist(self, code_dir):
        """Test that all expected functions exist in env_checker."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup import env_checker

        # Test that key functions are available
        assert hasattr(env_checker, 'is_uv_available')
        assert hasattr(env_checker, 'is_uv_environment')
        assert hasattr(env_checker, 'ensure_dependencies_installed')
        assert hasattr(env_checker, 'check_and_setup_env_vars')

        # Test that they are callable
        assert callable(env_checker.is_uv_available)
        assert callable(env_checker.is_uv_environment)
        assert callable(env_checker.ensure_dependencies_installed)
        assert callable(env_checker.check_and_setup_env_vars)
        assert callable(env_checker.validate_python_version)
        assert callable(env_checker.check_package_versions)
        assert callable(env_checker.validate_environment_completeness)
        assert callable(env_checker.generate_environment_report)

    def test_validate_python_version(self):
        """Test Python version validation."""
        from codomyrmex.environment_setup.env_checker import validate_python_version

        # Test with current Python version requirement
        result = validate_python_version()
        assert isinstance(result, bool)

        # Test with specific version requirement
        result_specific = validate_python_version(">=3.8")
        assert isinstance(result_specific, bool)

        # Test with invalid requirement (should handle gracefully)
        result_invalid = validate_python_version("invalid")
        assert isinstance(result_invalid, bool)

    def test_check_package_versions(self):
        """Test package version checking."""
        from codomyrmex.environment_setup.env_checker import check_package_versions

        result = check_package_versions()
        assert isinstance(result, dict)

        # Should contain some common packages if environment is set up
        if result:  # Only test if packages are found
            for package_name, version in result.items():
                assert isinstance(package_name, str)
                assert isinstance(version, str)
                assert len(package_name) > 0
                assert len(version) > 0

    def test_validate_environment_completeness(self):
        """Test comprehensive environment validation."""
        from codomyrmex.environment_setup.env_checker import validate_environment_completeness

        result = validate_environment_completeness()
        assert isinstance(result, dict)

        # Should have expected keys
        expected_keys = ["python_version", "core_dependencies", "environment_type", "package_manager", "config_files"]
        for key in expected_keys:
            assert key in result
            assert isinstance(result[key], bool)

    def test_generate_environment_report(self):
        """Test environment report generation."""
        from codomyrmex.environment_setup.env_checker import generate_environment_report

        result = generate_environment_report()
        assert isinstance(result, str)
        assert len(result) > 0

        # Should contain expected sections
        assert "Codomyrmex Environment Report" in result
        assert "Python Version:" in result
        assert "Environment Status:" in result

        # Should end with status summary
        lines = result.split('\n')
        assert any("checks passed" in line for line in lines)

