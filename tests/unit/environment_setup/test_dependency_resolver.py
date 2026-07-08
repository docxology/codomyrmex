"""Comprehensive unit tests for environment_setup.dependency_resolver module.

Tests DependencyResolver, DependencyInfo, and Conflict dataclasses.
Strictly zero-mock tests, uses real objects and tmp_path for filesystem.
"""

from __future__ import annotations

import sys

import pytest


@pytest.mark.unit
class TestDependencyInfoDataclass:
    """Test the DependencyInfo dataclass."""

    def test_create_minimal(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyInfo

        info = DependencyInfo(name="requests", version="2.31.0")
        assert info.name == "requests"
        assert info.version == "2.31.0"
        assert info.required_by == []
        assert info.requires == []

    def test_create_with_relations(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyInfo

        info = DependencyInfo(
            name="urllib3",
            version="2.0.4",
            required_by=["requests"],
            requires=["certifi"],
        )
        assert info.required_by == ["requests"]
        assert info.requires == ["certifi"]


@pytest.mark.unit
class TestConflictDataclass:
    """Test the Conflict dataclass."""

    def test_create_default_severity(self):
        from codomyrmex.environment_setup.dependency_resolver import Conflict

        c = Conflict(
            package="numpy",
            installed_version="1.24.0",
            required_version=">=1.25.0",
            required_by="scipy",
        )
        assert c.package == "numpy"
        assert c.severity == "warning"


@pytest.mark.unit
class TestDependencyResolverInit:
    """Test DependencyResolver constructor."""

    def test_default_python_path(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver()
        assert resolver._python == "python"

    def test_custom_python_path(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver(python_path="/usr/bin/python3")
        assert resolver._python == "/usr/bin/python3"


@pytest.mark.unit
class TestParsePipCheck:
    """Test the _parse_pip_check internal method."""

    def test_empty_output(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver()
        result = resolver._parse_pip_check("")
        assert result == []

    def test_single_conflict(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        output = "scipy 1.11.0 requires numpy>=1.25.0, but numpy 1.24.0 is installed"
        resolver = DependencyResolver()
        conflicts = resolver._parse_pip_check(output)
        assert len(conflicts) == 1
        assert conflicts[0].package == "numpy>=1.25.0"
        assert conflicts[0].required_by == "scipy 1.11.0"
        assert "1.24.0" in conflicts[0].installed_version


@pytest.mark.unit
class TestCheckConflicts:
    """Test check_conflicts using real python executable."""

    def test_check_conflicts_returns_list(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver(python_path=sys.executable)
        result = resolver.check_conflicts()
        assert isinstance(result, list)


@pytest.mark.unit
class TestListInstalled:
    """Test list_installed method."""

    def test_list_installed_returns_list(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver(python_path=sys.executable)
        result = resolver.list_installed()
        assert isinstance(result, list)
        if result:
            assert hasattr(result[0], "name")
            assert hasattr(result[0], "version")


@pytest.mark.unit
class TestSuggestResolution:
    """Test suggest_resolution method."""

    def test_empty_conflicts(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver()
        result = resolver.suggest_resolution([])
        assert result == []

    def test_single_conflict_suggestion(self):
        from codomyrmex.environment_setup.dependency_resolver import (
            Conflict,
            DependencyResolver,
        )

        conflict = Conflict(
            package="numpy",
            installed_version="1.24.0",
            required_version=">=1.25.0",
            required_by="scipy",
        )
        resolver = DependencyResolver()
        suggestions = resolver.suggest_resolution([conflict])
        assert len(suggestions) == 1
        assert "numpy" in suggestions[0]
        assert "pip install" in suggestions[0]


@pytest.mark.unit
class TestValidatePyproject:
    """Test validate_pyproject method."""

    def test_missing_file(self, tmp_path):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver()
        issues = resolver.validate_pyproject(tmp_path / "nonexistent.toml")
        assert len(issues) == 1
        assert "not found" in issues[0]

    def test_valid_pyproject_with_pinned_deps(self, tmp_path):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            '[project]\nname = "test"\ndependencies = [\n'
            '    "requests>=2.28.0",\n'
            '    "numpy==1.25.0",\n'
            "]\n"
        )
        resolver = DependencyResolver()
        issues = resolver.validate_pyproject(pyproject)
        # All deps pinned, should have no "Unpinned" issues
        unpinned = [i for i in issues if "Unpinned" in i]
        assert unpinned == []


@pytest.mark.unit
class TestInstallDependencies:
    """Test install_dependencies method."""

    def test_install_dependencies_missing_file(self, tmp_path):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver(python_path=sys.executable)
        # Attempt to install from missing requirements file
        result = resolver.install_dependencies(str(tmp_path / "missing.txt"))
        assert result is False


@pytest.mark.unit
class TestDetectVirtualenv:
    """Test detect_virtualenv method."""

    def test_returns_dict_with_expected_keys(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver()
        result = resolver.detect_virtualenv()
        assert isinstance(result, dict)
        assert "active" in result
        assert "path" in result
        assert "type" in result

    def test_type_is_valid(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver()
        result = resolver.detect_virtualenv()
        assert result["type"] in ("venv", "uv", "conda", "virtualenv", "none")


@pytest.mark.unit
class TestGetEnvironmentInfo:
    """Test get_environment_info method."""

    def test_returns_expected_keys(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver(python_path=sys.executable)
        info = resolver.get_environment_info()
        assert "python_version" in info
        assert "platform" in info
        assert "virtualenv" in info
        assert "installed_packages" in info


@pytest.mark.unit
class TestGenerateReport:
    """Test generate_report method."""

    def test_report_is_string(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver(python_path=sys.executable)
        report = resolver.generate_report()
        assert isinstance(report, str)
        assert "Dependency Health Report" in report


@pytest.mark.unit
class TestFullAudit:
    """Test full_audit method."""

    def test_audit_without_pyproject(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver(python_path=sys.executable)
        audit = resolver.full_audit()
        assert "environment" in audit
        assert "conflicts" in audit
        assert "pyproject_issues" in audit
        assert "suggestions" in audit
        assert "conflict_count" in audit
        assert "issue_count" in audit
