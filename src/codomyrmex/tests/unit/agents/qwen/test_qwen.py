"""Unit tests for codomyrmex.agents.qwen module.

Tests follow the Zero-Mock policy — all assertions use real objects.
API-dependent tests are skipped when DASHSCOPE_API_KEY is not set.
"""

import os

import pytest

from codomyrmex.agents.qwen import DEFAULT_MODEL, QWEN_MODELS, QwenClient
from codomyrmex.agents.qwen.qwen_client import DEFAULT_BASE_URL


# --- Model Registry ---


class TestQwenModelRegistry:
    """Tests for the Qwen model registry."""

    def test_registry_has_models(self):
        assert len(QWEN_MODELS) >= 14

    def test_default_model_in_registry(self):
        assert DEFAULT_MODEL in QWEN_MODELS

    def test_all_models_have_context(self):
        for name, info in QWEN_MODELS.items():
            assert "context" in info, f"{name} missing context"
            assert isinstance(info["context"], int)
            assert info["context"] > 0

    def test_all_models_have_category(self):
        for name, info in QWEN_MODELS.items():
            assert "category" in info, f"{name} missing category"
            assert info["category"] in {
                "flagship", "code", "general", "long", "vision", "lightweight",
            }

    def test_code_models_exist(self):
        code_models = QwenClient.get_code_models()
        assert len(code_models) >= 3
        assert "qwen-coder-turbo" in code_models

    def test_list_models_returns_copy(self):
        models = QwenClient.list_models()
        assert models == QWEN_MODELS
        # Modifying copy doesn't affect original
        models["test-model"] = {"context": 1, "category": "test"}
        assert "test-model" not in QWEN_MODELS


# --- Client Construction ---


class TestQwenClientConstruction:
    """Tests for QwenClient initialization.

    Uses a dummy API key to test construction without real credentials.
    """

    DUMMY_CONFIG = {"qwen_api_key": "test-dummy-key-for-construction"}

    def test_client_name(self):
        client = QwenClient(config=self.DUMMY_CONFIG)
        assert client.name == "qwen"

    def test_default_base_url(self):
        client = QwenClient(config=self.DUMMY_CONFIG)
        assert client._base_url == DEFAULT_BASE_URL

    def test_custom_config_base_url(self):
        config = {**self.DUMMY_CONFIG, "qwen_base_url": "https://custom.api/v1"}
        client = QwenClient(config=config)
        assert client._base_url == "https://custom.api/v1"

    def test_capabilities_include_streaming(self):
        from codomyrmex.agents.core import AgentCapabilities
        client = QwenClient(config=self.DUMMY_CONFIG)
        caps = client.capabilities
        assert AgentCapabilities.STREAMING in caps
        assert AgentCapabilities.CODE_GENERATION in caps
        assert AgentCapabilities.MULTI_TURN in caps


# --- Imports ---


class TestQwenImports:
    """Tests for module imports and lazy loading."""

    def test_core_imports(self):
        from codomyrmex.agents.qwen import DEFAULT_MODEL, QWEN_MODELS, QwenClient
        assert QwenClient is not None
        assert isinstance(QWEN_MODELS, dict)
        assert isinstance(DEFAULT_MODEL, str)

    def test_mcp_tools_importable(self):
        from codomyrmex.agents.qwen import mcp_tools
        assert hasattr(mcp_tools, "qwen_chat")
        assert hasattr(mcp_tools, "qwen_list_models")
        assert hasattr(mcp_tools, "qwen_code_review")
        assert hasattr(mcp_tools, "qwen_chat_with_tools")
        assert hasattr(mcp_tools, "qwen_create_agent")

    def test_wrapper_importable(self):
        from codomyrmex.agents.qwen import qwen_agent_wrapper
        assert hasattr(qwen_agent_wrapper, "create_assistant")
        assert hasattr(qwen_agent_wrapper, "run_assistant")
        assert hasattr(qwen_agent_wrapper, "stream_assistant")
        assert hasattr(qwen_agent_wrapper, "launch_webui")
        assert hasattr(qwen_agent_wrapper, "create_codomyrmex_assistant")

    def test_lazy_import_attribute_error(self):
        import codomyrmex.agents.qwen as qwen_mod
        with pytest.raises(AttributeError):
            _ = qwen_mod.nonexistent_attribute


# --- MCP Tools (offline) ---


class TestQwenMCPTools:
    """Tests for MCP tool functions (offline, no API calls)."""

    def test_list_models_tool(self):
        from codomyrmex.agents.qwen.mcp_tools import qwen_list_models
        result = qwen_list_models()
        assert "models" in result
        assert "code_models" in result
        assert "total" in result
        assert result["total"] >= 14


# --- API Integration (requires DASHSCOPE_API_KEY) ---


HAS_API_KEY = bool(os.getenv("DASHSCOPE_API_KEY") or os.getenv("QWEN_API_KEY"))


@pytest.mark.skipif(not HAS_API_KEY, reason="DASHSCOPE_API_KEY not set")
class TestQwenAPIIntegration:
    """Integration tests requiring real API access."""

    def test_simple_chat(self):
        from codomyrmex.agents.core import AgentRequest
        client = QwenClient()
        request = AgentRequest(
            prompt="What is 2+2? Answer with just the number.",
        )
        response = client._execute_impl(request)
        assert response.content
        assert "4" in response.content

    def test_streaming(self):
        from codomyrmex.agents.core import AgentRequest
        client = QwenClient()
        request = AgentRequest(prompt="Say hello")
        chunks = list(client._stream_impl(request))
        assert len(chunks) > 0
        full = "".join(chunks)
        assert len(full) > 0
