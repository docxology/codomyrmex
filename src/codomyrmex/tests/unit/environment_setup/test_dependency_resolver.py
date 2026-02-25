"""Comprehensive unit tests for environment_setup.dependency_resolver module.

Tests DependencyResolver, DependencyInfo, and Conflict dataclasses.
Zero-mock policy: uses real objects and tmp_path for filesystem.
"""

from __future__ import annotations

import sys
from pathlib import Path

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

    def test_default_factory_isolation(self):
        """Ensure default list factories produce independent lists."""
        from codomyrmex.environment_setup.dependency_resolver import DependencyInfo

        a = DependencyInfo(name="a", version="1.0")
        b = DependencyInfo(name="b", version="2.0")
        a.required_by.append("x")
        assert b.required_by == []


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

    def test_create_error_severity(self):
        from codomyrmex.environment_setup.dependency_resolver import Conflict

        c = Conflict(
            package="numpy",
            installed_version="1.24.0",
            required_version=">=1.25.0",
            required_by="scipy",
            severity="error",
        )
        assert c.severity == "error"


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

    def test_sys_executable_python(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver(python_path=sys.executable)
        assert resolver._python == sys.executable


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

    def test_multiple_conflicts(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        output = (
            "scipy 1.11.0 requires numpy>=1.25.0, but numpy 1.24.0 is installed\n"
            "requests 2.31.0 requires urllib3>=2.0, but urllib3 1.26.0 is installed"
        )
        resolver = DependencyResolver()
        conflicts = resolver._parse_pip_check(output)
        assert len(conflicts) == 2

    def test_no_conflict_lines(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        output = "No broken requirements found.\n"
        resolver = DependencyResolver()
        result = resolver._parse_pip_check(output)
        assert result == []

    def test_mixed_output(self):
        """Lines without 'requires' and 'but' are skipped."""
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        output = (
            "Some unrelated line\n"
            "scipy 1.11.0 requires numpy>=1.25.0, but numpy 1.24.0 is installed\n"
            "Another unrelated line"
        )
        resolver = DependencyResolver()
        conflicts = resolver._parse_pip_check(output)
        assert len(conflicts) == 1


@pytest.mark.unit
class TestCheckConflicts:
    """Test check_conflicts using real python executable."""

    def test_check_conflicts_returns_list(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver(python_path=sys.executable)
        result = resolver.check_conflicts()
        assert isinstance(result, list)

    def test_check_conflicts_bad_python_returns_empty(self):
        """A non-existent python path should return empty list (FileNotFoundError caught)."""
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver(python_path="/nonexistent/python99")
        result = resolver.check_conflicts()
        assert result == []


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

    def test_list_installed_bad_python_returns_empty(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver(python_path="/nonexistent/python99")
        result = resolver.list_installed()
        assert result == []


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

    def test_multiple_conflict_suggestions(self):
        from codomyrmex.environment_setup.dependency_resolver import (
            Conflict,
            DependencyResolver,
        )

        conflicts = [
            Conflict(package="numpy", installed_version="1.24", required_version=">=1.25", required_by="scipy"),
            Conflict(package="urllib3", installed_version="1.26", required_version=">=2.0", required_by="requests"),
        ]
        resolver = DependencyResolver()
        suggestions = resolver.suggest_resolution(conflicts)
        assert len(suggestions) == 2


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

    def test_unpinned_dependencies(self, tmp_path):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            '[project]\nname = "test"\ndependencies = [\n'
            '    "requests",\n'
            '    "numpy",\n'
            "]\n"
        )
        resolver = DependencyResolver()
        issues = resolver.validate_pyproject(pyproject)
        unpinned = [i for i in issues if "Unpinned" in i]
        assert len(unpinned) == 2

    def test_no_dependencies_section(self, tmp_path):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "test"\n')
        resolver = DependencyResolver()
        issues = resolver.validate_pyproject(pyproject)
        assert any("No dependencies" in i for i in issues)

    def test_mixed_pinned_and_unpinned(self, tmp_path):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            '[project]\nname = "test"\ndependencies = [\n'
            '    "requests>=2.28.0",\n'
            '    "flask",\n'
            '    "numpy~=1.25",\n'
            "]\n"
        )
        resolver = DependencyResolver()
        issues = resolver.validate_pyproject(pyproject)
        unpinned = [i for i in issues if "Unpinned" in i]
        assert len(unpinned) == 1
        assert "flask" in unpinned[0]

    def test_tilde_equals_pinned(self, tmp_path):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            '[project]\nname = "test"\ndependencies = ["numpy~=1.25"]\n'
        )
        resolver = DependencyResolver()
        issues = resolver.validate_pyproject(pyproject)
        unpinned = [i for i in issues if "Unpinned" in i]
        assert unpinned == []

    def test_real_pyproject(self):
        """Validate the actual project pyproject.toml."""
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        real_path = Path("/Users/mini/Documents/GitHub/codomyrmex/pyproject.toml")
        if not real_path.exists():
            pytest.skip("Real pyproject.toml not found")
        resolver = DependencyResolver()
        issues = resolver.validate_pyproject(real_path)
        assert isinstance(issues, list)


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

    def test_active_is_bool(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver()
        result = resolver.detect_virtualenv()
        assert isinstance(result["active"], bool)


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

    def test_python_version_nonempty(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver(python_path=sys.executable)
        info = resolver.get_environment_info()
        assert len(info["python_version"]) > 0

    def test_installed_packages_is_int(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver(python_path=sys.executable)
        info = resolver.get_environment_info()
        assert isinstance(info["installed_packages"], int)


@pytest.mark.unit
class TestGenerateReport:
    """Test generate_report method."""

    def test_report_is_string(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver(python_path=sys.executable)
        report = resolver.generate_report()
        assert isinstance(report, str)
        assert "Dependency Health Report" in report

    def test_report_contains_python_info(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver(python_path=sys.executable)
        report = resolver.generate_report()
        assert "Python" in report
        assert "Platform" in report
        assert "Virtualenv" in report

    def test_report_with_pyproject(self, tmp_path):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            '[project]\nname = "test"\ndependencies = ["requests>=2.0"]\n'
        )
        resolver = DependencyResolver(python_path=sys.executable)
        report = resolver.generate_report(pyproject_path=pyproject)
        assert "pyproject.toml" in report or "looks good" in report

    def test_report_with_missing_pyproject(self, tmp_path):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver(python_path=sys.executable)
        report = resolver.generate_report(pyproject_path=tmp_path / "missing.toml")
        assert "not found" in report

    def test_report_without_pyproject(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver(python_path=sys.executable)
        report = resolver.generate_report(pyproject_path=None)
        assert isinstance(report, str)
        # Should not contain pyproject section
        assert "pyproject.toml issues" not in report or "looks good" not in report


@pytest.mark.unit
class TestFindOutdated:
    """Test find_outdated method."""

    def test_returns_list(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver(python_path=sys.executable)
        result = resolver.find_outdated()
        assert isinstance(result, list)

    def test_bad_python_returns_empty(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver(python_path="/nonexistent/python99")
        result = resolver.find_outdated()
        assert result == []

    def test_result_shape_if_any(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver(python_path=sys.executable)
        result = resolver.find_outdated()
        if result:
            assert "name" in result[0]
            assert "version" in result[0]
            assert "latest_version" in result[0]


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
        assert isinstance(audit["conflicts"], list)
        assert isinstance(audit["pyproject_issues"], list)
        assert audit["issue_count"] == 0  # No pyproject given

    def test_audit_with_pyproject(self, tmp_path):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            '[project]\nname = "test"\ndependencies = ["flask"]\n'
        )
        resolver = DependencyResolver(python_path=sys.executable)
        audit = resolver.full_audit(pyproject_path=pyproject)
        assert audit["issue_count"] >= 1  # unpinned flask

    def test_audit_conflict_count_matches_list(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver(python_path=sys.executable)
        audit = resolver.full_audit()
        assert audit["conflict_count"] == len(audit["conflicts"])

    def test_audit_environment_has_expected_keys(self):
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver(python_path=sys.executable)
        audit = resolver.full_audit()
        env = audit["environment"]
        assert "python_version" in env
        assert "platform" in env
        assert "virtualenv" in env
        assert "installed_packages" in env
