<!-- readme: generated -->

# llm

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/llm/`

## Overview

LLM integration modules for Codomyrmex.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `safety:` | Consolidated safety capabilities. |
| `multimodal:` | Consolidated multimodal capabilities. |
| `ollama:` | Local LLM model management via Ollama |
| `mlx:` | Native Apple Silicon LLM inference via MLX |
| `fabric:` | Microsoft Fabric AI integration |
| `providers:` | Multi-provider LLM client interfaces |
| `chains:` | Multi-step reasoning chains |
| `memory:` | Conversation and context memory |
| `tools:` | LLM tool/function calling support |
| `guardrails:` | Input/output safety validation |
| `streaming:` | Streaming response handlers |
| `embeddings:` | Text embedding generation and caching |
| `rag:` | Retrieval-Augmented Generation pipeline |
| `cost_tracking:` | Token counting and billing estimation |
| `prompts:` | Prompt versioning and template management |

## Public Exports

`llm` exports 34 public symbols via `__all__`:

`ConfigManager`, `FabricConfigManager`, `FabricManager`, `FabricOrchestrator`, `LLMConfig`, `LLMConfigPresets`, `MCPBridge`, `MCPPrompt`, `MCPResource`, `MLXConfig`, `MLXRunner`, `ModelRunner`, `OllamaManager`, `OutputManager`, `ask`, `chains`, `cli_commands`, `convert_tool_to_mcp`, `cost_tracking`, `create_mcp_bridge_from_registry`, `embeddings`, `get_config`, `guardrails`, `memory` …

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../llm/](../../../../llm/)
