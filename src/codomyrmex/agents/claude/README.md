# claude

## Signposting
- **Parent**: [agents](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Integration with Claude API (Anthropic). Provides client for interacting with Claude API, streaming support, multi-turn conversations, and integration adapters for Codomyrmex modules. Supports code generation, code editing, code analysis, and text completion capabilities.

## Unique Features

- **API-based integration**: Direct integration with Anthropic's Claude API
- **Advanced reasoning**: High-quality responses with advanced reasoning capabilities
- **Production-ready**: Suitable for production use cases
- **Multi-turn conversations**: Maintains conversation context across multiple turns
- **Streaming support**: Real-time streaming of responses
- **Model selection**: Support for various Claude models (claude-3-opus, claude-3-sonnet, etc.)

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `claude_client.py` – File
- `claude_integration.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [agents](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.agents.claude import ClaudeClient, ClaudeIntegrationAdapter
from codomyrmex.agents.core import AgentRequest

# Initialize Claude client
client = ClaudeClient(config={"claude_api_key": "your-api-key"})

# Execute a request
from codomyrmex.agents.core import AgentRequest

request = AgentRequest(
    prompt="Write a Python function to sort a list",
    context={"language": "python"}
)
response = client.execute(request)
print(f"Generated code: {response.content}")

# Stream responses
for chunk in client.stream(request):
    print(chunk, end="", flush=True)

# Use integration adapter
adapter = ClaudeIntegrationAdapter(client)
code = adapter.adapt_for_ai_code_editing(
    prompt="Create a REST API endpoint",
    language="python"
)
```

