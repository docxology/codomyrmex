# codex

## Signposting
- **Parent**: [agents](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Integration with OpenAI Codex API. Provides client for interacting with Codex API, supports code generation and completion, and provides integration adapters for Codomyrmex modules.

## Unique Features

- **API-based integration**: Direct integration with OpenAI's Codex API
- **Code-focused models**: Specialized for code generation and completion tasks
- **OpenAI ecosystem**: Integrates with OpenAI's broader API infrastructure
- **Temperature control**: Fine-grained control over response creativity
- **Token management**: Configurable max tokens and token usage tracking

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `codex_client.py` – File
- `codex_integration.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [agents](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.agents.codex import CodexClient, CodexIntegrationAdapter

from codomyrmex.agents.core import AgentRequest

# Initialize Codex client
client = CodexClient(config={"codex_api_key": "your-api-key"})

# Execute a request
request = AgentRequest(
    prompt="Create a function to calculate factorial",
    context={"language": "python"}
)
response = client.execute(request)
print(f"Generated code: {response.content}")

# Use integration adapter
adapter = CodexIntegrationAdapter(client)
code = adapter.adapt_for_ai_code_editing(
    prompt="Create a REST API endpoint",
    language="python"
)
```

