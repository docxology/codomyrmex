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
| `prefill_step_size` | `MLX_PREFILL_STEP_SIZE` | `None` (automatic policy below) |
| `kv_bits` | `MLX_KV_BITS` | `None` (no KV-cache quantization) |
| `kv_group_size` | `MLX_KV_GROUP_SIZE` | `64` |
| `quantized_kv_start` | `MLX_QUANTIZED_KV_START` | `0` |
| `cache_dir` | `MLX_CACHE_DIR` | `~/.cache/mlx-models` |

### Long prompts and KV-cache safety

`max_kv_size` limits attention history, not model weights or total Metal memory.
It discards older context except the first four attention-sink tokens; do not
enable it when retrieval requires the entire prompt. The cap must be an integer
greater than four. Synchronous, streaming, and chat generation share the same
validated cache settings.
Malformed cache environment values raise `ValueError` during configuration
construction rather than silently disabling a requested memory control.

Codomyrmex uses the following prefill policy:

- Unbounded, unquantized KV cache: 2048 tokens per chunk.
- Quantized KV cache: 512 tokens per chunk unless explicitly overridden.
- Bounded KV cache: one token per step. Explicit larger chunks are rejected
  while the upstream attention-sink masking fix remains unverified here.

The bounded policy is a correctness workaround for
[mlx-lm PR #1978](https://github.com/ml-explore/mlx-lm/pull/1978), which was still
open on October 17, 2026. It can substantially slow prefill; it is not the
upstream mask fix. No upstream classes are monkeypatched. Ordinary full-attention
`KVCache` layers, including those returned by `model.make_cache()`, are explicitly
replaced with bounded caches. Model-specific cache layouts are rejected rather
than silently ignoring the cap or changing their attention semantics.

Quantized and bounded caches cannot be combined: upstream rotating-cache
quantization is not implemented. Quantization accepts 2, 3, 4, 5, 6, or 8 bits,
with groups of 32, 64, or 128 elements. Group size must also divide the model's
attention head dimension; model-specific incompatibilities remain runtime errors.
Only standard full-attention KV-cache layouts are supported for these optional
cache controls. Model weight quantization is independent of KV-cache quantization.

```python
from codomyrmex.llm.mlx import MLXConfig

bounded = MLXConfig(max_kv_size=4096)  # automatically uses one-token prefill
quantized = MLXConfig(kv_bits=4, prefill_step_size=512, quantized_kv_start=0)
assert bounded.get_cache_kwargs()["prefill_step_size"] == 1
assert quantized.validate()["valid"]
```

The smaller quantized prefill default is a memory-oriented policy motivated by
[Bobby's upstream measurements](https://gist.github.com/robertcprice/88f542f29ec8b97f2a8b1edde3fdc903),
not a promise of a particular RAM or throughput improvement. Those measurements
used specific models, hardware, and mlx-lm 0.31.3; the largest reported savings
compare both quantization and chunk size against an fp16 baseline. Smaller chunks
can also help unquantized caches. Measure peak memory, prefill time, decode
throughput, and recall together on your workload.

Native execution remains opt-in with `RUN_LIVE_MLX=1`. Portable regression tests
do not import the native backend; the opt-in tests use tiny random models and
real cache transitions without downloading model weights:

```bash
uv run --locked --python 3.13 pytest -q tests/unit/llm/test_mlx_kv_cache.py
RUN_LIVE_MLX=1 uv run --locked --python 3.13 pytest -q tests/unit/llm/test_mlx_kv_cache.py
```

The native cache suite was verified on Python 3.13 with the locked
`mlx==0.31.1` / `mlx-lm==0.31.1` pair and, separately, the report's
`mlx==0.31.2` / `mlx-lm==0.31.3` pair. Use compatible core/LM versions;
mixing mlx-lm 0.31.3 with mlx 0.31.1 fails upstream during import because
`new_thread_local_stream` is unavailable. These are compatibility checks,
not the 8k–30k production-model memory or recall benchmarks.

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
