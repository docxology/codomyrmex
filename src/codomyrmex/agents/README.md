# agents

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [ai_code_editing](ai_code_editing/README.md)
    - [claude](claude/README.md)
    - [codex](codex/README.md)
    - [droid](droid/README.md)
    - [every_code](every_code/README.md)
    - [gemini](gemini/README.md)
    - [generic](generic/README.md)
    - [jules](jules/README.md)
    - [mistral_vibe](mistral_vibe/README.md)
    - [opencode](opencode/README.md)
    - [tests](tests/README.md)
    - [theory](theory/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Integration with various agentic frameworks including Jules CLI, Claude API, OpenAI Codex, OpenCode CLI, Gemini CLI, Mistral Vibe CLI, and Every Code CLI. Includes theoretical foundations, generic utilities, and framework-specific implementations that integrate seamlessly with Codomyrmex modules. Provides unified interface for all agents through `AgentInterface` abstract base class.

### Agent Types

**CLI-based Agents** (execute via command-line tools):
- `jules`: Jules CLI tool integration
- `gemini`: Google Gemini CLI integration
- `opencode`: OpenCode CLI integration
- `mistral_vibe`: Mistral Vibe CLI integration
- `every_code`: Every Code CLI integration with multi-agent orchestration

**API-based Agents** (direct API integration):
- `claude`: Anthropic Claude API integration
- `codex`: OpenAI Codex API integration

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `ai_code_editing/` – Subdirectory
- `claude/` – Subdirectory
- `codex/` – Subdirectory
- `config.py` – File
- `core.py` – File
- `droid/` – Subdirectory
- `every_code/` – Subdirectory
- `exceptions.py` – File
- `gemini/` – Subdirectory
- `generic/` – Subdirectory
- `jules/` – Subdirectory
- `mistral_vibe/` – Subdirectory
- `opencode/` – Subdirectory
- `tests/` – Subdirectory
- `theory/` – Subdirectory

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Agent Comparison**: [AGENT_COMPARISON.md](AGENT_COMPARISON.md) - Guide to choosing the right agent
- **Test Coverage**: [TEST_COVERAGE.md](TEST_COVERAGE.md) - Test coverage summary
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.agents import AgentInterface, AgentRequest, AgentResponse
from codomyrmex.agents.core import AgentCapabilities

# Example: Using a CLI-based agent (Jules)
from codomyrmex.agents.jules import JulesClient

client = JulesClient()
request = AgentRequest(prompt="Generate a Python function to sort a list")
response = client.execute(request)
print(f"Result: {response.content}")

# Example: Using an API-based agent (Claude)
from codomyrmex.agents.claude import ClaudeClient

client = ClaudeClient(config={"claude_api_key": "your-api-key"})
request = AgentRequest(prompt="Explain machine learning in simple terms")
response = client.execute(request)
print(f"Result: {response.content}")

# Example: Using integration adapter
from codomyrmex.agents.gemini import GeminiClient, GeminiIntegrationAdapter

client = GeminiClient()
adapter = GeminiIntegrationAdapter(client)
code = adapter.adapt_for_ai_code_editing(
    prompt="Create a fibonacci function",
    language="python"
)
print(f"Generated code: {code}")
```

