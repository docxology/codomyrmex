# Codomyrmex Agents — src/codomyrmex/llm/mlx

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Native Apple Silicon LLM inference via MLX. Provides model management, text generation (sync + streaming), chat, and quantization utilities optimised for single small models on 16 GB Mac Mini M4.

## Active Components

- `__init__.py` — Public API exports
- `config.py` — `MLXConfig`, `MLXConfigPresets`, model recommendations, singleton accessor
- `model_manager.py` — `MLXModelManager` for download/list/inspect/delete of HuggingFace models
- `runner.py` — `MLXRunner` for generate/stream_generate/chat, `MLXGenerationResult`, `MLXStreamChunk`
- `quantization.py` — `MLXQuantizer`, `QuantizationPreset`, size estimation utilities
- `profiling.py` — Portable `MLXConfig` setup measurements, not native inference
- `profile_report.py` — Offline JSON/SVG/HTML/Markdown bundle with a hash manifest

## Operating Contracts

- All generation returns `MLXGenerationResult` dataclasses — never raw strings.
- Model loading is lazy: first call to `generate()` triggers load.
- All imports of `mlx` / `mlx_lm` are guarded; the module can be imported without these installed.
- Environment variables (`MLX_*`) take precedence over defaults.
- Native MLX/MLX-LM execution is explicitly gated behind `RUN_LIVE_MLX=1`; the
  default suite exercises portable configuration paths without importing the
  native backend.
- Forward cache controls through the shared generation helper for both sync and
  streaming requests; validate before loading a model.
- Bounded caches require `max_kv_size > 4` and one-token prefill until the upstream
  sink-mask fix is verified. Never silently ignore caps on model-owned caches.
- Quantized caches default to 512-token prefill and cannot be combined with
  bounded caches. Preserve model-specific cache semantics by rejecting unsupported
  layouts rather than replacing them indiscriminately.
- Streaming errors retain compatibility text and expose `success=False` plus an
  `error_message` on the terminal chunk.
- Keep timing, cProfile, and tracemalloc passes separate. Never interpret Python
  allocation peaks as Metal memory or scenario names as native cache validation.
- Run the Python 3.15 PEP 723 script with a fresh output location; preserve failed
  partial bundles and caller-owned tracing. Do not publish unmeasured results.
- Follow the [profiling study protocol](../../../../docs/modules/llm/mlx-profiling-study.md)
  for provenance and claim boundaries; KIVI is background, not the MLX algorithm.

## Key Files

- `README.md` — User-facing documentation
- `AGENTS.md` — This file: agent coordination
- `SPEC.md` — Functional specification
- `config.py` — Configuration and presets
- `runner.py` — Core inference engine
- `model_manager.py` — Model lifecycle management
- `quantization.py` — Quantization utilities

## Dependencies

- Inherits from parent `llm` module.
- Requires `mlx-lm` for inference (optional — graceful degradation without it).
- Requires `huggingface-hub` for model downloads.

## Development Guidelines

- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to PEP 8 and the project zero-mock testing policy.
- All new features must include corresponding tests.

## Navigation Links

- **📁 Parent Directory**: [llm](../README.md) — LLM module documentation
- **🏠 Project Root**: [Codomyrmex](../../../../README.md) — Main project documentation
- **🔗 Sibling**: [ollama](../ollama/AGENTS.md) — Ollama integration
