# LLM Examples

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Example implementations demonstrating real LLM provider integrations and usage patterns.

## Examples

### OpenRouter Usage (`openrouter_usage.py`)

**Complete OpenRouter example with CLI interface.**

```bash
# List available free models
python openrouter_usage.py --list-models

# Simple completion
python openrouter_usage.py --prompt "Explain Python in one sentence"

# Streaming response
python openrouter_usage.py --prompt "Write a haiku" --stream

# Specific model
python openrouter_usage.py --prompt "Hello" --model "nvidia/nemotron-3-nano-30b-a3b:free"
```

**Environment:**

```bash
export OPENROUTER_API_KEY='your-key-here'  # Get at https://openrouter.ai/keys
```

### Basic Usage (`basic_usage.py`)

Demonstrates core LLM integration patterns:

- Configuration management
- Ollama and Fabric manager interfaces
- Model runners and output handlers

### Advanced Workflow (`advanced_workflow.py`)

Demonstrates complex multi-step LLM workflows and integration patterns.

## Quick Start

```python
from codomyrmex.llm.providers import get_provider, ProviderType, Message
import os

# Create provider (context manager for auto-cleanup)
with get_provider(
    ProviderType.OPENROUTER,
    api_key=os.environ["OPENROUTER_API_KEY"]
) as provider:
    
    # Simple completion
    response = provider.complete(
        messages=[Message(role="user", content="Hello!")],
        model="openrouter/free"
    )
    print(response.content)
    
    # Streaming
    for chunk in provider.complete_stream(messages):
        print(chunk, end="", flush=True)
```

## Free Models

OpenRouter provides free models for development:

| Model | Description |
|-------|-------------|
| `openrouter/free` | Auto-selects best available |
| `nvidia/nemotron-3-nano-30b-a3b:free` | NVIDIA Nemotron |
| `liquid/lfm-2.5-1.2b-instruct:free` | Liquid LFM |
| `arcee-ai/trinity-mini:free` | Arcee Trinity |

## Navigation

- **Parent Directory**: [scripts/llm](../README.md)
- **Project Root**: [codomyrmex](../../../README.md)
- **LLM Source**: [src/codomyrmex/llm](../../../src/codomyrmex/llm/README.md)
