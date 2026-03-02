# Codomyrmex Agents — src/codomyrmex/llm/ollama

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Local LLM integration via Ollama. Manages server lifecycle, model listing/downloading, prompt execution (sync, async, streaming, batch), output persistence, and configuration management for self-hosted inference.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `ollama_manager.py` | `OllamaModel` | Dataclass: name, id, size, modified, parameters, family, format, status |
| `ollama_manager.py` | `ModelExecutionResult` | Dataclass: model_name, prompt, response, execution_time, tokens_used, success, error_message |
| `ollama_manager.py` | `OllamaManager` | Core manager: server lifecycle, model listing (cached 30s), download, run_model (HTTP + CLI fallback), async execution, stats |
| `model_runner.py` | `ExecutionOptions` | Dataclass: temperature, top_p, top_k, repeat_penalty, max_tokens, timeout, stream, format, system_prompt, context_window |
| `model_runner.py` | `StreamingChunk` | Dataclass: content, done, token_count |
| `model_runner.py` | `ModelRunner` | Advanced execution: `run_with_options`, `run_streaming`, `run_batch`, `run_conversation`, `run_with_context`, `benchmark_model`, `create_model_comparison`, plus async variants (`async_run_model`, `async_chat`, `async_generate_stream`, `async_run_batch`) |
| `output_manager.py` | `OutputManager` | Saves outputs, execution results, configs, batch results, benchmark reports, and comparison reports to organized directory structure |
| `config_manager.py` | `OllamaConfig` | Dataclass: server settings, output settings, model preferences, execution defaults, integration flags |
| `config_manager.py` | `ConfigManager` | Load/save/update/validate/export/import configuration; execution presets (fast, creative, balanced, precise, long_form); model-specific config management |

## Operating Contracts

- `OllamaManager` auto-starts the Ollama server if `auto_start_server=True` and server is not running.
- Model listing uses a 30-second TTL cache; `force_refresh=True` bypasses it.
- `run_model` tries HTTP API first, falls back to CLI subprocess.
- `base_url` defaults to `os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_URL)`.
- `ModelRunner.run_batch` uses `asyncio.Semaphore` for concurrency control.
- `OutputManager` creates directory structure (`outputs/`, `configs/`, `logs/`, `reports/`) on init.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring`, `codomyrmex.config_management.defaults`
- **External**: `requests`, `aiohttp` (for async HTTP)
- **Used by**: `codomyrmex.llm` parent module (MCP tools: `generate_text`, `list_local_models`)

## Navigation

- **Parent**: [llm](../README.md)
- **Root**: [Root](../../../../README.md)
