"""Unit tests for codomyrmex.system_discovery.reporting.status_reporter.

Covers StatusReporter: constructor, all check_* methods, format_message,
display helpers, generate_comprehensive_report, export_report, and error paths.
"""

import json
import sys
from pathlib import Path

import pytest


@pytest.mark.unit
class TestStatusReporterInit:
    """Tests for StatusReporter constructor."""

    def test_default_project_root_is_cwd(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        assert reporter.project_root == Path.cwd()
        assert reporter.src_path == Path.cwd() / "src"

    def test_explicit_project_root(self, tmp_path):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter(project_root=tmp_path)
        assert reporter.project_root == tmp_path
        assert reporter.src_path == tmp_path / "src"

    def test_formatter_attribute_set(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        # formatter is either a TerminalFormatter instance or None
        assert hasattr(reporter, "formatter")


@pytest.mark.unit
class TestFormatMessage:
    """Tests for StatusReporter.format_message."""

    def test_format_info_returns_string(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        result = reporter.format_message("hello", "info")
        assert isinstance(result, str)
        assert "hello" in result

    def test_format_success_returns_string(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        result = reporter.format_message("ok", "success")
        assert isinstance(result, str)
        assert "ok" in result

    def test_format_error_returns_string(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        result = reporter.format_message("fail", "error")
        assert isinstance(result, str)
        assert "fail" in result

    def test_format_warning_returns_string(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        result = reporter.format_message("warn", "warning")
        assert isinstance(result, str)
        assert "warn" in result

    def test_format_default_type(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        result = reporter.format_message("default")
        assert isinstance(result, str)
        assert "default" in result

    def test_format_no_formatter(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        reporter.formatter = None
        result = reporter.format_message("raw", "success")
        assert result == "raw"


@pytest.mark.unit
class TestCheckPythonEnvironment:
    """Tests for check_python_environment."""

    def test_returns_expected_keys(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        env = reporter.check_python_environment()
        assert "version" in env
        assert "version_string" in env
        assert "executable" in env
        assert "virtual_env" in env
        assert "path" in env
        assert "platform" in env

    def test_version_string_matches_sys(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        env = reporter.check_python_environment()
        assert env["version_string"] == sys.version.split()[0]

    def test_executable_matches_sys(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        env = reporter.check_python_environment()
        assert env["executable"] == sys.executable

    def test_platform_matches_sys(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        env = reporter.check_python_environment()
        assert env["platform"] == sys.platform

    def test_path_is_list_max_5(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        env = reporter.check_python_environment()
        assert isinstance(env["path"], list)
        assert len(env["path"]) <= 5

    def test_virtual_env_is_bool(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        env = reporter.check_python_environment()
        assert isinstance(env["virtual_env"], bool)


@pytest.mark.unit
class TestInVirtualEnv:
    """Tests for _in_virtual_env."""

    def test_returns_bool(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        result = reporter._in_virtual_env()
        assert isinstance(result, bool)


@pytest.mark.unit
class TestCheckProjectStructure:
    """Tests for check_project_structure."""

    def test_returns_expected_keys(self, tmp_path):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter(project_root=tmp_path)
        structure = reporter.check_project_structure()
        assert "project_root_exists" in structure
        assert "src_exists" in structure
        assert "codomyrmex_package" in structure
        assert "testing_dir" in structure
        assert "docs_dir" in structure
        assert "virtual_env_dir" in structure
        assert "config_files" in structure

    def test_empty_dir_reports_missing(self, tmp_path):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter(project_root=tmp_path)
        structure = reporter.check_project_structure()
        assert structure["project_root_exists"] is True
        assert structure["src_exists"] is False
        assert structure["codomyrmex_package"] is False

    def test_populated_dir_reports_present(self, tmp_path):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        # Create expected structure
        (tmp_path / "src" / "codomyrmex" / "documentation").mkdir(parents=True)
        (tmp_path / "testing").mkdir()
        (tmp_path / ".venv").mkdir()
        (tmp_path / "pyproject.toml").touch()
        (tmp_path / "README.md").touch()

        reporter = StatusReporter(project_root=tmp_path)
        structure = reporter.check_project_structure()
        assert structure["project_root_exists"] is True
        assert structure["src_exists"] is True
        assert structure["codomyrmex_package"] is True
        assert structure["testing_dir"] is True
        assert structure["docs_dir"] is True
        assert structure["virtual_env_dir"] is True
        assert structure["config_files"]["pyproject.toml"] is True
        assert structure["config_files"]["README.md"] is True


@pytest.mark.unit
class TestCheckVirtualEnvDir:
    """Tests for _check_virtual_env_dir."""

    def test_no_venv_dir(self, tmp_path):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter(project_root=tmp_path)
        assert reporter._check_virtual_env_dir() is False

    def test_dotenv_dir_detected(self, tmp_path):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        (tmp_path / ".venv").mkdir()
        reporter = StatusReporter(project_root=tmp_path)
        assert reporter._check_virtual_env_dir() is True

    def test_venv_dir_detected(self, tmp_path):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        (tmp_path / "venv").mkdir()
        reporter = StatusReporter(project_root=tmp_path)
        assert reporter._check_virtual_env_dir() is True

    def test_env_dir_detected(self, tmp_path):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        (tmp_path / "env").mkdir()
        reporter = StatusReporter(project_root=tmp_path)
        assert reporter._check_virtual_env_dir() is True


@pytest.mark.unit
class TestCheckConfigFiles:
    """Tests for _check_config_files."""

    def test_empty_dir_all_false(self, tmp_path):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter(project_root=tmp_path)
        config = reporter._check_config_files()
        assert all(v is False for v in config.values())

    def test_detects_present_files(self, tmp_path):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        (tmp_path / "pyproject.toml").touch()
        (tmp_path / "pytest.ini").touch()
        reporter = StatusReporter(project_root=tmp_path)
        config = reporter._check_config_files()
        assert config["pyproject.toml"] is True
        assert config["pytest.ini"] is True
        assert config["setup.py"] is False

    def test_returns_expected_keys(self, tmp_path):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter(project_root=tmp_path)
        config = reporter._check_config_files()
        expected_keys = {
            "pyproject.toml",
            "requirements.txt",
            "setup.py",
            ".env",
            "pytest.ini",
            "README.md",
        }
        assert set(config.keys()) == expected_keys


@pytest.mark.unit
class TestCheckImport:
    """Tests for _check_import."""

    def test_existing_module_returns_true(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        assert reporter._check_import("sys") is True

    def test_nonexistent_module_returns_false(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        assert reporter._check_import("nonexistent_module_xyz_123") is False

    def test_json_module_returns_true(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        assert reporter._check_import("json") is True


@pytest.mark.unit
class TestCheckDependencies:
    """Tests for check_dependencies."""

    def test_returns_expected_structure(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        deps = reporter.check_dependencies()
        assert "dependencies" in deps
        assert "available_count" in deps
        assert "total_count" in deps
        assert "success_rate" in deps

    def test_total_count_is_14(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        deps = reporter.check_dependencies()
        assert deps["total_count"] == 14

    def test_available_count_lte_total(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        deps = reporter.check_dependencies()
        assert deps["available_count"] <= deps["total_count"]
        assert deps["available_count"] >= 0

    def test_success_rate_is_percentage(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        deps = reporter.check_dependencies()
        assert 0 <= deps["success_rate"] <= 100

    def test_pytest_is_available(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        deps = reporter.check_dependencies()
        # pytest must be importable since we are running under it
        assert deps["dependencies"]["pytest"] is True

    def test_dependency_values_are_bool(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        deps = reporter.check_dependencies()
        for name, val in deps["dependencies"].items():
            assert isinstance(val, bool), f"{name} should be bool, got {type(val)}"


@pytest.mark.unit
class TestCheckGitStatus:
    """Tests for check_git_status."""

    def test_returns_expected_keys(self, tmp_path):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter(project_root=tmp_path)
        git = reporter.check_git_status()
        assert "is_git_repo" in git
        assert "git_available" in git
        assert "current_branch" in git
        assert "clean_working_tree" in git
        assert "remotes" in git
        assert "recent_commits" in git
        assert "staged_changes" in git
        assert "unstaged_changes" in git

    def test_non_repo_dir(self, tmp_path):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter(project_root=tmp_path)
        git = reporter.check_git_status()
        # tmp_path is not a git repo
        assert git["is_git_repo"] is False

    def test_real_repo_detected(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        # Use the actual codomyrmex project root which is a git repo
        repo_root = Path("/Users/mini/Documents/GitHub/codomyrmex")
        reporter = StatusReporter(project_root=repo_root)
        git = reporter.check_git_status()
        assert git["git_available"] is True
        assert git["is_git_repo"] is True
        assert git["current_branch"] is not None

    def test_git_init_fresh_repo(self, tmp_path):
        """Test against a freshly initialized git repo."""
        import subprocess

        subprocess.run(
            ["git", "init"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter(project_root=tmp_path)
        git = reporter.check_git_status()
        assert git["is_git_repo"] is True
        assert git["clean_working_tree"] is True
        assert git["remotes"] == []
        assert git["recent_commits"] == []


@pytest.mark.unit
class TestCheckExternalTools:
    """Tests for check_external_tools."""

    def test_returns_expected_keys(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        tools = reporter.check_external_tools()
        expected_keys = {"git", "npm", "node", "docker", "uv"}
        assert set(tools.keys()) == expected_keys

    def test_values_are_bool(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        tools = reporter.check_external_tools()
        for name, val in tools.items():
            assert isinstance(val, bool), f"{name} should be bool"

    def test_git_available(self):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        tools = reporter.check_external_tools()
        # git is available in this CI/dev environment
        assert tools["git"] is True


@pytest.mark.unit
class TestGenerateComprehensiveReport:
    """Tests for generate_comprehensive_report."""

    def test_returns_all_sections(self, tmp_path):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter(project_root=tmp_path)
        report = reporter.generate_comprehensive_report()
        assert "timestamp" in report
        assert "python_environment" in report
        assert "project_structure" in report
        assert "dependencies" in report
        assert "git_status" in report
        assert "external_tools" in report

    def test_timestamp_is_iso_format(self, tmp_path):
        from datetime import datetime

        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter(project_root=tmp_path)
        report = reporter.generate_comprehensive_report()
        # Should parse without error
        datetime.fromisoformat(report["timestamp"])

    def test_report_values_are_dicts(self, tmp_path):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter(project_root=tmp_path)
        report = reporter.generate_comprehensive_report()
        assert isinstance(report["python_environment"], dict)
        assert isinstance(report["project_structure"], dict)
        assert isinstance(report["dependencies"], dict)
        assert isinstance(report["git_status"], dict)
        assert isinstance(report["external_tools"], dict)


@pytest.mark.unit
class TestDisplayStatusReport:
    """Tests for display_status_report (smoke test -- runs to completion)."""

    def test_display_runs_without_error(self, tmp_path, capsys):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter(project_root=tmp_path)
        reporter.display_status_report()
        captured = capsys.readouterr()
        assert "CODOMYRMEX SYSTEM STATUS REPORT" in captured.out

    def test_display_contains_sections(self, tmp_path, capsys):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter(project_root=tmp_path)
        reporter.display_status_report()
        captured = capsys.readouterr()
        assert "Python Environment" in captured.out
        assert "Project Structure" in captured.out
        assert "Dependencies" in captured.out
        assert "Git" in captured.out
        assert "External Tools" in captured.out
        assert "Summary" in captured.out


@pytest.mark.unit
class TestDisplayHelpers:
    """Tests for individual _display_* helpers."""

    def test_display_python_status_venv_active(self, capsys):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        env = {
            "version_string": "3.12.0",
            "executable": "/usr/bin/python3",
            "virtual_env": True,
            "platform": "linux",
        }
        reporter._display_python_status(env)
        captured = capsys.readouterr()
        assert "3.12.0" in captured.out
        assert "Active" in captured.out

    def test_display_python_status_no_venv(self, capsys):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        env = {
            "version_string": "3.12.0",
            "executable": "/usr/bin/python3",
            "virtual_env": False,
            "platform": "linux",
        }
        reporter._display_python_status(env)
        captured = capsys.readouterr()
        assert "Not detected" in captured.out

    def test_display_git_status_no_git(self, capsys):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        git = {
            "git_available": False,
            "is_git_repo": False,
            "current_branch": None,
            "clean_working_tree": False,
            "remotes": [],
            "recent_commits": [],
            "staged_changes": 0,
            "unstaged_changes": 0,
        }
        reporter._display_git_status(git)
        captured = capsys.readouterr()
        assert "not available" in captured.out

    def test_display_git_status_not_repo(self, capsys):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        git = {
            "git_available": True,
            "is_git_repo": False,
            "current_branch": None,
            "clean_working_tree": False,
            "remotes": [],
            "recent_commits": [],
            "staged_changes": 0,
            "unstaged_changes": 0,
        }
        reporter._display_git_status(git)
        captured = capsys.readouterr()
        assert "Not a git repository" in captured.out

    def test_display_git_status_full(self, capsys):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        git = {
            "git_available": True,
            "is_git_repo": True,
            "current_branch": "main",
            "clean_working_tree": False,
            "remotes": ["origin"],
            "recent_commits": ["abc1234 Initial commit", "def5678 Second commit"],
            "staged_changes": 2,
            "unstaged_changes": 3,
        }
        reporter._display_git_status(git)
        captured = capsys.readouterr()
        assert "main" in captured.out
        assert "2 staged" in captured.out
        assert "3 unstaged" in captured.out
        assert "Recent commits" in captured.out

    def test_display_git_status_clean(self, capsys):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        git = {
            "git_available": True,
            "is_git_repo": True,
            "current_branch": "main",
            "clean_working_tree": True,
            "remotes": [],
            "recent_commits": [],
            "staged_changes": 0,
            "unstaged_changes": 0,
        }
        reporter._display_git_status(git)
        captured = capsys.readouterr()
        assert "clean" in captured.out

    def test_display_external_tools(self, capsys):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        tools = {"git": True, "docker": False}
        reporter._display_external_tools(tools)
        captured = capsys.readouterr()
        assert "git" in captured.out
        assert "docker" in captured.out

    def test_display_project_structure(self, capsys):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        structure = {
            "project_root_exists": True,
            "src_exists": True,
            "codomyrmex_package": False,
            "testing_dir": False,
            "docs_dir": False,
            "virtual_env_dir": True,
            "config_files": {"pyproject.toml": True, "setup.py": False},
        }
        reporter._display_project_structure(structure)
        captured = capsys.readouterr()
        assert "Project Structure" in captured.out
        assert "Configuration Files" in captured.out

    def test_display_dependencies_status(self, capsys):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        deps = {
            "dependencies": {
                "python-dotenv": True,
                "cased-kit": False,
                "openai": False,
                "anthropic": True,
                "google-generativeai": False,
                "numpy": True,
                "matplotlib": False,
                "pandas": True,
                "pytest": True,
                "pylint": False,
                "black": True,
                "mypy": False,
                "fastapi": True,
                "uvicorn": True,
            },
            "available_count": 7,
            "total_count": 14,
            "success_rate": 50.0,
        }
        reporter._display_dependencies_status(deps)
        captured = capsys.readouterr()
        assert "7/14" in captured.out
        assert "50.0%" in captured.out


@pytest.mark.unit
class TestDisplaySummary:
    """Tests for _display_summary with various health scores."""

    def _make_report(self, venv=True, src=True, pkg=True, dep_rate=90.0, git=True, tools_any=True):
        return {
            "python_environment": {"virtual_env": venv},
            "project_structure": {"src_exists": src, "codomyrmex_package": pkg},
            "dependencies": {"success_rate": dep_rate},
            "git_status": {"is_git_repo": git},
            "external_tools": {"git": tools_any, "docker": False},
        }

    def test_excellent_health(self, capsys):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        report = self._make_report()
        reporter._display_summary(report)
        captured = capsys.readouterr()
        assert "100.0%" in captured.out

    def test_fair_health_with_recommendations(self, capsys):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        report = self._make_report(venv=False, dep_rate=50.0, git=False)
        reporter._display_summary(report)
        captured = capsys.readouterr()
        assert "Recommendations" in captured.out
        assert "virtual environment" in captured.out
        assert "git init" in captured.out

    def test_needs_attention_health(self, capsys):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        report = self._make_report(
            venv=False, src=False, pkg=False, dep_rate=10.0, git=False, tools_any=False,
        )
        reporter._display_summary(report)
        captured = capsys.readouterr()
        assert "0.0%" in captured.out

    def test_docker_recommendation(self, capsys):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter()
        report = self._make_report()
        report["external_tools"]["docker"] = False
        reporter._display_summary(report)
        captured = capsys.readouterr()
        assert "Docker" in captured.out


@pytest.mark.unit
class TestExportReport:
    """Tests for export_report."""

    def test_export_with_custom_filename(self, tmp_path):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter(project_root=tmp_path)
        result = reporter.export_report(filename="test_report.json")
        assert result == str(tmp_path / "test_report.json")
        assert (tmp_path / "test_report.json").exists()

        # Verify JSON is valid
        with open(tmp_path / "test_report.json") as f:
            data = json.load(f)
        assert "timestamp" in data
        assert "python_environment" in data

    def test_export_default_filename(self, tmp_path):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter(project_root=tmp_path)
        result = reporter.export_report()
        assert result != ""
        assert "codomyrmex_status_report_" in result
        assert result.endswith(".json")
        assert Path(result).exists()

    def test_export_to_unwritable_subdir_returns_empty(self, tmp_path):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        # Use an existing directory but request writing into a nonexistent subdirectory
        # by embedding a path separator in the filename, so open() fails.
        reporter = StatusReporter(project_root=tmp_path)
        result = reporter.export_report(filename="nonexistent_subdir/out.json")
        assert result == ""

    def test_export_json_contains_all_sections(self, tmp_path):
        from codomyrmex.system_discovery.reporting.status_reporter import (
            StatusReporter,
        )

        reporter = StatusReporter(project_root=tmp_path)
        result = reporter.export_report(filename="full.json")
        with open(result) as f:
            data = json.load(f)
        for key in [
            "timestamp",
            "python_environment",
            "project_structure",
            "dependencies",
            "git_status",
            "external_tools",
        ]:
            assert key in data, f"Missing key: {key}"
