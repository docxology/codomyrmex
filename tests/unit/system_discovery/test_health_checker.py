"""Tests for codomyrmex.system_discovery.core.health_checker module.

Covers:
- SystemHealthChecker.check_git_status (zero-mock policy applied)
- SystemHealthChecker.get_system_status_dict
"""

import subprocess
import sys
from pathlib import Path

import pytest

from codomyrmex.system_discovery.core.health_checker import SystemHealthChecker


@pytest.mark.unit
class TestSystemHealthCheckerGitStatus:
    """Test the check_git_status method."""

    def test_not_a_git_repo(self, tmp_path, capsys):
        """Test output when directory is not a Git repository."""
        checker = SystemHealthChecker(tmp_path, tmp_path / "src", tmp_path / "tests")
        checker.check_git_status()
        out, _ = capsys.readouterr()
        assert "Not a git repository" in out

    def test_git_not_found(self, tmp_path, capsys, monkeypatch):
        """Test output when git command is not found in PATH."""
        monkeypatch.setenv("PATH", "")
        checker = SystemHealthChecker(tmp_path, tmp_path / "src", tmp_path / "tests")
        checker.check_git_status()
        out, _ = capsys.readouterr()
        assert "Git not found" in out

    def test_git_repo_clean(self, tmp_path, capsys):
        """Test output when in a clean Git repository."""
        # Initialize a real git repo
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Create a commit so we have a clean working tree and a current branch
        (tmp_path / "file.txt").write_text("hello")
        subprocess.run(
            ["git", "add", "file.txt"], cwd=tmp_path, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "init"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Ensure we're on a known branch name to test output parsing
        subprocess.run(
            ["git", "branch", "-M", "main"],
            cwd=tmp_path,
            check=False,
            capture_output=True,
        )

        checker = SystemHealthChecker(tmp_path, tmp_path / "src", tmp_path / "tests")
        checker.check_git_status()
        out, _ = capsys.readouterr()

        assert "Git repository initialized" in out
        assert "Working tree clean" in out
        assert "Current branch: main" in out

    def test_git_repo_uncommitted_changes(self, tmp_path, capsys):
        """Test output when Git repository has uncommitted changes."""
        # Initialize a real git repo
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Create a commit
        (tmp_path / "file.txt").write_text("hello")
        subprocess.run(
            ["git", "add", "file.txt"], cwd=tmp_path, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "init"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Create uncommitted changes (one new file, one modified file)
        (tmp_path / "file2.txt").write_text("hello2")
        (tmp_path / "file.txt").write_text("modified")

        checker = SystemHealthChecker(tmp_path, tmp_path / "src", tmp_path / "tests")
        checker.check_git_status()
        out, _ = capsys.readouterr()

        assert "Git repository initialized" in out
        assert "2 uncommitted changes" in out


@pytest.fixture
def health_checker(tmp_path: Path) -> SystemHealthChecker:
    """Provide a SystemHealthChecker instance with a temporary directory structure."""
    project_root = tmp_path / "project"
    project_root.mkdir()

    src_path = project_root / "src"
    src_path.mkdir()

    testing_path = project_root / "tests"
    testing_path.mkdir()

    # Create fake venv directory so venv_exists returns True
    venv_path = project_root / ".venv"
    venv_path.mkdir()

    return SystemHealthChecker(
        project_root=project_root, src_path=src_path, testing_path=testing_path
    )


def test_get_system_status_dict(health_checker: SystemHealthChecker) -> None:
    """Test get_system_status_dict returns correct structure and types."""
    status = health_checker.get_system_status_dict()

    # Verify main keys exist
    assert "python" in status
    assert "project" in status
    assert "dependencies" in status
    assert "git" in status

    # Check Python status dictionary
    assert "version" in status["python"]
    assert status["python"]["version"] == sys.version.split()[0]

    assert "executable" in status["python"]
    assert status["python"]["executable"] == sys.executable

    assert "virtual_env" in status["python"]
    assert isinstance(status["python"]["virtual_env"], bool)

    # Check Project status dictionary
    assert "src_exists" in status["project"]
    assert status["project"]["src_exists"] is True

    assert "tests_exist" in status["project"]
    assert status["project"]["tests_exist"] is True

    assert "venv_exists" in status["project"]
    assert status["project"]["venv_exists"] is True

    # Check dependencies dictionary structure against the source of truth.
    # get_system_status_dict deliberately skips fastapi (optional extra),
    # so only the remaining mapped dependencies must appear as booleans.
    from codomyrmex.system_discovery.core.health_checker import _DEP_MAPPING

    assert "fastapi" not in status["dependencies"]
    for dep in _DEP_MAPPING:
        if dep == "fastapi":
            continue
        assert dep in status["dependencies"]
        assert isinstance(status["dependencies"][dep], bool)

    # Check git dictionary
    assert "is_repo" in status["git"]
    assert isinstance(status["git"]["is_repo"], bool)

    # The tmp_path is not a git repo, so is_repo should be False
    assert status["git"]["is_repo"] is False
    # When is_repo is False, these keys aren't set
    assert "branch" not in status["git"]
    assert "clean" not in status["git"]


def test_get_system_status_dict_git_repo(
    health_checker: SystemHealthChecker, tmp_path: Path
) -> None:
    """Test git-related keys when executed within a git repository."""
    # Initialize a simple git repository in the tmp_path/project
    project_root = health_checker.project_root
    subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"], cwd=project_root, check=True
    )
    subprocess.run(["git", "config", "user.name", "test"], cwd=project_root, check=True)

    # Needs at least one commit for branch to show up
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "Initial commit"],
        cwd=project_root,
        check=True,
        capture_output=True,
    )

    # Switch to main branch to have deterministic output
    subprocess.run(
        ["git", "checkout", "-b", "main"],
        cwd=project_root,
        check=False,
        capture_output=True,
    )

    status = health_checker.get_system_status_dict()

    assert status["git"]["is_repo"] is True
    assert status["git"]["branch"] == "main"
    assert status["git"]["clean"] is True

    # Introduce an uncommitted change
    (project_root / "untracked.txt").write_text("hello")
    status = health_checker.get_system_status_dict()
    assert status["git"]["clean"] is False
