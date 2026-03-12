"""Codomyrmex MLX Integration Module.

Provides native Apple Silicon LLM inference via the ``mlx-lm`` package.
Optimised for single-model use on Mac Mini M4 (16 GB unified memory).

Key components:

- :class:`MLXConfig` / :class:`MLXConfigPresets` — configuration and presets
- :class:`MLXRunner` — load, generate, stream, and chat
- :class:`MLXModelManager` — download, list, inspect, and delete models
- :class:`MLXQuantizer` — quantize HuggingFace models for MLX

Quick start::

    from codomyrmex.llm.mlx import MLXRunner, MLXConfig

    runner = MLXRunner(MLXConfig(model="mlx-community/Llama-3.2-3B-Instruct-4bit"))
    result = runner.generate("Explain quantum computing in one paragraph.")
    print(result.response)
"""

from .config import (
    DEFAULT_MLX_CACHE_DIR,
    DEFAULT_MLX_MODEL,
    RECOMMENDED_MODELS,
    MLXConfig,
    MLXConfigPresets,
    ModelRecommendation,
    get_mlx_config,
    get_models_for_ram,
    reset_mlx_config,
    set_mlx_config,
)
from .model_manager import MLXModelInfo, MLXModelManager
from .quantization import (
    DEFAULT_QUANTIZATION,
    QUANTIZATION_PRESETS,
    MLXQuantizer,
    QuantizationPreset,
    estimate_model_size_gb,
    estimate_ram_required_gb,
    read_quantization_info,
)
from .runner import MLXGenerationResult, MLXRunner, MLXStreamChunk

__all__ = [
    # Config
    "DEFAULT_MLX_CACHE_DIR",
    "DEFAULT_MLX_MODEL",
    # Quantization
    "DEFAULT_QUANTIZATION",
    "QUANTIZATION_PRESETS",
    "RECOMMENDED_MODELS",
    "MLXConfig",
    "MLXConfigPresets",
    # Runner
    "MLXGenerationResult",
    # Model management
    "MLXModelInfo",
    "MLXModelManager",
    "MLXQuantizer",
    "MLXRunner",
    "MLXStreamChunk",
    "ModelRecommendation",
    "QuantizationPreset",
    "estimate_model_size_gb",
    "estimate_ram_required_gb",
    "get_mlx_config",
    "get_models_for_ram",
    "read_quantization_info",
    "reset_mlx_config",
    "set_mlx_config",
]

__version__ = "1.0.0"
