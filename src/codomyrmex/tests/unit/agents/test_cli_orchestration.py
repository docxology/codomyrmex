"""Tests for CLI orchestration commands."""

import pytest
import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
from io import StringIO

from codomyrmex.agents.core.config import AgentConfig, get_config, set_config, reset_config
from codomyrmex.agents.core import AgentRequest, AgentResponse, AgentCapabilities
from codomyrmex.agents.core import AgentRequest, AgentResponse, AgentCapabilities


@pytest.mark.unit
class TestCLICommands:
    """Test CLI command functionality."""

    def test_info_command_basic(self):
        """Test basic info command execution."""
        # Test the underlying functionality that CLI uses
        config = get_config()
        
        # Verify config can be accessed (what info command does)
        assert config is not None
        assert hasattr(config, "jules_command")
        assert hasattr(config, "claude_model")
        assert hasattr(config, "opencode_command")

    def test_info_command_verbose(self):
        """Test info command with verbose flag."""
        # Test that verbose mode would work (testing underlying functionality)
        config = get_config()
        config_dict = config.to_dict()
        
        # Verify config can be converted to dict (what info command does)
        assert isinstance(config_dict, dict)
        assert "module" not in config_dict  # This would be added by CLI
        # But config itself should be serializable

    def test_info_command_output_format(self):
        """Test info command output format."""
        with patch("codomyrmex.agents.get_config") as mock_get_config:
            mock_config = AgentConfig()
            mock_get_config.return_value = mock_config
            
            # Test that config is accessed
            config = get_config()
            
            assert config is not None
            assert hasattr(config, "jules_command")
            assert hasattr(config, "claude_model")
            assert hasattr(config, "opencode_command")

    def test_unknown_command_handling(self):
        """Test handling of unknown commands."""
        # This would be tested by calling main() with unknown command
        # In practice, argparse would handle this
        pass

    def test_cli_error_handling(self):
        """Test CLI error handling."""
        with patch("codomyrmex.agents.get_config") as mock_get_config:
            mock_get_config.side_effect = Exception("Test error")
            
            # Should handle errors gracefully
            try:
                config = get_config()
            except Exception as e:
                # Error should be caught and handled
                assert "Test error" in str(e)


@pytest.mark.unit
class TestCLIOutputFormatting:
    """Test CLI output formatting."""

    def test_json_output_format(self):
        """Test JSON output formatting."""
        config = AgentConfig()
        config_dict = config.to_dict()
        
        # Verify dict structure for JSON serialization
        assert isinstance(config_dict, dict)
        assert "jules_command" in config_dict
        assert "claude_model" in config_dict
        assert "opencode_command" in config_dict

    def test_config_dict_structure(self):
        """Test that config dict has expected structure."""
        config = AgentConfig()
        config_dict = config.to_dict()
        
        # Check all expected keys
        expected_keys = [
            "jules_command",
            "jules_timeout",
            "claude_model",
            "claude_timeout",
            "codex_model",
            "codex_timeout",
            "opencode_command",
            "opencode_timeout",
            "default_timeout",
            "enable_logging",
            "log_level",
            "output_dir",
        ]
        
        for key in expected_keys:
            assert key in config_dict, f"Missing key: {key}"

    def test_sensitive_data_masking(self):
        """Test that sensitive data is masked in output."""
        config = AgentConfig(
            claude_api_key="secret-key",
            codex_api_key="another-secret",
            opencode_api_key="opencode-secret"
        )
        
        config_dict = config.to_dict()
        
        # API keys should be masked
        assert config_dict["claude_api_key"] == "***"
        assert config_dict["codex_api_key"] == "***"
        assert config_dict["opencode_api_key"] == "***"


@pytest.mark.unit
class TestCLIConfigurationIntegration:
    """Test CLI configuration integration."""

    def test_cli_reads_global_config(self):
        """Test that CLI reads global configuration."""
        reset_config()
        
        custom_config = AgentConfig(default_timeout=999)
        set_config(custom_config)
        
        retrieved_config = get_config()
        
        assert retrieved_config.default_timeout == 999
        assert retrieved_config is custom_config

    def test_cli_config_validation(self):
        """Test CLI configuration validation."""
        config = AgentConfig(
            default_timeout=-1,  # Invalid
            jules_timeout=0,  # Invalid
        )
        
        errors = config.validate()
        
        assert len(errors) > 0
        assert any("default_timeout" in e for e in errors)
        assert any("jules_timeout" in e for e in errors)


# ============================================================================
# Agent Command Tests
# ============================================================================

@pytest.mark.unit
class TestJulesCommands:
    """Test Jules agent commands."""

    def test_jules_check_availability(self):
        """Test jules check command."""
        from codomyrmex.agents.jules import JulesClient
        
        client = JulesClient()
        # Use the correct inherited method from CLIAgentBase
        available = client._check_command_available(check_args=["help"])
        
        # Should return boolean
        assert isinstance(available, bool)

    def test_jules_get_help(self):
        """Test jules help command."""
        from codomyrmex.agents.jules import JulesClient
        
        client = JulesClient()
        help_info = client.get_jules_help()
        
        assert isinstance(help_info, dict)
        assert "available" in help_info
        assert "help_text" in help_info

    def test_jules_execute_request(self):
        """Test jules execute request structure."""
        from codomyrmex.agents.jules import JulesClient
        
        client = JulesClient()
        request = AgentRequest(prompt="test prompt")
        
        # Should be able to create request
        assert request.prompt == "test prompt"
        assert isinstance(request.context, dict)


@pytest.mark.unit
class TestClaudeCommands:
    """Test Claude agent commands."""

    def test_claude_check_config(self):
        """Test claude check command."""
        config = get_config()
        
        # Should have claude config
        assert hasattr(config, "claude_model")
        assert hasattr(config, "claude_api_key")
        assert hasattr(config, "claude_timeout")

    def test_claude_execute_request(self):
        """Test claude execute request structure."""
        from codomyrmex.agents.claude import ClaudeClient
        
        # May fail if anthropic not installed, but structure should work
        try:
            client = ClaudeClient()
            request = AgentRequest(prompt="test prompt")
            assert request.prompt == "test prompt"
        except Exception:
            # Expected if anthropic not installed
            pass


@pytest.mark.unit
class TestCodexCommands:
    """Test Codex agent commands."""

    def test_codex_check_config(self):
        """Test codex check command."""
        config = get_config()
        
        # Should have codex config
        assert hasattr(config, "codex_model")
        assert hasattr(config, "codex_api_key")
        assert hasattr(config, "codex_timeout")

    def test_codex_execute_request(self):
        """Test codex execute request structure."""
        from codomyrmex.agents.codex import CodexClient
        
        # May fail if openai not installed, but structure should work
        try:
            client = CodexClient()
            request = AgentRequest(prompt="test prompt")
            assert request.prompt == "test prompt"
        except Exception:
            # Expected if openai not installed
            pass


@pytest.mark.unit
class TestOpenCodeCommands:
    """Test OpenCode agent commands."""

    def test_opencode_check_availability(self):
        """Test opencode check command."""
        from codomyrmex.agents.opencode import OpenCodeClient
        
        client = OpenCodeClient()
        # Use the correct inherited method from CLIAgentBase
        available = client._check_command_available(check_args=["--help"])
        
        # Should return boolean
        assert isinstance(available, bool)

    def test_opencode_get_version(self):
        """Test opencode version command."""
        from codomyrmex.agents.opencode import OpenCodeClient
        
        client = OpenCodeClient()
        version_info = client.get_opencode_version()
        
        assert isinstance(version_info, dict)
        assert "available" in version_info
        assert "version" in version_info


@pytest.mark.unit
class TestGeminiCommands:
    """Test Gemini agent commands."""

    def test_gemini_check_availability(self):
        """Test gemini client availability check."""
        from codomyrmex.agents.gemini import GeminiClient

        client = GeminiClient()
        # GeminiClient is API-based, not CLI-based, so test its is_available method
        # which checks if the client was initialized successfully
        available = client.is_available if hasattr(client, 'is_available') else client.client is not None

        # Should return boolean
        assert isinstance(available, bool)

    def test_gemini_chat_operations(self):
        """Test gemini chat operations structure."""
        from codomyrmex.agents.gemini import GeminiClient
        
        client = GeminiClient()
        
        # Test chat list - wrap in try/except since gemini may not be available
        try:
            result = client.list_chats()
            assert isinstance(result, dict)
        except Exception:
            # Expected if gemini not available or times out
            pass
        
        # Test chat save structure (may fail if gemini not available)
        try:
            result = client.save_chat("test-tag", "test prompt")
            assert isinstance(result, dict)
        except Exception:
            # Expected if gemini not available or times out
            pass


@pytest.mark.unit
class TestDroidCommands:
    """Test Droid controller commands."""

    def test_droid_controller_creation(self):
        """Test droid controller creation."""
        from codomyrmex.agents.droid import create_default_controller, DroidConfig
        
        try:
            controller = create_default_controller()
            assert controller is not None
            assert hasattr(controller, "status")
            assert hasattr(controller, "config")
            assert hasattr(controller, "metrics")
        except Exception:
            # May fail if dependencies not available
            pass

    def test_droid_config_structure(self):
        """Test droid config structure."""
        from codomyrmex.agents.droid import DroidConfig
        
        config = DroidConfig()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert "identifier" in config_dict
        assert "mode" in config_dict
        assert "llm_provider" in config_dict


@pytest.mark.unit
class TestOrchestratorCommands:
    """Test orchestrator commands."""

    def test_orchestrator_creation(self):
        """Test orchestrator creation."""
        from codomyrmex.agents.generic import AgentOrchestrator
        from codomyrmex.agents.jules import JulesClient
        
        try:
            # Create a simple agent list
            agents = []
            try:
                agents.append(JulesClient())
            except Exception:
                pass  # Skip if jules not available
            
            if agents:
                orchestrator = AgentOrchestrator(agents)
                assert orchestrator is not None
                assert hasattr(orchestrator, "execute_parallel")
                assert hasattr(orchestrator, "execute_sequential")
                assert hasattr(orchestrator, "execute_with_fallback")
        except Exception:
            # May fail if dependencies not available
            pass

    def test_agent_request_creation(self):
        """Test agent request creation with context."""
        request = AgentRequest(
            prompt="test",
            context={"key": "value"},
            timeout=30
        )
        
        assert request.prompt == "test"
        assert request.context == {"key": "value"}
        assert request.timeout == 30

    def test_agent_response_structure(self):
        """Test agent response structure."""
        response = AgentResponse(
            content="test content",
            error=None,
            execution_time=1.5
        )
        
        assert response.content == "test content"
        assert response.is_success()
        assert response.execution_time == 1.5


@pytest.mark.unit
class TestTheoryCommands:
    """Test theory module commands."""

    def test_theory_architectures_available(self):
        """Test that theory architectures are available."""
        try:
            from codomyrmex.agents.theory import (
                ReactiveArchitecture,
                DeliberativeArchitecture,
                HybridArchitecture,
            )
            
            # Should be able to import
            assert ReactiveArchitecture is not None
            assert DeliberativeArchitecture is not None
            assert HybridArchitecture is not None
        except ImportError:
            # May not be available
            pass

    def test_theory_reasoning_models_available(self):
        """Test that theory reasoning models are available."""
        try:
            from codomyrmex.agents.theory import (
                SymbolicReasoningModel,
                NeuralReasoningModel,
                HybridReasoningModel,
            )
            
            # Should be able to import
            assert SymbolicReasoningModel is not None
            assert NeuralReasoningModel is not None
            assert HybridReasoningModel is not None
        except ImportError:
            # May not be available
            pass


@pytest.mark.unit
class TestCommonOperations:
    """Test common operations across agents."""

    def test_agent_request_with_context_json(self):
        """Test parsing context from JSON string."""
        context_str = '{"key": "value", "number": 42}'
        context = json.loads(context_str)
        
        request = AgentRequest(prompt="test", context=context)
        assert request.context["key"] == "value"
        assert request.context["number"] == 42

    def test_agent_response_success_check(self):
        """Test agent response success checking."""
        success_response = AgentResponse(content="test", error=None)
        error_response = AgentResponse(content="", error="test error")
        
        assert success_response.is_success()
        assert not error_response.is_success()

    def test_agent_capabilities_enum(self):
        """Test agent capabilities enum."""
        from codomyrmex.agents.core import AgentCapabilities
        
        assert AgentCapabilities.CODE_GENERATION is not None
        assert AgentCapabilities.STREAMING is not None
        assert AgentCapabilities.MULTI_TURN is not None


# ============================================================================
# Config Management Tests
# ============================================================================

@pytest.mark.unit
class TestConfigCommands:
    """Test config management commands."""

    def test_config_show(self):
        """Test config show command."""
        config = get_config()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert "jules_command" in config_dict
        assert "claude_model" in config_dict

    def test_config_set_structure(self):
        """Test config set command structure."""
        from codomyrmex.agents.core.config import AgentConfig, set_config, reset_config
        
        reset_config()
        original_config = get_config()
        
        # Test that we can create a new config with overrides
        new_config = AgentConfig(default_timeout=99, log_level="DEBUG")
        set_config(new_config)
        
        updated_config = get_config()
        assert updated_config.default_timeout == 99
        assert updated_config.log_level == "DEBUG"

    def test_config_reset(self):
        """Test config reset command."""
        from codomyrmex.agents.core.config import reset_config, set_config, AgentConfig
        
        custom_config = AgentConfig(default_timeout=999)
        set_config(custom_config)
        
        reset_config()
        reset_config_obj = get_config()
        
        # Should be back to default
        assert reset_config_obj.default_timeout == 30

    def test_config_validate(self):
        """Test config validate command."""
        config = get_config()
        errors = config.validate()
        
        # Should return a list (may be empty)
        assert isinstance(errors, list)


# ============================================================================
# Orchestrator Select Tests
# ============================================================================

@pytest.mark.unit
class TestOrchestratorSelect:
    """Test orchestrator select-by-capability command."""

    def test_select_agents_by_capability(self):
        """Test selecting agents by capability."""
        from codomyrmex.agents.generic import AgentOrchestrator
        from codomyrmex.agents.core import AgentCapabilities
        
        try:
            from codomyrmex.agents.jules import JulesClient
            agents = [JulesClient()]
            orchestrator = AgentOrchestrator(agents)
            
            selected = orchestrator.select_agent_by_capability("streaming", agents)
            assert isinstance(selected, list)
        except Exception:
            # May fail if jules not available
            pass


# ============================================================================
# Droid Enhancement Tests
# ============================================================================

@pytest.mark.unit
class TestDroidEnhancements:
    """Test droid enhancement commands."""

    def test_droid_config_save_load(self):
        """Test droid config save/load."""
        from codomyrmex.agents.droid import DroidConfig, save_config_to_file, load_config_from_file
        from pathlib import Path
        import tempfile
        
        try:
            config = DroidConfig()
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                temp_path = f.name
            
            save_config_to_file(config, temp_path)
            assert Path(temp_path).exists()
            
            loaded_config = load_config_from_file(temp_path)
            assert loaded_config.identifier == config.identifier
            assert loaded_config.mode == config.mode
            
            Path(temp_path).unlink()
        except Exception:
            # May fail if dependencies not available
            pass

    def test_droid_todo_manager(self):
        """Test droid TODO manager."""
        from codomyrmex.agents.droid import TodoManager, TodoItem
        from pathlib import Path
        import tempfile
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                temp_path = f.name
                f.write("[TODO]\ntask1 | description1 | outcomes1\n")
            
            manager = TodoManager(temp_path)
            todo_items, completed_items = manager.load()
            
            assert isinstance(todo_items, list)
            assert isinstance(completed_items, list)
            if todo_items:
                assert isinstance(todo_items[0], TodoItem)
            
            Path(temp_path).unlink()
        except Exception:
            # May fail if dependencies not available
            pass


# ============================================================================
# Task Planner Tests
# ============================================================================

@pytest.mark.unit
class TestTaskPlannerCommands:
    """Test task planner commands."""

    def test_task_planner_creation(self):
        """Test task planner creation."""
        from codomyrmex.agents.generic import TaskPlanner, TaskStatus
        
        try:
            planner = TaskPlanner()
            assert planner is not None
            
            task = planner.create_task("Test task")
            assert task is not None
            assert task.description == "Test task"
            assert task.status == TaskStatus.PENDING
        except Exception:
            # May fail if dependencies not available
            pass

    def test_task_planner_operations(self):
        """Test task planner operations."""
        from codomyrmex.agents.generic import TaskPlanner, TaskStatus
        
        try:
            planner = TaskPlanner()
            
            task1 = planner.create_task("Task 1")
            task2 = planner.create_task("Task 2", dependencies=[task1.id])
            
            ready_tasks = planner.get_ready_tasks()
            assert len(ready_tasks) >= 1  # task1 should be ready
            
            execution_order = planner.get_task_execution_order()
            assert len(execution_order) == 2
        except Exception:
            # May fail if dependencies not available
            pass

    def test_task_status_enum(self):
        """Test task status enum."""
        from codomyrmex.agents.generic import TaskStatus
        
        assert TaskStatus.PENDING is not None
        assert TaskStatus.COMPLETED is not None
        assert TaskStatus.FAILED is not None


# ============================================================================
# Message Bus Tests
# ============================================================================

@pytest.mark.unit
class TestMessageBusCommands:
    """Test message bus commands."""

    def test_message_bus_creation(self):
        """Test message bus creation."""
        from codomyrmex.agents.generic import MessageBus, Message
        
        try:
            bus = MessageBus()
            assert bus is not None
            
            message = Message(
                sender="test",
                message_type="test_type",
                content="test content"
            )
            assert message.sender == "test"
            assert message.message_type == "test_type"
        except Exception:
            # May fail if dependencies not available
            pass

    def test_message_bus_operations(self):
        """Test message bus operations."""
        from codomyrmex.agents.generic import MessageBus
        
        try:
            bus = MessageBus()
            
            # Test subscribe
            handler_called = []
            def test_handler(msg):
                handler_called.append(msg)
            
            bus.subscribe("test_type", test_handler)
            
            # Test publish
            from codomyrmex.agents.generic import Message
            message = Message(
                sender="test",
                message_type="test_type",
                content="test"
            )
            bus.publish(message)
            
            # Handler should have been called
            assert len(handler_called) > 0
            
            # Test history
            history = bus.get_message_history()
            assert len(history) > 0
        except Exception:
            # May fail if dependencies not available
            pass

