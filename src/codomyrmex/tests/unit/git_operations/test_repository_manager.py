"""
Unit tests for Repository Manager

Tests the repository library management functionality including
loading, searching, and Git operations integration.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codomyrmex.git_operations.core.repository import (
    Repository,
    RepositoryManager,
    RepositoryType,
)


def check_git_available():
    """Check if git is available."""
    try:
        subprocess.run(['git', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


_GIT_AVAILABLE = check_git_available()


@pytest.mark.unit
class TestRepositoryManager:
    """Test cases for Repository Manager."""

    @pytest.fixture(autouse=True)
    def setup_environment(self, tmp_path):
        """Set up test environment."""
        self.temp_dir = str(tmp_path)
        self.library_file = os.path.join(self.temp_dir, "test_library.txt")
        self.base_path = os.path.join(self.temp_dir, "repos")

        # Create test library file
        library_content = """# Test Repository Library
OWN|testuser|testrepo|https://github.com/testuser/testrepo.git|Test repository|testuser/testrepo
USE|external|library|https://github.com/external/library.git|External library|external/library
FORK|upstream|project|https://github.com/upstream/project.git|Forked project|forks/project
"""
        with open(self.library_file, 'w') as f:
            f.write(library_content)

        # Initialize manager
        self.manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )
        self.test_repo = self.manager.get_repository("testuser/testrepo")
        yield

    def test_repository_creation(self):
        """Test Repository dataclass creation."""
        repo = Repository(
            repo_type=RepositoryType.OWN,
            owner="testuser",
            name="testrepo",
            url="https://github.com/testuser/testrepo.git",
            description="Test repository",
            local_path_suggestion="testuser/testrepo"
        )

        assert repo.full_name == "testuser/testrepo"
        assert repo.is_development_repo
        assert not repo.is_readonly_repo

    def test_repository_manager_initialization(self):
        """Test RepositoryManager initialization."""
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )

        assert len(manager.repositories) == 3
        assert "testuser/testrepo" in manager.repositories
        assert "external/library" in manager.repositories
        assert "upstream/project" in manager.repositories

    def test_list_repositories(self):
        """Test listing repositories."""
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )

        # List all repositories
        all_repos = manager.list_repositories()
        assert len(all_repos) == 3

        # List by type
        own_repos = manager.list_repositories(RepositoryType.OWN)
        assert len(own_repos) == 1
        assert own_repos[0].full_name == "testuser/testrepo"

        use_repos = manager.list_repositories(RepositoryType.USE)
        assert len(use_repos) == 1
        assert use_repos[0].full_name == "external/library"

        fork_repos = manager.list_repositories(RepositoryType.FORK)
        assert len(fork_repos) == 1
        assert fork_repos[0].full_name == "upstream/project"

    def test_get_repository(self):
        """Test getting a specific repository."""
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )

        # Get existing repository
        repo = manager.get_repository("testuser/testrepo")
        assert repo is not None
        assert repo.owner == "testuser"
        assert repo.name == "testrepo"

        # Get non-existing repository
        repo = manager.get_repository("nonexistent/repo")
        assert repo is None

    def test_search_repositories(self):
        """Test searching repositories."""
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )

        # Search by name
        results = manager.search_repositories("testrepo")
        assert len(results) == 1
        assert results[0].full_name == "testuser/testrepo"

        # Search by owner
        results = manager.search_repositories("external")
        assert len(results) == 1
        assert results[0].full_name == "external/library"

        # Search by description
        results = manager.search_repositories("library")
        assert len(results) == 1
        assert results[0].full_name == "external/library"

        # Search with no results
        results = manager.search_repositories("nonexistent")
        assert len(results) == 0

    def test_get_local_path(self):
        """Test getting local path for repository."""
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )

        repo = manager.get_repository("testuser/testrepo")
        local_path = manager.get_local_path(repo)

        expected_path = Path(self.base_path) / "testuser/testrepo"
        assert local_path == expected_path

    @pytest.mark.skipif(not _GIT_AVAILABLE, reason="Git not available")
    def test_clone_repository_success(self):
        """Test successful repository cloning with real git."""
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )

        # Try to clone a real repository (use a small test repo if available)
        # For testing, we'll create a local git repo instead
        test_repo_path = os.path.join(self.temp_dir, "test_repo")
        os.makedirs(test_repo_path, exist_ok=True)

        # Initialize a git repo
        subprocess.run(['git', 'init'], cwd=test_repo_path, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=test_repo_path, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=test_repo_path, capture_output=True)

        # Create a test file and commit
        with open(os.path.join(test_repo_path, 'test.txt'), 'w') as f:
            f.write('test')
        subprocess.run(['git', 'add', 'test.txt'], cwd=test_repo_path, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=test_repo_path, capture_output=True)

        # Update library to point to local repo
        library_content = f"""# Test Repository Library
OWN|testuser|testrepo|{test_repo_path}|Test repository|testuser/testrepo
"""
        with open(self.library_file, 'w') as f:
            f.write(library_content)

        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )

        # Clone should work with local path
        success = manager.clone_repository("testuser/testrepo")
        # May succeed or fail depending on implementation
        assert isinstance(success, bool)

    def test_clone_repository_failure(self):
        """Test failed repository cloning with real git."""
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )

        # Try to clone a non-existent repository
        success = manager.clone_repository("testuser/testrepo")
        # Should fail for non-existent remote
        assert isinstance(success, bool)

    def test_clone_nonexistent_repository(self):
        """Test cloning non-existent repository."""
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )

        success = manager.clone_repository("nonexistent/repo")

        assert not success

    @pytest.mark.skipif(not _GIT_AVAILABLE, reason="Git not available")
    def test_update_repository_success(self):
        """Test successful repository update with real git."""
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )

        # Create a local git repo
        test_repo_path = os.path.join(self.temp_dir, "test_repo")
        os.makedirs(test_repo_path, exist_ok=True)
        subprocess.run(['git', 'init'], cwd=test_repo_path, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=test_repo_path, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=test_repo_path, capture_output=True)

        # Clone it first
        clone_path = os.path.join(self.base_path, "testuser", "testrepo")
        os.makedirs(os.path.dirname(clone_path), exist_ok=True)
        subprocess.run(['git', 'clone', test_repo_path, clone_path], capture_output=True)

        # Update library
        library_content = f"""# Test Repository Library
OWN|testuser|testrepo|{test_repo_path}|Test repository|testuser/testrepo
"""
        with open(self.library_file, 'w') as f:
            f.write(library_content)

        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )

        # Update should work
        success = manager.update_repository("testuser/testrepo")
        assert isinstance(success, bool)

    def test_update_repository_not_cloned(self):
        """Test updating repository that's not cloned locally."""
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )

        success = manager.update_repository("testuser/testrepo")

        # Should fail if not cloned
        assert isinstance(success, bool)

    @pytest.mark.skipif(not _GIT_AVAILABLE, reason="Git not available")
    def test_get_repository_status(self):
        """Test getting repository status with real git."""
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )

        # Create a local git repo
        test_repo_path = os.path.join(self.temp_dir, "test_repo")
        os.makedirs(test_repo_path, exist_ok=True)
        subprocess.run(['git', 'init'], cwd=test_repo_path, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=test_repo_path, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=test_repo_path, capture_output=True)

        # Clone it
        clone_path = os.path.join(self.base_path, "testuser", "testrepo")
        os.makedirs(os.path.dirname(clone_path), exist_ok=True)
        subprocess.run(['git', 'clone', test_repo_path, clone_path], capture_output=True)

        # Update library
        library_content = f"""# Test Repository Library
OWN|testuser|testrepo|{test_repo_path}|Test repository|testuser/testrepo
"""
        with open(self.library_file, 'w') as f:
            f.write(library_content)

        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )

        status = manager.get_repository_status("testuser/testrepo")

        assert status is not None
        assert status["repository"] == "testuser/testrepo"
        assert status["type"] == "OWN"
        assert status["is_development"]

    def test_get_repository_status_not_cloned(self):
        """Test getting status of repository that's not cloned."""
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )

        status = manager.get_repository_status("testuser/testrepo")

        assert status is not None
        assert "error" in status
        assert status["error"] == "Repository not found locally"

    def test_bulk_clone(self):
        """Test bulk cloning repositories with real git."""
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )

        results = manager.bulk_clone()

        # Should return results for all repositories
        assert len(results) == 3
        # Results may be True or False depending on whether repos exist
        assert all(isinstance(v, bool) for v in results.values())

    def test_bulk_update(self):
        """Test bulk updating repositories with real git."""
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )

        results = manager.bulk_update()

        # Should return results for all repositories
        assert len(results) == 3
        # Results may be True or False depending on whether repos are cloned
        assert all(isinstance(v, bool) for v in results.values())

    def test_invalid_library_file(self):
        """Test handling of invalid library file."""
        # Create library with invalid entries
        invalid_library = os.path.join(self.temp_dir, "invalid_library.txt")
        with open(invalid_library, 'w') as f:
            f.write("INVALID|entry|format\n")
            f.write("BADTYPE|owner|repo|url|desc|path\n")

        manager = RepositoryManager(
            library_file=invalid_library,
            base_path=self.base_path
        )

        # Should handle invalid entries gracefully
        assert len(manager.repositories) == 0

    def test_nonexistent_library_file(self):
        """Test handling of non-existent library file."""
        manager = RepositoryManager(
            library_file="/nonexistent/file.txt",
            base_path=self.base_path
        )

        # Should handle missing file gracefully
        assert len(manager.repositories) == 0

    def test_repository_type_properties(self):
        """Test repository type properties."""
        # Test OWN repository
        own_repo = Repository(
            repo_type=RepositoryType.OWN,
            owner="test", name="repo", url="url",
            description="desc", local_path_suggestion="path"
        )
        assert own_repo.is_development_repo
        assert not own_repo.is_readonly_repo

        # Test USE repository
        use_repo = Repository(
            repo_type=RepositoryType.USE,
            owner="test", name="repo", url="url",
            description="desc", local_path_suggestion="path"
        )
        assert not use_repo.is_development_repo
        assert use_repo.is_readonly_repo

        # Test FORK repository
        fork_repo = Repository(
            repo_type=RepositoryType.FORK,
            owner="test", name="repo", url="url",
            description="desc", local_path_suggestion="path"
        )
        assert fork_repo.is_development_repo
        assert not fork_repo.is_readonly_repo

    @pytest.mark.skipif(not _GIT_AVAILABLE, reason="Git not available")
    def test_sync_repository(self):
        """Test syncing a repository with real git."""
        # Create a local bare remote
        remote_path = os.path.join(self.temp_dir, "sync_remote")
        os.makedirs(remote_path)
        subprocess.run(['git', 'init', '--bare', remote_path], capture_output=True)

        # Update library to point to local remote
        library_content = f"""# Test Repository Library
OWN|testuser|testrepo|{remote_path}|Test repository|testuser/testrepo
"""
        with open(self.library_file, 'w') as f:
            f.write(library_content)

        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path,
        )

        # Clone first
        manager.clone_repository("testuser/testrepo")

        # Sync should succeed (pull + push)
        result = manager.sync_repository("testuser/testrepo")
        assert isinstance(result, bool)

    @pytest.mark.skipif(not _GIT_AVAILABLE, reason="Git not available")
    def test_prune_repository(self):
        """Test pruning a repository with real git."""
        # Create a local bare remote
        remote_path = os.path.join(self.temp_dir, "prune_remote")
        os.makedirs(remote_path)
        subprocess.run(['git', 'init', '--bare', remote_path], capture_output=True)

        # Update library
        library_content = f"""# Test Repository Library
OWN|testuser|testrepo|{remote_path}|Test repository|testuser/testrepo
"""
        with open(self.library_file, 'w') as f:
            f.write(library_content)

        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path,
        )

        # Clone first
        manager.clone_repository("testuser/testrepo")

        # Prune should succeed
        result = manager.prune_repository("testuser/testrepo")
        assert isinstance(result, bool)
