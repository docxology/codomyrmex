# LLM Providers -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unified abstraction layer for multiple LLM providers. Defines a common `LLMProvider` interface that normalizes sync completions, streaming, and async operations across OpenAI, Anthropic, and OpenRouter.

## Architecture

Strategy pattern with factory: `LLMProvider` (ABC) defines the contract. Three concrete providers implement it. `get_provider(ProviderType, ...)` instantiates the right class. Data models (`Message`, `CompletionResponse`, `ProviderConfig`) are shared across all providers.

## Key Classes

### `LLMProvider` (ABC)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `complete` | `messages, model, temperature, max_tokens, **kwargs` | `CompletionResponse` | Synchronous completion |
| `complete_stream` | `messages, model, temperature, max_tokens, **kwargs` | `Iterator[str]` | Yields content deltas |
| `complete_async` | `messages, model, temperature, max_tokens, **kwargs` | `CompletionResponse` | Async completion |
| `list_models` | -- | `list[str]` | Available models for this provider |
| `get_model` | `model: str \| None` | `str` | Resolves model name with fallback to default |
| `cleanup` | -- | `None` | Release resources (called by context manager exit) |

### `OpenAIProvider`

- SDK: `openai.OpenAI` / `openai.AsyncOpenAI`
- Default model: `gpt-4o`
- `list_models()` queries API, filters for models containing "gpt"
- Supports `tool_calls` in response

### `AnthropicProvider`

- SDK: `anthropic.Anthropic` / `anthropic.AsyncAnthropic`
- Default model: `claude-3-5-sonnet-20241022`
- System message extracted and passed as `system` parameter (not in messages list)
- `complete_stream` uses `client.messages.stream()` context manager
- `list_models()` returns static list of known Claude models

### `OpenRouterProvider`

- SDK: `openai.OpenAI` (OpenAI-compatible API)
- Base URL: `https://openrouter.ai/api/v1`
- Default model: `openrouter/free`
- Adds `HTTP-Referer` and `X-Title` headers for OpenRouter attribution
- `FREE_MODELS` class attribute lists verified free-tier models
- `list_models()` returns `FREE_MODELS` list

### `get_provider` (Factory)

| Parameter | Type | Description |
|-----------|------|-------------|
| `provider_type` | `ProviderType` | Which provider to instantiate |
| `config` | `ProviderConfig \| None` | Optional config object |
| `**kwargs` | -- | Passed to `ProviderConfig` if config is None |

Returns: `LLMProvider` instance. Raises `ValueError` for unsupported provider types.

## Dependencies

- **Internal**: None
- **External**: `openai` (optional), `anthropic` (optional)

## Constraints

- Only OPENAI, ANTHROPIC, and OPENROUTER are implemented; others raise `ValueError`.
- SDK packages are lazily imported; `RuntimeError` raised at call time if missing.
- `CompletionResponse.usage` normalizes token counts to `prompt_tokens`, `completion_tokens`, `total_tokens` across all providers.
- Zero-mock: real API calls only; `NotImplementedError` for unimplemented paths.

## Error Handling

- `RuntimeError` raised when SDK not installed and `complete()` called.
- `ValueError` from `get_provider` for unsupported provider types.
- All errors logged before propagation.
