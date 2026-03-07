"""Comprehensive unit tests for codomyrmex.agents.qwen module.

Tests follow the Zero-Mock policy — all assertions use real objects.
API-dependent tests are skipped when DASHSCOPE_API_KEY is not set.
qwen-agent framework tests are skipped when qwen-agent is not installed.

Coverage:
- QwenClient: __init__, _execute_impl, _stream_impl, chat_with_tools,
  list_models, get_code_models, _extract_tools
- qwen_agent_wrapper: create_assistant, run_assistant, stream_assistant,
  launch_webui, create_codomyrmex_assistant, QWEN_BUILTIN_TOOLS
- mcp_tools: qwen_chat, qwen_chat_with_tools, qwen_list_models,
  qwen_create_agent, qwen_code_review (offline + API)
"""

import os

import pytest

from codomyrmex.agents.qwen import DEFAULT_MODEL, QWEN_MODELS, QwenClient
from codomyrmex.agents.qwen.qwen_client import DEFAULT_BASE_URL

HAS_API_KEY = bool(os.getenv("DASHSCOPE_API_KEY") or os.getenv("QWEN_API_KEY"))
DUMMY_CONFIG = {"qwen_api_key": "test-dummy-key-for-construction"}

try:
    from qwen_agent.agents import Assistant as _QwenAssistant

    HAS_QWEN_AGENT = True
except ImportError:
    HAS_QWEN_AGENT = False


# ============================================================================
# Model Registry
# ============================================================================


class TestQwenModelRegistry:
    """Tests for the Qwen model registry (14 models)."""

    def test_registry_has_models(self):
        assert len(QWEN_MODELS) >= 14

    def test_default_model_in_registry(self):
        assert DEFAULT_MODEL in QWEN_MODELS

    def test_default_model_is_coder(self):
        assert QWEN_MODELS[DEFAULT_MODEL]["category"] == "code"

    def test_all_models_have_context(self):
        for name, info in QWEN_MODELS.items():
            assert "context" in info, f"{name} missing context"
            assert isinstance(info["context"], int)
            assert info["context"] > 0

    def test_all_models_have_category(self):
        categories = {"flagship", "code", "general", "long", "vision", "lightweight"}
        for name, info in QWEN_MODELS.items():
            assert "category" in info, f"{name} missing category"
            assert info["category"] in categories, (
                f"{name} has unknown category {info['category']}"
            )

    def test_code_models_exist(self):
        code_models = QwenClient.get_code_models()
        assert len(code_models) >= 3
        assert "qwen-coder-turbo" in code_models
        assert "qwen-coder-plus" in code_models

    def test_list_models_returns_copy(self):
        models = QwenClient.list_models()
        assert models == QWEN_MODELS
        models["test-model"] = {"context": 1, "category": "test"}
        assert "test-model" not in QWEN_MODELS

    def test_flagship_models_exist(self):
        flagship = [k for k, v in QWEN_MODELS.items() if v["category"] == "flagship"]
        assert len(flagship) >= 2
        assert "qwen3-max" in flagship

    def test_vision_models_exist(self):
        vision = [k for k, v in QWEN_MODELS.items() if v["category"] == "vision"]
        assert len(vision) >= 2
        assert "qwen-vl-max" in vision

    def test_long_context_model(self):
        long_models = [k for k, v in QWEN_MODELS.items() if v["category"] == "long"]
        assert len(long_models) >= 1
        for m in long_models:
            assert QWEN_MODELS[m]["context"] >= 1000000

    def test_context_lengths_reasonable(self):
        for name, info in QWEN_MODELS.items():
            assert info["context"] >= 4096, f"{name} context too small"
            assert info["context"] <= 10_000_000, f"{name} context unreasonably large"


# ============================================================================
# Client Construction
# ============================================================================


class TestQwenClientConstruction:
    """Tests for QwenClient initialization (uses dummy API key)."""

    def test_client_name(self):
        client = QwenClient(config=DUMMY_CONFIG)
        assert client.name == "qwen"

    def test_default_base_url(self):
        client = QwenClient(config=DUMMY_CONFIG)
        assert client._base_url == DEFAULT_BASE_URL

    def test_custom_base_url(self):
        config = {**DUMMY_CONFIG, "qwen_base_url": "https://custom.api/v1"}
        client = QwenClient(config=config)
        assert client._base_url == "https://custom.api/v1"

    def test_capabilities_code_generation(self):
        from codomyrmex.agents.core import AgentCapabilities

        client = QwenClient(config=DUMMY_CONFIG)
        caps = client.capabilities
        assert AgentCapabilities.CODE_GENERATION in caps

    def test_capabilities_streaming(self):
        from codomyrmex.agents.core import AgentCapabilities

        client = QwenClient(config=DUMMY_CONFIG)
        assert AgentCapabilities.STREAMING in client.capabilities

    def test_capabilities_multi_turn(self):
        from codomyrmex.agents.core import AgentCapabilities

        client = QwenClient(config=DUMMY_CONFIG)
        assert AgentCapabilities.MULTI_TURN in client.capabilities

    def test_capabilities_code_editing(self):
        from codomyrmex.agents.core import AgentCapabilities

        client = QwenClient(config=DUMMY_CONFIG)
        assert AgentCapabilities.CODE_EDITING in client.capabilities

    def test_capabilities_code_analysis(self):
        from codomyrmex.agents.core import AgentCapabilities

        client = QwenClient(config=DUMMY_CONFIG)
        assert AgentCapabilities.CODE_ANALYSIS in client.capabilities

    def test_capabilities_text_completion(self):
        from codomyrmex.agents.core import AgentCapabilities

        client = QwenClient(config=DUMMY_CONFIG)
        assert AgentCapabilities.TEXT_COMPLETION in client.capabilities

    def test_all_six_capabilities(self):
        from codomyrmex.agents.core import AgentCapabilities

        client = QwenClient(config=DUMMY_CONFIG)
        expected = {
            AgentCapabilities.CODE_GENERATION,
            AgentCapabilities.CODE_EDITING,
            AgentCapabilities.CODE_ANALYSIS,
            AgentCapabilities.TEXT_COMPLETION,
            AgentCapabilities.STREAMING,
            AgentCapabilities.MULTI_TURN,
        }
        assert expected == set(client.capabilities)

    def test_extract_tools_no_metadata(self):
        """_extract_tools returns None when request has no metadata."""
        from codomyrmex.agents.core import AgentRequest

        client = QwenClient(config=DUMMY_CONFIG)
        request = AgentRequest(prompt="test")
        result = client._extract_tools(request)
        assert result is None


# ============================================================================
# Imports and Lazy Loading
# ============================================================================


class TestQwenImports:
    """Tests for module imports and lazy loading."""

    def test_core_imports(self):
        from codomyrmex.agents.qwen import DEFAULT_MODEL, QWEN_MODELS, QwenClient

        assert QwenClient is not None
        assert isinstance(QWEN_MODELS, dict)
        assert isinstance(DEFAULT_MODEL, str)

    def test_module_version(self):
        from codomyrmex.agents.qwen import __version__

        assert __version__ == "1.1.4"

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

    def test_lazy_import_create_assistant(self):
        """Lazy import for create_assistant should work."""
        import codomyrmex.agents.qwen as qwen_mod

        fn = qwen_mod.create_assistant
        assert callable(fn)

    def test_lazy_import_run_assistant(self):
        import codomyrmex.agents.qwen as qwen_mod

        fn = qwen_mod.run_assistant
        assert callable(fn)

    def test_lazy_import_stream_assistant(self):
        import codomyrmex.agents.qwen as qwen_mod

        fn = qwen_mod.stream_assistant
        assert callable(fn)

    def test_lazy_import_launch_webui(self):
        import codomyrmex.agents.qwen as qwen_mod

        fn = qwen_mod.launch_webui
        assert callable(fn)

    def test_lazy_import_create_codomyrmex_assistant(self):
        import codomyrmex.agents.qwen as qwen_mod

        fn = qwen_mod.create_codomyrmex_assistant
        assert callable(fn)

    def test_lazy_import_attribute_error(self):
        import codomyrmex.agents.qwen as qwen_mod

        with pytest.raises(AttributeError):
            _ = qwen_mod.nonexistent_attribute


# ============================================================================
# MCP Tools (offline)
# ============================================================================


class TestQwenMCPToolsOffline:
    """Tests for MCP tool functions that work offline (no API calls)."""

    def test_list_models_tool_returns_dict(self):
        from codomyrmex.agents.qwen.mcp_tools import qwen_list_models

        result = qwen_list_models()
        assert isinstance(result, dict)

    def test_list_models_tool_has_models(self):
        from codomyrmex.agents.qwen.mcp_tools import qwen_list_models

        result = qwen_list_models()
        assert "models" in result
        assert len(result["models"]) >= 14

    def test_list_models_tool_has_code_models(self):
        from codomyrmex.agents.qwen.mcp_tools import qwen_list_models

        result = qwen_list_models()
        assert "code_models" in result
        assert "qwen-coder-turbo" in result["code_models"]

    def test_list_models_tool_has_total(self):
        from codomyrmex.agents.qwen.mcp_tools import qwen_list_models

        result = qwen_list_models()
        assert result["total"] >= 14
        assert result["total"] == len(result["models"])

    def test_create_agent_without_qwen_agent(self):
        """qwen_create_agent returns error when qwen-agent not installed."""
        from codomyrmex.agents.qwen.mcp_tools import qwen_create_agent

        result = qwen_create_agent()
        if not HAS_QWEN_AGENT:
            assert result["status"] == "error"
            assert (
                "qwen-agent" in result["error"].lower()
                or "not installed" in result["error"].lower()
            )
        else:
            assert result["status"] == "success"

    def test_all_mcp_tools_have_decorator(self):
        """All 5 MCP tool functions should have _mcp_tool_name attribute."""
        from codomyrmex.agents.qwen.mcp_tools import (
            qwen_chat,
            qwen_chat_with_tools,
            qwen_code_review,
            qwen_create_agent,
            qwen_list_models,
        )

        for tool in [
            qwen_chat,
            qwen_chat_with_tools,
            qwen_list_models,
            qwen_create_agent,
            qwen_code_review,
        ]:
            assert hasattr(tool, "_mcp_tool_name"), (
                f"{tool.__name__} missing _mcp_tool_name"
            )
            assert isinstance(tool._mcp_tool_name, str)
            assert len(tool._mcp_tool_name) > 0

    def test_mcp_tool_names_unique(self):
        """All MCP tool names must be unique."""
        from codomyrmex.agents.qwen.mcp_tools import (
            qwen_chat,
            qwen_chat_with_tools,
            qwen_code_review,
            qwen_create_agent,
            qwen_list_models,
        )

        names = [
            t._mcp_tool_name
            for t in [
                qwen_chat,
                qwen_chat_with_tools,
                qwen_list_models,
                qwen_create_agent,
                qwen_code_review,
            ]
        ]
        assert len(names) == len(set(names)), f"Duplicate MCP tool names: {names}"

    def test_all_mcp_tools_have_descriptions(self):
        from codomyrmex.agents.qwen.mcp_tools import (
            qwen_chat,
            qwen_chat_with_tools,
            qwen_code_review,
            qwen_create_agent,
            qwen_list_models,
        )

        for tool in [
            qwen_chat,
            qwen_chat_with_tools,
            qwen_list_models,
            qwen_create_agent,
            qwen_code_review,
        ]:
            assert hasattr(tool, "_mcp_tool_description"), (
                f"{tool.__name__} missing description"
            )
            assert len(tool._mcp_tool_description) > 10


# ============================================================================
# Wrapper Functions (offline)
# ============================================================================


class TestQwenWrapperOffline:
    """Tests for qwen_agent_wrapper functions that work offline."""

    def test_builtin_tools_list(self):
        from codomyrmex.agents.qwen.qwen_agent_wrapper import QWEN_BUILTIN_TOOLS

        assert isinstance(QWEN_BUILTIN_TOOLS, list)
        assert "code_interpreter" in QWEN_BUILTIN_TOOLS
        assert "image_gen" in QWEN_BUILTIN_TOOLS

    def test_create_assistant_raises_without_qwen_agent(self):
        """Should raise ImportError if qwen-agent is not installed."""
        from codomyrmex.agents.qwen.qwen_agent_wrapper import create_assistant

        if not HAS_QWEN_AGENT:
            with pytest.raises(ImportError, match="qwen-agent"):
                create_assistant()

    def test_create_codomyrmex_assistant_raises_without_qwen_agent(self):
        from codomyrmex.agents.qwen.qwen_agent_wrapper import (
            create_codomyrmex_assistant,
        )

        if not HAS_QWEN_AGENT:
            with pytest.raises(ImportError, match="qwen-agent"):
                create_codomyrmex_assistant()

    def test_launch_webui_raises_without_webui(self):
        """Should raise ImportError if gradio/WebUI not available."""
        from codomyrmex.agents.qwen.qwen_agent_wrapper import WebUI, launch_webui

        if WebUI is None:
            with pytest.raises(ImportError, match="gradio"):
                launch_webui(None)

    def test_run_assistant_is_callable(self):
        from codomyrmex.agents.qwen.qwen_agent_wrapper import run_assistant

        assert callable(run_assistant)

    def test_stream_assistant_is_callable(self):
        from codomyrmex.agents.qwen.qwen_agent_wrapper import stream_assistant

        assert callable(stream_assistant)


# ============================================================================
# Constants & Defaults
# ============================================================================


class TestQwenConstants:
    """Test module-level constants and defaults."""

    def test_default_model_value(self):
        assert DEFAULT_MODEL == "qwen-coder-turbo"

    def test_default_base_url_value(self):
        assert DEFAULT_BASE_URL == "https://dashscope.aliyuncs.com/compatible-mode/v1"

    def test_default_base_url_is_https(self):
        assert DEFAULT_BASE_URL.startswith("https://")

    def test_qwen_models_is_not_empty(self):
        assert len(QWEN_MODELS) > 0

    def test_default_model_has_128k_context(self):
        assert QWEN_MODELS[DEFAULT_MODEL]["context"] == 131072


# ============================================================================
# API Integration (requires DASHSCOPE_API_KEY)
# ============================================================================


@pytest.mark.skipif(not HAS_API_KEY, reason="DASHSCOPE_API_KEY not set")
class TestQwenAPIIntegration:
    """Integration tests requiring real DashScope API access."""

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
        request = AgentRequest(prompt="Say hello in 3 words")
        chunks = list(client._stream_impl(request))
        assert len(chunks) > 0
        full = "".join(chunks)
        assert len(full) > 0

    def test_response_has_tokens(self):
        from codomyrmex.agents.core import AgentRequest

        client = QwenClient()
        request = AgentRequest(prompt="Say hi")
        response = client._execute_impl(request)
        assert response.tokens_used is not None
        assert response.tokens_used > 0

    def test_response_has_metadata(self):
        from codomyrmex.agents.core import AgentRequest

        client = QwenClient()
        request = AgentRequest(prompt="Echo test")
        response = client._execute_impl(request)
        assert "usage" in response.metadata  # type: ignore
        assert "finish_reason" in response.metadata  # type: ignore

    def test_mcp_qwen_chat(self):
        from codomyrmex.agents.qwen.mcp_tools import qwen_chat

        result = qwen_chat("What is 1+1? Just the number.")
        assert result["status"] == "success"
        assert "2" in result["content"]

    def test_mcp_code_review(self):
        from codomyrmex.agents.qwen.mcp_tools import qwen_code_review

        result = qwen_code_review(
            code="def add(a, b):\n    return a + b",
            language="python",
            focus="general",
        )
        assert result["status"] == "success"
        assert len(result["review"]) > 0
