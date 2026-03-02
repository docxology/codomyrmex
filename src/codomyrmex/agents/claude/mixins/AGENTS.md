# Codomyrmex Agents -- src/codomyrmex/agents/claude/mixins

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Mixin classes that decompose the `ClaudeClient` into focused capabilities: API execution with retry logic, tool/function calling, session management, file operations, code intelligence, and system operations. Each mixin is composed into `ClaudeClient` via multiple inheritance.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `execution.py` | `ExecutionMixin` | Core API execution with exponential backoff retry, streaming, system-message handling, cost calculation, and response extraction |
| `tools.py` | `ToolsMixin` | Tool registration, handler dispatch, and automatic multi-round tool execution loop |
| `session.py` | `SessionMixin` | Multi-turn conversation management via `AgentSession`, context injection from history |
| `file_ops.py` | `FileOpsMixin` | AI-guided file editing (`edit_file`), file generation (`create_file`), and code-block extraction |
| `code_intel.py` | `CodeIntelMixin` | Code review, explanation, diff generation, and test suggestion using Claude as analyst |
| `system_ops.py` | `SystemOpsMixin` | Directory scanning, shell command execution, and project structure analysis |
| `__init__.py` | -- | Package marker (no exports) |

## Operating Contracts

- Each mixin assumes it will be composed with `APIAgentBase` and accesses `self.client`, `self.model`, `self.max_tokens`, `self.temperature`, `self._tools`, and `self.logger`.
- `ExecutionMixin._execute_with_retry` implements exponential backoff with jitter (25% variance) and honours `Retry-After` headers from rate-limit responses.
- `ToolsMixin.execute_with_tools` loops up to `max_tool_rounds` (default 10), executing registered tool handlers and feeding results back to Claude.
- `FileOpsMixin.edit_file` auto-detects language from file extension; returns original content, modified content, and unified diff.
- `SystemOpsMixin.run_command` executes shell commands via `subprocess.run` with configurable timeout and working directory.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.agents.core` (AgentRequest, AgentResponse, AgentSession, ClaudeError), `codomyrmex.agents.core.session` (SessionManager), `codomyrmex.logging_monitoring`
- **Used by**: `codomyrmex.agents.claude.claude_client.ClaudeClient` (composes all six mixins)

## Navigation

- **Parent**: [claude](../AGENTS.md)
- **Root**: [Root](../../../../../README.md)
