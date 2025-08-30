"""
Unit tests for Repository Manager

Tests the repository library management functionality including
loading, searching, and Git operations integration.
"""

import unittest
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codomyrmex.git_operations.repository_manager import (
    RepositoryManager, Repository, RepositoryType
)


class TestRepositoryManager(unittest.TestCase):
    """Test cases for Repository Manager."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
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
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
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
        
        self.assertEqual(repo.full_name, "testuser/testrepo")
        self.assertTrue(repo.is_development_repo)
        self.assertFalse(repo.is_readonly_repo)
    
    def test_repository_manager_initialization(self):
        """Test RepositoryManager initialization."""
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )
        
        self.assertEqual(len(manager.repositories), 3)
        self.assertIn("testuser/testrepo", manager.repositories)
        self.assertIn("external/library", manager.repositories)
        self.assertIn("upstream/project", manager.repositories)
    
    def test_list_repositories(self):
        """Test listing repositories."""
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )
        
        # List all repositories
        all_repos = manager.list_repositories()
        self.assertEqual(len(all_repos), 3)
        
        # List by type
        own_repos = manager.list_repositories(RepositoryType.OWN)
        self.assertEqual(len(own_repos), 1)
        self.assertEqual(own_repos[0].full_name, "testuser/testrepo")
        
        use_repos = manager.list_repositories(RepositoryType.USE)
        self.assertEqual(len(use_repos), 1)
        self.assertEqual(use_repos[0].full_name, "external/library")
        
        fork_repos = manager.list_repositories(RepositoryType.FORK)
        self.assertEqual(len(fork_repos), 1)
        self.assertEqual(fork_repos[0].full_name, "upstream/project")
    
    def test_get_repository(self):
        """Test getting a specific repository."""
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )
        
        # Get existing repository
        repo = manager.get_repository("testuser/testrepo")
        self.assertIsNotNone(repo)
        self.assertEqual(repo.owner, "testuser")
        self.assertEqual(repo.name, "testrepo")
        
        # Get non-existing repository
        repo = manager.get_repository("nonexistent/repo")
        self.assertIsNone(repo)
    
    def test_search_repositories(self):
        """Test searching repositories."""
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )
        
        # Search by name
        results = manager.search_repositories("testrepo")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].full_name, "testuser/testrepo")
        
        # Search by owner
        results = manager.search_repositories("external")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].full_name, "external/library")
        
        # Search by description
        results = manager.search_repositories("library")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].full_name, "external/library")
        
        # Search with no results
        results = manager.search_repositories("nonexistent")
        self.assertEqual(len(results), 0)
    
    def test_get_local_path(self):
        """Test getting local path for repository."""
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )
        
        repo = manager.get_repository("testuser/testrepo")
        local_path = manager.get_local_path(repo)
        
        expected_path = Path(self.base_path) / "testuser/testrepo"
        self.assertEqual(local_path, expected_path)
    
    @patch('codomyrmex.git_operations.repository_manager.clone_repository')
    @patch('codomyrmex.git_operations.repository_manager.get_current_branch')
    @patch('codomyrmex.git_operations.repository_manager.create_branch')
    def test_clone_repository_success(self, mock_create_branch, mock_get_current_branch, mock_clone):
        """Test successful repository cloning."""
        mock_clone.return_value = True
        mock_get_current_branch.return_value = "main"
        mock_create_branch.return_value = True
        
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )
        
        success = manager.clone_repository("testuser/testrepo")
        
        self.assertTrue(success)
        mock_clone.assert_called_once()
        
        # Verify clone was called with correct parameters
        args, kwargs = mock_clone.call_args
        self.assertEqual(args[0], "https://github.com/testuser/testrepo.git")
        self.assertTrue(args[1].endswith("testuser/testrepo"))
    
    @patch('codomyrmex.git_operations.repository_manager.clone_repository')
    def test_clone_repository_failure(self, mock_clone):
        """Test failed repository cloning."""
        mock_clone.return_value = False
        
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )
        
        success = manager.clone_repository("testuser/testrepo")
        
        self.assertFalse(success)
        mock_clone.assert_called_once()
    
    def test_clone_nonexistent_repository(self):
        """Test cloning non-existent repository."""
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )
        
        success = manager.clone_repository("nonexistent/repo")
        
        self.assertFalse(success)
    
    @patch('codomyrmex.git_operations.repository_manager.is_git_repository')
    @patch('codomyrmex.git_operations.repository_manager.pull_changes')
    @patch('codomyrmex.git_operations.repository_manager.get_current_branch')
    def test_update_repository_success(self, mock_get_branch, mock_pull, mock_is_git):
        """Test successful repository update."""
        mock_is_git.return_value = True
        mock_get_branch.return_value = "main"
        mock_pull.return_value = True
        
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )
        
        success = manager.update_repository("testuser/testrepo")
        
        self.assertTrue(success)
        mock_pull.assert_called_once_with("origin", "main", unittest.mock.ANY)
    
    @patch('codomyrmex.git_operations.repository_manager.is_git_repository')
    def test_update_repository_not_cloned(self, mock_is_git):
        """Test updating repository that's not cloned locally."""
        mock_is_git.return_value = False
        
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )
        
        success = manager.update_repository("testuser/testrepo")
        
        self.assertFalse(success)
    
    @patch('codomyrmex.git_operations.repository_manager.is_git_repository')
    @patch('codomyrmex.git_operations.repository_manager.get_status')
    @patch('codomyrmex.git_operations.repository_manager.get_current_branch')
    def test_get_repository_status(self, mock_get_branch, mock_get_status, mock_is_git):
        """Test getting repository status."""
        mock_is_git.return_value = True
        mock_get_branch.return_value = "main"
        mock_get_status.return_value = {"clean": True}
        
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )
        
        status = manager.get_repository_status("testuser/testrepo")
        
        self.assertIsNotNone(status)
        self.assertEqual(status["repository"], "testuser/testrepo")
        self.assertEqual(status["branch"], "main")
        self.assertEqual(status["type"], "OWN")
        self.assertTrue(status["is_development"])
        self.assertEqual(status["status"], {"clean": True})
    
    @patch('codomyrmex.git_operations.repository_manager.is_git_repository')
    def test_get_repository_status_not_cloned(self, mock_is_git):
        """Test getting status of repository that's not cloned."""
        mock_is_git.return_value = False
        
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )
        
        status = manager.get_repository_status("testuser/testrepo")
        
        self.assertIsNotNone(status)
        self.assertIn("error", status)
        self.assertEqual(status["error"], "Repository not found locally")
    
    @patch('codomyrmex.git_operations.repository_manager.RepositoryManager.clone_repository')
    def test_bulk_clone(self, mock_clone):
        """Test bulk cloning repositories."""
        mock_clone.side_effect = [True, False, True]  # Mixed results
        
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )
        
        results = manager.bulk_clone()
        
        self.assertEqual(len(results), 3)
        self.assertEqual(sum(results.values()), 2)  # 2 successful
        self.assertEqual(mock_clone.call_count, 3)
    
    @patch('codomyrmex.git_operations.repository_manager.RepositoryManager.update_repository')
    @patch('codomyrmex.git_operations.repository_manager.is_git_repository')
    def test_bulk_update(self, mock_is_git, mock_update):
        """Test bulk updating repositories."""
        mock_is_git.side_effect = [True, False, True]  # Only 2 repos are cloned
        mock_update.side_effect = [True, True]  # Both updates successful
        
        manager = RepositoryManager(
            library_file=self.library_file,
            base_path=self.base_path
        )
        
        results = manager.bulk_update()
        
        self.assertEqual(len(results), 3)
        self.assertEqual(sum(results.values()), 2)  # 2 successful
        self.assertEqual(mock_update.call_count, 2)  # Only called for cloned repos
    
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
        self.assertEqual(len(manager.repositories), 0)
    
    def test_nonexistent_library_file(self):
        """Test handling of non-existent library file."""
        manager = RepositoryManager(
            library_file="/nonexistent/file.txt",
            base_path=self.base_path
        )
        
        # Should handle missing file gracefully
        self.assertEqual(len(manager.repositories), 0)
    
    def test_repository_type_properties(self):
        """Test repository type properties."""
        # Test OWN repository
        own_repo = Repository(
            repo_type=RepositoryType.OWN,
            owner="test", name="repo", url="url", 
            description="desc", local_path_suggestion="path"
        )
        self.assertTrue(own_repo.is_development_repo)
        self.assertFalse(own_repo.is_readonly_repo)
        
        # Test USE repository
        use_repo = Repository(
            repo_type=RepositoryType.USE,
            owner="test", name="repo", url="url",
            description="desc", local_path_suggestion="path"
        )
        self.assertFalse(use_repo.is_development_repo)
        self.assertTrue(use_repo.is_readonly_repo)
        
        # Test FORK repository
        fork_repo = Repository(
            repo_type=RepositoryType.FORK,
            owner="test", name="repo", url="url",
            description="desc", local_path_suggestion="path"
        )
        self.assertTrue(fork_repo.is_development_repo)
        self.assertFalse(fork_repo.is_readonly_repo)


if __name__ == '__main__':
    unittest.main()
