"""Integration tests for llm_inference.py — llm + collaboration integration."""

import sys
from pathlib import Path

import pytest

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestLLMImports:
    """Verify codomyrmex.llm imports used in llm_inference."""

    def test_import_llm_config(self):
        """LLMConfig is importable and constructable."""
        from codomyrmex.llm import LLMConfig

        config = LLMConfig()
        assert config is not None

    def test_import_llm_config_presets(self):
        """LLMConfigPresets is importable and constructable."""
        from codomyrmex.llm import LLMConfigPresets

        presets = LLMConfigPresets()
        assert presets is not None

    def test_import_ollama_manager(self):
        """OllamaManager is importable."""
        from codomyrmex.llm import OllamaManager

        assert OllamaManager is not None

    def test_import_mcp_bridge(self):
        """MCPBridge is importable."""
        from codomyrmex.llm import MCPBridge

        assert MCPBridge is not None

    def test_import_providers_submodule(self):
        """providers submodule is importable."""
        from codomyrmex.llm import providers

        assert providers is not None

    def test_import_fabric_manager(self):
        """FabricManager is importable."""
        from codomyrmex.llm import FabricManager

        assert FabricManager is not None


class TestCollaborationImports:
    """Verify codomyrmex.collaboration imports used in llm_inference."""

    def test_import_swarm_manager(self):
        """SwarmManager is importable and constructable."""
        from codomyrmex.collaboration import SwarmManager

        manager = SwarmManager()
        assert manager is not None

    def test_import_agent_pool(self):
        """AgentPool is importable."""
        from codomyrmex.collaboration import AgentPool

        assert AgentPool is not None

    def test_import_message_bus(self):
        """MessageBus is importable and constructable."""
        from codomyrmex.collaboration import MessageBus

        bus = MessageBus()
        assert bus is not None

    def test_import_task_decomposer(self):
        """TaskDecomposer is importable and constructable."""
        from codomyrmex.collaboration import TaskDecomposer

        decomposer = TaskDecomposer()
        assert decomposer is not None

    def test_import_task_priority(self):
        """TaskPriority enum is importable with expected values."""
        from codomyrmex.collaboration import TaskPriority

        values = [p.value for p in TaskPriority]
        assert len(values) > 0
        assert "normal" in values or "NORMAL" in values or any(v for v in values)

    def test_import_task_status(self):
        """TaskStatus enum is importable with expected values."""
        from codomyrmex.collaboration import TaskStatus

        values = [s.value for s in TaskStatus]
        assert len(values) > 0

    def test_import_task_model(self):
        """Task model is importable."""
        from codomyrmex.collaboration import Task, TaskPriority

        task = Task(
            id="test-task-001",
            description="Test task",
            priority=TaskPriority.NORMAL,
        )
        assert task is not None
        assert task.id == "test-task-001"


class TestLLMInferenceModule:
    """Functional tests for LLMInference class."""

    def test_has_llm_modules_flag(self):
        """HAS_LLM_MODULES flag is True in llm_inference.py."""
        from src.llm_inference import HAS_LLM_MODULES

        assert HAS_LLM_MODULES is True

    def test_llm_inference_instantiation(self):
        """LLMInference can be instantiated without errors."""
        from src.llm_inference import LLMInference

        inference = LLMInference()
        assert inference is not None
        assert inference.config is not None
        assert inference.swarm is not None
        assert inference.bus is not None

    def test_config_summary_returns_dict(self):
        """config_summary() returns a dict with expected keys."""
        from src.llm_inference import LLMInference

        inference = LLMInference()
        summary = inference.config_summary()
        assert isinstance(summary, dict)
        assert "config_class" in summary
        assert "presets_class" in summary
        assert "ollama_manager" in summary
        assert "providers_module" in summary

    def test_list_models_returns_dict(self):
        """list_models() returns dict with ollama_available key."""
        from src.llm_inference import LLMInference

        inference = LLMInference()
        result = inference.list_models()
        assert isinstance(result, dict)
        assert "ollama_available" in result
        assert "models" in result
        assert "model_count" in result
        assert isinstance(result["models"], list)
        assert isinstance(result["ollama_available"], bool)

    def test_agent_pool_status_returns_dict(self):
        """agent_pool_status() returns dict with required keys."""
        from src.llm_inference import LLMInference

        inference = LLMInference()
        result = inference.agent_pool_status()
        assert isinstance(result, dict)
        assert "pool_available" in result
        assert "swarm_class" in result
        assert "pool_class" in result
        assert "bus_class" in result
        assert result["pool_available"] is True

    def test_swarm_task_returns_dict(self):
        """swarm_task() returns dict with task_submitted key."""
        from src.llm_inference import LLMInference

        inference = LLMInference()
        result = inference.swarm_task("Summarize this test description")
        assert isinstance(result, dict)
        assert "task_submitted" in result
        assert "description" in result
        assert isinstance(result["task_submitted"], bool)

    def test_ollama_availability_check(self):
        """_ollama_available() returns a boolean without raising."""
        from src.llm_inference import _ollama_available

        result = _ollama_available()
        assert isinstance(result, bool)
