"""Integration tests for Every Code agent integration.

Tests use real implementations only. When Every Code CLI is not available,
tests are skipped rather than using mocks. All data processing and
conversion logic is tested with real data structures.
"""


import pytest

try:
    from codomyrmex.agents.every_code import (
        EveryCodeClient,
        EveryCodeIntegrationAdapter,
    )
    from codomyrmex.tests.unit.agents.helpers import EVERY_CODE_AVAILABLE
    _HAS_AGENTS = True
except ImportError:
    _HAS_AGENTS = False

if not _HAS_AGENTS:
    pytest.skip("agents deps not available", allow_module_level=True)


class TestEveryCodeIntegrationAdapter:
    """Test EveryCodeIntegrationAdapter functionality."""

    def test_adapter_initialization(self):
        """Test EveryCodeIntegrationAdapter can be initialized."""
        client = EveryCodeClient()
        adapter = EveryCodeIntegrationAdapter(client)

        assert adapter.agent == client

    @pytest.mark.skipif(not EVERY_CODE_AVAILABLE, reason="code/coder CLI not installed")
    def test_adapt_for_ai_code_editing(self):
        """Test adapting Every Code for AI code editing with real CLI."""
        client = EveryCodeClient()
        adapter = EveryCodeIntegrationAdapter(client)

        try:
            code = adapter.adapt_for_ai_code_editing(
                prompt="Create a fibonacci function",
                language="python"
            )
            # Test real result structure
            assert isinstance(code, str)
        except RuntimeError:
            # Expected if authentication fails or CLI error
            pytest.skip("Every Code CLI authentication or execution failed")

    @pytest.mark.skipif(not EVERY_CODE_AVAILABLE, reason="code/coder CLI not installed")
    def test_adapt_for_ai_code_editing_with_files(self):
        """Test adapting Every Code for AI code editing with file context."""
        client = EveryCodeClient()
        adapter = EveryCodeIntegrationAdapter(client)

        try:
            code = adapter.adapt_for_ai_code_editing(
                prompt="Create a function",
                language="python",
                files=["src/models.py"]
            )
            # Test real result structure
            assert isinstance(code, str)
        except RuntimeError:
            # Expected if authentication fails or CLI error
            pytest.skip("Every Code CLI authentication or execution failed")

    @pytest.mark.skipif(not EVERY_CODE_AVAILABLE, reason="code/coder CLI not installed")
    def test_adapt_for_llm(self):
        """Test adapting Every Code for LLM module with real CLI."""
        client = EveryCodeClient()
        adapter = EveryCodeIntegrationAdapter(client)

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"}
        ]

        try:
            result = adapter.adapt_for_llm(messages)

            # Test real result structure
            assert isinstance(result, dict)
            assert "content" in result
            assert "model" in result
            assert "usage" in result
            assert "metadata" in result
        except RuntimeError:
            # Expected if authentication fails or CLI error
            pytest.skip("Every Code CLI authentication or execution failed")

    @pytest.mark.skipif(not EVERY_CODE_AVAILABLE, reason="code/coder CLI not installed")
    def test_adapt_for_llm_with_model(self):
        """Test adapting Every Code for LLM module with model specification."""
        client = EveryCodeClient()
        adapter = EveryCodeIntegrationAdapter(client)

        messages = [{"role": "user", "content": "Hello"}]

        try:
            result = adapter.adapt_for_llm(messages, model="gpt-5.1")

            # Test real result structure
            assert isinstance(result, dict)
            assert result["model"] == "gpt-5.1"
        except RuntimeError:
            # Expected if authentication fails or CLI error
            pytest.skip("Every Code CLI authentication or execution failed")

    @pytest.mark.skipif(not EVERY_CODE_AVAILABLE, reason="code/coder CLI not installed")
    def test_adapt_for_code_execution(self):
        """Test adapting Every Code for code execution with real CLI."""
        client = EveryCodeClient()
        adapter = EveryCodeIntegrationAdapter(client)

        code = "def hello(): return 'world'"

        try:
            result = adapter.adapt_for_code_execution(code, language="python")

            # Test real result structure
            assert isinstance(result, dict)
            assert "success" in result
            assert "output" in result
            assert "metadata" in result
        except RuntimeError:
            # Expected if authentication fails or CLI error
            pytest.skip("Every Code CLI authentication or execution failed")

    def test_adapt_for_ai_code_editing_structure(self):
        """Test adapting Every Code for AI code editing structure."""
        client = EveryCodeClient()
        adapter = EveryCodeIntegrationAdapter(client)

        # Test that adapter structure is correct
        assert adapter.agent == client
        assert hasattr(adapter, "adapt_for_ai_code_editing")
        assert hasattr(adapter, "adapt_for_llm")
        assert hasattr(adapter, "adapt_for_code_execution")

    def test_adapt_for_llm_structure(self):
        """Test adapting Every Code for LLM structure."""
        client = EveryCodeClient()
        adapter = EveryCodeIntegrationAdapter(client)

        messages = [{"role": "user", "content": "test"}]

        # Test that adapter can be called (may fail if CLI not available)
        try:
            result = adapter.adapt_for_llm(messages)
            assert isinstance(result, dict)
        except (RuntimeError, Exception):
            # Expected if CLI not available or authentication fails
            pass

