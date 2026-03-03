# Codomyrmex Agents — scripts/llm

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Purpose

This module provides automation scripts and demonstrations for LLM (Large Language Model) integrations. It enables AI agents and developers to interact with multiple LLM providers through a unified interface.

## Primary Capabilities

### 1. Multi-Provider LLM Access

- **OpenRouter**: Unified API for 100+ models including free tier
- **Ollama**: Local LLM inference
- **OpenAI**: GPT models
- **Anthropic**: Claude models

### 2. Key Operations

- Chat completions (sync, async, streaming)
- Model discovery and listing
- Prompt template management
- Cost tracking and token counting

## Active Components

| Component | Type | Purpose |
|-----------|------|---------|
| `examples/openrouter_usage.py` | Script | Complete OpenRouter demo with streaming |
| `examples/basic_usage.py` | Script | LLM integration patterns |
| `test_ollama.py` | Script | Ollama connectivity testing |
| `prompt_template_demo.py` | Script | Prompt template demonstrations |
| `cost_tracking/` | Module | Token counting and billing |
| `embeddings/` | Module | Text embedding generation |
| `guardrails/` | Module | Input/output safety validation |
| `streaming/` | Module | Streaming response handlers |

## Operating Contracts

### For AI Agents

1. **Provider Selection**: Use `get_provider(ProviderType.OPENROUTER, ...)` for unified access
2. **API Key Handling**: Always read from environment variables, never hardcode
3. **Error Handling**: Catch and handle `RuntimeError` for uninitialized clients
4. **Resource Cleanup**: Use context manager pattern (`with provider as p:`)
5. **Model Selection**: Use `openrouter/free` for development/testing

### Code Patterns

```python
# Preferred: Context manager for automatic cleanup
from codomyrmex.llm.providers import get_provider, ProviderType, Message

with get_provider(ProviderType.OPENROUTER, api_key=os.environ["OPENROUTER_API_KEY"]) as provider:
    response = provider.complete([Message(role="user", content="Hello")])
    print(response.content)
# Client automatically cleaned up here
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | For OpenRouter | Get at <https://openrouter.ai/keys> |
| `OPENAI_API_KEY` | For OpenAI | OpenAI API key |
| `ANTHROPIC_API_KEY` | For Anthropic | Anthropic API key |

## Integration Points

- **Source Module**: `src/codomyrmex/llm/providers/` - Provider implementations
- **Tests**: `src/codomyrmex/tests/unit/llm/test_openrouter_provider.py`
- **Config**: `src/codomyrmex/llm/config.py` - LLM configuration management

## Telemetry & Monitoring

- Log all LLM requests via `codomyrmex.logging_monitoring`
- Track token usage from `CompletionResponse.usage`
- Monitor costs via `cost_tracking/` module

## Navigation Links

- **📁 Parent Directory**: [scripts](../README.md)
- **🏠 Project Root**: [codomyrmex](../../README.md)
- **📦 LLM Source**: [src/codomyrmex/llm](../../src/codomyrmex/llm/README.md)
