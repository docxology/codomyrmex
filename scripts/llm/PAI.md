# Personal AI Infrastructure - LLM Scripts Context

**Module**: scripts/llm  
**Status**: Active  
**Last Updated**: February 2026

## Context

This module provides LLM integration scripts and demonstrations for the Codomyrmex ecosystem. It enables unified access to multiple LLM providers including OpenRouter, OpenAI, Anthropic, and Ollama.

## AI Strategy

As an AI agent working with this module:

### 1. Provider Selection

- **Development/Testing**: Use `ProviderType.OPENROUTER` with `openrouter/free` model
- **Production**: Use appropriate provider based on requirements
- **Local**: Use Ollama for offline/privacy-sensitive operations

### 2. API Key Management

```python
# ✅ Correct: Load from environment
api_key = os.environ.get("OPENROUTER_API_KEY")
if not api_key:
    raise EnvironmentError("OPENROUTER_API_KEY not set")

# ❌ Never: Hardcode keys
api_key = "sk-..."  # NEVER DO THIS
```

### 3. Resource Management

```python
# ✅ Correct: Use context manager
with get_provider(ProviderType.OPENROUTER, api_key=key) as provider:
    response = provider.complete(messages)
# Resources automatically cleaned up

# ⚠️ Alternative: Manual cleanup
provider = get_provider(...)
try:
    response = provider.complete(messages)
finally:
    provider.cleanup()
```

### 4. Error Handling

```python
from codomyrmex.llm.providers import get_provider, ProviderType, Message

try:
    with get_provider(ProviderType.OPENROUTER, api_key=key) as provider:
        response = provider.complete([Message(role="user", content="Hello")])
except RuntimeError as e:
    # Client initialization failed (missing openai package)
    log.error(f"Provider init failed: {e}")
except Exception as e:
    # API errors, network issues, etc.
    log.error(f"Completion failed: {e}")
```

## Key Files

| File | Purpose |
|------|---------|
| `examples/openrouter_usage.py` | Complete OpenRouter example with CLI |
| `examples/basic_usage.py` | Basic integration patterns |
| `test_ollama.py` | Ollama connectivity testing |
| `SPEC.md` | Technical specification |
| `README.md` | Module documentation |

## Module Integration

### Source Dependencies

- `codomyrmex.llm.providers` - Provider implementations
- `codomyrmex.llm.config` - Configuration management
- `codomyrmex.utils.cli_helpers` - CLI utilities

### Test Coverage

```bash
# Run OpenRouter tests
uv run pytest src/codomyrmex/tests/unit/llm/test_openrouter_provider.py -v
```

## Future Considerations

### Planned Enhancements

- **Caching**: Implement response caching for repeated prompts
- **Batching**: Support batch completions for efficiency
- **Fallback**: Automatic provider fallback on failure
- **Metrics**: Enhanced telemetry and cost tracking

### Provider Roadmap

- ✅ OpenRouter (implemented)
- ✅ OpenAI (implemented)
- ✅ Anthropic (implemented)
- ⏳ Google Gemini (planned)
- ⏳ Azure OpenAI (planned)
- ⏳ Mistral (planned)
