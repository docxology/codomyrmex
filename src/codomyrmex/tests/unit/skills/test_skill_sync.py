"""Tests for SkillSync."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from codomyrmex.skills.skill_sync import SkillSync


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


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


@patch("codomyrmex.skills.skill_sync.clone_repository")
def test_clone_upstream(mock_clone, temp_dir):
    """Test cloning upstream repository."""
    mock_clone.return_value = True

    sync = SkillSync(
        temp_dir / "upstream",
        "https://github.com/test/repo",
        "main",
    )

    result = sync.clone_upstream()
    assert result is True
    mock_clone.assert_called_once()


@patch("codomyrmex.skills.skill_sync.clone_repository")
def test_clone_upstream_force(mock_clone, temp_dir):
    """Test force cloning upstream repository."""
    mock_clone.return_value = True

    upstream_dir = temp_dir / "upstream"
    upstream_dir.mkdir()

    sync = SkillSync(upstream_dir, "https://github.com/test/repo", "main")

    result = sync.clone_upstream(force=True)
    assert result is True
    mock_clone.assert_called_once()


@patch("codomyrmex.skills.skill_sync.pull_changes")
@patch("codomyrmex.skills.skill_sync.is_git_repository")
def test_pull_upstream(mock_is_git, mock_pull, temp_dir):
    """Test pulling upstream changes."""
    mock_is_git.return_value = True
    mock_pull.return_value = True

    upstream_dir = temp_dir / "upstream"
    upstream_dir.mkdir()

    sync = SkillSync(upstream_dir, "https://github.com/test/repo", "main")

    result = sync.pull_upstream()
    assert result is True
    mock_pull.assert_called_once()


@patch("codomyrmex.skills.skill_sync.clone_repository")
@patch("codomyrmex.skills.skill_sync.is_git_repository")
def test_pull_upstream_not_git(mock_is_git, mock_clone, temp_dir):
    """Test pulling when directory is not a git repo."""
    mock_is_git.return_value = False
    mock_clone.return_value = True

    upstream_dir = temp_dir / "upstream"
    upstream_dir.mkdir()

    sync = SkillSync(upstream_dir, "https://github.com/test/repo", "main")

    result = sync.pull_upstream()
    assert result is True
    mock_clone.assert_called_once()


@patch("subprocess.run")
def test_get_upstream_version(mock_subprocess, temp_dir):
    """Test getting upstream version."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "abc123def\n"
    mock_subprocess.return_value = mock_result

    upstream_dir = temp_dir / "upstream"
    upstream_dir.mkdir()

    sync = SkillSync(upstream_dir, "https://github.com/test/repo", "main")

    # Mock is_git_repository
    with patch("codomyrmex.skills.skill_sync.is_git_repository", return_value=True):
        version = sync.get_upstream_version()
        assert version == "abc123def"

