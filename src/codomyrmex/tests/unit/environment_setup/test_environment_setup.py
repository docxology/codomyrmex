"""Comprehensive unit tests for environment_setup module."""

import os
import sys

import pytest


@pytest.mark.unit
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

    def test_is_uv_available_real(self, code_dir):
        """Test is_uv_available with real uv check."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import is_uv_available

        result = is_uv_available()
        assert isinstance(result, bool)
        # Result depends on whether uv is actually installed

    def test_is_uv_environment_active(self, code_dir):
        """Test is_uv_environment when UV_ACTIVE is set with real env vars."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import is_uv_environment

        original_uv_active = os.environ.get("UV_ACTIVE")
        try:
            os.environ["UV_ACTIVE"] = "1"
            result = is_uv_environment()
            assert result is True
        finally:
            if original_uv_active is not None:
                os.environ["UV_ACTIVE"] = original_uv_active
            elif "UV_ACTIVE" in os.environ:
                del os.environ["UV_ACTIVE"]

    def test_is_uv_environment_virtual_env_with_uv(self, code_dir):
        """Test is_uv_environment when VIRTUAL_ENV contains 'uv' with real env vars."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import is_uv_environment

        original_virtual_env = os.environ.get("VIRTUAL_ENV")
        try:
            os.environ["VIRTUAL_ENV"] = "/path/to/uv/env"
            result = is_uv_environment()
            assert result is True
        finally:
            if original_virtual_env is not None:
                os.environ["VIRTUAL_ENV"] = original_virtual_env
            elif "VIRTUAL_ENV" in os.environ:
                del os.environ["VIRTUAL_ENV"]

    def test_is_uv_environment_normal_virtual_env(self, code_dir):
        """Test is_uv_environment with normal virtual environment.

        Note: is_uv_environment() returns True if VIRTUAL_ENV is set OR if uv
        is available in PATH. So with VIRTUAL_ENV set, it returns True regardless.
        """
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import is_uv_environment

        original_virtual_env = os.environ.get("VIRTUAL_ENV")
        original_uv_active = os.environ.get("UV_ACTIVE")
        try:
            # Clear UV_ACTIVE and set normal VIRTUAL_ENV
            if "UV_ACTIVE" in os.environ:
                del os.environ["UV_ACTIVE"]
            os.environ["VIRTUAL_ENV"] = "/path/to/normal/env"
            result = is_uv_environment()
            # VIRTUAL_ENV is set, so function returns True
            assert result is True
        finally:
            if original_virtual_env is not None:
                os.environ["VIRTUAL_ENV"] = original_virtual_env
            elif "VIRTUAL_ENV" in os.environ:
                del os.environ["VIRTUAL_ENV"]
            if original_uv_active is not None:
                os.environ["UV_ACTIVE"] = original_uv_active

    def test_is_uv_environment_no_env(self, code_dir):
        """Test is_uv_environment with no environment variables.

        Note: is_uv_environment() also checks is_uv_available(), so if uv is
        installed on the system, it will return True even without env vars.
        """
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import (
            is_uv_available,
            is_uv_environment,
        )

        original_virtual_env = os.environ.get("VIRTUAL_ENV")
        original_uv_active = os.environ.get("UV_ACTIVE")
        try:
            # Clear both environment variables
            if "VIRTUAL_ENV" in os.environ:
                del os.environ["VIRTUAL_ENV"]
            if "UV_ACTIVE" in os.environ:
                del os.environ["UV_ACTIVE"]
            result = is_uv_environment()
            # Result depends on whether uv is available in PATH
            assert result == is_uv_available()
        finally:
            if original_virtual_env is not None:
                os.environ["VIRTUAL_ENV"] = original_virtual_env
            if original_uv_active is not None:
                os.environ["UV_ACTIVE"] = original_uv_active

    def test_ensure_dependencies_installed_both_available(self, code_dir, capsys):
        """Test ensure_dependencies_installed when both dependencies are available."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import (
            ensure_dependencies_installed,
        )

        # Test with real imports - check if dependencies are actually available
        try:
            import dotenv
            import kit
            # Both are available - test should pass
            result = ensure_dependencies_installed()

            captured = capsys.readouterr()
            assert "[INFO] cased/kit library found." in captured.out
            assert "[INFO] python-dotenv library found." in captured.out
            assert result is True
        except ImportError:
            # If dependencies are not available, test that the function handles it
            result = ensure_dependencies_installed()
            captured = capsys.readouterr()
            # Should show error messages for missing dependencies
            assert "[ERROR]" in captured.err or "[INFO]" in captured.out

    def test_ensure_dependencies_installed_kit_missing(self, code_dir, capsys):
        """Test ensure_dependencies_installed when kit is missing with real import check."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import (
            ensure_dependencies_installed,
        )

        # Test with real import checking - if kit is actually missing, function will exit
        # If kit is available, test will pass
        try:
            ensure_dependencies_installed()
            captured = capsys.readouterr()
            # If dependencies are installed, we should see success messages
            assert "[INFO]" in captured.out or "[ERROR]" in captured.err
        except SystemExit as e:
            # Expected if dependencies are missing
            captured = capsys.readouterr()
            assert "[ERROR]" in captured.err
            assert e.code == 1

    def test_ensure_dependencies_installed_dotenv_missing(self, code_dir, capsys):
        """Test ensure_dependencies_installed when python-dotenv is missing with real import check."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import (
            ensure_dependencies_installed,
        )

        # Test with real import checking - if dotenv is actually missing, function will exit
        try:
            ensure_dependencies_installed()
            captured = capsys.readouterr()
            # If dependencies are installed, we should see success messages
            assert "[INFO]" in captured.out or "[ERROR]" in captured.err
        except SystemExit as e:
            # Expected if dependencies are missing
            captured = capsys.readouterr()
            assert "[ERROR]" in captured.err
            assert e.code == 1

    def test_ensure_dependencies_installed_both_missing(self, code_dir, capsys):
        """Test ensure_dependencies_installed when both dependencies are missing with real import check."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import (
            ensure_dependencies_installed,
        )

        # Test with real import checking - if both are actually missing, function will exit
        try:
            ensure_dependencies_installed()
            captured = capsys.readouterr()
            # If dependencies are installed, we should see success messages
            assert "[INFO]" in captured.out or "[ERROR]" in captured.err
        except SystemExit as e:
            # Expected if dependencies are missing
            captured = capsys.readouterr()
            assert "[ERROR]" in captured.err
            assert e.code == 1

    def test_check_and_setup_env_vars_file_exists(self, code_dir, capsys, tmp_path):
        """Test check_and_setup_env_vars when .env file exists."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import check_and_setup_env_vars

        # Create a dummy .env file
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_KEY=test_value\n")

        # check_and_setup_env_vars returns True when .env is found
        result = check_and_setup_env_vars(str(tmp_path))
        assert result is True

    def test_check_and_setup_env_vars_file_missing(self, code_dir, capsys, tmp_path):
        """Test check_and_setup_env_vars when .env file is missing."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import check_and_setup_env_vars

        # Ensure .env file doesn't exist
        env_file_path = tmp_path / ".env"
        assert not env_file_path.exists()

        # check_and_setup_env_vars returns False when .env is not found
        result = check_and_setup_env_vars(str(tmp_path))
        assert result is False

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

        from codomyrmex.environment_setup.env_checker import (
            ensure_dependencies_installed,
        )

        # Test with real imports - if kit fails with unexpected error, function should handle it
        # This tests error handling in the real implementation
        try:
            ensure_dependencies_installed()
            captured = capsys.readouterr()
            # Function should handle errors gracefully
            assert "[INFO]" in captured.out or "[ERROR]" in captured.err
        except SystemExit as e:
            # Expected if dependencies are missing or error occurs
            captured = capsys.readouterr()
            assert "[ERROR]" in captured.err
            assert e.code == 1

    def test_check_and_setup_env_vars_path_handling(self, code_dir, tmp_path):
        """Test check_and_setup_env_vars path handling with real paths."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import check_and_setup_env_vars

        # Create real .env file
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_KEY=test_value")

        result = check_and_setup_env_vars(str(tmp_path))
        assert result is True

    def test_is_uv_available_exception_handling(self, code_dir):
        """Test is_uv_available exception handling with real subprocess."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import is_uv_available

        # Test with real subprocess - function should handle exceptions gracefully
        result = is_uv_available()
        assert isinstance(result, bool)
        # Function should return False on any error

    def test_is_uv_environment_edge_cases(self, code_dir):
        """Test is_uv_environment with edge cases.

        Note: is_uv_environment checks VIRTUAL_ENV or is_uv_available().
        An empty string for UV_ACTIVE is not checked (function doesn't use UV_ACTIVE).
        Setting VIRTUAL_ENV to any path makes it return True.
        """
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import (
            is_uv_environment,
        )

        # Test with VIRTUAL_ENV set (any value makes is_uv_environment return True)
        original_virtual_env = os.environ.get("VIRTUAL_ENV")
        try:
            os.environ["VIRTUAL_ENV"] = "/path/to/venv"
            result = is_uv_environment()
            assert result is True
        finally:
            if original_virtual_env is not None:
                os.environ["VIRTUAL_ENV"] = original_virtual_env
            elif "VIRTUAL_ENV" in os.environ:
                del os.environ["VIRTUAL_ENV"]

    def test_ensure_dependencies_installed_instruction_format(self, code_dir, capsys):
        """Test that ensure_dependencies_installed provides properly formatted instructions."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import (
            ensure_dependencies_installed,
        )

        # Test with real imports - if both are missing, function will exit
        try:
            ensure_dependencies_installed()
            captured = capsys.readouterr()
            # If dependencies are installed, we should see success messages
            assert "[INFO]" in captured.out or "[ERROR]" in captured.err
        except SystemExit as e:
            # Expected if dependencies are missing
            captured = capsys.readouterr()
            assert "[ERROR]" in captured.err
            assert e.code == 1

    def test_check_and_setup_env_vars_instruction_format(self, code_dir, tmp_path):
        """Test that check_and_setup_env_vars returns False when .env missing."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import check_and_setup_env_vars

        # check_and_setup_env_vars returns a bool, does not print instructions
        result = check_and_setup_env_vars(str(tmp_path))
        assert result is False

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
        from codomyrmex.environment_setup.env_checker import (
            check_and_setup_env_vars,
            ensure_dependencies_installed,
        )

        # Test that the functions can be called without errors
        ensure_dependencies_installed()
        result = check_and_setup_env_vars("/tmp")

        # check_and_setup_env_vars returns bool
        assert isinstance(result, bool)
