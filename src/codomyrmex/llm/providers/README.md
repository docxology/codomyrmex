# llm/providers

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

LLM provider abstractions for unified API access. Provides a common interface for interacting with different LLM providers through synchronous, streaming, and asynchronous completion methods. Supports context manager protocol for clean resource management.

## Key Exports

### Enums

- **`ProviderType`** -- Supported LLM providers. Implemented: `OPENAI`, `ANTHROPIC`, `OPENROUTER`. Planned: `GOOGLE`, `OLLAMA`, `AZURE_OPENAI`, `COHERE`, `MISTRAL`

### Data Classes

- **`Message`** -- A chat message with role (system/user/assistant/tool), content, optional name, tool calls, and tool call ID. Includes `to_dict()` for API serialization
- **`CompletionResponse`** -- Response from a completion request with content, model name, provider type, finish reason, token usage, optional tool calls, and raw response access. Includes `total_tokens` property
- **`ProviderConfig`** -- Provider configuration: API key, base URL, organization, timeout (60s default), max retries (3 default), default model, and extra headers

### Abstract Base Class

- **`LLMProvider`** -- ABC with context manager support (`with provider:`). Defines:
  - `complete()` -- Synchronous completion from messages
  - `complete_stream()` -- Streaming completion returning an iterator of text chunks
  - `complete_async()` -- Asynchronous completion
  - `list_models()` -- List available models for the provider
  - `get_model()` -- Resolve model name with fallback to defaults

### Provider Implementations

- **`OpenAIProvider`** -- OpenAI API integration (requires `openai` package). Default model: `gpt-4o`. Supports sync, streaming, and async completions with full tool call handling. Lists GPT models from the API
- **`AnthropicProvider`** -- Anthropic Claude API integration (requires `anthropic` package). Default model: `claude-3-5-sonnet-20241022`. Extracts system messages for the Anthropic API format. Lists Claude 3/3.5 model family. Supports streaming via `messages.stream()`
- **`OpenRouterProvider`** -- OpenRouter API for multi-model access via OpenAI-compatible endpoint. Default model: `openrouter/free`. Automatically sets base URL (`https://openrouter.ai/api/v1`) and required headers (HTTP-Referer, X-Title). Includes free model tier: nvidia nemotron, liquid lfm, arcee trinity mini

### Factory Function

- **`get_provider()`** -- Create a provider instance by `ProviderType`. Accepts a `ProviderConfig` or keyword arguments for inline configuration

## Directory Contents

- `__init__.py` - Provider ABC, three implementations, message/response models, config, and factory (642 lines)
- `py.typed` - PEP 561 typing marker
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration documentation
- `PAI.md` - PAI integration notes

## Navigation

- **Parent Module**: [llm](../README.md)
- **Project Root**: [codomyrmex](../../../../README.md)
