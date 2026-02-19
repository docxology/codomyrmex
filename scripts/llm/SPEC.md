# LLM Scripts Specification

**Module**: scripts/llm  
**Version**: v0.1.7  
**Status**: Active

## 1. Functional Requirements

The `scripts/llm` module must:

- Provide real, functional demonstrations of LLM provider integrations
- Support multiple providers: OpenRouter, OpenAI, Anthropic, Ollama
- Handle API errors gracefully with informative messages
- Demonstrate sync, async, and streaming patterns
- Expose clear CLI interfaces for all demo scripts

## 2. Provider Specifications

### OpenRouter Provider

| Property | Value |
|----------|-------|
| Base URL | `https://openrouter.ai/api/v1` |
| Auth | `OPENROUTER_API_KEY` environment variable |
| Default Model | `openrouter/free` (auto-selects best free model) |
| Protocol | OpenAI-compatible REST API |

**Required Headers:**

```
HTTP-Referer: https://github.com/codomyrmex
X-Title: Codomyrmex
Authorization: Bearer <api_key>
```

**Supported Operations:**

- `complete()` - Synchronous chat completion
- `complete_stream()` - Streaming chat completion
- `complete_async()` - Asynchronous chat completion
- `list_models()` - List available models

### Ollama Provider

| Property | Value |
|----------|-------|
| Base URL | `http://localhost:11434` (configurable) |
| Auth | None (local) |
| Protocol | Ollama native REST API |

## 3. API Surface

### OpenRouter via `codomyrmex.llm.providers`

```python
from codomyrmex.llm.providers import (
    ProviderType,
    ProviderConfig,
    Message,
    CompletionResponse,
    OpenRouterProvider,
    get_provider,
)

# Factory function
provider = get_provider(
    ProviderType.OPENROUTER,
    api_key="...",
    timeout=60.0,
    max_retries=3
)

# Direct instantiation
config = ProviderConfig(api_key="...", default_model="openrouter/free")
provider = OpenRouterProvider(config)
```

### Message Format

```python
Message(
    role: str,      # "system" | "user" | "assistant" | "tool"
    content: str,
    name: Optional[str] = None,
    tool_calls: Optional[List[Dict]] = None,
    tool_call_id: Optional[str] = None,
)
```

### CompletionResponse

```python
CompletionResponse(
    content: str,           # Response text
    model: str,             # Model used
    provider: ProviderType, # Provider type
    finish_reason: str,     # "stop" | "length" | etc.
    usage: Dict[str, int],  # Token counts
    tool_calls: List[Dict], # If function calling used
    raw_response: Any,      # Original API response
)
```

## 4. Dependencies

### Internal

- `codomyrmex.llm.providers` - Provider implementations
- `codomyrmex.llm.config` - LLM configuration
- `codomyrmex.utils.cli_helpers` - CLI utilities
- `codomyrmex.logging_monitoring` - Logging

### External

- `openai` - OpenAI Python client (used for OpenRouter via compatibility layer)

## 5. Constraints

### Performance

- Default timeout: 60 seconds
- Max retries: 3
- Streaming preferred for long responses

### Security

- API keys MUST be loaded from environment variables
- Never log or print API keys
- Validate all user inputs before sending to LLM

### Rate Limiting

- Respect provider rate limits
- Implement exponential backoff on retries
- Free tier models have lower limits

## 6. Error Handling

| Error | Action |
|-------|--------|
| Missing API key | Exit with clear message and setup instructions |
| Network timeout | Retry with exponential backoff |
| Rate limited | Wait and retry |
| Invalid model | Return available models list |
| API error | Log details, raise with context |
