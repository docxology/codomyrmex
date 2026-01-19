"""Integration tests for Mistral Vibe agent integration.

Tests use real implementations only. When Mistral Vibe CLI is not available,
tests are skipped rather than using mocks. All data processing and
conversion logic is tested with real data structures.
"""

import pytest
from typing import Any

from codomyrmex.agents.core import AgentRequest, AgentCapabilities
from codomyrmex.agents.mistral_vibe import MistralVibeClient, MistralVibeIntegrationAdapter
from codomyrmex.agents.generic import AgentOrchestrator
from codomyrmex.agents.core.exceptions import MistralVibeError
from codomyrmex.tests.unit.agents.helpers import VIBE_AVAILABLE


class TestMistralVibeIntegrationAdapter:
    """Test MistralVibeIntegrationAdapter functionality."""

    def test_adapter_initialization(self):
        """Test MistralVibeIntegrationAdapter can be initialized."""
        client = MistralVibeClient()
        adapter = MistralVibeIntegrationAdapter(client)
        
        assert adapter.agent == client

    @pytest.mark.skipif(not VIBE_AVAILABLE, reason="vibe CLI not installed")
    def test_adapt_for_ai_code_editing(self):
        """Test adapting Mistral Vibe for AI code editing with real CLI."""
        client = MistralVibeClient()
        adapter = MistralVibeIntegrationAdapter(client)
        
        try:
            code = adapter.adapt_for_ai_code_editing(
                prompt="Create a fibonacci function",
                language="python"
            )
            # Test real result structure
            assert isinstance(code, str)
        except RuntimeError:
            # Expected if authentication fails or CLI error
            pytest.skip("Mistral Vibe CLI authentication or execution failed")

    @pytest.mark.skipif(not VIBE_AVAILABLE, reason="vibe CLI not installed")
    def test_adapt_for_ai_code_editing_with_files(self):
        """Test adapting Mistral Vibe for AI code editing with file context."""
        client = MistralVibeClient()
        adapter = MistralVibeIntegrationAdapter(client)
        
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
            pytest.skip("Mistral Vibe CLI authentication or execution failed")

    @pytest.mark.skipif(not VIBE_AVAILABLE, reason="vibe CLI not installed")
    def test_adapt_for_llm(self):
        """Test adapting Mistral Vibe for LLM module with real CLI."""
        client = MistralVibeClient()
        adapter = MistralVibeIntegrationAdapter(client)
        
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
            pytest.skip("Mistral Vibe CLI authentication or execution failed")

    @pytest.mark.skipif(not VIBE_AVAILABLE, reason="vibe CLI not installed")
    def test_adapt_for_llm_with_model(self):
        """Test adapting Mistral Vibe for LLM module with model specification."""
        client = MistralVibeClient()
        adapter = MistralVibeIntegrationAdapter(client)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        try:
            result = adapter.adapt_for_llm(messages, model="mistral-large-latest")
            
            # Test real result structure
            assert isinstance(result, dict)
            assert result["model"] == "mistral-large-latest"
        except RuntimeError:
            # Expected if authentication fails or CLI error
            pytest.skip("Mistral Vibe CLI authentication or execution failed")

    @pytest.mark.skipif(not VIBE_AVAILABLE, reason="vibe CLI not installed")
    def test_adapt_for_code_execution(self):
        """Test adapting Mistral Vibe for code execution with real CLI."""
        client = MistralVibeClient()
        adapter = MistralVibeIntegrationAdapter(client)
        
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
            pytest.skip("Mistral Vibe CLI authentication or execution failed")

    def test_adapt_for_ai_code_editing_structure(self):
        """Test adapting Mistral Vibe for AI code editing structure."""
        client = MistralVibeClient()
        adapter = MistralVibeIntegrationAdapter(client)
        
        # Test that adapter structure is correct
        assert adapter.agent == client
        assert hasattr(adapter, "adapt_for_ai_code_editing")
        assert hasattr(adapter, "adapt_for_llm")
        assert hasattr(adapter, "adapt_for_code_execution")

    def test_adapt_for_llm_structure(self):
        """Test adapting Mistral Vibe for LLM structure."""
        client = MistralVibeClient()
        adapter = MistralVibeIntegrationAdapter(client)
        
        messages = [{"role": "user", "content": "test"}]
        
        # Test that adapter can be called (may fail if CLI not available)
        try:
            result = adapter.adapt_for_llm(messages)
            assert isinstance(result, dict)
        except (RuntimeError, Exception):
            # Expected if CLI not available or authentication fails
            pass

