"""Workflow integration test: /codomyrmexMemory."""

import pytest

from codomyrmex.agentic_memory import AgentMemory, InMemoryStore


@pytest.mark.integration
class TestWorkflowMemory:
    """Tests mirroring the /codomyrmexMemory workflow."""

    def test_add_memory_returns_result(self):
        """add_memory with valid content returns a result."""
        memory = AgentMemory(store=InMemoryStore())
        result = memory.remember("Test memory entry")
        assert result.content == "Test memory entry"
        assert memory.store.get(result.id) == result

    def test_add_memory_with_high_importance(self):
        """High-importance memory is accepted."""
        from codomyrmex.agentic_memory import MemoryImportance

        memory = AgentMemory(store=InMemoryStore())
        result = memory.remember(
            "Critical finding: module X has O(n²) loop",
            importance=MemoryImportance.HIGH,
        )
        assert result.importance is MemoryImportance.HIGH
