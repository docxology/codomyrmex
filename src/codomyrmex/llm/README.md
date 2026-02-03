# LLM Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

LLM module providing language model integration, prompt management, and output handling for the Codomyrmex platform. Supports multi-provider backends with unified API.

## Supported Providers

| Provider | Status | Class | Description |
|----------|--------|-------|-------------|
| **OpenRouter** | ✅ Active | `OpenRouterProvider` | Unified access to 100+ models including free tier |
| **OpenAI** | ✅ Active | `OpenAIProvider` | GPT models |
| **Anthropic** | ✅ Active | `AnthropicProvider` | Claude models |
| **Ollama** | ✅ Active | `OllamaManager` | Local LLM inference |

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

## Navigation

- **Parent**: [codomyrmex](../README.md)
- **Spec**: [SPEC.md](SPEC.md)
- **Agents**: [AGENTS.md](AGENTS.md)
- **API**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Scripts**: [scripts/llm](../../../scripts/llm/README.md)
