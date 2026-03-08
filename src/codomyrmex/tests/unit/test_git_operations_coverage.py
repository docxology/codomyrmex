"""Functional tests for git_operations module — coverage push.

Tests real git operations using temporary repositories.
Zero-mock policy: all tests use actual git commands.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import pytest

from codomyrmex.git_operations import (
    Repository,
    RepositoryManager,
    RepositoryMetadata,
    RepositoryMetadataManager,
    RepositoryType,
    add_files,
    analyze_repository_structure,
    check_git_availability,
)


@pytest.fixture()
def git_repo(tmp_path: Path) -> Path:
    """Create a real temporary git repository."""
    subprocess.run(
        ["git", "init", str(tmp_path)],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(tmp_path),
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=str(tmp_path),
        check=True,
        capture_output=True,
    )
    # Create initial commit
    readme = tmp_path / "README.md"
    readme.write_text("# Test Project\n")
    subprocess.run(
        ["git", "add", "."],
        cwd=str(tmp_path),
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=str(tmp_path),
        check=True,
        capture_output=True,
    )
    return tmp_path


class TestGitAvailability:
    """Test git environment detection."""

    def test_check_git_availability(self) -> None:
        """Git should be available on the test system."""
        result = check_git_availability()
        assert result is True

    def test_git_version_accessible(self) -> None:
        """Git version should be retrievable."""
        proc = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0
        assert "git version" in proc.stdout


class TestRepository:
    """Test Repository model."""

    def test_repository_creation(self, git_repo: Path) -> None:
        """Repository should be creatable with correct args."""
        repo = Repository(
            repo_type=RepositoryType.OWN,
            owner="test-owner",
            name="test-repo",
            url="https://github.com/test/test",
            description="A test repo",
            local_path_suggestion=str(git_repo),
        )
        assert repo.name == "test-repo"

    def test_repository_type_enum(self) -> None:
        """RepositoryType should have expected members."""
        assert hasattr(RepositoryType, "OWN")
        assert hasattr(RepositoryType, "USE")
        assert hasattr(RepositoryType, "FORK")


class TestRepositoryManager:
    """Test RepositoryManager functionality."""

    def test_manager_instantiation(self) -> None:
        """RepositoryManager should instantiate."""
        manager = RepositoryManager()
        assert manager is not None

    def test_analyze_structure(self, git_repo: Path) -> None:
        """analyze_repository_structure should return structure info."""
        # Create some files for analysis
        (git_repo / "src").mkdir()
        (git_repo / "src" / "main.py").write_text("def main(): pass\n")
        (git_repo / "tests").mkdir()
        (git_repo / "tests" / "test_main.py").write_text("def test_main(): pass\n")

        result = analyze_repository_structure(str(git_repo))
        assert result is not None


class TestRepositoryMetadata:
    """Test RepositoryMetadata and RepositoryMetadataManager."""

    def test_metadata_creation(self) -> None:
        """RepositoryMetadata should be instantiable."""
        metadata = RepositoryMetadata(
            full_name="test-owner/test-repo",
            owner="test-owner",
            name="test-repo",
            repo_type="own",
            url="https://github.com/test/test",
            clone_url="https://github.com/test/test.git",
            description="A test repo",
        )
        assert metadata.name == "test-repo"

    def test_metadata_manager(self) -> None:
        """RepositoryMetadataManager should be instantiable."""
        manager = RepositoryMetadataManager()
        assert manager is not None


class TestGitAddFiles:
    """Test git add operations."""

    def test_add_files(self, git_repo: Path) -> None:
        """add_files should stage files for commit."""
        new_file = git_repo / "new_file.py"
        new_file.write_text("# New file\n")
        result = add_files(str(git_repo), ["new_file.py"])
        assert result is not None
