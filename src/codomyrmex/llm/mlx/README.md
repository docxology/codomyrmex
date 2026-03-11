# Codomyrmex MLX Module

**Version**: 1.0.0 | **Status**: Active | **Last Updated**: March 2026

Native Apple Silicon LLM inference via [MLX](https://github.com/ml-explore/mlx) and [mlx-lm](https://pypi.org/project/mlx-lm/). Optimised for single-model use on Mac Mini M4 (16 GB unified memory).

## Quick Start

```python
from codomyrmex.llm.mlx import MLXRunner, MLXConfig

runner = MLXRunner(MLXConfig(model="mlx-community/Llama-3.2-3B-Instruct-4bit"))
result = runner.generate("Explain quantum computing in one paragraph.")
print(result.response)
```

## Features

| Feature | Description |
|:--|:--|
| **Zero-copy inference** | Leverages Apple Silicon unified memory — no CPU↔GPU transfer |
| **Lazy model loading** | Model is loaded on first call and kept resident |
| **Streaming** | Token-by-token streaming via `stream_generate()` |
| **Chat templates** | Automatic chat-template application via tokenizer |
| **Model management** | Download, list, inspect, and delete cached models |
| **Quantization** | Convert HuggingFace models to 2–8 bit MLX format |
| **RAM-aware recommendations** | Model suggestions filtered by available memory |

## Architecture

```
mlx/
├── __init__.py          # Public API exports
├── config.py            # MLXConfig, presets, model recommendations
├── model_manager.py     # Download / list / inspect / delete
├── runner.py            # generate / stream_generate / chat
├── quantization.py      # Presets, size estimation, conversion
├── README.md            # This file
├── AGENTS.md            # Agent coordination
└── SPEC.md              # Functional specification
```

## Configuration

All parameters support environment variable overrides:

| Parameter | Env Variable | Default |
|:--|:--|:--|
| `model` | `MLX_MODEL` | `mlx-community/Llama-3.2-3B-Instruct-4bit` |
| `temperature` | `MLX_TEMPERATURE` | `0.7` |
| `max_tokens` | `MLX_MAX_TOKENS` | `1000` |
| `top_p` | `MLX_TOP_P` | `0.9` |
| `repetition_penalty` | `MLX_REPETITION_PENALTY` | `1.1` |
| `max_kv_size` | `MLX_MAX_KV_SIZE` | `None` (unlimited) |
| `cache_dir` | `MLX_CACHE_DIR` | `~/.cache/mlx-models` |

## Recommended Models (16 GB Mac Mini M4)

| Model | Size | RAM | Notes |
|:--|:--|:--|:--|
| Llama 3.2 3B 4-bit | ~2 GB | 8 GB+ | Default — best quality-to-size |
| Qwen 2.5 3B 4-bit | ~2 GB | 8 GB+ | Multilingual + coding |
| Mistral 7B 4-bit | ~4.5 GB | 16 GB | Step-up quality |
| Llama 3.1 8B 4-bit | ~5 GB | 16 GB | Strongest at 16 GB limit |

## Dependencies

- `mlx` — core array framework (Apple Silicon only)
- `mlx-lm` — LLM inference and fine-tuning
- `huggingface-hub` — model downloads

Install: `pip install mlx-lm` (pulls `mlx` and `huggingface-hub` automatically).

## Navigation

- **Parent**: [LLM Module](../README.md)
- **Root**: [Codomyrmex](../../../../README.md)
- **Sibling**: [Ollama Module](../ollama/README.md)
