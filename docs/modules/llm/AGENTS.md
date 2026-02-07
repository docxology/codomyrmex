# LLM Module — Agent Coordination

## Purpose

LLM integration modules for Codomyrmex.

## Key Capabilities

- LLM operations and management

## Agent Usage Patterns

```python
from codomyrmex.llm import *

# Agent uses llm capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/llm/](../../../src/codomyrmex/llm/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`LLMConfig`** — Configuration manager for LLM parameters and settings.
- **`LLMConfigPresets`** — Preset configurations for different use cases.
- **`LLMError`** — Base exception for LLM-related errors.
- **`LLMConnectionError`** — Raised when connection to LLM service fails.
- **`LLMAuthenticationError`** — Raised when LLM authentication fails.
- **`get_config()`** — Get global LLM configuration instance.
- **`set_config()`** — Set global LLM configuration instance.
- **`reset_config()`** — Reset global configuration to default.

### Submodules

- `chains` — Chains
- `cost_tracking` — Cost Tracking
- `embeddings` — Embeddings
- `fabric` — Fabric
- `guardrails` — Guardrails
- `memory` — Memory
- `ollama` — Ollama
- `prompts` — Prompts

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k llm -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
