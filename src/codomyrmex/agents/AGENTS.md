# Codomyrmex Agents — src/codomyrmex/agents

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The Agents module provides integration with various agentic AI frameworks for AI-powered code editing, task automation, and multi-agent orchestration. It supports Claude, Jules, Codex, Gemini, Mistral Vibe, OpenCode, and Every Code providers.

## Active Components

### Core Infrastructure

- `core/` - Base classes, interfaces, and configuration
  - Key Classes: `AgentInterface`, `BaseAgent`, `AgentConfig`, `AgentSession`, `SessionManager`
  - Key Functions: `get_config()`, `set_config()`, `reset_config()`
- `generic/` - Generic agent base classes and utilities
  - Key Classes: `APIAgentBase`, `CLIAgentBase`, `AgentOrchestrator`

### Provider Integrations

- `claude/` - Claude API integration
  - Key Classes: `ClaudeClient`
  - Key Functions: `generate()`, `stream()`, `chat()`
- `codex/` - OpenAI Codex integration
  - Key Classes: `CodexClient`
- `gemini/` - Google Gemini CLI integration
  - Key Classes: `GeminiClient`
- `jules/` - Jules CLI integration
  - Key Classes: `JulesClient`
- `mistral_vibe/` - Mistral Vibe CLI integration
  - Key Classes: `MistralVibeClient`
- `opencode/` - OpenCode CLI integration
  - Key Classes: `OpenCodeClient`
- `every_code/` - Multi-agent orchestration
  - Key Classes: `EveryCodeClient`

### Specialized Agents

- `ai_code_editing/` - AI-powered code generation and editing
  - Key Classes: `CodeEditor`
  - Key Functions: `refactor()`, `generate()`, `review()`
- `droid/` - Task management and agent coordination
  - Key Classes: `DroidController`
- `git_agent/` - Git operations agent
  - Key Classes: `GitAgent`

### Theory

- `theory/` - Agent architecture theory and foundations
  - Key Classes: `ReactiveArchitecture`, `DeliberativeArchitecture`, `HybridArchitecture`, `KnowledgeBase`

## Key Classes and Functions

| Class/Function | Module | Purpose |
| :--- | :--- | :--- |
| `AgentInterface` | core | Abstract base class for all agents |
| `BaseAgent` | core | Concrete base with common functionality |
| `AgentOrchestrator` | generic | Multi-agent workflow coordination |
| `CodeEditor` | ai_code_editing | AI-powered code refactoring and generation |
| `ClaudeClient` | claude | Anthropic Claude API client |
| `AgentConfig` | core | Configuration management |
| `AgentSession` | core | Session state management |
| `SessionManager` | core | Multi-session handling |
| `parse_json_response()` | core | Parse JSON from agent responses |
| `parse_code_blocks()` | core | Extract code blocks from responses |

## Operating Contracts

1. **Logging**: All agents use `logging_monitoring` for structured logging
2. **Configuration**: Configuration managed via `AgentConfig` and environment variables
3. **Session Management**: Long-running tasks use `AgentSession` for state preservation
4. **Error Handling**: All agents raise `AgentError` subclasses for consistent error handling
5. **MCP Compatibility**: Agents expose MCP-compatible tool specifications

## Integration Points

- **logging_monitoring** - All agents log via centralized logger
- **llm** - LLM infrastructure for model management
- **coding** - Safe code execution and sandboxing
- **pattern_matching** - Pattern-based code analysis
- **model_context_protocol** - MCP tool specifications

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| llm | [../llm/AGENTS.md](../llm/AGENTS.md) | LLM infrastructure |
| coding | [../coding/AGENTS.md](../coding/AGENTS.md) | Code execution |
| cerebrum | [../cerebrum/AGENTS.md](../cerebrum/AGENTS.md) | Reasoning engine |

### Child Directories

| Directory | Purpose |
| :--- | :--- |
| core/ | Base classes and configuration |
| ai_code_editing/ | AI code generation |
| claude/ | Claude API integration |
| codex/ | OpenAI Codex integration |
| droid/ | Task management |

### Related Documentation

- [README.md](README.md) - User documentation
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [AGENT_COMPARISON.md](AGENT_COMPARISON.md) - Provider comparison
- [SPEC.md](SPEC.md) - Functional specification
