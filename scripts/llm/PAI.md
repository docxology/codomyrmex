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

```

Never embed provider credentials as string literals in source code.

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

## Portable MLX Configuration Evidence

Use the Python 3.15 PEP 723 script, not a provider or native inference runner:

```bash
uv run --python 3.15 --script scripts/llm/mlx_profile.py \
    --output-dir output/mlx-profile-study --iterations 2000 --repeats 7
make mlx-profile MLX_PROFILE_OUTPUT=output/mlx-profile-make
just mlx-profile output/mlx-profile-just
```

These are alternative invocations; use a fresh location for each collection.
The inline environment excludes native MLX and needs no provider credentials or
`RUN_LIVE_MLX`. Unset `MLX_MAX_KV_SIZE`, `MLX_KV_BITS`, and
`MLX_PREFILL_STEP_SIZE`. Active profiling/tracing/monitoring is rejected; launch
an uninstrumented subprocess rather than disabling caller-owned instrumentation.
Four configuration-only scenarios produce JSON, SVG, offline HTML, companion
Markdown, and a final SHA-256 manifest. No native imports, model loading,
inference, or Metal metrics belong to this workflow. See the
[study protocol](../../docs/modules/llm/mlx-profiling-study.md).

## Artifact Security and Sharing

Use a trusted local output directory with appropriately restricted permissions.
The writer rejects symlink destinations and named-artifact overwrite, but is not
a filesystem sandbox or atomic transaction. Preserve incomplete bundles; do not
retry over existing files. Review Python/build/platform/dependency metadata,
revision/dirty status, source hashes, and profiler filenames/function names before
sharing. Synthetic model paths and basename-only hotspots reduce incidental
disclosure, not all identifying metadata. Renderers escape HTML/SVG and encode
Markdown metadata; do not execute report content. Verify manifest hashes, while
recognizing that hashes alone do not authenticate the author or validate claims.
Dependency installation can use the network; artifact viewing needs none. Follow
the [LLM security guidance](../../src/codomyrmex/llm/SECURITY.md#portable-mlx-profiling-artifacts).

## Key Files

| File | Purpose |
| --- | --- |
| `mlx_profile.py` | Portable configuration collector CLI; no native inference |
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
uv run pytest tests/unit/llm/test_openrouter_provider.py -v
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
