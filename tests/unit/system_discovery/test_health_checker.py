"""Tests for codomyrmex.system_discovery.core.health_checker module.

Covers:
- SystemHealthChecker.check_git_status (zero-mock policy applied)
"""

import subprocess

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
