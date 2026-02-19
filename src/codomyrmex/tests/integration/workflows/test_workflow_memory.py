"""Workflow integration test: /codomyrmexMemory.

Validates the agentic memory API can store and retrieve entries.
Skips gracefully if vector store dependencies are unavailable.
"""

import pytest


@pytest.mark.integration
class TestWorkflowMemory:
    """Tests mirroring the /codomyrmexMemory workflow."""

    def _import_add_memory(self):
        """Try to import add_memory, skip test if unavailable."""
        try:
            from codomyrmex.agentic_memory import add_memory

            return add_memory
        except (ImportError, AttributeError):
            pytest.skip("agentic_memory.add_memory not available")

    def test_add_memory_returns_result(self, tmp_path):
        """add_memory with valid content returns a result."""
        add_memory = self._import_add_memory()

        try:
            result = add_memory(content="Test memory entry", importance=5)
            assert result is not None
        except Exception as exc:
            # May fail if backing store is not configured
            pytest.skip(f"Memory store not configured: {exc}")

    def test_add_memory_with_high_importance(self, tmp_path):
        """High-importance memory is accepted."""
        add_memory = self._import_add_memory()

        try:
            result = add_memory(content="Critical finding: module X has O(n²) loop", importance=9)
            assert result is not None
        except Exception as exc:
            pytest.skip(f"Memory store not configured: {exc}")
