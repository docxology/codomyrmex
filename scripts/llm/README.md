# LLM Scripts Module

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

This module provides automation scripts and demonstrations for the Codomyrmex LLM integration layer. It showcases real, functional implementations for multi-provider LLM access, including **OpenRouter**, Ollama, and prompt template management.

## Supported Providers

| Provider | Status | API Key Env Variable | Description |
|----------|--------|---------------------|-------------|
| **OpenRouter** | ✅ Active | `OPENROUTER_API_KEY` | Unified access to 100+ models including free tier |
| **Ollama** | ✅ Active | N/A (local) | Local LLM inference |
| **OpenAI** | ✅ Active | `OPENAI_API_KEY` | GPT models |
| **Anthropic** | ✅ Active | `ANTHROPIC_API_KEY` | Claude models |

## Quick Start: OpenRouter

OpenRouter provides access to multiple LLM providers through a single API, including **free models** for development.

```bash
# 1. Get your API key at https://openrouter.ai/keys
export OPENROUTER_API_KEY='your-key-here'

# 2. Run the OpenRouter example
cd scripts/llm/examples
python openrouter_usage.py --list-models      # List free models
python openrouter_usage.py --prompt "Hello"   # Simple completion
python openrouter_usage.py --prompt "Hi" --stream  # Streaming
```

### Programmatic Usage

```python
from codomyrmex.llm.providers import get_provider, ProviderType, Message
import os

# Create OpenRouter provider
provider = get_provider(
    ProviderType.OPENROUTER,
    api_key=os.environ["OPENROUTER_API_KEY"]
)

# Simple completion
response = provider.complete(
    messages=[Message(role="user", content="Hello!")],
    model="openrouter/free"  # Auto-selects best free model
)
print(response.content)

# Streaming
for chunk in provider.complete_stream(messages):
    print(chunk, end="", flush=True)
```

## Directory Contents

### Core Scripts

| File | Description |
|------|-------------|
| `orchestrate.py` | Orchestrator for running all LLM scripts |
| `test_ollama.py` | Test local Ollama server connectivity |
| `prompt_template_demo.py` | Demonstrate prompt template loading and variable substitution |

### Examples (`examples/`)

| File | Description |
|------|-------------|
| `openrouter_usage.py` | **Complete OpenRouter example** with streaming, model listing |
| `basic_usage.py` | Basic LLM integration patterns |
| `advanced_workflow.py` | Complex multi-step LLM workflows |

### Feature Demonstrations

Each subdirectory contains a demo script and an `openrouter_free_example.py`:

| Directory | Description | README |
|-----------|-------------|--------|
| `cost_tracking/` | Token counting and billing estimation | [📄](cost_tracking/README.md) |
| `embeddings/` | Text embedding generation and similarity search | [📄](embeddings/README.md) |
| `guardrails/` | Input/output safety validation | [📄](guardrails/README.md) |
| `prompts/` | Prompt versioning and template management | [📄](prompts/README.md) |
| `rag/` | Retrieval-Augmented Generation pipeline | [📄](rag/README.md) |
| `streaming/` | Streaming response handlers | [📄](streaming/README.md) |

## Free Models on OpenRouter

OpenRouter provides several free models for development:

- `openrouter/free` - Auto-selects best available free model
- `nvidia/nemotron-3-nano-30b-a3b:free`
- `nvidia/nemotron-nano-12b-v2-vl:free`
- `liquid/lfm-2.5-1.2b-instruct:free`
- `arcee-ai/trinity-mini:free`

See full list: <https://openrouter.ai/models>

## Testing

```bash
# Run OpenRouter provider tests
cd /path/to/codomyrmex
uv run pytest src/codomyrmex/tests/unit/llm/test_openrouter_provider.py -v

# Test Ollama connectivity
python scripts/llm/test_ollama.py
```

## Navigation

- **Parent Directory**: [scripts](../README.md)
- **Project Root**: [codomyrmex](../../README.md)
- **LLM Module Source**: [src/codomyrmex/llm](../../src/codomyrmex/llm/README.md)
