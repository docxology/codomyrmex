import unittest
from unittest.mock import MagicMock, patch

import pytest

from codomyrmex.git_operations.cli.repo import (
    cmd_clean,
    cmd_prune,
    cmd_remote,
    cmd_sync,
)
from codomyrmex.git_operations.core.repository import RepositoryManager


@pytest.mark.unit
class TestRepoCLI(unittest.TestCase):
    def setUp(self):
        self.manager = MagicMock(spec=RepositoryManager)
        self.args = MagicMock()
        self.args.repository = "owner/repo"
        self.args.path = None
        self.args.verbose = False

        # Mock repo object
        self.repo = MagicMock()
        self.repo.full_name = "owner/repo"
        self.manager.get_repository.return_value = self.repo
        self.manager.get_local_path.return_value = "/tmp/repo"

    @patch('codomyrmex.git_operations.cli.repo.list_remotes')
    @patch('codomyrmex.git_operations.cli.repo.add_remote')
    @patch('codomyrmex.git_operations.cli.repo.remove_remote')
    @patch('codomyrmex.git_operations.cli.repo.prune_remote')
    @patch('codomyrmex.git_operations.cli.repo.Path')
    def test_cmd_remote(self, mock_path, mock_prune, mock_remove, mock_add, mock_list):
        mock_path.return_value.exists.return_value = True

        # Test List
        self.args.list = True
        self.args.add = None
        self.args.remove = None
        self.args.prune = None
        mock_list.return_value = [{"name": "origin", "url": "url"}]
        cmd_remote(self.manager, self.args)
        mock_list.assert_called()

        # Test Add
        self.args.list = False
        self.args.add = "upstream"
        self.args.url = "new_url"
        mock_add.return_value = True
        cmd_remote(self.manager, self.args)
        mock_add.assert_called_with("upstream", "new_url", "/tmp/repo")

        # Test Remove
        self.args.add = None
        self.args.remove = "upstream"
        mock_remove.return_value = True
        cmd_remote(self.manager, self.args)
        mock_remove.assert_called_with("upstream", "/tmp/repo")

        # Test Prune
        self.args.remove = None
        self.args.prune = "origin"
        mock_prune.return_value = True
        cmd_remote(self.manager, self.args)
        mock_prune.assert_called_with("origin", "/tmp/repo")

    def test_cmd_sync(self):
        self.manager.sync_repository.return_value = True
        cmd_sync(self.manager, self.args)
        self.manager.sync_repository.assert_called_with("owner/repo", None)

    def test_cmd_prune(self):
        self.manager.prune_repository.return_value = True
        cmd_prune(self.manager, self.args)
        self.manager.prune_repository.assert_called_with("owner/repo", None)

    @patch('codomyrmex.git_operations.cli.repo.clean_repository')
    def test_cmd_clean(self, mock_clean):
        self.args.force = False
        mock_clean.return_value = True
        cmd_clean(self.manager, self.args)
        mock_clean.assert_called_with(force=False, directories=True, repository_path="/tmp/repo")

if __name__ == '__main__':
    unittest.main()
