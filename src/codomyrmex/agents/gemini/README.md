# gemini

## Signposting
- **Parent**: [agents](../README.md)
- **Children**:
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Integration with Google Gemini CLI tool. Provides client for interacting with Gemini CLI, supports code generation and completion, and provides integration adapters for Codomyrmex modules.

## Unique Features

- **CLI-based execution**: Google Gemini CLI tool integration
- **Dual authentication**: Supports both OAuth and API key authentication
- **Slash commands**: Special commands like /model, /settings, /chat
- **File operations**: @ commands for including files in prompts
- **Session management**: Save and resume chat sessions
- **Google ecosystem**: Integration with Google's AI services

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `gemini_client.py` – File
- `gemini_integration.py` – File
- `tests/` – Subdirectory

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [agents](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.agents.gemini import GeminiClient, GeminiIntegrationAdapter

# Initialize Gemini client
client = GeminiClient(config={"gemini_api_key": "your-api-key"})

# Generate content
result = client.generate(
    prompt="Explain machine learning in simple terms",
    model="gemini-pro"
)
print(f"Response: {result.content}")

# Use integration adapter
adapter = GeminiIntegrationAdapter()
response = adapter.execute_task("text_generation", {"prompt": "..."})
```

