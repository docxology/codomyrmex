# MLX Module — Functional Specification

**Version**: 1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The MLX module provides native Apple Silicon LLM inference within the Codomyrmex ecosystem. It wraps the `mlx-lm` Python package to offer model management, text generation, streaming, and quantization — all running on-device with zero data leaving the machine.

## Scope

### In Scope

- Single-model loading and inference on Apple Silicon (M1–M5)
- Synchronous and streaming text generation
- Chat-style generation with template application
- Model download, caching, listing, and deletion
- Quantization presets and model conversion (HuggingFace → MLX)
- RAM-aware model recommendations for 8–64 GB machines
- Environment-variable-based configuration

### Out of Scope

- Distributed inference across multiple devices (use `exo` or MLX distributed)
- Vision-language models (see `mlx-vlm` / the `multimodal` submodule)
- Audio processing (see `mlx-audio` / the `audio` module)
- HTTP API serving (use `mlx_lm.server` or `vllm-mlx` directly)
- Fine-tuning (use `mlx_lm.lora` CLI directly)

## Key Classes

| Class | File | Responsibility |
|:--|:--|:--|
| `MLXConfig` | `config.py` | Configuration with env-var overrides |
| `MLXConfigPresets` | `config.py` | Pre-built configs (creative, precise, fast, coding) |
| `MLXModelManager` | `model_manager.py` | Model lifecycle management |
| `MLXRunner` | `runner.py` | Load model, generate, stream, chat |
| `MLXQuantizer` | `quantization.py` | Convert/quantize HuggingFace models |

## Key Dataclasses

| Dataclass | File | Purpose |
|:--|:--|:--|
| `MLXGenerationResult` | `runner.py` | Complete generation result with timing |
| `MLXStreamChunk` | `runner.py` | Single streaming token/fragment |
| `MLXModelInfo` | `model_manager.py` | Cached model metadata |
| `ModelRecommendation` | `config.py` | RAM-tier model suggestion |
| `QuantizationPreset` | `quantization.py` | Named quantization configuration |

## Interfaces

### Generate Text

```python
runner = MLXRunner(config)
result: MLXGenerationResult = runner.generate("prompt")
```

### Stream Text

```python
for chunk in runner.stream_generate("prompt"):
    print(chunk.content, end="", flush=True)
```

### Chat

```python
result = runner.chat([
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is MLX?"},
])
```

### Model Management

```python
manager = MLXModelManager(config)
manager.download_model("mlx-community/Llama-3.2-3B-Instruct-4bit")
models = manager.list_cached_models()
manager.delete_model("mlx-community/Llama-3.2-3B-Instruct-4bit")
```

## Error Handling

- `ImportError` raised when `mlx-lm` is not installed (guarded at call sites, not import time)
- `RuntimeError` raised on model load or conversion failures
- `MLXGenerationResult.success=False` with `error_message` on generation failures
- All operations log via `codomyrmex.logging_monitoring`

## Security

All inference runs entirely on-device. No data leaves the machine. Model downloads use HTTPS from HuggingFace Hub.
