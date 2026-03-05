"""Integration tests for agent_brain.py — agents + agentic_memory integration."""

import sys
from pathlib import Path

import pytest

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestAgentImports:
    """Verify codomyrmex.agents imports used in agent_brain."""

    def test_import_agent_interface(self):
        """AgentInterface is importable from codomyrmex.agents."""
        from codomyrmex.agents import AgentInterface

        assert AgentInterface is not None

    def test_import_base_agent(self):
        """BaseAgent is importable from codomyrmex.agents."""
        from codomyrmex.agents import BaseAgent

        assert BaseAgent is not None

    def test_import_agent_request_response(self):
        """AgentRequest and AgentResponse are importable."""
        from codomyrmex.agents import AgentRequest, AgentResponse

        assert AgentRequest is not None
        assert AgentResponse is not None

    def test_import_agent_capabilities(self):
        """AgentCapabilities enum is importable and has values."""
        from codomyrmex.agents import AgentCapabilities

        assert AgentCapabilities is not None
        assert len(list(AgentCapabilities)) > 0

    def test_import_get_config(self):
        """get_config() function is importable and callable."""
        from codomyrmex.agents import get_config

        assert callable(get_config)
        config = get_config()
        assert config is not None


class TestAgenticMemoryImports:
    """Verify codomyrmex.agentic_memory imports used in agent_brain."""

    def test_import_agent_memory(self):
        """AgentMemory is importable."""
        from codomyrmex.agentic_memory import AgentMemory

        assert AgentMemory is not None

    def test_import_memory_types(self):
        """MemoryType enum is importable and has expected values."""
        from codomyrmex.agentic_memory import MemoryType

        assert MemoryType is not None
        values = [t.value for t in MemoryType]
        assert "knowledge" in values

    def test_import_memory_importance(self):
        """MemoryImportance enum is importable."""
        from codomyrmex.agentic_memory import MemoryImportance

        assert MemoryImportance is not None
        values = [i.value for i in MemoryImportance]
        assert "normal" in values

    def test_import_in_memory_store(self):
        """InMemoryStore is importable and constructable."""
        from codomyrmex.agentic_memory import InMemoryStore

        store = InMemoryStore()
        assert store is not None

    def test_import_memory_model(self):
        """Memory and RetrievalResult models are importable."""
        from codomyrmex.agentic_memory import Memory, RetrievalResult

        assert Memory is not None
        assert RetrievalResult is not None


class TestAgentBrainModule:
    """Functional tests for AgentBrain class."""

    def test_has_agent_modules_flag(self):
        """HAS_AGENT_MODULES flag is True in agent_brain.py."""
        from src.agent_brain import HAS_AGENT_MODULES

        assert HAS_AGENT_MODULES is True

    def test_agent_brain_instantiation(self):
        """AgentBrain can be instantiated without errors."""
        from src.agent_brain import AgentBrain

        brain = AgentBrain()
        assert brain is not None
        assert brain.memory is not None

    def test_list_available_agents_returns_list(self):
        """list_available_agents() returns a list."""
        from src.agent_brain import AgentBrain

        result = AgentBrain.list_available_agents()
        assert isinstance(result, list)

    def test_remember_returns_memory(self):
        """remember() stores content and returns a Memory object."""
        from codomyrmex.agentic_memory import Memory
        from src.agent_brain import AgentBrain

        brain = AgentBrain()
        mem = brain.remember("Test knowledge content", "knowledge", "normal")
        assert mem is not None
        assert isinstance(mem, Memory)

    def test_recall_returns_list(self):
        """recall() returns a list of results after storing content."""
        from src.agent_brain import AgentBrain

        brain = AgentBrain()
        brain.remember("Python is a programming language", "knowledge")
        results = brain.recall("Python", k=5)
        assert isinstance(results, list)

    def test_agent_config_summary_has_required_keys(self):
        """agent_config_summary() returns dict with required keys."""
        from src.agent_brain import AgentBrain

        brain = AgentBrain()
        summary = brain.agent_config_summary()
        assert isinstance(summary, dict)
        assert "available_providers" in summary
        assert "agent_interface" in summary
        assert "base_agent" in summary
        assert isinstance(summary["available_providers"], list)
