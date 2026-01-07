# opencode

## Signposting
- **Parent**: [agents](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Integration with OpenCode CLI tool. Provides client wrapper for executing opencode commands, handles command failures and timeouts gracefully, and provides integration adapters for Codomyrmex modules.

## Unique Features

- **Open-source alternative**: Open-source CLI tool for code generation
- **CLI-based execution**: Command-line tool integration
- **No API keys required**: Uses locally installed OpenCode CLI
- **Local processing**: Code generation runs locally
- **TUI support**: Terminal User Interface support (limited programmatic access)

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `opencode_client.py` – File
- `opencode_integration.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [agents](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.agents.opencode import OpenCodeClient, OpenCodeIntegrationAdapter

from codomyrmex.agents.core import AgentRequest

# Initialize OpenCode client
client = OpenCodeClient()

# Execute a request
request = AgentRequest(
    prompt="Create a function to calculate factorial",
    context={"language": "python"}
)
response = client.execute(request)
print(f"Result: {response.content}")

# Use integration adapter
adapter = OpenCodeIntegrationAdapter(client)
code = adapter.adapt_for_ai_code_editing(
    prompt="Create a sorting function",
    language="python"
)
```

