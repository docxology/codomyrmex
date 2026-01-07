# every_code

## Signposting
- **Parent**: [agents](../README.md)
- **Children**:
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Integration with Every Code CLI tool. Every Code is a fork of the Codex CLI that provides validation, automation, browser integration, multi-agents, theming, and more. It can orchestrate agents from OpenAI, Claude, Gemini, or any provider.

## Unique Features

- **Multi-agent orchestration**: Coordinates multiple agents (Claude, Gemini, GPT-5) for complex tasks
- **Special commands**: 
  - `/plan`: Multi-agent consensus planning
  - `/solve`: Fastest agent problem solving
  - `/code`: Multi-agent code generation with worktrees
  - `/auto`: Auto Drive for multi-step task coordination
- **Browser integration**: `/chrome` and `/browser` commands for web automation
- **Dual command support**: Uses `code` or `coder` (to avoid VS Code conflicts)
- **Enhanced reasoning**: Configurable reasoning levels (low, medium, high)
- **Theme system**: Customizable UI themes
- **Worktree management**: Creates worktrees for safe code generation

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `every_code_client.py` – File
- `every_code_integration.py` – File
- `tests/` – Subdirectory

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [agents](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.agents.every_code import EveryCodeClient, EveryCodeIntegrationAdapter

# Initialize Every Code client
client = EveryCodeClient(config={"every_code_api_key": "your-api-key"})

# Generate content using /code command
result = client.execute(
    prompt="/code Create a fibonacci function in Python"
)
print(f"Response: {result.content}")

# Use integration adapter
adapter = EveryCodeIntegrationAdapter(client)
code = adapter.adapt_for_ai_code_editing(
    prompt="Create a sorting function",
    language="python"
)
```

## Special Commands

Every Code supports special commands that can be used in prompts:

- `/plan "description"` - Plan code changes with multi-agent consensus
- `/solve "problem"` - Solve complex problems with fastest agent
- `/code "description"` - Write code with multi-agent consensus
- `/auto "task"` - Hand off multi-step tasks to Auto Drive
- `/chrome [port]` - Connect to external Chrome browser
- `/browser [url]` - Use internal headless browser

## References

- [Every Code GitHub Repository](https://github.com/just-every/code)
- [Every Code Documentation](https://github.com/just-every/code#readme)

