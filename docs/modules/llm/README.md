# LLM Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Large Language Model integration with Ollama, OpenAI, Anthropic, and Fabric.

## Key Features

- **Multi-Provider** — OpenAI, Anthropic, Ollama
- **Local-First** — Privacy with local models
- **Templates** — Prompt templates
- **Streaming** — Stream responses

## Quick Start

```python
from codomyrmex.llm import LLMClient, OllamaManager

# Cloud provider
client = LLMClient(provider="openai", model="gpt-4")
response = client.complete("Explain this code")

# Local with Ollama
ollama = OllamaManager()
ollama.pull_model("codellama:13b")
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/llm/](../../../src/codomyrmex/llm/)
- **Parent**: [Modules](../README.md)
