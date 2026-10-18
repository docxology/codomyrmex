# llm

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: August 2026

## Overview

Validation coverage, fixtures, and regression checks for Llm.

## Directory Contents

- `PAI.md` – File
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `chains/` – Subdirectory
- `cost_tracking/` – Subdirectory
- `embeddings/` – Subdirectory
- `examples/` – Subdirectory
- `guardrails/` – Subdirectory
- `ollama_test_helpers.py` – File
- `rag/` – Subdirectory
- `streaming/` – Subdirectory
- `test_chain_of_thought.py` – File
- `test_config.py` – File
- `test_context_manager.py` – File
- `test_gemini_provider.py` – File
- `test_guardrails_detectors.py` – File
- `test_llm.py` – File
- `test_llm_base.py` – File
- `test_llm_exceptions.py` – File
- `test_llm_exceptions_direct.py` – File
- `test_multimodal_models.py` – File
- `test_ollama_integration.py` – File
- `test_openrouter_provider.py` – File
- `test_output_manager.py` – File
- `test_provider_models.py` – File
- `test_providers.py` – File
- `test_reasoning_models.py` – File
- `test_router.py` – File
- `test_safety_fabric_multimodal.py` – File

## MLX KV-cache regressions

`test_mlx_kv_cache.py` covers configuration precedence, invalid combinations,
serialization, forwarding, and pre-load failure receipts without native imports.
With `RUN_LIVE_MLX=1`, it also exercises real tiny-model generation and cache
transitions without model downloads. See the
[MLX configuration guide](../../../src/codomyrmex/llm/mlx/README.md).

```bash
uv run --locked --python 3.13 pytest -q tests/unit/llm/test_mlx_kv_cache.py
```

## Navigation

- **Parent Directory**: [unit](../README.md)
- **Project Root**: ../../../../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)

## Fabric CLI controls

`test_fabric_cli_contract.py` exercises real temporary executables for metadata, successful/empty listing, explicit nonzero errors, and local stdin execution. Installed Fabric listing and provider workflows require `RUN_LIVE_FABRIC=1`. Configuration tests pass temporary paths through `get_fabric_config(config_path=...)`.
