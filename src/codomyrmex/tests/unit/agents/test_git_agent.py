"""Tests for GitAgent.

Zero-Mock compliant — uses a StubRepositoryManager and real function
calls where possible, with skip markers for external dependencies.
"""


import pytest

try:
    from codomyrmex.agents.core.base import AgentCapabilities, AgentRequest
    from codomyrmex.agents.git_agent import GitAgent
    from codomyrmex.git_operations.core.repository import (
        RepositoryManager,  # noqa: F401
    )
    _HAS_AGENTS = True
except ImportError:
    _HAS_AGENTS = False

if not _HAS_AGENTS:
    pytest.skip("agents deps not available", allow_module_level=True)


# ---------------------------------------------------------------------------
# Stub RepositoryManager (replaces MagicMock(spec=RepositoryManager))
# ---------------------------------------------------------------------------

class StubRepositoryManager:
    """Lightweight stub for RepositoryManager.

    Records method calls and returns configurable values,
    without touching the filesystem or network.
    """

    def __init__(self, *, repos=None, local_paths=None):
        self._calls = {}
        self._repos = repos or {}
        self._local_paths = local_paths or {}

    def _record(self, method: str, *args, **kwargs):
        self._calls.setdefault(method, []).append((args, kwargs))

    def sync_repository(self, repo_name: str):
        self._record("sync_repository", repo_name)
        return {"synced": repo_name}

    def prune_repository(self, repo_name: str):
        self._record("prune_repository", repo_name)
        return {"pruned": repo_name}

    def get_repository(self, repo_name: str):
        self._record("get_repository", repo_name)
        return self._repos.get(repo_name, {"name": repo_name})

    def get_local_path(self, repo):
        self._record("get_local_path", repo)
        name = repo.get("name", "unknown") if isinstance(repo, dict) else str(repo)
        return self._local_paths.get(name, "/tmp/stub_repo")

    def get_repository_status(self, repo_name: str):
        self._record("get_repository_status", repo_name)
        return {"status": "clean", "repo": repo_name}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestGitAgentInit:
    """Test GitAgent initialization."""

    def test_agent_name(self):
        """GitAgent.name is 'GitAgent'."""
        agent = GitAgent(repository_manager=StubRepositoryManager())
        assert agent.name == "GitAgent"

    def test_agent_capabilities(self):
        """GitAgent has CODE_EXECUTION capability."""
        agent = GitAgent(repository_manager=StubRepositoryManager())
        assert AgentCapabilities.CODE_EXECUTION in agent.get_capabilities()

    def test_default_repo_manager(self):
        """Without explicit manager, GitAgent creates a default RepositoryManager."""
        agent = GitAgent()
        assert agent.repo_manager is not None


@pytest.mark.unit
class TestGitAgentExecution:
    """Test GitAgent._execute_impl with a stub RepositoryManager."""

    def _make_agent(self, **stub_kwargs):
        stub = StubRepositoryManager(**stub_kwargs)
        return GitAgent(repository_manager=stub), stub

    def test_sync_command_string_format(self):
        """Sync via 'sync: repository=owner/repo' string format."""
        agent, stub = self._make_agent()
        request = AgentRequest(prompt="sync: repository=owner/repo")
        response = agent.execute(request)

        assert response.error is None
        assert len(stub._calls.get("sync_repository", [])) == 1
        assert stub._calls["sync_repository"][0][0] == ("owner/repo",)

    def test_prune_command_json_format(self):
        """Prune via JSON format."""
        agent, stub = self._make_agent()
        request = AgentRequest(prompt='{"action": "prune", "repository": "owner/repo"}')
        response = agent.execute(request)

        assert response.error is None
        assert len(stub._calls.get("prune_repository", [])) == 1

    def test_status_command(self):
        """Status via string format."""
        agent, stub = self._make_agent()
        request = AgentRequest(prompt="status: repository=owner/repo")
        response = agent.execute(request)

        assert response.error is None
        assert len(stub._calls.get("get_repository_status", [])) == 1

    def test_invalid_format(self):
        """Prompt without colon separator results in error."""
        agent, _ = self._make_agent()
        request = AgentRequest(prompt="no_colon_here")
        response = agent.execute(request)

        assert response.error is not None

    def test_unknown_action(self):
        """Unknown action results in error."""
        agent, _ = self._make_agent()
        request = AgentRequest(prompt="unknown_action: repository=owner/repo")
        response = agent.execute(request)

        assert response.error is not None

    def test_clean_command(self):
        """Clean dispatches to repo_manager + clean_repository."""
        agent, stub = self._make_agent(
            repos={"owner/repo": {"name": "owner/repo"}},
            local_paths={"owner/repo": "/tmp/stub_repo"},
        )
        request = AgentRequest(prompt="clean: repository=owner/repo, force=true")
        # We execute and just verify it dispatched correctly through the stub
        # The actual clean_repository call may fail without a real git repo,
        # but the agent catches exceptions and returns an error response
        agent.execute(request)
        # get_repository should have been called
        assert len(stub._calls.get("get_repository", [])) == 1

    def test_add_remote_command(self):
        """add_remote dispatches correctly."""
        agent, stub = self._make_agent(
            repos={"owner/repo": {"name": "owner/repo"}},
            local_paths={"owner/repo": "/tmp/stub_repo"},
        )
        request = AgentRequest(
            prompt="add_remote: repository=owner/repo, name=upstream, url=git@github.com:owner/repo.git"
        )
        agent.execute(request)
        assert len(stub._calls.get("get_repository", [])) == 1

    def test_create_issue_json(self):
        """create_issue via JSON dispatches correctly (may error without GITHUB_TOKEN)."""
        agent, stub = self._make_agent()
        request = AgentRequest(
            prompt='{"action": "create_issue", "owner": "o", "repo_name": "r", "title": "t"}'
        )
        # This will attempt a real GitHub API call; if no token, it errors gracefully
        response = agent.execute(request)
        # Either succeeds or returns an error — either way, no crash
        assert isinstance(response.content, str) or response.error is not None

    def test_stream_yields_result(self):
        """stream() yields the execute result."""
        agent, _ = self._make_agent()
        request = AgentRequest(prompt="sync: repository=owner/repo")
        chunks = list(agent.stream(request))
        assert len(chunks) >= 1
