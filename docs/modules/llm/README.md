# LLM Module Documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

LLM integration modules for Codomyrmex.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `chains` | Chain implementations for LLM reasoning. |
| `cost_tracking` | LLM Cost Tracking Module |
| `embeddings` | LLM Embeddings Module |
| `fabric` | Codomyrmex Fabric Integration Module |
| `guardrails` | LLM Guardrails Module |
| `memory` | Conversation memory management for LLMs. |
| `ollama` | Codomyrmex Ollama Integration Module |
| `prompts` | LLM Prompts Module |
| `providers` | LLM Provider abstractions for unified API access. |
| `rag` | LLM RAG Module |
| `streaming` | LLM Streaming Module |
| `tools` | Tool calling framework for LLMs. |


## Installation

```bash
uv pip install codomyrmex
```

## Quick Start

```python
from codomyrmex.llm import *  # See source for specific imports
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k llm -v
```

## Navigation

- **Source**: [src/codomyrmex/llm/](../../../src/codomyrmex/llm/)
- **Parent**: [Modules](../README.md)
