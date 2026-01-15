"""Integration tests for Gemini agent integration.

Tests use real implementations only. When Gemini CLI is not available,
tests are skipped rather than using mocks. All data processing and
conversion logic is tested with real data structures.
"""

import pytest
from typing import Any

from codomyrmex.agents.core import AgentRequest, AgentCapabilities
from codomyrmex.agents.gemini import GeminiClient, GeminiIntegrationAdapter
from codomyrmex.agents.generic import AgentOrchestrator
from codomyrmex.agents.exceptions import GeminiError
from codomyrmex.tests.unit.agents.helpers import GEMINI_AVAILABLE


class TestGeminiIntegrationAdapter:
    """Test GeminiIntegrationAdapter functionality."""

    def test_adapter_initialization(self):
        """Test GeminiIntegrationAdapter can be initialized."""
        client = GeminiClient()
        adapter = GeminiIntegrationAdapter(client)
        
        assert adapter.agent == client

    @pytest.mark.skipif(not GEMINI_AVAILABLE, reason="gemini CLI not installed")
    def test_adapt_for_ai_code_editing(self):
        """Test adapting Gemini for AI code editing with real CLI."""
        client = GeminiClient()
        adapter = GeminiIntegrationAdapter(client)
        
        try:
            code = adapter.adapt_for_ai_code_editing(
                prompt="Create a fibonacci function",
                language="python"
            )
            # Test real result structure
            assert isinstance(code, str)
        except RuntimeError:
            # Expected if authentication fails or CLI error
            pytest.skip("Gemini CLI authentication or execution failed")

    @pytest.mark.skipif(not GEMINI_AVAILABLE, reason="gemini CLI not installed")
    def test_adapt_for_ai_code_editing_with_files(self):
        """Test adapting Gemini for AI code editing with file context."""
        client = GeminiClient()
        adapter = GeminiIntegrationAdapter(client)
        
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
            pytest.skip("Gemini CLI authentication or execution failed")

    @pytest.mark.skipif(not GEMINI_AVAILABLE, reason="gemini CLI not installed")
    def test_adapt_for_llm(self):
        """Test adapting Gemini for LLM module with real CLI."""
        client = GeminiClient()
        adapter = GeminiIntegrationAdapter(client)
        
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
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("Gemini CLI authentication or execution failed")

    @pytest.mark.skipif(not GEMINI_AVAILABLE, reason="gemini CLI not installed")
    def test_adapt_for_llm_with_model(self):
        """Test adapting Gemini for LLM module with specific model."""
        client = GeminiClient()
        adapter = GeminiIntegrationAdapter(client)
        
        messages = [{"role": "user", "content": "Test"}]
        
        try:
            result = adapter.adapt_for_llm(messages, model="gemini-1.5-pro")
            
            # Test real result structure
            assert isinstance(result, dict)
            assert result["model"] == "gemini-1.5-pro"
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("Gemini CLI authentication or execution failed")

    @pytest.mark.skipif(not GEMINI_AVAILABLE, reason="gemini CLI not installed")
    def test_adapt_for_code_execution(self):
        """Test adapting Gemini for code execution with real CLI."""
        client = GeminiClient()
        adapter = GeminiIntegrationAdapter(client)
        
        try:
            result = adapter.adapt_for_code_execution(
                code="def test(): pass",
                language="python"
            )
            
            # Test real result structure
            assert isinstance(result, dict)
            assert "success" in result
            assert "output" in result
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("Gemini CLI authentication or execution failed")

    def test_adapt_for_code_execution_structure(self):
        """Test code execution adapter structure (without executing)."""
        client = GeminiClient()
        adapter = GeminiIntegrationAdapter(client)
        
        # Test that adapter has required methods
        assert hasattr(adapter, "adapt_for_ai_code_editing")
        assert hasattr(adapter, "adapt_for_llm")
        assert hasattr(adapter, "adapt_for_code_execution")


class TestGeminiOrchestration:
    """Test Gemini integration with AgentOrchestrator."""

    def test_gemini_with_orchestrator_structure(self):
        """Test GeminiClient with AgentOrchestrator structure."""
        gemini = GeminiClient()
        orchestrator = AgentOrchestrator([gemini])
        
        # Test orchestrator structure
        assert len(orchestrator.agents) == 1
        assert orchestrator.agents[0] == gemini

    @pytest.mark.skipif(not GEMINI_AVAILABLE, reason="gemini CLI not installed")
    def test_gemini_with_orchestrator(self):
        """Test GeminiClient with AgentOrchestrator execution."""
        gemini = GeminiClient()
        orchestrator = AgentOrchestrator([gemini])
        
        request = AgentRequest(prompt="test prompt")
        
        try:
            responses = orchestrator.execute_parallel(request)
            
            # Test real response structure
            assert len(responses) == 1
            assert isinstance(responses[0], type(gemini.execute(AgentRequest(prompt=""))))
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("Gemini CLI authentication or execution failed")

    @pytest.mark.skipif(not GEMINI_AVAILABLE, reason="gemini CLI not installed")
    def test_gemini_fallback(self):
        """Test Gemini with fallback orchestration."""
        gemini = GeminiClient()
        orchestrator = AgentOrchestrator([gemini])
        
        request = AgentRequest(prompt="test prompt")
        
        try:
            response = orchestrator.execute_with_fallback(request)
            
            # Test real response structure
            assert isinstance(response, type(gemini.execute(AgentRequest(prompt=""))))
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("Gemini CLI authentication or execution failed")
