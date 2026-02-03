import pytest

import unittest
from unittest.mock import MagicMock, patch
from codomyrmex.agents.git_agent import GitAgent
from codomyrmex.agents.core.base import AgentRequest
from codomyrmex.git_operations.core.repository import RepositoryManager

@pytest.mark.unit
class TestGitAgent(unittest.TestCase):
    def setUp(self):
        self.mock_repo_manager = MagicMock(spec=RepositoryManager)
        self.agent = GitAgent(repository_manager=self.mock_repo_manager)

    def test_sync_command(self):
        request = AgentRequest(prompt="sync: repository=owner/repo")
        response = self.agent.execute(request)
        
        self.mock_repo_manager.sync_repository.assert_called_with("owner/repo")
        self.assertIsNone(response.error)

    def test_prune_command(self):
        request = AgentRequest(prompt='{"action": "prune", "repository": "owner/repo"}')
        response = self.agent.execute(request)
        
        self.mock_repo_manager.prune_repository.assert_called_with("owner/repo")
        self.assertIsNone(response.error)

    @patch('codomyrmex.agents.git_agent.agent.clean_repository')
    @patch('codomyrmex.agents.git_agent.agent.RepositoryManager.get_local_path') # Patch get_local_path
    def test_clean_command(self, mock_get_path, mock_clean):
        # Mock repo lookup
        repo = MagicMock()
        self.mock_repo_manager.get_repository.return_value = repo
        self.mock_repo_manager.get_local_path.return_value = "/tmp/repo"
        mock_get_path.return_value = "/tmp/repo" # needed for the actual clean call? No, patch is on module

        request = AgentRequest(prompt="clean: repository=owner/repo, force=true")
        
        # We need to set the repo manager on the agent to use our mock with side effects if needed 
        # But we passed it in __init__, so self.agent.repo_manager IS self.mock_repo_manager
        
        self.agent.execute(request)
        
        self.mock_repo_manager.get_repository.assert_called_with("owner/repo")
        mock_clean.assert_called_with(force=True, directories=True, repository_path="/tmp/repo")

    @patch('codomyrmex.agents.git_agent.agent.add_remote')
    def test_add_remote_command(self, mock_add_remote):
        repo = MagicMock()
        self.mock_repo_manager.get_repository.return_value = repo
        self.mock_repo_manager.get_local_path.return_value = "/tmp/repo"
        
        request = AgentRequest(prompt="add_remote: repository=owner/repo, name=upstream, url=git@github.com:owner/repo.git")
        response = self.agent.execute(request)
        
        mock_add_remote.assert_called_with("upstream", "git@github.com:owner/repo.git", "/tmp/repo")
        self.assertIsNone(response.error)

    @patch('codomyrmex.agents.git_agent.agent.create_issue')
    def test_create_issue_command(self, mock_create):
        request = AgentRequest(prompt='{"action": "create_issue", "owner": "o", "repo_name": "r", "title": "t"}')
        self.agent.execute(request)
        
        mock_create.assert_called_with(
            owner="o", repo_name="r", title="t", body="", labels=None
        )

if __name__ == '__main__':
    unittest.main()
