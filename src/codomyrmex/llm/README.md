# LLM Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

LLM module providing language model integration, prompt management, and output handling for the Codomyrmex platform. Supports multi-provider backends with unified API.

## PAI Integration

The llm module powers PAI's local-first inference strategy. `generate_text` is used by `Engineer` agents during BUILD for code generation and documentation synthesis. `list_local_models` is called during OBSERVE for capability discovery — the Algorithm uses this to know which local models are available before capability selection. Local Ollama models run via `OLLAMA_BASE_URL` (default: `http://localhost:11434`). See [AGENTS.md](AGENTS.md) for the full agent role access matrix.

| Algorithm Phase | LLM Role |
|----------------|----------|
| OBSERVE | `Researcher` → `list_local_models` for capability inventory |
| BUILD | `Engineer` → `generate_text` for code and doc generation |
| VERIFY | `QATester` → `generate_text` for prompt regression testing |

## Supported Providers

| Provider | Status | Class | Description |
|----------|--------|-------|-------------|
| **OpenRouter** | ✅ Active | `OpenRouterProvider` | Unified access to 100+ models including free tier |
| **OpenAI** | ✅ Active | `OpenAIProvider` | GPT models |
| **Anthropic** | ✅ Active | `AnthropicProvider` | Claude models |
| **Ollama** | ✅ Active | `OllamaManager` | Local LLM inference |

## Key Exports

### Ollama Integration
- **`OllamaManager`** — Main Ollama integration manager for local LLM model management
- **`ModelRunner`** — Advanced model execution engine for running Ollama models with streaming and batching
- **`OutputManager`** — Manages output saving and configuration for Ollama inference results
- **`ConfigManager`** — Manages all configuration aspects of the Ollama integration (paths, defaults, profiles)

### Fabric Integration
- **`FabricManager`** — Main Fabric integration manager for Codomyrmex workflows
- **`FabricOrchestrator`** — Orchestrates workflows combining Fabric patterns with Codomyrmex capabilities
- **`FabricConfigManager`** — Manages Fabric configuration and patterns

### Configuration
- **`LLMConfig`** — Configuration manager for LLM parameters and settings (temperature, tokens, model selection)
- **`LLMConfigPresets`** — Preset configurations for different use cases (creative, precise, balanced)
- `get_config` / `set_config` / `reset_config` — Global configuration access

### MCP Integration
- **`MCPBridge`** — Bridge between Codomyrmex tools and the Model Context Protocol
- **`MCPResource`** — MCP resource definition for exposing data to LLM clients
- **`MCPPrompt`** — MCP prompt definition for structured prompt templates
- **`convert_tool_to_mcp`** — Convert a Codomyrmex tool function into an MCP-compatible tool descriptor
- **`create_mcp_bridge_from_registry`** — Create an MCPBridge instance from the tool registry

### MCP Tools
- **`ask`** — Ask a question to an LLM provider (default: OpenRouter free tier)

### Consolidated Submodules
- **`safety`** — Content safety filtering and PII detection
- **`multimodal`** — Vision and audio AI model support

### Submodules
- `providers` / `chains` / `memory` / `tools` / `guardrails` / `streaming` / `embeddings` / `rag` / `cost_tracking` / `prompts`

## Quick Start

### OpenRouter (Recommended for Development)

```python
from codomyrmex.llm.providers import get_provider, ProviderType, Message
import os

# OpenRouter provides free models for development
provider = get_provider(
    ProviderType.OPENROUTER,
    api_key=os.environ["OPENROUTER_API_KEY"]
)

response = provider.complete(
    messages=[Message(role="user", content="Hello!")],
    model="openrouter/free"  # Auto-selects best free model
)
print(response.content)
```

### Streaming Response

```python
for chunk in provider.complete_stream(messages):
    print(chunk, end="", flush=True)
```

### Context Manager (Recommended)

```python
with get_provider(ProviderType.OPENROUTER, api_key=key) as provider:
    response = provider.complete(messages)
# Resources automatically cleaned up
```

## Directory Contents

### Core Files

| File | Description |
|------|-------------|
| `__init__.py` | Module exports |
| `config.py` | LLM configuration management |
| `exceptions.py` | Custom exceptions |

### Submodules

| Directory | Description |
|-----------|-------------|
| `providers/` | Multi-provider LLM client interfaces (OpenRouter, OpenAI, Anthropic) |
| `ollama/` | Local LLM model management via Ollama |
| `fabric/` | Microsoft Fabric AI integration |
| `chains/` | Multi-step reasoning chains |
| `memory/` | Conversation and context memory |
| `tools/` | LLM tool/function calling support |
| `guardrails/` | Input/output safety validation |
| `streaming/` | Streaming response handlers |
| `embeddings/` | Text embedding generation and caching |
| `rag/` | Retrieval-Augmented Generation pipeline |
| `cost_tracking/` | Token counting and billing estimation |
| `prompts/` | Prompt versioning and template management |
| `prompt_templates/` | Prompt template storage |
| `outputs/` | Output handling and formatting |

## Environment Variables

| Variable | Provider | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | OpenRouter | Get at <https://openrouter.ai/keys> |
| `OPENAI_API_KEY` | OpenAI | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic | Anthropic API key |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k llm -v
```

## Consolidated Sub-modules

The following modules have been consolidated into this module as sub-packages:

| Sub-module | Description |
|------------|-------------|
| **`multimodal/`** | Vision and audio AI model support |
| **`safety/`** | Content safety filtering and PII detection |

Original standalone modules remain as backward-compatible re-export wrappers.

## Navigation

- **Full Documentation**: [docs/modules/llm/](../../../docs/modules/llm/)
- **Parent**: [codomyrmex](../README.md)
- **Spec**: [SPEC.md](SPEC.md)
- **Agents**: [AGENTS.md](AGENTS.md)
- **API**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Scripts**: [scripts/llm](../../../scripts/llm/README.md)
