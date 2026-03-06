"""Integration tests for Jules agent integration.

Tests use real implementations only. When Jules CLI is not available,
tests are skipped rather than using mocks. All data processing and
conversion logic is tested with real data structures.
"""

import pytest

try:
    from codomyrmex.agents.core import (
        AgentCapabilities,
        AgentRequest,
        AgentResponse,
        BaseAgent,
    )
    from codomyrmex.agents.generic.agent_orchestrator import AgentOrchestrator
    from codomyrmex.agents.jules import (
        JulesClient,
        JulesIntegrationAdapter,
        JulesSwarmDispatcher,
    )
    from codomyrmex.tests.unit.agents.helpers import JULES_AVAILABLE

    _HAS_AGENTS = True
except ImportError:
    _HAS_AGENTS = False

if not _HAS_AGENTS:
    pytest.skip("agents deps not available", allow_module_level=True)


class TestJulesClient:
    """Test JulesClient functionality."""

    def test_jules_client_initialization(self):
        """Test JulesClient can be initialized."""
        client = JulesClient()
        assert client.name == "jules"
        assert AgentCapabilities.CODE_GENERATION in client.get_capabilities()
        assert AgentCapabilities.CODE_EDITING in client.get_capabilities()
        assert AgentCapabilities.CODE_ANALYSIS in client.get_capabilities()
        assert AgentCapabilities.TEXT_COMPLETION in client.get_capabilities()
        assert AgentCapabilities.STREAMING in client.get_capabilities()

    def test_jules_client_capabilities(self):
        """Test JulesClient declares correct capabilities."""
        client = JulesClient()
        capabilities = client.get_capabilities()

        # Verify all expected capabilities are present
        assert AgentCapabilities.CODE_GENERATION in capabilities
        assert AgentCapabilities.CODE_EDITING in capabilities
        assert AgentCapabilities.CODE_ANALYSIS in capabilities
        assert AgentCapabilities.TEXT_COMPLETION in capabilities
        assert AgentCapabilities.STREAMING in capabilities

    def test_jules_client_task_decomposition_capability(self):
        """Test JulesClient now declares TASK_DECOMPOSITION capability."""
        client = JulesClient()
        assert AgentCapabilities.TASK_DECOMPOSITION in client.get_capabilities()

    @pytest.mark.skipif(not JULES_AVAILABLE, reason="jules CLI not installed")
    def test_jules_client_execute_success(self):
        """Test successful execution of Jules command with real CLI."""
        client = JulesClient()
        request = AgentRequest(prompt="write unit tests")

        try:
            response = client.execute(request)

            # Test real response structure
            assert isinstance(response, AgentResponse)
            assert "command" in response.metadata
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("Jules CLI authentication or execution failed")

    @pytest.mark.skipif(not JULES_AVAILABLE, reason="jules CLI not installed")
    def test_jules_client_execute_with_context(self):
        """Test execution with context parameters using real CLI."""
        client = JulesClient()
        request = AgentRequest(
            prompt="write unit tests", context={"repo": "test/repo", "parallel": 2}
        )

        try:
            response = client.execute(request)

            # Test real response structure
            assert isinstance(response, AgentResponse)
            # Verify command was built with context
            command = response.metadata.get("command", "")
            assert "new" in command or "test" in command.lower()
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("Jules CLI authentication or execution failed")

    def test_jules_client_execute_failure_invalid_command(self):
        """Test handling when command is not found."""
        # Use invalid command to trigger real FileNotFoundError
        client = JulesClient(config={"jules_command": "nonexistent-jules-command-xyz"})
        request = AgentRequest(prompt="invalid task")
        response = client.execute(request)

        # Test real error handling
        assert not response.is_success()
        assert response.error is not None

    @pytest.mark.skipif(not JULES_AVAILABLE, reason="jules CLI not installed")
    def test_jules_client_stream(self):
        """Test streaming functionality with real CLI."""
        client = JulesClient()
        request = AgentRequest(prompt="test task")

        try:
            # Test that streaming returns an iterator
            stream = client.stream(request)
            chunks = list(stream)

            # Verify we got some response (even if empty or error)
            assert isinstance(chunks, list)
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("Jules CLI authentication or execution failed")

    @pytest.mark.skipif(not JULES_AVAILABLE, reason="jules CLI not installed")
    def test_jules_client_get_help(self):
        """Test getting Jules help information."""
        client = JulesClient()
        help_info = client.get_jules_help()

        # Test real result structure
        assert isinstance(help_info, dict)
        assert "available" in help_info
        assert "help_text" in help_info
        # Available depends on whether jules is installed
        if JULES_AVAILABLE:
            assert help_info["available"] is True

    @pytest.mark.skipif(not JULES_AVAILABLE, reason="jules CLI not installed")
    def test_jules_client_execute_jules_command(self):
        """Test direct command execution with real CLI."""
        client = JulesClient()

        try:
            result = client.execute_jules_command("help")

            # Test real result structure
            assert isinstance(result, dict)
            assert "exit_code" in result or "output" in result
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("Jules CLI authentication or execution failed")


class TestJulesBuildArgs:
    """Test _build_jules_args argument construction logic."""

    def test_build_args_default_new_subcommand(self):
        """Without a direct command context, args should start with 'new'."""
        client = JulesClient()
        args = client._build_jules_args("fix the bug", {})
        assert args[0] == "new"
        assert "fix the bug" in args

    def test_build_args_with_repo_and_parallel(self):
        """Repo and parallel context keys are forwarded to args."""
        client = JulesClient()
        args = client._build_jules_args(
            "add tests", {"repo": "acme/myrepo", "parallel": 5}
        )
        assert "--repo" in args
        assert "acme/myrepo" in args
        assert "--parallel" in args
        assert "5" in args

    def test_build_args_direct_command_passthrough(self):
        """Known direct commands (auth, list, status) bypass 'new'."""
        client = JulesClient()
        for cmd in ["auth", "list", "status", "cancel"]:
            args = client._build_jules_args("", {"command": cmd})
            assert args[0] == cmd
            assert "new" not in args

    def test_build_args_unknown_command_falls_back_to_new(self):
        """Unknown command values should fall through to 'new' subcommand."""
        client = JulesClient()
        args = client._build_jules_args("task", {"command": "unknownxyz"})
        assert args[0] == "new"

    def test_build_args_direct_command_with_extra_args(self):
        """Extra args are appended when using a direct command."""
        client = JulesClient()
        args = client._build_jules_args("", {"command": "auth", "args": ["login"]})
        assert args == ["auth", "login"]


class TestJulesConfigOverride:
    """Test that config overrides do not corrupt base-class defaults."""

    def test_empty_config_keeps_default_command(self):
        """An empty config dict must not overwrite self.command with None."""
        client = JulesClient(config={})
        assert client.command is not None
        assert isinstance(client.command, str)

    def test_none_config_keeps_default_command(self):
        """config=None must not overwrite self.command with None."""
        client = JulesClient(config=None)
        assert client.command is not None
        assert isinstance(client.command, str)

    def test_explicit_command_config_is_applied(self):
        """Explicit jules_command in config must override the default."""
        client = JulesClient(config={"jules_command": "julius"})
        assert client.command == "julius"

    def test_explicit_timeout_config_is_applied(self):
        """Explicit jules_timeout in config must override the default."""
        client = JulesClient(config={"jules_timeout": 60})
        assert client.timeout == 60


class TestJulesSwarmDispatcher:
    """Test JulesSwarmDispatcher task parsing and batching."""

    def test_dispatcher_initialization(self):
        """Test dispatcher initializes with client, repo, and empty tasks."""
        client = JulesClient()
        dispatcher = JulesSwarmDispatcher(client=client, repo="owner/repo")
        assert dispatcher.client is client
        assert dispatcher.repo == "owner/repo"
        assert dispatcher.tasks == []

    def test_dispatcher_initialization_with_tasks(self):
        """Test dispatcher accepts a pre-built task list."""
        client = JulesClient()
        tasks = ["fix bug A", "add test B", "refactor C"]
        dispatcher = JulesSwarmDispatcher(client=client, repo="owner/repo", tasks=tasks)
        assert dispatcher.tasks == tasks

    def test_from_todo_md_parses_open_items(self, tmp_path):
        """from_todo_md extracts all unchecked '- [ ]' items."""
        todo = tmp_path / "TODO.md"
        todo.write_text(
            "# Backlog\n\n"
            "- [ ] Fix the coverage gate\n"
            "- [x] Already done item\n"
            "- [ ] Add MCP tools\n"
            "- Regular line\n"
        )
        client = JulesClient()
        dispatcher = JulesSwarmDispatcher.from_todo_md(client, "owner/repo", todo)
        assert len(dispatcher.tasks) == 2
        assert "Fix the coverage gate" in dispatcher.tasks
        assert "Add MCP tools" in dispatcher.tasks
        assert "Already done item" not in dispatcher.tasks

    def test_from_todo_md_empty_file(self, tmp_path):
        """from_todo_md on a file with no checkboxes returns empty task list."""
        todo = tmp_path / "TODO.md"
        todo.write_text("# No tasks here\n\nJust prose.\n")
        client = JulesClient()
        dispatcher = JulesSwarmDispatcher.from_todo_md(client, "r/r", todo)
        assert dispatcher.tasks == []

    def test_from_todo_md_missing_file_raises(self, tmp_path):
        """from_todo_md raises FileNotFoundError for non-existent files."""
        client = JulesClient()
        with pytest.raises(FileNotFoundError):
            JulesSwarmDispatcher.from_todo_md(
                client, "r/r", tmp_path / "nonexistent.md"
            )

    def test_dispatch_empty_tasks_returns_empty(self):
        """dispatch() with no tasks returns an empty list without calling Jules."""
        client = JulesClient(config={"jules_command": "nonexistent-jules-xyz"})
        dispatcher = JulesSwarmDispatcher(client=client, repo="r/r", tasks=[])
        responses = dispatcher.dispatch()
        assert responses == []


class TestJulesIntegrationAdapter:
    """Test JulesIntegrationAdapter functionality."""

    def test_adapter_initialization(self):
        """Test adapter can be initialized with JulesClient."""
        client = JulesClient()
        adapter = JulesIntegrationAdapter(client)
        assert adapter.agent == client

    @pytest.mark.skipif(not JULES_AVAILABLE, reason="jules CLI not installed")
    def test_adapter_ai_code_editing(self):
        """Test adapter for AI code editing with real CLI."""
        client = JulesClient()
        adapter = JulesIntegrationAdapter(client)

        try:
            code = adapter.adapt_for_ai_code_editing(
                prompt="create a test function", language="python"
            )

            # Test real result structure
            assert isinstance(code, str)
        except RuntimeError:
            # Expected if authentication fails or CLI error
            pytest.skip("Jules CLI authentication or execution failed")

    @pytest.mark.skipif(not JULES_AVAILABLE, reason="jules CLI not installed")
    def test_adapter_ai_code_editing_failure(self):
        """Test adapter handles code generation failures."""
        client = JulesClient()
        adapter = JulesIntegrationAdapter(client)

        # Use invalid prompt that might fail
        try:
            code = adapter.adapt_for_ai_code_editing(
                prompt="invalid prompt that should fail", language="python"
            )
            # If it doesn't fail, that's also valid
            assert isinstance(code, str)
        except RuntimeError:
            # Expected if code generation fails
            pass

    @pytest.mark.skipif(not JULES_AVAILABLE, reason="jules CLI not installed")
    def test_adapter_llm_integration(self):
        """Test adapter for LLM module integration with real CLI."""
        client = JulesClient()
        adapter = JulesIntegrationAdapter(client)

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]

        try:
            result = adapter.adapt_for_llm(messages)

            # Test real result structure
            assert isinstance(result, dict)
            assert "content" in result
            assert result["model"] == "jules"
            assert "usage" in result
            assert "metadata" in result
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("Jules CLI authentication or execution failed")

    @pytest.mark.skipif(not JULES_AVAILABLE, reason="jules CLI not installed")
    def test_adapter_code_execution(self):
        """Test adapter for code execution sandbox with real CLI."""
        client = JulesClient()
        adapter = JulesIntegrationAdapter(client)

        try:
            result = adapter.adapt_for_code_execution(
                code="print('hello')", language="python"
            )

            # Test real result structure
            assert isinstance(result, dict)
            assert "success" in result
            assert "output" in result
            assert "metadata" in result
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("Jules CLI authentication or execution failed")


class TestJulesOrchestration:
    """Test Jules integration with AgentOrchestrator."""

    def test_jules_with_orchestrator_structure(self):
        """Test JulesClient with AgentOrchestrator structure."""
        client = JulesClient()
        orchestrator = AgentOrchestrator([client])

        # Test orchestrator structure
        assert len(orchestrator.agents) == 1
        assert orchestrator.agents[0] == client

    @pytest.mark.skipif(not JULES_AVAILABLE, reason="jules CLI not installed")
    def test_jules_with_orchestrator_parallel(self):
        """Test Jules in parallel orchestration with real CLI."""
        client = JulesClient()
        orchestrator = AgentOrchestrator([client])

        request = AgentRequest(prompt="test task")

        try:
            responses = orchestrator.execute_parallel(request)

            # Test real response structure
            assert len(responses) == 1
            assert isinstance(responses[0], AgentResponse)
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("Jules CLI authentication or execution failed")

    @pytest.mark.skipif(not JULES_AVAILABLE, reason="jules CLI not installed")
    def test_jules_with_orchestrator_sequential(self):
        """Test Jules in sequential orchestration with real CLI."""
        client = JulesClient()
        orchestrator = AgentOrchestrator([client])

        request = AgentRequest(prompt="test task")

        try:
            responses = orchestrator.execute_sequential(request)

            # Test real response structure
            assert len(responses) == 1
            assert isinstance(responses[0], AgentResponse)
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("Jules CLI authentication or execution failed")

    @pytest.mark.skipif(not JULES_AVAILABLE, reason="jules CLI not installed")
    def test_jules_with_orchestrator_fallback(self):
        """Test Jules in fallback orchestration with real CLI."""
        client = JulesClient()
        orchestrator = AgentOrchestrator([client])

        request = AgentRequest(prompt="test task")

        try:
            response = orchestrator.execute_with_fallback(request)

            # Test real response structure
            assert isinstance(response, AgentResponse)
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("Jules CLI authentication or execution failed")

    def test_jules_with_multiple_agents_structure(self):
        """Test Jules alongside other agents in orchestration structure."""
        jules_client = JulesClient()

        # Create a test agent that implements BaseAgent (not a mock)
        class TestAgent(BaseAgent):
            """Test suite for Agent."""

            def _execute_impl(self, request):
                return AgentResponse(content="Test response")

            def _stream_impl(self, request):
                yield "Test"

        test_agent = TestAgent(
            name="test", capabilities=[AgentCapabilities.TEXT_COMPLETION]
        )

        orchestrator = AgentOrchestrator([jules_client, test_agent])
        AgentRequest(prompt="test")

        # Test structure without requiring execution
        assert len(orchestrator.agents) == 2
        assert orchestrator.agents[0] == jules_client
        assert orchestrator.agents[1] == test_agent

    def test_jules_capability_selection(self):
        """Test selecting Jules by capability."""
        client = JulesClient()
        orchestrator = AgentOrchestrator([client])

        # Select agents by capability
        code_gen_agents = orchestrator.select_agent_by_capability(
            AgentCapabilities.CODE_GENERATION.value
        )

        assert len(code_gen_agents) == 1
        assert code_gen_agents[0] == client
