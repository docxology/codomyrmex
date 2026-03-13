"""Comprehensive tests for MLXRunner.

Pure-logic tests cover dataclass construction, message formatting, and
token estimation. Integration tests (model loading + generation) are
gated behind ``mlx_available``.
"""

import importlib.util

import pytest

# ---------------------------------------------------------------------------
# MLX availability guard
# ---------------------------------------------------------------------------
mlx_available = importlib.util.find_spec("mlx") is not None
_skip_no_mlx = pytest.mark.skipif(not mlx_available, reason="mlx not installed")


# ===========================================================================
# 1. MLXStreamChunk dataclass
# ===========================================================================


@pytest.mark.unit
class TestMLXStreamChunk:
    """Tests for MLXStreamChunk construction and defaults."""

    def test_defaults(self):
        from codomyrmex.llm.mlx.runner import MLXStreamChunk

        chunk = MLXStreamChunk(content="hello")
        assert chunk.content == "hello"
        assert chunk.done is False
        assert chunk.token_count is None

    def test_final_chunk(self):
        from codomyrmex.llm.mlx.runner import MLXStreamChunk

        chunk = MLXStreamChunk(content="", done=True, token_count=42)
        assert chunk.done is True
        assert chunk.token_count == 42

    def test_empty_content(self):
        from codomyrmex.llm.mlx.runner import MLXStreamChunk

        chunk = MLXStreamChunk(content="")
        assert chunk.content == ""


# ===========================================================================
# 2. MLXGenerationResult dataclass
# ===========================================================================


@pytest.mark.unit
class TestMLXGenerationResult:
    """Tests for MLXGenerationResult construction."""

    def test_success_result(self):
        from codomyrmex.llm.mlx.runner import MLXGenerationResult

        r = MLXGenerationResult(
            model="test/model",
            prompt="Hello",
            response="Hi there",
            execution_time=1.5,
            tokens_generated=10,
            tokens_per_second=6.7,
            success=True,
        )
        assert r.success is True
        assert r.error_message is None
        assert r.tokens_generated == 10

    def test_failure_result(self):
        from codomyrmex.llm.mlx.runner import MLXGenerationResult

        r = MLXGenerationResult(
            model="test/model",
            prompt="Hello",
            response="",
            execution_time=0.0,
            success=False,
            error_message="Model not found",
        )
        assert r.success is False
        assert "not found" in r.error_message.lower()

    def test_metadata_default_empty(self):
        from codomyrmex.llm.mlx.runner import MLXGenerationResult

        r = MLXGenerationResult(model="m", prompt="p", response="r", execution_time=0.0)
        assert r.metadata == {}

    def test_metadata_custom(self):
        from codomyrmex.llm.mlx.runner import MLXGenerationResult

        r = MLXGenerationResult(
            model="m",
            prompt="p",
            response="r",
            execution_time=0.0,
            metadata={"backend": "mlx"},
        )
        assert r.metadata["backend"] == "mlx"


# ===========================================================================
# 3. Message formatting (pure logic)
# ===========================================================================


@pytest.mark.unit
class TestMessageFormatting:
    """Tests for MLXRunner._format_messages — pure string logic."""

    @staticmethod
    def _format(messages):
        from codomyrmex.llm.mlx.runner import MLXRunner

        return MLXRunner._format_messages(messages)

    def test_system_role_prefix(self):
        result = self._format([{"role": "system", "content": "Be concise"}])
        assert result == "System: Be concise"

    def test_user_role_prefix(self):
        result = self._format([{"role": "user", "content": "Hi"}])
        assert result == "User: Hi"

    def test_assistant_role_prefix(self):
        result = self._format([{"role": "assistant", "content": "Hello!"}])
        assert result == "Assistant: Hello!"

    def test_unknown_role_defaults_to_user(self):
        result = self._format([{"role": "tool", "content": "data"}])
        assert result == "User: data"

    def test_multi_turn_separated(self):
        result = self._format(
            [
                {"role": "system", "content": "sys"},
                {"role": "user", "content": "q"},
                {"role": "assistant", "content": "a"},
            ]
        )
        parts = result.split("\n\n")
        assert len(parts) == 3

    def test_empty_content(self):
        result = self._format([{"role": "user", "content": ""}])
        assert result == "User: "

    def test_missing_content_key(self):
        result = self._format([{"role": "user"}])
        assert result == "User: "


# ===========================================================================
# 4. Token estimation (pure logic)
# ===========================================================================


@pytest.mark.unit
class TestTokenEstimation:
    """Tests for MLXRunner._estimate_tokens — character heuristic."""

    @staticmethod
    def _estimate(text):
        from codomyrmex.llm.mlx.runner import MLXRunner

        return MLXRunner._estimate_tokens(text)

    @pytest.mark.parametrize(
        ("text", "min_tok", "max_tok"),
        [
            ("Hello", 1, 3),
            ("The quick brown fox jumps over the lazy dog", 8, 15),
            ("a" * 400, 80, 120),
            ("", 1, 1),
        ],
        ids=["short", "sentence", "long", "empty"],
    )
    def test_estimate(self, text, min_tok, max_tok):
        est = self._estimate(text)
        assert min_tok <= est <= max_tok


# ===========================================================================
# 5. MLXRunner state management (no model load)
# ===========================================================================


@pytest.mark.unit
class TestMLXRunnerState:
    """Runner state before model is loaded."""

    def test_initial_not_loaded(self):
        from codomyrmex.llm.mlx.config import MLXConfig
        from codomyrmex.llm.mlx.runner import MLXRunner

        runner = MLXRunner(MLXConfig())
        assert runner.is_loaded is False
        assert runner.loaded_model is None

    def test_performance_stats_initial(self):
        from codomyrmex.llm.mlx.config import MLXConfig
        from codomyrmex.llm.mlx.runner import MLXRunner

        runner = MLXRunner(MLXConfig())
        stats = runner.get_performance_stats()
        assert stats["is_loaded"] is False
        assert stats["loaded_model"] is None
        assert stats["load_time_seconds"] is None
        assert "model" in stats["config"]

    def test_unload_when_not_loaded(self):
        from codomyrmex.llm.mlx.config import MLXConfig
        from codomyrmex.llm.mlx.runner import MLXRunner

        runner = MLXRunner(MLXConfig())
        # Should not raise
        runner.unload_model()
        assert runner.is_loaded is False


# ===========================================================================
# 6. Integration: real model loading + generation (gated)
# ===========================================================================


@_skip_no_mlx
@pytest.mark.integration
class TestMLXRunnerIntegration:
    """Integration tests requiring mlx and a downloaded model.

    These will only run if mlx is installed AND the default model is cached.
    """

    @pytest.fixture(autouse=True)
    def _check_model(self):
        """Skip if the default model is not downloaded."""
        from codomyrmex.llm.mlx.config import MLXConfig
        from codomyrmex.llm.mlx.model_manager import MLXModelManager

        cfg = MLXConfig()
        mgr = MLXModelManager(cfg)
        if not mgr.is_model_cached(cfg.model):
            pytest.skip(f"Model {cfg.model} not cached — download first")

    def test_load_model(self):
        from codomyrmex.llm.mlx.config import MLXConfig
        from codomyrmex.llm.mlx.runner import MLXRunner

        runner = MLXRunner(MLXConfig())
        runner.load_model()
        assert runner.is_loaded
        assert runner.loaded_model is not None
        runner.unload_model()

    def test_generate_short(self):
        from codomyrmex.llm.mlx.config import MLXConfig
        from codomyrmex.llm.mlx.runner import MLXRunner

        cfg = MLXConfig(max_tokens=20)
        runner = MLXRunner(cfg)
        result = runner.generate("Say hello in one word.")
        assert result.success is True
        assert len(result.response) > 0
        assert result.tokens_generated > 0
        assert result.tokens_per_second > 0
        runner.unload_model()

    def test_chat(self):
        from codomyrmex.llm.mlx.config import MLXConfig
        from codomyrmex.llm.mlx.runner import MLXRunner

        cfg = MLXConfig(max_tokens=30)
        runner = MLXRunner(cfg)
        result = runner.chat(
            [
                {"role": "user", "content": "What is 2+2? Reply with just the number."},
            ]
        )
        assert result.success is True
        assert len(result.response) > 0
        runner.unload_model()

    def test_stream_generate(self):
        from codomyrmex.llm.mlx.config import MLXConfig
        from codomyrmex.llm.mlx.runner import MLXRunner

        cfg = MLXConfig(max_tokens=10)
        runner = MLXRunner(cfg)
        chunks = list(runner.stream_generate("Count to 3."))
        assert len(chunks) > 0
        assert chunks[-1].done is True
        runner.unload_model()
