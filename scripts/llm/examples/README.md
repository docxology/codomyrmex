# LLM Examples

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Example implementations demonstrating real LLM provider integrations and usage patterns.

## Examples

### OpenRouter Usage (`openrouter_usage.py`)

**Complete OpenRouter example with CLI interface and flexible API key handling.**

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

**API Key Options (in order of precedence):**

```bash
# 1. Command line argument
python openrouter_usage.py --api-key "sk-..." --prompt "Hello"

# 2. Environment variable
export OPENROUTER_API_KEY='your-key-here'
python openrouter_usage.py --prompt "Hello"

# 3. Config file (auto-detected)
mkdir -p ~/.config/openrouter
echo 'your-key-here' > ~/.config/openrouter/api_key
chmod 600 ~/.config/openrouter/api_key
python openrouter_usage.py --prompt "Hello"

# 4. Custom config file path
python openrouter_usage.py --config /path/to/api_key.txt --prompt "Hello"

# 5. Interactive prompt
python openrouter_usage.py --prompt-key --prompt "Hello"
```

**Get your free API key at:** <https://openrouter.ai/keys>

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
