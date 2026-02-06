import unittest
from concurrent.futures import Future
from unittest.mock import MagicMock, patch

import pytest

from codomyrmex.git_operations.core.repository import (
    Repository,
    RepositoryManager,
    RepositoryType,
)


@pytest.mark.unit
class TestRepositoryPerformance(unittest.TestCase):
    def setUp(self):
        self.manager = RepositoryManager(library_file="/tmp/dummy", base_path="/tmp/repos")
        # Mock repositories
        self.repo1 = Repository(RepositoryType.OWN, "owner", "repo1", "url1", "desc", "path1")
        self.repo2 = Repository(RepositoryType.OWN, "owner", "repo2", "url2", "desc", "path2")
        self.manager.repositories = {
            "owner/repo1": self.repo1,
            "owner/repo2": self.repo2
        }

    @patch('codomyrmex.git_operations.core.repository.ThreadPoolExecutor')
    @patch('codomyrmex.git_operations.core.repository.as_completed')
    def test_bulk_clone_parallel(self, mock_as_completed, mock_executor):
        # Setup mocks
        mock_pool = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_pool

        f1 = Future()
        f1.set_result(True)
        f2 = Future()
        f2.set_result(True)

        mock_pool.submit.side_effect = [f1, f2]
        mock_as_completed.return_value = [f1, f2]

        # Test
        self.manager.bulk_clone(max_workers=2)

        # Verify
        self.assertEqual(mock_pool.submit.call_count, 2)
        mock_executor.assert_called_with(max_workers=2)

    @patch('codomyrmex.git_operations.core.repository.ThreadPoolExecutor')
    @patch('codomyrmex.git_operations.core.repository.as_completed')
    @patch('codomyrmex.git_operations.core.repository.is_git_repository')
    def test_bulk_update_parallel(self, mock_is_git, mock_as_completed, mock_executor):
        # Setup mocks
        mock_is_git.return_value = True # ensure they are treated as existing locally
        mock_pool = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_pool

        f1 = Future()
        f1.set_result(True)
        f2 = Future()
        f2.set_result(True)

        mock_pool.submit.side_effect = [f1, f2]
        mock_as_completed.return_value = [f1, f2]

        # Test
        self.manager.bulk_update(max_workers=2)

        # Verify
        self.assertEqual(mock_pool.submit.call_count, 2)
        mock_executor.assert_called_with(max_workers=2)

if __name__ == '__main__':
    unittest.main()
