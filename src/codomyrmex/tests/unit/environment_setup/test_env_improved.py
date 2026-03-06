"""Improved zero-mock tests for environment_setup module.

Focuses on Python version validation, dependency checking with version constraints,
and environment report generation.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


@pytest.mark.unit
class TestEnvironmentImproved:
    """Tests for the improved environment setup functionality."""

    def test_validate_python_version_variants(self, code_dir):
        """Test validate_python_version with different version strings."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import validate_python_version

        # Current version
        current_v = f"{sys.version_info.major}.{sys.version_info.minor}"
        assert validate_python_version(current_v) is True

        # Lower version
        assert validate_python_version("3.0") is True

        # Higher version
        assert validate_python_version("10.0") is False

        # Multi-part version
        assert validate_python_version("3.10.0") is True

        # Invalid format (should fallback to 3.10 check and probably be True)
        assert validate_python_version("invalid") is True

    def test_check_dependencies_with_constraints(self, code_dir):
        """Test check_dependencies with version constraints."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import check_dependencies

        # Test with an installed package and a satisfied constraint
        # 'pytest' is definitely installed as it's running this test
        results = check_dependencies(["pytest>=7.0.0"])
        assert len(results) == 1
        assert results[0].name == "pytest"
        assert results[0].installed is True
        assert results[0].satisfied is True
        assert results[0].version is not None

        # Test with an installed package and an unsatisfied constraint
        results = check_dependencies(["pytest>=100.0.0"])
        assert results[0].satisfied is False

        # Test with multiple operators
        results = check_dependencies(["pytest==100.0.0"])
        assert results[0].satisfied is False

        # Test with non-existent package
        results = check_dependencies(["nonexistent-package-abc-123"])
        assert results[0].installed is False
        assert results[0].satisfied is False

    def test_check_dependencies_module_vs_package(self, code_dir):
        """Test check_dependencies when module name differs from package name."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import check_dependencies

        # 'dotenv' is the module, 'python-dotenv' is the package
        results = check_dependencies(["dotenv"])
        assert len(results) == 1
        # It should correctly identify it as python-dotenv if possible
        assert results[0].name in ["python-dotenv", "dotenv"]
        assert results[0].installed is True

    def test_generate_environment_report_content(self, code_dir):
        """Test that generate_environment_report contains expected sections."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import generate_environment_report

        report = generate_environment_report()
        assert "Codomyrmex Environment Report" in report
        assert "Python Version" in report
        assert "Core Dependencies" in report
        assert "python-dotenv" in report
        assert "cased-kit" in report

    def test_validate_environment_details(self, code_dir):
        """Test validate_environment returns details."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.environment_setup.env_checker import validate_environment

        report = validate_environment()
        assert hasattr(report, "details")
        assert "python_version" in report.details
        assert "dependencies" in report.details
