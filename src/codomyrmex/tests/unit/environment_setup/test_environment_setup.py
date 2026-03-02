"""Comprehensive unit tests for environment_setup module.

Strictly zero-mock tests, uses real objects and tmp_path for filesystem.
"""

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

    def test_validate_python_version_real(self, code_dir):
        """Test validate_python_version with real sys.version."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import validate_python_version

        # Test with current version (should be True)
        current_v = f"{sys.version_info.major}.{sys.version_info.minor}"
        assert validate_python_version(current_v) is True

        # Test with an old version (should be True)
        assert validate_python_version("3.0") is True

        # Test with an impossibly high version (should be False)
        assert validate_python_version("10.0") is False

    def test_is_uv_available_real(self, code_dir):
        """Test is_uv_available with real uv check."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import is_uv_available

        result = is_uv_available()
        assert isinstance(result, bool)

    def test_get_uv_path_real(self, code_dir):
        """Test get_uv_path with real uv check."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import get_uv_path, is_uv_available

        path = get_uv_path()
        if is_uv_available():
            assert path is not None
            assert os.path.exists(path)
        else:
            assert path is None

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

    def test_check_dependencies_standard_library(self, code_dir):
        """Test check_dependencies with standard library packages."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import check_dependencies

        # 'os' and 'sys' are built-in, but can be checked via find_spec
        results = check_dependencies(["os", "sys", "nonexistent_pkg_xyz"])
        
        assert results[0].name == "os"
        assert results[0].installed is True
        
        assert results[1].name == "sys"
        assert results[1].installed is True
        
        assert results[2].name == "nonexistent_pkg_xyz"
        assert results[2].installed is False

    def test_ensure_dependencies_installed_real(self, code_dir):
        """Test ensure_dependencies_installed with real packages."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import ensure_dependencies_installed

        # Test with packages that should exist
        assert ensure_dependencies_installed(["os", "pathlib"]) is True

        # Test with package that doesn't exist
        assert ensure_dependencies_installed(["nonexistent_pkg_abc"]) is False

    def test_check_and_setup_env_vars_real(self, code_dir, tmp_path):
        """Test check_and_setup_env_vars with real .env file."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import check_and_setup_env_vars

        # Create a dummy .env file
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_REQUIRED_VAR=present\n")

        # Test with required var that is present in .env
        missing = check_and_setup_env_vars(
            repo_root=str(tmp_path),
            required=["TEST_REQUIRED_VAR"]
        )
        assert "TEST_REQUIRED_VAR" not in missing
        assert os.environ.get("TEST_REQUIRED_VAR") == "present"

        # Test with required var that is missing
        missing = check_and_setup_env_vars(
            repo_root=str(tmp_path),
            required=["MISSING_VAR_XYZ"]
        )
        assert "MISSING_VAR_XYZ" in missing

    def test_check_api_keys_real(self, code_dir):
        """Test check_api_keys with real env vars."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import check_api_keys

        original_val = os.environ.get("MY_TEST_API_KEY")
        try:
            os.environ["MY_TEST_API_KEY"] = "sk-test"
            report = check_api_keys(["MY_TEST_API_KEY", "NONEXISTENT_KEY"])
            
            assert report.all_present is False
            assert "MY_TEST_API_KEY" not in report.missing
            assert "NONEXISTENT_KEY" in report.missing
        finally:
            if original_val is not None:
                os.environ["MY_TEST_API_KEY"] = original_val
            elif "MY_TEST_API_KEY" in os.environ:
                del os.environ["MY_TEST_API_KEY"]

    def test_validate_environment_real(self, code_dir):
        """Test validate_environment status."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import validate_environment

        report = validate_environment(min_python="3.0")
        assert isinstance(report.valid, bool)
        assert isinstance(report.missing_items, list)

    def test_generate_environment_report_real(self, code_dir):
        """Test generate_environment_report format."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import generate_environment_report

        report = generate_environment_report()
        assert "Codomyrmex Environment Report" in report
        assert "Python Version" in report
        assert "UV Available" in report

    def test_validate_environment_completeness_legacy(self, code_dir, tmp_path):
        """Test legacy wrapper validate_environment_completeness."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import validate_environment_completeness

        # Should return a boolean
        result = validate_environment_completeness(repo_root=str(tmp_path))
        assert isinstance(result, bool)
