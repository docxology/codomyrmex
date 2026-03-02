# Codomyrmex Agents — src/codomyrmex/llm/providers

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Unified LLM provider abstraction layer. Defines a common interface (`LLMProvider`) for interacting with OpenAI, Anthropic, and OpenRouter APIs through sync, async, and streaming completions. Includes a factory function for provider instantiation.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `models.py` | `ProviderType` | Enum: OPENAI, ANTHROPIC, OPENROUTER, GOOGLE, OLLAMA, AZURE_OPENAI, COHERE, MISTRAL |
| `models.py` | `Message` | Dataclass: role, content, name, tool_calls, tool_call_id; `to_dict()` for API format |
| `models.py` | `CompletionResponse` | Dataclass: content, model, provider, finish_reason, usage, tool_calls, raw_response |
| `models.py` | `ProviderConfig` | Dataclass: api_key, base_url, organization, timeout, max_retries, default_model, extra_headers |
| `base.py` | `LLMProvider` | Abstract base: `complete`, `complete_stream`, `complete_async`, `list_models`, context manager support |
| `openai.py` | `OpenAIProvider` | OpenAI implementation; lazy `openai.OpenAI` import; default model `gpt-4o` |
| `anthropic.py` | `AnthropicProvider` | Anthropic implementation; extracts system message for `messages.create`; default model `claude-3-5-sonnet-20241022` |
| `openrouter.py` | `OpenRouterProvider` | OpenRouter (OpenAI-compatible API); sets `HTTP-Referer` and `X-Title` headers; maintains `FREE_MODELS` list |
| `factory.py` | `get_provider` | Factory: maps `ProviderType` to provider class; creates `ProviderConfig` from kwargs |

## Operating Contracts

- All providers implement `complete`, `complete_stream`, and `complete_async` uniformly.
- Providers support context manager protocol (`with get_provider(...) as p:`).
- If the SDK package is not installed, `_init_client` sets `self._client = None`; calling `complete()` then raises `RuntimeError`.
- `AnthropicProvider` separates system messages from chat messages (Anthropic API requirement).
- `OpenRouterProvider` adds `HTTP-Referer` and `X-Title` headers automatically.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Standard library; `openai` (optional), `anthropic` (optional)
- **Used by**: `codomyrmex.llm` parent module, `codomyrmex.agents.llm_client`, MCP tool `generate_text`

## Navigation

- **Parent**: [llm](../README.md)
- **Root**: [Root](../../../../README.md)
