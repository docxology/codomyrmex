"""MLX configuration management for Apple Silicon LLM inference.

Provides centralized configuration for mlx-lm model selection,
generation parameters, and cache settings with environment variable support.
Optimized for Mac Mini M4 (16GB unified memory).
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def _env_str(key: str, default: str) -> str:
    """Get environment variable as string with default."""
    return os.getenv(key, default)


def _env_float(key: str, default: float) -> float:
    """Get environment variable as float with default."""
    try:
        return float(os.getenv(key, str(default)))
    except (ValueError, TypeError):
        return default


def _env_int(key: str, default: int) -> int:
    """Get environment variable as int with default."""
    try:
        return int(os.getenv(key, str(default)))
    except (ValueError, TypeError):
        return default


def _env_optional_int(key: str) -> int | None:
    """Get environment variable as optional int (None if unset)."""
    val = os.getenv(key)
    if val is None:
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Default model — fits well within 16 GB Mac Mini M4
# ---------------------------------------------------------------------------
DEFAULT_MLX_MODEL = "mlx-community/Llama-3.2-3B-Instruct-4bit"
DEFAULT_MLX_CACHE_DIR = str(Path.home() / ".cache" / "mlx-models")


@dataclass
class MLXConfig:
    """Configuration for MLX-based local LLM inference.

    All parameters can be overridden via environment variables prefixed
    with ``MLX_``.

    Environment Variables:
        MLX_MODEL              Model repo id (default: Llama-3.2-3B-Instruct-4bit)
        MLX_TEMPERATURE        Generation temperature 0.0–2.0 (default: 0.7)
        MLX_MAX_TOKENS         Maximum tokens to generate (default: 1000)
        MLX_TOP_P              Top-p / nucleus sampling (default: 0.9)
        MLX_REPETITION_PENALTY Repetition penalty ≥1.0 (default: 1.1)
        MLX_MAX_KV_SIZE        Rotating KV-cache cap (default: None / unlimited)
        MLX_CACHE_DIR          Local cache for downloaded models
        MLX_SEED               Random seed for reproducibility (default: None)

    Example::

        export MLX_MODEL="mlx-community/Mistral-7B-Instruct-v0.3-4bit"
        export MLX_TEMPERATURE="0.3"

        config = MLXConfig()                  # picks up env vars
        config = MLXConfig(temperature=0.1)   # programmatic override wins
    """

    model: str = ""
    temperature: float = 0.0
    max_tokens: int = 0
    top_p: float = 0.0
    repetition_penalty: float = 0.0
    max_kv_size: int | None = None
    cache_dir: str = ""
    seed: int | None = None

    def __post_init__(self) -> None:
        """Apply environment-variable defaults for any field left at its
        zero-value sentinel."""
        if not self.model:
            self.model = _env_str("MLX_MODEL", DEFAULT_MLX_MODEL)
        if self.temperature == 0.0 and os.getenv("MLX_TEMPERATURE") is not None:
            self.temperature = _env_float("MLX_TEMPERATURE", 0.7)
        elif self.temperature == 0.0:
            self.temperature = 0.7
        if self.max_tokens == 0:
            self.max_tokens = _env_int("MLX_MAX_TOKENS", 1000)
        if self.top_p == 0.0 and os.getenv("MLX_TOP_P") is not None:
            self.top_p = _env_float("MLX_TOP_P", 0.9)
        elif self.top_p == 0.0:
            self.top_p = 0.9
        if self.repetition_penalty == 0.0:
            self.repetition_penalty = _env_float("MLX_REPETITION_PENALTY", 1.1)
        if self.max_kv_size is None:
            self.max_kv_size = _env_optional_int("MLX_MAX_KV_SIZE")
        if not self.cache_dir:
            self.cache_dir = _env_str("MLX_CACHE_DIR", DEFAULT_MLX_CACHE_DIR)

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to a JSON-serialisable dictionary."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "repetition_penalty": self.repetition_penalty,
            "max_kv_size": self.max_kv_size,
            "cache_dir": self.cache_dir,
            "seed": self.seed,
        }

    def get_generation_kwargs(self) -> dict[str, Any]:
        """Return the subset of parameters used by ``mlx_lm.generate``."""
        kwargs: dict[str, Any] = {
            "max_tokens": self.max_tokens,
            "temp": self.temperature,
            "top_p": self.top_p,
            "repetition_penalty": self.repetition_penalty,
        }
        if self.seed is not None:
            kwargs["seed"] = self.seed
        return kwargs

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> dict[str, Any]:
        """Validate configuration values.

        Returns:
            Dictionary with ``valid`` (bool) and ``errors`` (list[str]).
        """
        errors: list[str] = []
        if not self.model:
            errors.append("model must not be empty")
        if not 0.0 <= self.temperature <= 2.0:
            errors.append(f"temperature {self.temperature} outside [0.0, 2.0]")
        if self.max_tokens < 1:
            errors.append(f"max_tokens {self.max_tokens} must be >= 1")
        if not 0.0 <= self.top_p <= 1.0:
            errors.append(f"top_p {self.top_p} outside [0.0, 1.0]")
        if self.repetition_penalty < 1.0:
            errors.append(
                f"repetition_penalty {self.repetition_penalty} must be >= 1.0"
            )
        if self.max_kv_size is not None and self.max_kv_size < 1:
            errors.append(f"max_kv_size {self.max_kv_size} must be >= 1 or None")
        return {"valid": len(errors) == 0, "errors": errors}


# ---------------------------------------------------------------------------
# Presets
# ---------------------------------------------------------------------------


class MLXConfigPresets:
    """Pre-built configurations for common use cases."""

    @staticmethod
    def creative() -> MLXConfig:
        """High temperature, broad sampling — brainstorming & creative writing."""
        return MLXConfig(temperature=0.9, top_p=0.95, max_tokens=1500)

    @staticmethod
    def precise() -> MLXConfig:
        """Low temperature, narrow sampling — factual extraction."""
        return MLXConfig(
            temperature=0.1, top_p=0.5, max_tokens=800, repetition_penalty=1.0
        )

    @staticmethod
    def fast() -> MLXConfig:
        """Short output, moderate temperature — quick answers."""
        return MLXConfig(temperature=0.5, max_tokens=256)

    @staticmethod
    def comprehensive() -> MLXConfig:
        """Low temperature, long output — detailed analysis."""
        return MLXConfig(temperature=0.3, top_p=0.8, max_tokens=2000)

    @staticmethod
    def coding() -> MLXConfig:
        """Optimised for code generation — low temperature, no repeat penalty."""
        return MLXConfig(
            temperature=0.2, top_p=0.9, max_tokens=2000, repetition_penalty=1.0
        )


# ---------------------------------------------------------------------------
# Model recommendations by RAM tier
# ---------------------------------------------------------------------------


@dataclass
class ModelRecommendation:
    """A recommended model with its expected resource footprint."""

    repo_id: str
    label: str
    min_ram_gb: int
    approx_size_gb: float
    notes: str = ""


# Ordered from smallest to largest.
RECOMMENDED_MODELS: list[ModelRecommendation] = [
    ModelRecommendation(
        repo_id="mlx-community/Llama-3.2-3B-Instruct-4bit",
        label="Llama 3.2 3B (4-bit)",
        min_ram_gb=8,
        approx_size_gb=2.0,
        notes="Default — great quality-to-size ratio for general chat.",
    ),
    ModelRecommendation(
        repo_id="mlx-community/Qwen2.5-3B-Instruct-4bit",
        label="Qwen 2.5 3B (4-bit)",
        min_ram_gb=8,
        approx_size_gb=2.0,
        notes="Multilingual alternative with strong coding support.",
    ),
    ModelRecommendation(
        repo_id="mlx-community/Mistral-7B-Instruct-v0.3-4bit",
        label="Mistral 7B (4-bit)",
        min_ram_gb=16,
        approx_size_gb=4.5,
        notes="Step-up quality — fits 16 GB Mac with headroom.",
    ),
    ModelRecommendation(
        repo_id="mlx-community/Llama-3.1-8B-Instruct-4bit",
        label="Llama 3.1 8B (4-bit)",
        min_ram_gb=16,
        approx_size_gb=5.0,
        notes="Strong general-purpose — needs ~80 % of 16 GB unified memory.",
    ),
]


def get_models_for_ram(ram_gb: int) -> list[ModelRecommendation]:
    """Return models whose ``min_ram_gb`` is at or below *ram_gb*.

    Args:
        ram_gb: Available unified memory in gigabytes.

    Returns:
        Filtered list of model recommendations, smallest first.
    """
    return [m for m in RECOMMENDED_MODELS if m.min_ram_gb <= ram_gb]


# ---------------------------------------------------------------------------
# Singleton accessor (mirrors llm/config.py pattern)
# ---------------------------------------------------------------------------

_mlx_config_instance: MLXConfig | None = None


def get_mlx_config() -> MLXConfig:
    """Return the global MLX configuration singleton."""
    global _mlx_config_instance
    if _mlx_config_instance is None:
        _mlx_config_instance = MLXConfig()
    return _mlx_config_instance


def set_mlx_config(config: MLXConfig) -> None:
    """Replace the global MLX configuration singleton."""
    global _mlx_config_instance
    _mlx_config_instance = config


def reset_mlx_config() -> None:
    """Reset the global MLX configuration to default."""
    global _mlx_config_instance
    _mlx_config_instance = None
