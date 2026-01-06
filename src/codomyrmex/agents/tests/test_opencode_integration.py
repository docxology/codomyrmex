"""Integration tests for OpenCode agent integration."""

import pytest
from unittest.mock import MagicMock, patch, Mock
from typing import Any
from pathlib import Path

from codomyrmex.agents.core import AgentRequest, AgentCapabilities
from codomyrmex.agents.opencode import OpenCodeClient, OpenCodeIntegrationAdapter
from codomyrmex.agents.generic import AgentOrchestrator
from codomyrmex.agents.exceptions import OpenCodeError


class TestOpenCodeClient:
    """Test OpenCodeClient functionality."""

    def test_opencode_client_initialization(self):
        """Test OpenCodeClient can be initialized."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)
            client = OpenCodeClient()
            assert client.name == "opencode"
            assert AgentCapabilities.CODE_GENERATION in client.get_capabilities()
            assert AgentCapabilities.CODE_EDITING in client.get_capabilities()
            assert AgentCapabilities.CODE_ANALYSIS in client.get_capabilities()
            assert AgentCapabilities.TEXT_COMPLETION in client.get_capabilities()
            assert AgentCapabilities.MULTI_TURN in client.get_capabilities()

    def test_opencode_client_capabilities(self):
        """Test OpenCodeClient declares correct capabilities."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)
            client = OpenCodeClient()
            capabilities = client.get_capabilities()
            
            # Verify all expected capabilities are present
            assert AgentCapabilities.CODE_GENERATION in capabilities
            assert AgentCapabilities.CODE_EDITING in capabilities
            assert AgentCapabilities.CODE_ANALYSIS in capabilities
            assert AgentCapabilities.TEXT_COMPLETION in capabilities
            assert AgentCapabilities.MULTI_TURN in capabilities

    def test_opencode_client_execute_success(self):
        """Test successful execution of OpenCode command."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Task completed successfully",
                stderr="",
            )
            
            client = OpenCodeClient()
            request = AgentRequest(prompt="write unit tests")
            response = client.execute(request)
            
            assert response.is_success()
            assert "Task completed successfully" in response.content
            assert response.error is None
            assert "command" in response.metadata

    def test_opencode_client_execute_with_context(self):
        """Test execution with context parameters."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Task completed",
                stderr="",
            )
            
            client = OpenCodeClient()
            request = AgentRequest(
                prompt="write unit tests",
                context={"init": False, "language": "python"}
            )
            response = client.execute(request)
            
            assert response.is_success()

    def test_opencode_client_execute_with_init(self):
        """Test execution with initialization context."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Project initialized",
                stderr="",
            )
            
            client = OpenCodeClient()
            request = AgentRequest(
                prompt="init",  # Non-empty prompt to pass validation
                context={"init": True}
            )
            response = client.execute(request)
            
            assert response.is_success()
            # Verify init command was used
            command = response.metadata.get("command", "")
            assert "--init" in command

    def test_opencode_client_execute_failure(self):
        """Test handling of failed OpenCode command."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=1,
                stdout="",
                stderr="Error: Command failed",
            )
            
            client = OpenCodeClient()
            request = AgentRequest(prompt="invalid task")
            response = client.execute(request)
            
            assert not response.is_success()
            assert response.error is not None

    def test_opencode_client_stream(self):
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
                
                client = OpenCodeClient()
                request = AgentRequest(prompt="test task")
                
                chunks = list(client.stream(request))
                assert len(chunks) >= 2
                assert "Line 1" in chunks or "Line 2" in chunks

    def test_opencode_client_timeout(self):
        """Test timeout handling."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)
            with patch.object(OpenCodeClient, "_execute_opencode_command") as mock_exec:
                import subprocess
                mock_exec.side_effect = subprocess.TimeoutExpired("opencode", 30)
                
                client = OpenCodeClient()
                request = AgentRequest(prompt="long running task")
                
                response = client.execute(request)
                # Timeout should result in error response, not exception
                assert not response.is_success()
                assert response.error is not None
                assert "timeout" in response.error.lower() or "timed out" in response.error.lower()

    def test_opencode_client_command_not_found(self):
        """Test handling when OpenCode command is not found."""
        with patch("subprocess.run") as mock_run:
            # First call for availability check returns 0, second call raises FileNotFoundError
            mock_run.side_effect = [
                Mock(returncode=0),  # Availability check
                FileNotFoundError()  # Actual command execution
            ]
            
            client = OpenCodeClient(config={"opencode_command": "nonexistent"})
            request = AgentRequest(prompt="test")
            
            # Should return error response, not raise exception
            response = client.execute(request)
            assert not response.is_success()
            assert response.error is not None
            assert "not found" in response.error.lower() or "failed" in response.error.lower()

    def test_opencode_client_initialize_project(self):
        """Test project initialization."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Project initialized successfully",
                stderr="",
            )
            
            client = OpenCodeClient()
            result = client.initialize_project(project_path=Path("/tmp/test"))
            
            assert result["success"] is True
            assert "Project initialized" in result["output"]

    def test_opencode_client_get_version(self):
        """Test getting OpenCode version information."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="opencode 1.1.3",
                stderr="",
            )
            
            client = OpenCodeClient()
            version_info = client.get_opencode_version()
            
            assert version_info["available"] is True
            assert "1.1.3" in version_info["version"] or "opencode" in version_info["version"]


class TestOpenCodeIntegrationAdapter:
    """Test OpenCodeIntegrationAdapter functionality."""

    def test_adapter_initialization(self):
        """Test adapter can be initialized with OpenCodeClient."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)
            client = OpenCodeClient()
            adapter = OpenCodeIntegrationAdapter(client)
            assert adapter.agent == client

    def test_adapter_ai_code_editing(self):
        """Test adapter for AI code editing."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="def test_function():\n    pass",
                stderr="",
            )
            
            client = OpenCodeClient()
            adapter = OpenCodeIntegrationAdapter(client)
            
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
            
            client = OpenCodeClient()
            adapter = OpenCodeIntegrationAdapter(client)
            
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
            
            client = OpenCodeClient()
            adapter = OpenCodeIntegrationAdapter(client)
            
            messages = [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there"}
            ]
            
            result = adapter.adapt_for_llm(messages)
            
            assert "content" in result
            assert result["model"] == "opencode"
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
            
            client = OpenCodeClient()
            adapter = OpenCodeIntegrationAdapter(client)
            
            result = adapter.adapt_for_code_execution(
                code="print('hello')",
                language="python"
            )
            
            assert "success" in result
            assert "output" in result
            assert "metadata" in result


class TestOpenCodeOrchestration:
    """Test OpenCode integration with AgentOrchestrator."""

    def test_opencode_with_orchestrator_parallel(self):
        """Test OpenCode in parallel orchestration."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Task completed",
                stderr="",
            )
            
            client = OpenCodeClient()
            orchestrator = AgentOrchestrator([client])
            
            request = AgentRequest(prompt="test task")
            responses = orchestrator.execute_parallel(request)
            
            assert len(responses) == 1
            assert responses[0].is_success()

    def test_opencode_with_orchestrator_sequential(self):
        """Test OpenCode in sequential orchestration."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Task completed",
                stderr="",
            )
            
            client = OpenCodeClient()
            orchestrator = AgentOrchestrator([client])
            
            request = AgentRequest(prompt="test task")
            responses = orchestrator.execute_sequential(request)
            
            assert len(responses) == 1
            assert responses[0].is_success()

    def test_opencode_with_orchestrator_fallback(self):
        """Test OpenCode in fallback orchestration."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Task completed",
                stderr="",
            )
            
            client = OpenCodeClient()
            orchestrator = AgentOrchestrator([client])
            
            request = AgentRequest(prompt="test task")
            response = orchestrator.execute_with_fallback(request)
            
            assert response.is_success()

    def test_opencode_capability_selection(self):
        """Test selecting OpenCode by capability."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)
            
            client = OpenCodeClient()
            orchestrator = AgentOrchestrator([client])
            
            # Select agents by capability
            code_gen_agents = orchestrator.select_agent_by_capability(
                AgentCapabilities.CODE_GENERATION.value
            )
            
            assert len(code_gen_agents) == 1
            assert code_gen_agents[0] == client

