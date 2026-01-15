# Agents

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview
The `agents` module is the intelligence layer of the Codomyrmex ecosystem. It provides a unified interface for interacting with various Large Language Model (LLM) backends and specialized AI agents. This module orchestrates the lifecycle of AI agents, from initialization and configuration to task execution and result processing. It supports both general-purpose conversational agents (like Claude, Gemini, Mistral) and specialized coding agents (like Jules, Codex, EveryCode).

## Key Features
- **Unified Agent Interface**: A consistent API (`core.py`) for interacting with different agent types, abstracting away provider-specific details.
- **Multi-Provider Support**: Built-in support for major LLM providers including Anthropic (Claude), Google (Gemini), and Mistral.
- **Specialized Coding Agents**: dedicated submodules for code editing (`ai_code_editing`), synthesis (`codex`), and review (`jules`).
- **Configurable Personas**: The `theory` submodule provides foundational definitions for agent personas and capabilities.
- **Extensible Architecture**: Designed to easily add new agent types or providers via the `plugin_system`.

## Quick Start

```python
from codomyrmex.agents.core import AgentFactory
from codomyrmex.agents.config import AgentConfig

# Initialize a standard coding agent
config = AgentConfig(provider="anthropic", model="claude-3-opus", temperature=0.0)
agent = AgentFactory.create_agent("coding_assistant", config)

# Execute a task
response = agent.execute_task("Refactor the utils.py file to improve error handling.")
print(response.content)
```

## Module Structure

### Core Components
- `core.py`: Defines the base `Agent` class and the `AgentFactory`.
- `config.py`: Configuration schemas for agent instantiation.
- `exceptions.py`: Agent-specific exception hierarchy.
- `cli_handlers.py`: Integration with the CLI layer for agent commands.

### Agent Families
- **General Purpose**:
    - `claude/`: Integration with Anthropic's Claude models.
    - `gemini/`: Integration with Google's Gemini models.
    - `mistral_vibe/`: Integration with Mistral AI models.
- **Specialized**:
    - `ai_code_editing/`: Agents optimized for direct code manipulation and refactoring.
    - `jules/`: A specialized code review and quality assurance agent.
    - `codex/`: Agents focused on code generation and synthesis.
    - `droid/`: Task automation and script execution agents.
    - `every_code/`: Multi-language support agents.

## Navigation Links
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Comparison Guide**: [AGENT_COMPARISON.md](AGENT_COMPARISON.md)
- **📁 Parent Directory**: [codomyrmex](../README.md)
- **🏠 Project Root**: [README](../../../README.md)
