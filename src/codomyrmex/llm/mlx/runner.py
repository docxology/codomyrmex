"""MLX Runner — load models and generate text on Apple Silicon.

Wraps the ``mlx-lm`` Python API (``load``, ``generate``,
``stream_generate``) with Codomyrmex-standard dataclasses and logging.
Designed for single-model use on a Mac Mini M4 (16 GB).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from codomyrmex.logging_monitoring import get_logger

from .config import MLXConfig, get_mlx_config

if TYPE_CHECKING:
    from collections.abc import Generator

logger = get_logger(__name__)


def _make_generation_kwargs(cfg: MLXConfig) -> dict[str, Any]:
    """Build kwargs dict for mlx_lm.generate / stream_generate.

    mlx_lm v0.31+ uses ``sampler`` and ``logits_processors`` callables
    instead of raw ``temp``/``top_p``/``repetition_penalty`` kwargs.
    """
    kwargs: dict[str, Any] = {
        "max_tokens": cfg.max_tokens,
    }

    try:
        from mlx_lm.sample_utils import make_logits_processors, make_sampler

        kwargs["sampler"] = make_sampler(temp=cfg.temperature, top_p=cfg.top_p)
        kwargs["logits_processors"] = make_logits_processors(
            repetition_penalty=cfg.repetition_penalty,
        )
    except ImportError:
        # Older mlx_lm — fall back to direct kwargs
        kwargs["temp"] = cfg.temperature
        kwargs["top_p"] = cfg.top_p
        kwargs["repetition_penalty"] = cfg.repetition_penalty

    return kwargs


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------


@dataclass
class MLXStreamChunk:
    """A single token (or fragment) emitted during streaming generation."""

    content: str
    done: bool = False
    token_count: int | None = None


@dataclass
class MLXGenerationResult:
    """Result of a synchronous generation call."""

    model: str
    prompt: str
    response: str
    execution_time: float
    tokens_generated: int | None = None
    tokens_per_second: float | None = None
    success: bool = True
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# MLXRunner
# ---------------------------------------------------------------------------


class MLXRunner:
    """Load an MLX model and run inference.

    The runner lazily loads the model on first use and keeps it resident
    in unified memory until :meth:`unload_model` is called.

    Args:
        config: Optional :class:`MLXConfig`.  Falls back to the global
            singleton when omitted.
    """

    def __init__(self, config: MLXConfig | None = None) -> None:
        self._config = config or get_mlx_config()
        self._model: Any | None = None
        self._tokenizer: Any | None = None
        self._loaded_model_name: str | None = None
        self._load_time: float | None = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_loaded(self) -> bool:
        """Whether a model is currently loaded in memory."""
        return self._model is not None

    @property
    def loaded_model(self) -> str | None:
        """Repo-id of the currently loaded model, or ``None``."""
        return self._loaded_model_name

    # ------------------------------------------------------------------
    # Model lifecycle
    # ------------------------------------------------------------------

    def load_model(self, model_name: str | None = None) -> None:
        """Load a model and tokenizer into unified memory.

        If the requested model is already loaded this is a no-op.

        Args:
            model_name: HuggingFace repo id.  Defaults to
                ``MLXConfig.model``.

        Raises:
            ImportError: If ``mlx_lm`` is not installed.
            RuntimeError: On load failure.
        """
        model_name = model_name or self._config.model

        if self._loaded_model_name == model_name and self._model is not None:
            logger.debug("Model %s already loaded — skipping", model_name)
            return

        # Unload previous model first to free memory
        if self._model is not None:
            self.unload_model()

        try:
            from mlx_lm import load as mlx_load
        except ImportError as exc:
            raise ImportError(
                "mlx-lm is required for MLX inference. "
                "Install it with: pip install mlx-lm"
            ) from exc

        logger.info("Loading MLX model: %s", model_name)
        t0 = time.perf_counter()

        try:
            self._model, self._tokenizer = mlx_load(model_name)
            self._loaded_model_name = model_name
            self._load_time = time.perf_counter() - t0
            logger.info("Model %s loaded in %.2f s", model_name, self._load_time)
        except Exception as exc:
            self._model = None
            self._tokenizer = None
            self._loaded_model_name = None
            raise RuntimeError(f"Failed to load MLX model {model_name}: {exc}") from exc

    def unload_model(self) -> None:
        """Release the currently loaded model and free memory."""
        if self._model is not None:
            logger.info("Unloading model %s", self._loaded_model_name)
        self._model = None
        self._tokenizer = None
        self._loaded_model_name = None
        self._load_time = None

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------

    def generate(
        self,
        prompt: str,
        config: MLXConfig | None = None,
    ) -> MLXGenerationResult:
        """Generate text synchronously.

        The model is loaded automatically on first call if necessary.

        Args:
            prompt: The input prompt string.
            config: Optional per-call config override.

        Returns:
            :class:`MLXGenerationResult` with response and timing stats.
        """
        cfg = config or self._config
        self.load_model(cfg.model)

        try:
            from mlx_lm import generate as mlx_generate
        except ImportError as exc:
            return MLXGenerationResult(
                model=cfg.model,
                prompt=prompt,
                response="",
                execution_time=0.0,
                success=False,
                error_message=f"mlx-lm not installed: {exc}",
            )

        logger.info(
            "Generating with %s (temp=%.2f, max_tokens=%d)",
            cfg.model,
            cfg.temperature,
            cfg.max_tokens,
        )
        t0 = time.perf_counter()

        gen_kwargs = _make_generation_kwargs(cfg)

        try:
            response_text = mlx_generate(
                model=self._model,
                tokenizer=self._tokenizer,
                prompt=prompt,
                verbose=False,
                **gen_kwargs,
            )
            elapsed = time.perf_counter() - t0

            # Rough token count from response length
            token_count = self._estimate_tokens(response_text)
            tps = token_count / elapsed if elapsed > 0 else 0.0

            logger.info(
                "Generated %d tokens in %.2f s (%.1f tok/s)",
                token_count,
                elapsed,
                tps,
            )

            return MLXGenerationResult(
                model=cfg.model,
                prompt=prompt,
                response=response_text,
                execution_time=elapsed,
                tokens_generated=token_count,
                tokens_per_second=round(tps, 2),
                success=True,
            )

        except Exception as exc:
            elapsed = time.perf_counter() - t0
            logger.error("Generation failed: %s", exc)
            return MLXGenerationResult(
                model=cfg.model,
                prompt=prompt,
                response="",
                execution_time=elapsed,
                success=False,
                error_message=str(exc),
            )

    def stream_generate(
        self,
        prompt: str,
        config: MLXConfig | None = None,
    ) -> Generator[MLXStreamChunk, None, None]:
        """Stream tokens as they are generated.

        Yields :class:`MLXStreamChunk` objects.  The last chunk has
        ``done=True`` and includes the total ``token_count``.

        Args:
            prompt: The input prompt string.
            config: Optional per-call config override.

        Yields:
            :class:`MLXStreamChunk` for each generated fragment.
        """
        cfg = config or self._config
        self.load_model(cfg.model)

        try:
            from mlx_lm import stream_generate as mlx_stream
        except ImportError as exc:
            yield MLXStreamChunk(
                content=f"Error: mlx-lm not installed: {exc}", done=True
            )
            return

        gen_kwargs = _make_generation_kwargs(cfg)

        token_count = 0
        try:
            for response in mlx_stream(
                model=self._model,
                tokenizer=self._tokenizer,
                prompt=prompt,
                **gen_kwargs,
            ):
                token_count += 1
                yield MLXStreamChunk(content=response.text, done=False)

            # Final "done" chunk
            yield MLXStreamChunk(content="", done=True, token_count=token_count)

        except Exception as exc:
            logger.error("Streaming generation failed: %s", exc)
            yield MLXStreamChunk(
                content=f"Error: {exc}", done=True, token_count=token_count
            )

    # ------------------------------------------------------------------
    # Chat (convenience)
    # ------------------------------------------------------------------

    def chat(
        self,
        messages: list[dict[str, str]],
        config: MLXConfig | None = None,
    ) -> MLXGenerationResult:
        """Chat-style generation using the tokenizer's chat template.

        Args:
            messages: List of ``{"role": ..., "content": ...}`` dicts.
            config: Optional per-call config override.

        Returns:
            :class:`MLXGenerationResult`.
        """
        cfg = config or self._config
        self.load_model(cfg.model)

        if self._tokenizer is None:
            return MLXGenerationResult(
                model=cfg.model,
                prompt=str(messages),
                response="",
                execution_time=0.0,
                success=False,
                error_message="Tokenizer not loaded",
            )

        try:
            if hasattr(self._tokenizer, "apply_chat_template"):
                prompt = self._tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                )
            else:
                # Fallback: manual formatting
                prompt = self._format_messages(messages)
        except Exception as exc:
            logger.warning("Chat template failed, falling back: %s", exc)
            prompt = self._format_messages(messages)

        return self.generate(prompt, config=cfg)

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def get_performance_stats(self) -> dict[str, Any]:
        """Return performance and status information.

        Returns:
            Dictionary of current runner state.
        """
        return {
            "is_loaded": self.is_loaded,
            "loaded_model": self._loaded_model_name,
            "load_time_seconds": self._load_time,
            "config": self._config.to_dict(),
        }

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Rough token estimate: ~4 chars per token for English."""
        return max(1, len(text) // 4)

    @staticmethod
    def _format_messages(messages: list[dict[str, str]]) -> str:
        """Fallback message formatter when no chat template is available."""
        role_map = {"system": "System", "user": "User", "assistant": "Assistant"}
        parts: list[str] = []
        for msg in messages:
            role = role_map.get(msg.get("role", "user"), "User")
            content = msg.get("content", "")
            parts.append(f"{role}: {content}")
        return "\n\n".join(parts)
