# Codomyrmex Agents -- src/codomyrmex/agents/gemini

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Google Gemini agent integration providing both an SDK-based API client (`GeminiClient`) and a CLI subprocess wrapper (`GeminiCLIWrapper`), plus an integration adapter that bridges Gemini with Codomyrmex's code-editing, LLM, and code-execution modules.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `gemini_client.py` | `GeminiClient` | Full-featured `google-genai` SDK client supporting text generation, streaming, multimodal input (images via PIL), embeddings, file management, cached content, tuned models, batch operations, and media generation (images/video) |
| `gemini_cli.py` | `GeminiCLIWrapper` | Subprocess wrapper around the `gemini` CLI executable; supports JSON output, session management, extension management, and MCP server management |
| `gemini_integration.py` | `GeminiIntegrationAdapter` | Adapts Gemini for Codomyrmex module interfaces: `adapt_for_ai_code_editing`, `adapt_for_llm`, `adapt_for_code_execution` |
| `__init__.py` | -- | Exports `GeminiClient`, `GeminiCLIWrapper`, `GeminiIntegrationAdapter` |

## Operating Contracts

- `GeminiClient` requires a `GEMINI_API_KEY` environment variable or config-dict entry; raises `GeminiError` if initialization fails.
- Default model is `gemini-2.0-flash`; override via `gemini_model` config key or per-request `context["model"]`.
- `GeminiCLIWrapper` requires the `gemini` CLI to be on `PATH`; raises `GeminiError` if the executable is not found.
- All SDK and subprocess errors are wrapped in `GeminiError` with structured log output.
- `GeminiIntegrationAdapter.adapt_for_ai_code_editing` forwards multimodal data (images, files, directories) when present in kwargs.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.agents.core` (BaseAgent, AgentRequest, AgentResponse, AgentCapabilities, AgentIntegrationAdapter, GeminiError), `codomyrmex.logging_monitoring`
- **External**: `google.genai` SDK, `PIL` (Pillow) for image loading, `gemini` CLI executable
- **Used by**: Agent orchestrator and any consumer that needs Gemini as an LLM backend

## Navigation

- **Parent**: [agents](../README.md)
- **Root**: [Root](../../../../README.md)
