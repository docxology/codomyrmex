"""MLX quantization utilities and presets.

Provides helper functions for converting / quantizing HuggingFace models
to MLX format, computing expected model sizes, and reading quantization
metadata from cached models.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Quantization presets
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class QuantizationPreset:
    """Describes a quantization configuration."""

    name: str
    bits: int
    group_size: int
    description: str


QUANTIZATION_PRESETS: dict[str, QuantizationPreset] = {
    "q2": QuantizationPreset(
        name="q2",
        bits=2,
        group_size=64,
        description="Extremely aggressive — significant quality loss, minimal memory.",
    ),
    "q3": QuantizationPreset(
        name="q3",
        bits=3,
        group_size=64,
        description="Minimum viable — for very constrained memory.",
    ),
    "q4": QuantizationPreset(
        name="q4",
        bits=4,
        group_size=64,
        description="Best balance of quality and size — recommended default.",
    ),
    "q6": QuantizationPreset(
        name="q6",
        bits=6,
        group_size=64,
        description="Near-lossless — higher quality, moderate size.",
    ),
    "q8": QuantizationPreset(
        name="q8",
        bits=8,
        group_size=64,
        description="Highest quantized quality — ~1 byte per parameter.",
    ),
}

DEFAULT_QUANTIZATION = "q4"


# ---------------------------------------------------------------------------
# Size estimation
# ---------------------------------------------------------------------------


def estimate_model_size_gb(
    total_params_billions: float,
    bits: int = 4,
) -> float:
    """Estimate the on-disk size of a quantized model in gigabytes.

    Args:
        total_params_billions: Number of parameters (in billions).
        bits: Quantization bit-width (2–16).

    Returns:
        Estimated size in GB, rounded to 2 decimal places.

    Raises:
        ValueError: If *bits* is not in [2, 16].
    """
    if not 2 <= bits <= 16:
        raise ValueError(f"bits must be in [2, 16], got {bits}")
    bytes_per_param = bits / 8
    size_bytes = total_params_billions * 1e9 * bytes_per_param
    return round(size_bytes / (1024**3), 2)


def estimate_ram_required_gb(
    total_params_billions: float,
    bits: int = 4,
    context_length: int = 4096,
    num_layers: int = 32,
    num_heads: int = 32,
    head_dim: int = 128,
) -> float:
    """Estimate total RAM required to load and run a model.

    Components:
        1. Weight memory  = params × bytes_per_param
        2. KV cache       ≈ 2 × layers × heads × context × head_dim × 2 bytes
        3. Fixed overhead  ≈ 0.5 GB (MLX graph, tokenizer, metadata)

    Args:
        total_params_billions: Number of parameters (in billions).
        bits: Weight quantization bit-width.
        context_length: Max context / KV-cache token slots.
        num_layers: Number of transformer layers.
        num_heads: Number of KV attention heads.
        head_dim: Dimension per attention head.

    Returns:
        Estimated total RAM in GB, rounded to 2 decimal places.
    """
    weight_gb = estimate_model_size_gb(total_params_billions, bits)

    # KV cache: 2 (K+V) × layers × heads × context × head_dim × 2 bytes (fp16)
    kv_bytes = 2 * num_layers * num_heads * context_length * head_dim * 2
    kv_gb = kv_bytes / (1024**3)

    overhead_gb = 0.5
    return round(weight_gb + kv_gb + overhead_gb, 2)


# ---------------------------------------------------------------------------
# Quantization info reader
# ---------------------------------------------------------------------------


def read_quantization_info(model_path: str | Path) -> dict[str, Any]:
    """Read quantization metadata from a cached model's ``config.json``.

    Args:
        model_path: Path to the model directory.

    Returns:
        Dictionary with quantization details, or empty dict if none found.
    """
    config_path = Path(model_path) / "config.json"
    if not config_path.is_file():
        return {}

    try:
        with config_path.open() as fh:
            config = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to read %s: %s", config_path, exc)
        return {}

    result: dict[str, Any] = {}

    # Top-level quantization key
    if "quantization" in config:
        result["quantization"] = config["quantization"]

    # Nested quantization_config
    if "quantization_config" in config:
        qcfg = config["quantization_config"]
        result["bits"] = qcfg.get("bits")
        result["group_size"] = qcfg.get("group_size")
        result["quant_method"] = qcfg.get("quant_method")

    return result


# ---------------------------------------------------------------------------
# Model conversion (wraps mlx_lm.convert)
# ---------------------------------------------------------------------------


class MLXQuantizer:
    """Convert and quantize HuggingFace models to MLX format.

    Wraps ``mlx_lm.convert`` to produce optimized model weights.

    Example::

        quantizer = MLXQuantizer()
        quantizer.convert_model(
            "meta-llama/Llama-3.2-3B-Instruct",
            bits=4,
            output_dir="/path/to/output",
        )
    """

    @staticmethod
    def convert_model(
        source_model: str,
        bits: int = 4,
        group_size: int = 64,
        output_dir: str | None = None,
    ) -> Path:
        """Convert a HuggingFace model to quantized MLX format.

        Args:
            source_model: HuggingFace repo id of the source model.
            bits: Quantization bit-width (2, 3, 4, 6, 8).
            group_size: Quantization group size.
            output_dir: Output directory path.  Defaults to
                ``<source_model>-<bits>bit`` in CWD.

        Returns:
            Path to the output directory.

        Raises:
            ImportError: If ``mlx_lm`` is not installed.
            RuntimeError: On conversion failure.
        """
        try:
            from mlx_lm import convert as mlx_convert
        except ImportError as exc:
            raise ImportError(
                "mlx-lm is required for model conversion. "
                "Install it with: pip install mlx-lm"
            ) from exc

        if output_dir is None:
            safe_name = source_model.replace("/", "--")
            output_dir = f"{safe_name}-{bits}bit"

        out_path = Path(output_dir)
        logger.info(
            "Converting %s → %s (q%d, group_size=%d)",
            source_model,
            out_path,
            bits,
            group_size,
        )

        try:
            mlx_convert(
                source_model,
                quantize=True,
                q_bits=bits,
                q_group_size=group_size,
                mlx_path=str(out_path),
            )
            logger.info("Conversion complete: %s", out_path)
            return out_path
        except Exception as exc:
            raise RuntimeError(
                f"Failed to convert model {source_model}: {exc}"
            ) from exc

    @staticmethod
    def get_preset(name: str) -> QuantizationPreset:
        """Look up a named quantization preset.

        Args:
            name: Preset name (e.g. ``"q4"``).

        Returns:
            :class:`QuantizationPreset`.

        Raises:
            KeyError: If *name* is not a valid preset.
        """
        if name not in QUANTIZATION_PRESETS:
            valid = ", ".join(sorted(QUANTIZATION_PRESETS))
            raise KeyError(f"Unknown preset '{name}'. Valid: {valid}")
        return QUANTIZATION_PRESETS[name]

    @staticmethod
    def list_presets() -> dict[str, QuantizationPreset]:
        """Return all available quantization presets."""
        return dict(QUANTIZATION_PRESETS)
