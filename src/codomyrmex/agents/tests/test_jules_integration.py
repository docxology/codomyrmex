"""Integration tests for Jules agent integration."""

import pytest
from unittest.mock import MagicMock, patch, Mock
from typing import Any

from codomyrmex.agents.core import AgentRequest, AgentCapabilities
from codomyrmex.agents.jules import JulesClient, JulesIntegrationAdapter
from codomyrmex.agents.generic import AgentOrchestrator
from codomyrmex.agents.exceptions import JulesError


class TestJulesClient:
    """Test JulesClient functionality."""

    def test_jules_client_initialization(self):
        """Test JulesClient can be initialized."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)
            client = JulesClient()
            assert client.name == "jules"
            assert AgentCapabilities.CODE_GENERATION in client.get_capabilities()
            assert AgentCapabilities.CODE_EDITING in client.get_capabilities()
            assert AgentCapabilities.CODE_ANALYSIS in client.get_capabilities()
            assert AgentCapabilities.TEXT_COMPLETION in client.get_capabilities()
            assert AgentCapabilities.STREAMING in client.get_capabilities()

    def test_jules_client_capabilities(self):
        """Test JulesClient declares correct capabilities."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)
            client = JulesClient()
            capabilities = client.get_capabilities()
            
            # Verify all expected capabilities are present
            assert AgentCapabilities.CODE_GENERATION in capabilities
            assert AgentCapabilities.CODE_EDITING in capabilities
            assert AgentCapabilities.CODE_ANALYSIS in capabilities
            assert AgentCapabilities.TEXT_COMPLETION in capabilities
            assert AgentCapabilities.STREAMING in capabilities

    def test_jules_client_execute_success(self):
        """Test successful execution of Jules command."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Task created successfully",
                stderr="",
            )
            
            client = JulesClient()
            request = AgentRequest(prompt="write unit tests")
            response = client.execute(request)
            
            assert response.is_success()
            assert "Task created successfully" in response.content
            assert response.error is None
            assert "command" in response.metadata

    def test_jules_client_execute_with_context(self):
        """Test execution with context parameters."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Task created",
                stderr="",
            )
            
            client = JulesClient()
            request = AgentRequest(
                prompt="write unit tests",
                context={"repo": "test/repo", "parallel": 2}
            )
            response = client.execute(request)
            
            assert response.is_success()
            # Verify command was built with context
            command = response.metadata.get("command", "")
            assert "new" in command
            assert "test/repo" in command or "--repo" in command

    def test_jules_client_execute_failure(self):
        """Test handling of failed Jules command."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=1,
                stdout="",
                stderr="Error: Command failed",
            )
            
            client = JulesClient()
            request = AgentRequest(prompt="invalid task")
            response = client.execute(request)
            
            assert not response.is_success()
            assert response.error is not None

    def test_jules_client_stream(self):
        """Test streaming functionality."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)
            with patch("subprocess.Popen") as mock_popen:
                # Create a proper mock file-like object with readline
                mock_stdout = Mock()
                mock_stdout.readline.side_effect = ["Line 1\n", "Line 2\n", ""]
                
                mock_process = Mock()
                mock_process.stdout = mock_stdout
                mock_process.stderr = Mock()
                mock_process.stderr.read.return_value = ""
                mock_process.wait.return_value = 0
                mock_process.returncode = 0
                mock_popen.return_value = mock_process
                
                client = JulesClient()
                request = AgentRequest(prompt="test task")
                
                chunks = list(client.stream(request))
                assert len(chunks) >= 2
                assert "Line 1" in chunks or "Line 2" in chunks

    def test_jules_client_timeout(self):
        """Test timeout handling."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)
            with patch.object(JulesClient, "_execute_jules_command") as mock_exec:
                import subprocess
                mock_exec.side_effect = subprocess.TimeoutExpired("jules", 30)
                
                client = JulesClient()
                request = AgentRequest(prompt="long running task")
                
                response = client.execute(request)
                # Timeout should result in error response, not exception
                assert not response.is_success()
                assert response.error is not None
                assert "timeout" in response.error.lower() or "timed out" in response.error.lower()

    def test_jules_client_command_not_found(self):
        """Test handling when Jules command is not found."""
        with patch("subprocess.run") as mock_run:
            # First call for availability check returns 0, second call raises FileNotFoundError
            mock_run.side_effect = [
                Mock(returncode=0),  # Availability check
                FileNotFoundError()  # Actual command execution
            ]
            
            client = JulesClient(config={"jules_command": "nonexistent"})
            request = AgentRequest(prompt="test")
            
            # Should return error response, not raise exception
            response = client.execute(request)
            assert not response.is_success()
            assert response.error is not None
            assert "not found" in response.error.lower() or "failed" in response.error.lower()

    def test_jules_client_get_help(self):
        """Test getting Jules help information."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Jules CLI help text",
                stderr="",
            )
            
            client = JulesClient()
            help_info = client.get_jules_help()
            
            assert help_info["available"] is True
            assert "Jules CLI help text" in help_info["help_text"]

    def test_jules_client_execute_jules_command(self):
        """Test direct command execution."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Command output",
                stderr="",
            )
            
            client = JulesClient()
            result = client.execute_jules_command("help", ["--verbose"])
            
            assert result["exit_code"] == 0
            assert "Command output" in result["output"]


class TestJulesIntegrationAdapter:
    """Test JulesIntegrationAdapter functionality."""

    def test_adapter_initialization(self):
        """Test adapter can be initialized with JulesClient."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)
            client = JulesClient()
            adapter = JulesIntegrationAdapter(client)
            assert adapter.agent == client

    def test_adapter_ai_code_editing(self):
        """Test adapter for AI code editing."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="def test_function():\n    pass",
                stderr="",
            )
            
            client = JulesClient()
            adapter = JulesIntegrationAdapter(client)
            
            code = adapter.adapt_for_ai_code_editing(
                prompt="create a test function",
                language="python"
            )
            
            assert "def test_function" in code or "test" in code.lower()

    def test_adapter_ai_code_editing_failure(self):
        """Test adapter handles code generation failures."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=1,
                stdout="",
                stderr="Error: Failed",
            )
            
            client = JulesClient()
            adapter = JulesIntegrationAdapter(client)
            
            with pytest.raises(RuntimeError):
                adapter.adapt_for_ai_code_editing(
                    prompt="invalid prompt",
                    language="python"
                )

    def test_adapter_llm_integration(self):
        """Test adapter for LLM module integration."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="LLM response text",
                stderr="",
            )
            
            client = JulesClient()
            adapter = JulesIntegrationAdapter(client)
            
            messages = [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there"}
            ]
            
            result = adapter.adapt_for_llm(messages)
            
            assert "content" in result
            assert result["model"] == "jules"
            assert "usage" in result
            assert "metadata" in result

    def test_adapter_code_execution(self):
        """Test adapter for code execution sandbox."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Code analysis complete",
                stderr="",
            )
            
            client = JulesClient()
            adapter = JulesIntegrationAdapter(client)
            
            result = adapter.adapt_for_code_execution(
                code="print('hello')",
                language="python"
            )
            
            assert "success" in result
            assert "output" in result
            assert "metadata" in result


class TestJulesOrchestration:
    """Test Jules integration with AgentOrchestrator."""

    def test_jules_with_orchestrator_parallel(self):
        """Test Jules in parallel orchestration."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Task completed",
                stderr="",
            )
            
            client = JulesClient()
            orchestrator = AgentOrchestrator([client])
            
            request = AgentRequest(prompt="test task")
            responses = orchestrator.execute_parallel(request)
            
            assert len(responses) == 1
            assert responses[0].is_success()

    def test_jules_with_orchestrator_sequential(self):
        """Test Jules in sequential orchestration."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Task completed",
                stderr="",
            )
            
            client = JulesClient()
            orchestrator = AgentOrchestrator([client])
            
            request = AgentRequest(prompt="test task")
            responses = orchestrator.execute_sequential(request)
            
            assert len(responses) == 1
            assert responses[0].is_success()

    def test_jules_with_orchestrator_fallback(self):
        """Test Jules in fallback orchestration."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Task completed",
                stderr="",
            )
            
            client = JulesClient()
            orchestrator = AgentOrchestrator([client])
            
            request = AgentRequest(prompt="test task")
            response = orchestrator.execute_with_fallback(request)
            
            assert response.is_success()

    def test_jules_with_multiple_agents(self):
        """Test Jules alongside other agents in orchestration."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Response",
                stderr="",
            )
            
            # Create mock agents
            jules_client = JulesClient()
            
            # Create a simple mock agent for comparison
            from codomyrmex.agents.generic import BaseAgent
            from codomyrmex.agents.core import AgentResponse
            
            class MockAgent(BaseAgent):
                def _execute_impl(self, request):
                    return AgentResponse(content="Mock response")
                def _stream_impl(self, request):
                    yield "Mock"
            
            mock_agent = MockAgent(
                name="mock",
                capabilities=[AgentCapabilities.TEXT_COMPLETION]
            )
            
            orchestrator = AgentOrchestrator([jules_client, mock_agent])
            request = AgentRequest(prompt="test")
            responses = orchestrator.execute_parallel(request)
            
            assert len(responses) == 2
            # At least one should succeed
            assert any(r.is_success() for r in responses)

    def test_jules_capability_selection(self):
        """Test selecting Jules by capability."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)
            
            client = JulesClient()
            orchestrator = AgentOrchestrator([client])
            
            # Select agents by capability
            code_gen_agents = orchestrator.select_agent_by_capability(
                AgentCapabilities.CODE_GENERATION.value
            )
            
            assert len(code_gen_agents) == 1
            assert code_gen_agents[0] == client

