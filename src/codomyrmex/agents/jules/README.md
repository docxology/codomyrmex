# jules

## Signposting
- **Parent**: [agents](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Integration with Jules CLI tool. Provides client wrapper for executing jules commands, handles command failures and timeouts gracefully, and provides integration adapters for Codomyrmex modules. Supports code generation, code editing, code analysis, text completion, and streaming capabilities.

## Unique Features

- **CLI-based execution**: Simple command-line tool integration
- **No API keys required**: Uses locally installed Jules CLI
- **Fast execution**: Direct CLI execution without API overhead
- **Command-based interface**: Simple command-based execution model
- **Lightweight**: Minimal dependencies and configuration

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `jules_client.py` – File
- `jules_integration.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [agents](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.agents.jules import JulesClient, JulesIntegrationAdapter

# Initialize Jules client
client = JulesClient()

from codomyrmex.agents.core import AgentRequest

# Execute a request
request = AgentRequest(
    prompt="Create a REST API endpoint",
    context={"language": "python"}
)
response = client.execute(request)
print(f"Result: {response.content}")

# Use integration adapter
adapter = JulesIntegrationAdapter(client)
code = adapter.adapt_for_ai_code_editing(
    prompt="Create a sorting function",
    language="python"
)
```

