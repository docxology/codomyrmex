# Codomyrmex Agents — scripts/agents

## Signposting
- **Parent**: [Agents](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
CLI orchestrator script providing comprehensive access to all agent types in the Codomyrmex agents module.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `orchestrate.py` – Main orchestrator script with CLI commands for all agent types
- `tests/` – Directory containing tests components

## Command Structure

The orchestrator provides commands for the following agent types:

### Core Agent Commands
- **Jules**: `execute`, `stream`, `check`, `help`, `command`
- **Claude**: `execute`, `stream`, `check`
- **Codex**: `execute`, `stream`, `check`
- **OpenCode**: `execute`, `stream`, `check`, `init`, `version`
- **Gemini**: `execute`, `stream`, `check`, `chat save`, `chat resume`, `chat list`

### Droid Controller Commands
- **Controller**: `start`, `stop`, `status`
- **Configuration**: `config show`, `config set`
- **Metrics**: `metrics`, `metrics reset`

### Orchestration Commands
- **Multi-agent**: `parallel`, `sequential`, `fallback`, `list`, `select`

### Theory Module Commands
- **Information**: `info`, `architectures`, `reasoning`

### Configuration Management Commands
- **Config**: `show`, `set`, `reset`, `validate`

### Task Planner Commands
- **Task Management**: `create`, `list`, `get`, `update`, `ready`, `order`, `clear`

### Message Bus Commands
- **Messaging**: `subscribe`, `publish`, `send`, `broadcast`, `history`

### Enhanced Droid Commands
- **Config Management**: `config save`, `config load`
- **Task Execution**: `execute-task`
- **TODO Management**: `todo load`, `todo save`, `todo validate`, `todo migrate`, `todo list`

## Key Functions

### Common Operations
- `_handle_agent_execute(client_class, client_name, args)`: Execute prompt with any agent
- `_handle_agent_stream(client_class, client_name, args)`: Stream response from any agent
- `_create_agent_request(prompt, args)`: Create AgentRequest from CLI arguments
- `_parse_context(context_str)`: Parse JSON context string

### Agent-Specific Handlers
- `handle_jules_*`: Jules-specific operations (help, command execution)
- `handle_claude_*`: Claude API operations
- `handle_codex_*`: Codex API operations
- `handle_opencode_*`: OpenCode CLI operations (init, version)
- `handle_gemini_*`: Gemini CLI operations (chat management)
- `handle_droid_*`: Droid controller operations (including TODO management)
- `handle_orchestrate_*`: Multi-agent orchestration (including capability selection)
- `handle_theory_*`: Theory module information
- `handle_config_*`: Configuration management
- `handle_task_*`: Task planner operations
- `handle_message_*`: Message bus operations

## Dependencies

- `codomyrmex.agents`: Core agent module with all client implementations
- `codomyrmex.agents.jules`: JulesClient
- `codomyrmex.agents.claude`: ClaudeClient
- `codomyrmex.agents.codex`: CodexClient
- `codomyrmex.agents.opencode`: OpenCodeClient
- `codomyrmex.agents.gemini`: GeminiClient
- `codomyrmex.agents.droid`: DroidController, DroidConfig
- `codomyrmex.agents.generic`: AgentOrchestrator, TaskPlanner, MessageBus
- `codomyrmex.agents.theory`: Theory module components
- `codomyrmex.agents.droid`: TodoManager, TodoItem, save_config_to_file, load_config_from_file
- `codomyrmex.logging_monitoring`: Logging infrastructure
- `_orchestrator_utils`: Shared CLI utilities

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Handle missing dependencies gracefully (agents may not be available if CLI tools or packages are not installed).
- Provide consistent error handling and user feedback across all commands.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [scripts](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../README.md) - Main project documentation