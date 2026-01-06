# Droid - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The `droid` module defines the **Autonomous Agent** abstraction within the `ai_code_editing` system. A "Droid" is a persisted or ephemeral agentic session that can maintain state, execute multi-step reasoning, and use tools.

## Design Principles

### Modularity
- **Persona Pattern**: Droids are instantiated with specific personas (e.g., "RefactoringDroid", "DocsDroid").
- **State Encapsulation**: Reasoning history and tool outputs are encapsulated within the Droid instance.

### Functionality
- **Loop**: Follows the `Think -> Act -> Observe` loop.
- **Tool Use**: Can invoke tools defined in `model_context_protocol`.

## Functional Requirements

### Core Capabilities
1.  **Chat Interface**: `chat(user_input: str) -> str`.
2.  **Tool Execution**: Automatic parsing of tool calls and execution.
3.  **Memory**: Support for short-term conversation history.

## Interface Contracts

### Public API
- `Droid(persona: str, model: str)`: Constructor.
- `Droid.run_task(task: str) -> str`: Execute a complex task.

### Dependencies
- `codomyrmex.language_models`
- `codomyrmex.model_context_protocol`

## Navigation
- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)

- **Parent**: [../SPEC.md](../SPEC.md)
