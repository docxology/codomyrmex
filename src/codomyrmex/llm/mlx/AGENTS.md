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

## Operating Contracts

- All generation returns `MLXGenerationResult` dataclasses — never raw strings.
- Model loading is lazy: first call to `generate()` triggers load.
- All imports of `mlx` / `mlx_lm` are guarded; the module can be imported without these installed.
- Environment variables (`MLX_*`) take precedence over defaults.
- Follows the zero-mock testing policy: integration tests gate behind `mlx_available`.

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
