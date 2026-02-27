"""Comprehensive unit tests for the Gemini client module.

Tests GeminiClient initialization, configuration, capabilities,
error handling, and method contracts without requiring a live API.

Zero-mock policy: all tests use real GeminiClient objects instantiated
without an API key (self.client=None), which exercises the guard-clause
paths that raise GeminiError for every API-dependent method.
"""

import inspect
import os

import pytest

from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
    BaseAgent,
)
from codomyrmex.agents.core.exceptions import GeminiError
from codomyrmex.agents.gemini.gemini_client import GeminiClient

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_GEMINI_ENV_VARS = ("GEMINI_API_KEY", "GEMINI_MODEL")


def _clear_gemini_env() -> dict[str, str]:
    """Remove all GEMINI_* env vars and reset global AgentConfig singleton.

    Returns a dict of saved values for later restoration.
    """
    saved: dict[str, str] = {}
    for var in _GEMINI_ENV_VARS:
        val = os.environ.pop(var, None)
        if val is not None:
            saved[var] = val

    # Reset the cached AgentConfig singleton so it doesn't retain stale
    # env-derived values from earlier tests (e.g. via load_dotenv).
    from codomyrmex.agents.core.config import reset_config
    reset_config()

    return saved


def _restore_gemini_env(saved: dict[str, str]) -> None:
    """Restore previously saved GEMINI_* env vars and reset config."""
    for var, val in saved.items():
        os.environ[var] = val
    # Re-create the singleton with the restored env
    from codomyrmex.agents.core.config import reset_config
    reset_config()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def client_no_key():
    """GeminiClient with no API key -- self.client is None."""
    saved = _clear_gemini_env()
    try:
        gc = GeminiClient(config={})
        yield gc
    finally:
        _restore_gemini_env(saved)


@pytest.fixture()
def client_with_custom_config():
    """GeminiClient with custom model and no API key."""
    saved = _clear_gemini_env()
    try:
        gc = GeminiClient(config={"gemini_model": "gemini-1.5-pro"})
        yield gc
    finally:
        _restore_gemini_env(saved)


# ---------------------------------------------------------------------------
# Initialization and configuration
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestGeminiClientInit:
    """Tests for GeminiClient constructor and configuration."""

    def test_init_no_config(self):
        """GeminiClient can be constructed with no config dict."""
        saved = _clear_gemini_env()
        try:
            gc = GeminiClient()
            assert gc is not None
            assert gc.name == "gemini"
        finally:
            _restore_gemini_env(saved)

    def test_init_empty_config(self, client_no_key):
        """GeminiClient constructed with empty config sets defaults."""
        assert client_no_key.name == "gemini"
        assert client_no_key.client is None
        assert client_no_key.api_key is None or client_no_key.api_key == ""

    def test_default_model(self, client_no_key):
        """Default model is gemini-2.0-flash when not overridden."""
        assert client_no_key.default_model == "gemini-2.0-flash"

    def test_custom_model_from_config(self, client_with_custom_config):
        """Model can be overridden via config dict."""
        assert client_with_custom_config.default_model == "gemini-1.5-pro"

    def test_inherits_base_agent(self, client_no_key):
        """GeminiClient is a BaseAgent subclass."""
        assert isinstance(client_no_key, BaseAgent)

    def test_config_stored(self, client_no_key):
        """Instance config dict is accessible."""
        assert isinstance(client_no_key.config, dict)

    def test_api_key_from_config(self):
        """API key can be provided via config dict."""
        saved = _clear_gemini_env()
        try:
            # This will try to create a real genai.Client and likely fail
            # with a network/auth error, which is caught and re-raised as GeminiError.
            # We just want to verify the key is picked up.
            gc = GeminiClient(config={"gemini_api_key": "test-key-not-real"})
            # If the SDK accepted the key without a network call, client might be set
            # Either way, the key should be stored
            assert gc.api_key == "test-key-not-real"
        except GeminiError:
            # Expected: SDK may fail to init with a fake key
            pass
        finally:
            _restore_gemini_env(saved)

    def test_none_config_defaults(self):
        """Passing config=None should be equivalent to empty dict."""
        saved = _clear_gemini_env()
        try:
            gc = GeminiClient(config=None)
            assert gc.name == "gemini"
            assert gc.default_model == "gemini-2.0-flash"
        finally:
            _restore_gemini_env(saved)


# ---------------------------------------------------------------------------
# Capabilities
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestGeminiClientCapabilities:
    """Tests for agent capabilities declarations."""

    def test_has_code_generation(self, client_no_key):
        assert client_no_key.supports_capability(AgentCapabilities.CODE_GENERATION)

    def test_has_code_editing(self, client_no_key):
        assert client_no_key.supports_capability(AgentCapabilities.CODE_EDITING)

    def test_has_code_analysis(self, client_no_key):
        assert client_no_key.supports_capability(AgentCapabilities.CODE_ANALYSIS)

    def test_has_text_completion(self, client_no_key):
        assert client_no_key.supports_capability(AgentCapabilities.TEXT_COMPLETION)

    def test_has_streaming(self, client_no_key):
        assert client_no_key.supports_capability(AgentCapabilities.STREAMING)

    def test_has_multi_turn(self, client_no_key):
        assert client_no_key.supports_capability(AgentCapabilities.MULTI_TURN)

    def test_has_vision(self, client_no_key):
        assert client_no_key.supports_capability(AgentCapabilities.VISION)

    def test_has_code_execution(self, client_no_key):
        assert client_no_key.supports_capability(AgentCapabilities.CODE_EXECUTION)

    def test_capabilities_count(self, client_no_key):
        """Exactly 8 capabilities are declared."""
        caps = client_no_key.get_capabilities()
        assert len(caps) == 8

    def test_does_not_have_tool_use(self, client_no_key):
        """TOOL_USE is not in the declared capabilities."""
        assert not client_no_key.supports_capability(AgentCapabilities.TOOL_USE)

    def test_get_capabilities_returns_list(self, client_no_key):
        caps = client_no_key.get_capabilities()
        assert isinstance(caps, list)
        assert all(isinstance(c, AgentCapabilities) for c in caps)


# ---------------------------------------------------------------------------
# Guard-clause error handling (client=None path)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestGeminiClientGuardClauses:
    """Every API method raises GeminiError when client is None."""

    def test_execute_impl_raises(self, client_no_key):
        req = AgentRequest(prompt="hello")
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key._execute_impl(req)

    def test_stream_impl_raises(self, client_no_key):
        req = AgentRequest(prompt="hello")
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            # _stream_impl is a generator; must consume it to trigger the raise
            list(client_no_key._stream_impl(req))

    def test_start_chat_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.start_chat()

    def test_list_models_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.list_models()

    def test_get_model_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.get_model("gemini-2.0-flash")

    def test_count_tokens_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.count_tokens("hello")

    def test_embed_content_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.embed_content("hello")

    def test_generate_images_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.generate_images("a cat")

    def test_upscale_image_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.upscale_image(None)

    def test_edit_image_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.edit_image("brighter", None)

    def test_generate_videos_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.generate_videos("sunset")

    def test_upload_file_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.upload_file("/tmp/test.txt")

    def test_list_files_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.list_files()

    def test_get_file_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.get_file("some-file")

    def test_delete_file_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.delete_file("some-file")

    def test_create_cached_content_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.create_cached_content("model", "content")

    def test_list_cached_contents_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.list_cached_contents()

    def test_get_cached_content_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.get_cached_content("cached-name")

    def test_delete_cached_content_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.delete_cached_content("cached-name")

    def test_update_cached_content_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.update_cached_content("cached-name")

    def test_create_tuned_model_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.create_tuned_model("base-model", [])

    def test_list_tuned_models_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.list_tuned_models()

    def test_get_tuned_model_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.get_tuned_model("tuned-name")

    def test_delete_tuned_model_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.delete_tuned_model("tuned-name")

    def test_create_batch_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.create_batch([])

    def test_get_batch_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.get_batch("batch-name")

    def test_list_batches_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.list_batches()

    def test_delete_batch_raises(self, client_no_key):
        with pytest.raises(GeminiError, match="Gemini Client not initialized"):
            client_no_key.delete_batch("batch-name")


# ---------------------------------------------------------------------------
# _build_contents (pure logic, no API needed)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestBuildContents:
    """Tests for the _build_contents helper method."""

    def test_simple_prompt_wraps_in_list(self, client_no_key):
        """A plain prompt returns [[prompt]]."""
        result = client_no_key._build_contents("hello world", {})
        assert result == [["hello world"]]

    def test_context_contents_passthrough(self, client_no_key):
        """When context has 'contents', it is returned directly."""
        custom = [{"role": "user", "parts": ["hi"]}]
        result = client_no_key._build_contents("ignored", {"contents": custom})
        assert result is custom

    def test_invalid_image_path_skipped(self, client_no_key, tmp_path):
        """Non-existent image paths are silently skipped with a warning."""
        result = client_no_key._build_contents(
            "describe this",
            {"images": [str(tmp_path / "nonexistent.png")]},
        )
        # Should still have the prompt, image was skipped
        assert len(result) == 1
        assert result[0][0] == "describe this"
        # Only the text part, no image was appended
        assert len(result[0]) == 1

    def test_empty_images_list(self, client_no_key):
        """Empty images list produces [[prompt]] with no extra parts."""
        result = client_no_key._build_contents("test", {"images": []})
        assert result == [["test"]]


# ---------------------------------------------------------------------------
# BaseAgent integration (execute wraps _execute_impl errors)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestBaseAgentIntegration:
    """Tests verifying GeminiClient interacts correctly with BaseAgent."""

    def test_execute_returns_error_response(self, client_no_key):
        """BaseAgent.execute catches GeminiError and returns error AgentResponse."""
        req = AgentRequest(prompt="hello")
        resp = client_no_key.execute(req)
        assert isinstance(resp, AgentResponse)
        assert resp.error is not None
        assert "not initialized" in resp.error.lower() or "Gemini" in resp.error

    def test_execute_empty_prompt_raises(self, client_no_key):
        """BaseAgent._validate_request rejects empty prompt."""
        req = AgentRequest(prompt="")
        resp = client_no_key.execute(req)
        assert resp.error is not None

    def test_stream_yields_error(self, client_no_key):
        """BaseAgent.stream catches GeminiError and yields error string."""
        req = AgentRequest(prompt="hello")
        chunks = list(client_no_key.stream(req))
        assert len(chunks) >= 1
        # Should contain error text
        error_text = "".join(chunks)
        assert "error" in error_text.lower() or "Error" in error_text

    def test_setup_does_not_raise(self, client_no_key):
        """Default setup() from BaseAgent should not raise."""
        client_no_key.setup()

    def test_test_connection_default(self, client_no_key):
        """Default test_connection() returns True."""
        assert client_no_key.test_connection() is True


# ---------------------------------------------------------------------------
# Method signatures and return type annotations
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestGeminiClientMethodSignatures:
    """Verify method existence and basic signatures."""

    def test_has_execute_impl(self):
        assert hasattr(GeminiClient, "_execute_impl")
        assert callable(GeminiClient._execute_impl)

    def test_has_stream_impl(self):
        assert hasattr(GeminiClient, "_stream_impl")
        assert callable(GeminiClient._stream_impl)

    def test_has_start_chat(self):
        assert hasattr(GeminiClient, "start_chat")
        sig = inspect.signature(GeminiClient.start_chat)
        params = list(sig.parameters.keys())
        assert "history" in params
        assert "enable_automatic_function_calling" in params
        assert "model" in params

    def test_has_list_models(self):
        assert hasattr(GeminiClient, "list_models")

    def test_has_get_model(self):
        sig = inspect.signature(GeminiClient.get_model)
        assert "model_name" in sig.parameters

    def test_has_count_tokens(self):
        sig = inspect.signature(GeminiClient.count_tokens)
        assert "content" in sig.parameters
        assert "model" in sig.parameters

    def test_has_embed_content(self):
        sig = inspect.signature(GeminiClient.embed_content)
        assert "content" in sig.parameters
        assert "model" in sig.parameters

    def test_has_generate_images(self):
        sig = inspect.signature(GeminiClient.generate_images)
        assert "prompt" in sig.parameters
        assert "model" in sig.parameters

    def test_has_upload_file(self):
        sig = inspect.signature(GeminiClient.upload_file)
        assert "file_path" in sig.parameters
        assert "mime_type" in sig.parameters

    def test_has_file_management_methods(self):
        for method in ("list_files", "get_file", "delete_file"):
            assert hasattr(GeminiClient, method), f"Missing method: {method}"

    def test_has_cache_management_methods(self):
        for method in (
            "create_cached_content",
            "list_cached_contents",
            "get_cached_content",
            "delete_cached_content",
            "update_cached_content",
        ):
            assert hasattr(GeminiClient, method), f"Missing method: {method}"

    def test_has_tuning_methods(self):
        for method in (
            "create_tuned_model",
            "list_tuned_models",
            "get_tuned_model",
            "delete_tuned_model",
        ):
            assert hasattr(GeminiClient, method), f"Missing method: {method}"

    def test_has_batch_methods(self):
        for method in ("create_batch", "get_batch", "list_batches", "delete_batch"):
            assert hasattr(GeminiClient, method), f"Missing method: {method}"


# ---------------------------------------------------------------------------
# GeminiError exception
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestGeminiError:
    """Tests for the GeminiError exception class."""

    def test_gemini_error_is_agent_error(self):
        from codomyrmex.agents.core.exceptions import AgentError
        assert issubclass(GeminiError, AgentError)

    def test_default_message(self):
        err = GeminiError()
        assert "Gemini operation failed" in str(err)

    def test_custom_message(self):
        err = GeminiError("custom failure")
        assert "custom failure" in str(err)

    def test_command_context(self):
        err = GeminiError("fail", command="gemini generate")
        assert err.context.get("command") == "gemini generate"

    def test_exit_code_context(self):
        err = GeminiError("fail", exit_code=1)
        assert err.context.get("exit_code") == 1


# ---------------------------------------------------------------------------
# AgentProtocol compliance (plan / act / observe)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAgentProtocol:
    """Verify GeminiClient satisfies the AgentProtocol interface."""

    def test_plan_returns_list(self, client_no_key):
        req = AgentRequest(prompt="test plan")
        result = client_no_key.plan(req)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == "test plan"

    def test_observe_returns_dict(self, client_no_key):
        resp = AgentResponse(content="result text")
        obs = client_no_key.observe(resp)
        assert isinstance(obs, dict)
        assert obs["content"] == "result text"
        assert obs["success"] is True
        assert obs["error"] is None

    def test_observe_error_response(self, client_no_key):
        resp = AgentResponse(content="", error="something broke")
        obs = client_no_key.observe(resp)
        assert obs["success"] is False
        assert obs["error"] == "something broke"

    def test_act_delegates_to_execute(self, client_no_key):
        """act() should call execute() internally, returning an AgentResponse."""
        resp = client_no_key.act("do something")
        assert isinstance(resp, AgentResponse)
        # Will have an error because client is None
        assert resp.error is not None
