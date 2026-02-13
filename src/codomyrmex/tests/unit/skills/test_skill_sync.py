"""Tests for SkillSync — Zero-Mock implementation.

Uses real git operations (git init, etc.) and temporary directories.
Tests that require network access to clone remote repos are skipped
when git is not available or network is unreachable.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from codomyrmex.skills.skill_sync import SkillSync

_GIT_AVAILABLE = shutil.which("git") is not None


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def _init_bare_repo(path: Path) -> None:
    """Create a minimal bare git repo at *path* for testing."""
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "init", "--bare"],
        cwd=str(path),
        capture_output=True,
        check=True,
    )


def _init_repo_with_commit(path: Path) -> None:
    """Create a git repo with a single commit at *path*."""
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=str(path), capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(path), capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=str(path), capture_output=True, check=True,
    )
    (path / "README.md").write_text("# test\n")
    subprocess.run(["git", "add", "."], cwd=str(path), capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=str(path), capture_output=True, check=True,
    )


# ---- Tests ----


@pytest.mark.unit
def test_check_upstream_status_not_exists(temp_dir):
    """Test checking status when upstream doesn't exist."""
    sync = SkillSync(
        temp_dir / "upstream",
        "https://github.com/test/repo",
        "main",
    )

    status = sync.check_upstream_status()
    assert status["exists"] is False
    assert status["is_git_repo"] is False


@pytest.mark.skipif(not _GIT_AVAILABLE, reason="git not installed")
def test_clone_upstream(temp_dir):
    """Test cloning upstream repository from a local bare repo."""
    bare = temp_dir / "bare_origin.git"
    _init_repo_with_commit(bare)

    upstream_dir = temp_dir / "skills" / "upstream"
    sync = SkillSync(upstream_dir, str(bare), "main")

    result = sync.clone_upstream()
    assert result is True
    assert upstream_dir.exists()


@pytest.mark.skipif(not _GIT_AVAILABLE, reason="git not installed")
def test_clone_upstream_force(temp_dir):
    """Test force-cloning upstream repository."""
    bare = temp_dir / "bare_origin.git"
    _init_repo_with_commit(bare)

    upstream_dir = temp_dir / "skills" / "upstream"
    upstream_dir.mkdir(parents=True, exist_ok=True)
    (upstream_dir / "stale_file.txt").write_text("stale")

    sync = SkillSync(upstream_dir, str(bare), "main")

    result = sync.clone_upstream(force=True)
    assert result is True
    assert upstream_dir.exists()


@pytest.mark.skipif(not _GIT_AVAILABLE, reason="git not installed")
def test_pull_upstream(temp_dir):
    """Test pulling upstream changes from a real cloned repo."""
    bare = temp_dir / "bare_origin.git"
    _init_repo_with_commit(bare)

    upstream_dir = temp_dir / "skills" / "upstream"
    sync = SkillSync(upstream_dir, str(bare), "main")
    sync.clone_upstream()

    result = sync.pull_upstream()
    assert result is True


@pytest.mark.skipif(not _GIT_AVAILABLE, reason="git not installed")
def test_pull_upstream_not_git(temp_dir):
    """Test pulling when directory exists but is not a git repo."""
    bare = temp_dir / "bare_origin.git"
    _init_repo_with_commit(bare)

    upstream_dir = temp_dir / "skills" / "upstream"
    upstream_dir.mkdir(parents=True)
    # Directory exists but is NOT a git repo → should re-clone
    sync = SkillSync(upstream_dir, str(bare), "main")

    result = sync.pull_upstream()
    assert result is True


@pytest.mark.skipif(not _GIT_AVAILABLE, reason="git not installed")
def test_get_upstream_version(temp_dir):
    """Test getting upstream version (commit hash)."""
    bare = temp_dir / "bare_origin.git"
    _init_repo_with_commit(bare)

    upstream_dir = temp_dir / "skills" / "upstream"
    sync = SkillSync(upstream_dir, str(bare), "main")
    sync.clone_upstream()

    version = sync.get_upstream_version()
    assert isinstance(version, str)
    assert len(version) >= 7  # short SHA or full
