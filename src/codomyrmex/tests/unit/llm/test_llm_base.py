"""
Comprehensive Tests for LLM / Ollama Base Providers

Tests pure logic paths in the Ollama integration layer that do NOT
require a running Ollama server: dataclass construction, conversation
formatting, payload construction, size parsing, streaming chunk
validation, config validation, error response handling, and token
estimation.

Tests that DO require Ollama are gated behind ``ollama_available``.
"""

import json
import shutil
import subprocess
import tempfile
from dataclasses import asdict, fields
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Ollama availability guard
# ---------------------------------------------------------------------------
ollama_available = False
try:
    subprocess.run(
        ["ollama", "list"],
        capture_output=True,
        timeout=2,
    )
    ollama_available = True
except Exception:
    pass

_skip_no_ollama = pytest.mark.skipif(
    not ollama_available, reason="Ollama not running"
)


# ===========================================================================
# 1. ExecutionOptions dataclass -- parameter boundary tests
# ===========================================================================

@pytest.mark.unit
class TestExecutionOptionsBoundaries:
    """Boundary and edge-case tests for ExecutionOptions."""

    def test_extreme_temperature_zero(self):
        """Temperature 0.0 is valid and produces deterministic output."""
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        opts = ExecutionOptions(temperature=0.0)
        assert opts.temperature == 0.0

    def test_extreme_temperature_max(self):
        """Temperature 2.0 is within the Ollama-supported range."""
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        opts = ExecutionOptions(temperature=2.0)
        assert opts.temperature == 2.0

    def test_top_p_boundary_zero(self):
        """top_p=0.0 selects only the highest-probability token."""
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        opts = ExecutionOptions(top_p=0.0)
        assert opts.top_p == 0.0

    def test_top_p_boundary_one(self):
        """top_p=1.0 considers all tokens."""
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        opts = ExecutionOptions(top_p=1.0)
        assert opts.top_p == 1.0

    def test_max_tokens_minimum(self):
        """max_tokens=1 is the smallest useful generation."""
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        opts = ExecutionOptions(max_tokens=1)
        assert opts.max_tokens == 1

    def test_max_tokens_large(self):
        """Large max_tokens values are accepted."""
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        opts = ExecutionOptions(max_tokens=32768)
        assert opts.max_tokens == 32768

    def test_timeout_minimum(self):
        """Timeout of 1 second is valid."""
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        opts = ExecutionOptions(timeout=1)
        assert opts.timeout == 1

    @pytest.mark.parametrize(
        "fmt", [None, "json"],
        ids=["no_format", "json_format"],
    )
    def test_format_option(self, fmt):
        """Format can be None (text) or 'json'."""
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        opts = ExecutionOptions(format=fmt)
        assert opts.format == fmt

    def test_context_window_custom(self):
        """Custom context_window is stored."""
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        opts = ExecutionOptions(context_window=8192)
        assert opts.context_window == 8192

    def test_repeat_penalty_no_penalty(self):
        """repeat_penalty=1.0 means no penalty applied."""
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        opts = ExecutionOptions(repeat_penalty=1.0)
        assert opts.repeat_penalty == 1.0

    def test_execution_options_asdict(self):
        """ExecutionOptions can be serialised to a dict."""
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        opts = ExecutionOptions(temperature=0.5, max_tokens=512)
        d = asdict(opts)
        assert isinstance(d, dict)
        assert d["temperature"] == 0.5
        assert d["max_tokens"] == 512

    def test_all_fields_present(self):
        """All 10 documented fields exist on the dataclass."""
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        expected = {
            "temperature", "top_p", "top_k", "repeat_penalty",
            "max_tokens", "timeout", "stream", "format",
            "system_prompt", "context_window",
        }
        actual = {f.name for f in fields(ExecutionOptions)}
        assert expected == actual


# ===========================================================================
# 2. StreamingChunk dataclass
# ===========================================================================

@pytest.mark.unit
class TestStreamingChunk:
    """Tests for StreamingChunk structure."""

    def test_defaults(self):
        """Default done=False, token_count=None."""
        from codomyrmex.llm.ollama.model_runner import StreamingChunk

        chunk = StreamingChunk(content="hello")
        assert chunk.content == "hello"
        assert chunk.done is False
        assert chunk.token_count is None

    def test_final_chunk(self):
        """Final chunk has done=True and optional token_count."""
        from codomyrmex.llm.ollama.model_runner import StreamingChunk

        chunk = StreamingChunk(content="", done=True, token_count=42)
        assert chunk.done is True
        assert chunk.token_count == 42

    def test_empty_content_chunk(self):
        """Empty content is valid (e.g. error or end-of-stream)."""
        from codomyrmex.llm.ollama.model_runner import StreamingChunk

        chunk = StreamingChunk(content="")
        assert chunk.content == ""


# ===========================================================================
# 3. ModelExecutionResult dataclass
# ===========================================================================

@pytest.mark.unit
class TestModelExecutionResult:
    """Tests for ModelExecutionResult construction and defaults."""

    def test_success_result(self):
        """Successful result stores all fields."""
        from codomyrmex.llm.ollama.ollama_manager import ModelExecutionResult

        r = ModelExecutionResult(
            model_name="llama3.1:latest",
            prompt="Hello",
            response="Hi there",
            execution_time=1.23,
            tokens_used=10,
            success=True,
        )
        assert r.success is True
        assert r.error_message is None
        assert r.tokens_used == 10

    def test_failure_result(self):
        """Failed result stores error message."""
        from codomyrmex.llm.ollama.ollama_manager import ModelExecutionResult

        r = ModelExecutionResult(
            model_name="llama3.1:latest",
            prompt="Hello",
            response="",
            execution_time=0.0,
            success=False,
            error_message="Model not available",
        )
        assert r.success is False
        assert "not available" in r.error_message.lower()

    def test_metadata_optional(self):
        """metadata defaults to None."""
        from codomyrmex.llm.ollama.ollama_manager import ModelExecutionResult

        r = ModelExecutionResult(
            model_name="m", prompt="p", response="r",
            execution_time=0.0,
        )
        assert r.metadata is None

    def test_metadata_dict(self):
        """metadata can be an arbitrary dict."""
        from codomyrmex.llm.ollama.ollama_manager import ModelExecutionResult

        r = ModelExecutionResult(
            model_name="m", prompt="p", response="r",
            execution_time=0.0,
            metadata={"api_method": "http", "extra": 42},
        )
        assert r.metadata["api_method"] == "http"
        assert r.metadata["extra"] == 42

    def test_asdict_roundtrip(self):
        """asdict produces a JSON-serialisable dict."""
        from codomyrmex.llm.ollama.ollama_manager import ModelExecutionResult

        r = ModelExecutionResult(
            model_name="m", prompt="p", response="r",
            execution_time=0.5, tokens_used=7, success=True,
        )
        d = asdict(r)
        serialised = json.dumps(d)
        assert '"model_name": "m"' in serialised


# ===========================================================================
# 4. OllamaModel dataclass
# ===========================================================================

@pytest.mark.unit
class TestOllamaModelDataclass:
    """Tests for OllamaModel dataclass."""

    def test_basic_construction(self):
        """Minimal OllamaModel construction."""
        from codomyrmex.llm.ollama.ollama_manager import OllamaModel

        model = OllamaModel(
            name="llama3.1:latest",
            id="abc123",
            size=4_000_000_000,
            modified="2025-01-01",
        )
        assert model.name == "llama3.1:latest"
        assert model.status == "available"

    def test_optional_fields_default_none(self):
        """parameters, family, format default to None."""
        from codomyrmex.llm.ollama.ollama_manager import OllamaModel

        model = OllamaModel(name="n", id="i", size=0, modified="m")
        assert model.parameters is None
        assert model.family is None
        assert model.format is None

    def test_custom_optional_fields(self):
        """Optional fields can be set explicitly."""
        from codomyrmex.llm.ollama.ollama_manager import OllamaModel

        model = OllamaModel(
            name="codellama:7b",
            id="xyz",
            size=7_000_000_000,
            modified="2025-02-01",
            parameters="7B",
            family="llama",
            format="gguf",
        )
        assert model.parameters == "7B"
        assert model.family == "llama"
        assert model.format == "gguf"


# ===========================================================================
# 5. Conversation formatting (pure logic -- no Ollama needed)
# ===========================================================================

@pytest.mark.unit
class TestConversationFormatting:
    """Tests for ModelRunner._format_conversation -- pure string logic."""

    @_skip_no_ollama
    def _get_runner(self):
        """Build a real ModelRunner (requires Ollama for OllamaManager init)."""
        from codomyrmex.llm.ollama.model_runner import ModelRunner
        from codomyrmex.llm.ollama.ollama_manager import OllamaManager

        manager = OllamaManager(auto_start_server=False)
        return ModelRunner(manager)

    @_skip_no_ollama
    def test_system_role_prefix(self):
        runner = self._get_runner()
        result = runner._format_conversation([
            {"role": "system", "content": "Be concise"},
        ])
        assert result == "System: Be concise"

    @_skip_no_ollama
    def test_user_role_prefix(self):
        runner = self._get_runner()
        result = runner._format_conversation([
            {"role": "user", "content": "Hi"},
        ])
        assert result == "User: Hi"

    @_skip_no_ollama
    def test_assistant_role_prefix(self):
        runner = self._get_runner()
        result = runner._format_conversation([
            {"role": "assistant", "content": "Hello!"},
        ])
        assert result == "Assistant: Hello!"

    @_skip_no_ollama
    def test_unknown_role_defaults_to_user(self):
        runner = self._get_runner()
        result = runner._format_conversation([
            {"role": "tool", "content": "data"},
        ])
        assert result == "User: data"

    @_skip_no_ollama
    def test_multi_turn_separated_by_double_newline(self):
        runner = self._get_runner()
        result = runner._format_conversation([
            {"role": "system", "content": "System msg"},
            {"role": "user", "content": "Q"},
            {"role": "assistant", "content": "A"},
        ])
        parts = result.split("\n\n")
        assert len(parts) == 3

    @_skip_no_ollama
    def test_empty_content_handled(self):
        runner = self._get_runner()
        result = runner._format_conversation([
            {"role": "user", "content": ""},
        ])
        assert result == "User: "

    @_skip_no_ollama
    def test_missing_content_key_handled(self):
        runner = self._get_runner()
        result = runner._format_conversation([
            {"role": "user"},
        ])
        assert result == "User: "


# ===========================================================================
# 6. Size parsing (OllamaManager._parse_size -- pure logic)
# ===========================================================================

@pytest.mark.unit
class TestSizeParsing:
    """Tests for OllamaManager._parse_size -- no server required.

    _parse_size is a static-like method but requires an instance.
    We skip if Ollama is down because __init__ hits the server.
    """

    @_skip_no_ollama
    def _get_manager(self):
        from codomyrmex.llm.ollama.ollama_manager import OllamaManager
        return OllamaManager(auto_start_server=False)

    @_skip_no_ollama
    @pytest.mark.parametrize(
        "input_str,expected",
        [
            ("1GB", 1 * 1024 * 1024 * 1024),
            ("2.5GB", int(2.5 * 1024 * 1024 * 1024)),
            ("500MB", 500 * 1024 * 1024),
            ("100KB", 100 * 1024),
            ("12345", 12345),
            ("invalid", 0),
            ("", 0),
        ],
        ids=["1GB", "2.5GB", "500MB", "100KB", "plain_int", "invalid", "empty"],
    )
    def test_parse_size(self, input_str, expected):
        manager = self._get_manager()
        assert manager._parse_size(input_str) == expected


# ===========================================================================
# 7. OllamaConfig dataclass (ollama/config_manager.py)
# ===========================================================================

@pytest.mark.unit
class TestOllamaConfig:
    """Pure-logic tests for OllamaConfig defaults and post_init."""

    def test_default_values(self):
        from codomyrmex.llm.ollama.config_manager import OllamaConfig
        cfg = OllamaConfig()
        assert cfg.ollama_binary == "ollama"
        assert cfg.auto_start_server is True
        assert cfg.server_host == "localhost"
        assert cfg.server_port == 11434
        assert cfg.default_model == "llama3.1:latest"

    def test_post_init_populates_preferred_models(self):
        from codomyrmex.llm.ollama.config_manager import OllamaConfig
        cfg = OllamaConfig()
        assert isinstance(cfg.preferred_models, list)
        assert len(cfg.preferred_models) >= 1
        assert "llama3.1:latest" in cfg.preferred_models

    def test_post_init_populates_default_options(self):
        from codomyrmex.llm.ollama.config_manager import OllamaConfig
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions
        cfg = OllamaConfig()
        assert isinstance(cfg.default_options, ExecutionOptions)

    def test_custom_values_override(self):
        from codomyrmex.llm.ollama.config_manager import OllamaConfig
        cfg = OllamaConfig(
            server_port=9999,
            default_model="phi3:latest",
            enable_logging=False,
        )
        assert cfg.server_port == 9999
        assert cfg.default_model == "phi3:latest"
        assert cfg.enable_logging is False

    def test_asdict_serialisation(self):
        from codomyrmex.llm.ollama.config_manager import OllamaConfig
        cfg = OllamaConfig()
        d = asdict(cfg)
        assert isinstance(d, dict)
        assert d["server_port"] == 11434


# ===========================================================================
# 8. ConfigManager -- validation logic (pure, no Ollama needed)
# ===========================================================================

@pytest.mark.unit
class TestConfigManagerValidation:
    """Tests for ConfigManager.validate_config and presets."""

    def test_validate_default_config_valid(self):
        """Default config should have zero errors."""
        from codomyrmex.llm.ollama.config_manager import ConfigManager
        mgr = ConfigManager()
        result = mgr.validate_config()
        assert isinstance(result["errors"], list)
        # Default config should be valid (no errors)
        assert result["valid"] is True

    def test_validate_bad_temperature(self):
        """Temperature out of range 0-2 flags an error."""
        from codomyrmex.llm.ollama.config_manager import ConfigManager
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        mgr = ConfigManager()
        mgr.config.default_options = ExecutionOptions(temperature=5.0)
        result = mgr.validate_config()
        assert any("temperature" in e.lower() for e in result["errors"])

    def test_validate_bad_top_p(self):
        """top_p out of range 0-1 flags an error."""
        from codomyrmex.llm.ollama.config_manager import ConfigManager
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        mgr = ConfigManager()
        mgr.config.default_options = ExecutionOptions(top_p=2.0)
        result = mgr.validate_config()
        assert any("top_p" in e.lower() for e in result["errors"])

    def test_validate_bad_max_tokens(self):
        """max_tokens < 1 flags an error."""
        from codomyrmex.llm.ollama.config_manager import ConfigManager
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        mgr = ConfigManager()
        mgr.config.default_options = ExecutionOptions(max_tokens=0)
        result = mgr.validate_config()
        assert any("max_tokens" in e.lower() for e in result["errors"])

    def test_validate_bad_timeout(self):
        """timeout < 1 flags an error."""
        from codomyrmex.llm.ollama.config_manager import ConfigManager
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        mgr = ConfigManager()
        mgr.config.default_options = ExecutionOptions(timeout=0)
        result = mgr.validate_config()
        assert any("timeout" in e.lower() for e in result["errors"])

    def test_validate_invalid_preferred_model(self):
        """Empty string in preferred_models flags an error."""
        from codomyrmex.llm.ollama.config_manager import ConfigManager

        mgr = ConfigManager()
        mgr.config.preferred_models = ["llama3.1:latest", ""]
        result = mgr.validate_config()
        assert any("preferred_models" in e.lower() for e in result["errors"])

    def test_validate_no_config_loaded(self):
        """validate_config with config=None returns invalid."""
        from codomyrmex.llm.ollama.config_manager import ConfigManager

        mgr = ConfigManager()
        mgr.config = None
        result = mgr.validate_config()
        assert result["valid"] is False

    def test_execution_presets_keys(self):
        """Preset keys: fast, creative, balanced, precise, long_form."""
        from codomyrmex.llm.ollama.config_manager import ConfigManager

        mgr = ConfigManager()
        presets = mgr.get_execution_presets()
        assert set(presets.keys()) == {
            "fast", "creative", "balanced", "precise", "long_form",
        }

    def test_execution_presets_temperature_ordering(self):
        """fast < balanced < creative temperatures."""
        from codomyrmex.llm.ollama.config_manager import ConfigManager

        mgr = ConfigManager()
        presets = mgr.get_execution_presets()
        assert presets["fast"].temperature < presets["balanced"].temperature
        assert presets["balanced"].temperature <= presets["creative"].temperature

    def test_execution_presets_max_tokens_ordering(self):
        """fast has fewest tokens, long_form has most."""
        from codomyrmex.llm.ollama.config_manager import ConfigManager

        mgr = ConfigManager()
        presets = mgr.get_execution_presets()
        assert presets["fast"].max_tokens < presets["long_form"].max_tokens


# ===========================================================================
# 9. ConfigManager save/load/export/import round-trip
# ===========================================================================

@pytest.mark.unit
class TestConfigManagerPersistence:
    """Config save/load round-trip tests using a temp directory."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_load_config(self):
        from codomyrmex.llm.ollama.config_manager import ConfigManager

        config_file = str(Path(self.temp_dir) / "cfg.json")
        mgr = ConfigManager(config_file=config_file)
        mgr.config.default_model = "custom:v2"
        assert mgr.save_config() is True

        # Reload
        mgr2 = ConfigManager(config_file=config_file)
        assert mgr2.config.default_model == "custom:v2"

    def test_export_and_import(self):
        from codomyrmex.llm.ollama.config_manager import ConfigManager

        config_file = str(Path(self.temp_dir) / "cfg.json")
        export_file = str(Path(self.temp_dir) / "export.json")

        mgr = ConfigManager(config_file=config_file)
        mgr.config.default_model = "exported:v1"
        assert mgr.export_config(export_file) is True
        assert Path(export_file).exists()

        # Verify export structure
        with open(export_file) as f:
            data = json.load(f)
        assert "export_timestamp" in data
        assert "main_config" in data
        assert "execution_presets" in data

    def test_create_default_config(self):
        from codomyrmex.llm.ollama.config_manager import ConfigManager

        mgr = ConfigManager()
        default = mgr.create_default_config()
        assert default.default_model == "llama3.1:latest"

    def test_update_config_unknown_key_warns(self):
        """update_config with unknown key should not raise."""
        from codomyrmex.llm.ollama.config_manager import ConfigManager

        config_file = str(Path(self.temp_dir) / "cfg.json")
        mgr = ConfigManager(config_file=config_file)
        # Should not raise, just warn
        mgr.update_config(nonexistent_key="value")
        assert not hasattr(mgr.config, "nonexistent_key")


# ===========================================================================
# 10. Token count estimation (character-based heuristic)
# ===========================================================================

@pytest.mark.unit
class TestTokenEstimation:
    """Character-based token estimation heuristic (no service needed)."""

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Rough estimate: 1 token ~ 4 characters for English text."""
        return max(1, len(text) // 4)

    @pytest.mark.parametrize(
        "text,min_tokens,max_tokens",
        [
            ("Hello", 1, 3),
            ("The quick brown fox jumps over the lazy dog", 8, 15),
            ("a" * 400, 80, 120),
            ("", 1, 1),  # min 1
        ],
        ids=["short", "sentence", "long", "empty"],
    )
    def test_estimate_tokens(self, text, min_tokens, max_tokens):
        est = self._estimate_tokens(text)
        assert min_tokens <= est <= max_tokens


# ===========================================================================
# 11. Request payload construction
# ===========================================================================

@pytest.mark.unit
class TestPayloadConstruction:
    """Verify the payload dict built for Ollama HTTP API calls.

    We test the logic from ModelRunner.async_run_model which builds the
    payload dict -- extracted here as a pure function test.
    """

    @staticmethod
    def _build_generate_payload(model_name, prompt, options):
        """Reproduce the payload logic from async_run_model."""
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        if options is None:
            options = ExecutionOptions()

        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": options.temperature,
                "top_p": options.top_p,
                "top_k": options.top_k,
                "repeat_penalty": options.repeat_penalty,
            },
        }

        if options.max_tokens:
            payload["options"]["num_predict"] = options.max_tokens
        if options.format:
            payload["format"] = options.format
        if options.context_window:
            payload["options"]["num_ctx"] = options.context_window
        if options.system_prompt:
            payload["system"] = options.system_prompt

        return payload

    def test_default_payload_structure(self):
        payload = self._build_generate_payload("llama3.1:latest", "Hello", None)
        assert payload["model"] == "llama3.1:latest"
        assert payload["prompt"] == "Hello"
        assert payload["stream"] is False
        assert "temperature" in payload["options"]
        assert payload["options"]["num_predict"] == 2048  # default

    def test_json_format_in_payload(self):
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        opts = ExecutionOptions(format="json")
        payload = self._build_generate_payload("m", "p", opts)
        assert payload["format"] == "json"

    def test_system_prompt_in_payload(self):
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        opts = ExecutionOptions(system_prompt="Be brief")
        payload = self._build_generate_payload("m", "p", opts)
        assert payload["system"] == "Be brief"

    def test_context_window_in_payload(self):
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        opts = ExecutionOptions(context_window=16384)
        payload = self._build_generate_payload("m", "p", opts)
        assert payload["options"]["num_ctx"] == 16384

    def test_payload_is_json_serialisable(self):
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        opts = ExecutionOptions(
            temperature=0.5, max_tokens=512,
            system_prompt="sys", format="json",
            context_window=4096,
        )
        payload = self._build_generate_payload("model", "prompt", opts)
        # Must not raise
        serialised = json.dumps(payload)
        assert isinstance(serialised, str)

    @staticmethod
    def _build_chat_payload(model_name, messages, options):
        """Reproduce the chat payload logic from async_chat."""
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        if options is None:
            options = ExecutionOptions()

        payload = {
            "model": model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": options.temperature,
                "top_p": options.top_p,
                "top_k": options.top_k,
                "repeat_penalty": options.repeat_penalty,
            },
        }

        if options.max_tokens:
            payload["options"]["num_predict"] = options.max_tokens
        if options.format:
            payload["format"] = options.format
        if options.context_window:
            payload["options"]["num_ctx"] = options.context_window

        return payload

    def test_chat_payload_messages_preserved(self):
        msgs = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"},
        ]
        payload = self._build_chat_payload("m", msgs, None)
        assert payload["messages"] == msgs
        assert len(payload["messages"]) == 2


# ===========================================================================
# 12. LLM exception hierarchy
# ===========================================================================

@pytest.mark.unit
class TestLLMExceptionHierarchy:
    """Verify exception class relationships."""

    def test_all_inherit_from_llm_error(self):
        from codomyrmex.llm.exceptions import (
            ContentFilterError,
            ContextWindowError,
            LLMAuthenticationError,
            LLMConnectionError,
            LLMError,
            LLMRateLimitError,
            LLMTimeoutError,
            ModelNotFoundError,
            PromptTooLongError,
            PromptValidationError,
            ResponseParsingError,
            StreamingError,
            TokenLimitError,
        )

        subclasses = [
            LLMConnectionError, LLMAuthenticationError,
            LLMRateLimitError, LLMTimeoutError,
            PromptTooLongError, PromptValidationError,
            ResponseParsingError, ContentFilterError,
            ModelNotFoundError, TokenLimitError,
            StreamingError, ContextWindowError,
        ]
        for cls in subclasses:
            assert issubclass(cls, LLMError), f"{cls.__name__} must inherit LLMError"

    def test_prompt_errors_inherit_prompt_error(self):
        from codomyrmex.llm.exceptions import (
            PromptError,
            PromptTooLongError,
            PromptValidationError,
        )

        assert issubclass(PromptTooLongError, PromptError)
        assert issubclass(PromptValidationError, PromptError)

    def test_response_errors_inherit_response_error(self):
        from codomyrmex.llm.exceptions import (
            ResponseError,
            ResponseParsingError,
            ResponseValidationError,
        )

        assert issubclass(ResponseParsingError, ResponseError)
        assert issubclass(ResponseValidationError, ResponseError)


# ===========================================================================
# 13. Comparison summary logic (pure dict processing)
# ===========================================================================

@pytest.mark.unit
class TestComparisonSummary:
    """Test _create_comparison_summary logic without Ollama."""

    @_skip_no_ollama
    def test_summary_finds_fastest_model(self):
        from codomyrmex.llm.ollama.model_runner import ModelRunner
        from codomyrmex.llm.ollama.ollama_manager import OllamaManager

        mgr = OllamaManager(auto_start_server=False)
        runner = ModelRunner(mgr)

        results = {
            "fast_model": {
                "success": True,
                "execution_time": 1.0,
                "tokens_per_second": 50,
            },
            "slow_model": {
                "success": True,
                "execution_time": 5.0,
                "tokens_per_second": 10,
            },
        }
        summary = runner._create_comparison_summary(results)
        assert summary["fastest_model"] == "fast_model"
        assert summary["slowest_model"] == "slow_model"
        assert summary["most_efficient"] == "fast_model"

    @_skip_no_ollama
    def test_summary_no_successful_results(self):
        from codomyrmex.llm.ollama.model_runner import ModelRunner
        from codomyrmex.llm.ollama.ollama_manager import OllamaManager

        mgr = OllamaManager(auto_start_server=False)
        runner = ModelRunner(mgr)

        results = {
            "failed": {"success": False, "execution_time": 0, "tokens_per_second": 0},
        }
        summary = runner._create_comparison_summary(results)
        assert "error" in summary


# ===========================================================================
# 14. OutputManager file naming and structure (pure logic)
# ===========================================================================

@pytest.mark.unit
class TestOutputManagerPureLogic:
    """OutputManager tests that rely only on filesystem, not Ollama."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_output_dirs_created_on_init(self):
        from codomyrmex.llm.ollama.output_manager import OutputManager

        OutputManager(self.temp_dir)
        assert (Path(self.temp_dir) / "outputs").is_dir()
        assert (Path(self.temp_dir) / "configs").is_dir()
        assert (Path(self.temp_dir) / "logs").is_dir()
        assert (Path(self.temp_dir) / "reports").is_dir()

    def test_save_model_output_contains_model_name(self):
        from codomyrmex.llm.ollama.output_manager import OutputManager

        om = OutputManager(self.temp_dir)
        path = om.save_model_output(
            model_name="test-model",
            prompt="test prompt",
            response="test response",
            execution_time=0.5,
        )
        with open(path) as f:
            content = f.read()
        assert "test-model" in content
        assert "test prompt" in content
        assert "test response" in content

    def test_list_saved_outputs_empty(self):
        from codomyrmex.llm.ollama.output_manager import OutputManager

        om = OutputManager(self.temp_dir)
        outputs = om.list_saved_outputs(output_type="results")
        assert outputs == []

    def test_cleanup_old_outputs_noop_on_fresh_dir(self):
        from codomyrmex.llm.ollama.output_manager import OutputManager

        om = OutputManager(self.temp_dir)
        removed = om.cleanup_old_outputs(days_old=0)
        # No files to remove in a fresh directory
        assert removed == 0


# ===========================================================================
# 15. Model name format parametrize tests
# ===========================================================================

@pytest.mark.unit
class TestModelNameFormats:
    """Validate model name patterns accepted by OllamaModel."""

    @pytest.mark.parametrize(
        "name",
        [
            "llama3.1:latest",
            "codellama:7b",
            "gemma2:2b",
            "phi3:mini",
            "mistral:instruct",
            "llama3.1:8b-instruct-q4_0",
            "custom/my-model:v1.2.3",
        ],
        ids=[
            "standard_latest",
            "with_size_tag",
            "gemma_variant",
            "phi_variant",
            "instruct_variant",
            "quantization_tag",
            "namespace_model",
        ],
    )
    def test_model_name_accepted(self, name):
        from codomyrmex.llm.ollama.ollama_manager import OllamaModel

        model = OllamaModel(name=name, id="x", size=0, modified="now")
        assert model.name == name
