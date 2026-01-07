# mistral_vibe

## Signposting
- **Parent**: [agents](../README.md)
- **Children**:
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Integration with Mistral Vibe CLI tool. Provides client for interacting with Mistral Vibe CLI, supports code generation and completion, and provides integration adapters for Codomyrmex modules.

## Unique Features

- **CLI-based execution**: Mistral Vibe CLI tool integration
- **Mistral AI models**: Access to Mistral AI's language models
- **Dual executables**: Supports both `vibe` and `vibe-acp` commands
- **API key authentication**: Simple API key-based authentication
- **Streaming support**: Real-time streaming of responses

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `mistral_vibe_client.py` – File
- `mistral_vibe_integration.py` – File
- `tests/` – Subdirectory

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [agents](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.agents.mistral_vibe import MistralVibeClient, MistralVibeIntegrationAdapter

# Initialize Mistral Vibe client
client = MistralVibeClient(config={"mistral_vibe_api_key": "your-api-key"})

# Generate content
result = client.execute(
    prompt="Explain machine learning in simple terms",
    model="mistral-large-latest"
)
print(f"Response: {result.content}")

# Use integration adapter
adapter = MistralVibeIntegrationAdapter()
response = adapter.execute_task("text_generation", {"prompt": "..."})
```

