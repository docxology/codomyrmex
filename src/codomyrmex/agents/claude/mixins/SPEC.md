# Claude Mixins -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `mixins` package decomposes `ClaudeClient` functionality into six single-responsibility mixin classes. This keeps each concern (retry logic, tool dispatch, session tracking, file I/O, code intelligence, system operations) isolated and testable while composing cleanly via Python multiple inheritance.

## Architecture

Mixin composition pattern: `ClaudeClient(ExecutionMixin, ToolsMixin, SessionMixin, FileOpsMixin, CodeIntelMixin, SystemOpsMixin, APIAgentBase)`. Method resolution order ensures mixins can call `self.execute()`, `self.client`, and other base-class members.

## Key Classes

### `ExecutionMixin`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `_execute_impl` | `request: AgentRequest` | `AgentResponse` | Delegates to `_execute_with_retry` |
| `_execute_with_retry` | `request, attempt=0` | `AgentResponse` | Retry with exponential backoff and jitter |
| `_stream_impl` | `request: AgentRequest` | `Iterator[str]` | Stream Claude API response chunks |
| `_build_messages_with_system` | `request: AgentRequest` | `tuple[list, str\|None]` | Extract system message and build message list with image support |
| `_calculate_cost` | `input_tokens, output_tokens` | `float` | USD cost from `CLAUDE_PRICING` lookup |
| `_extract_response_content` | `response` | `tuple[str, list[dict]]` | Split text content and tool-use blocks |

### `ToolsMixin`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register_tool` | `name, description, input_schema, handler` | `None` | Register or replace a tool definition and optional handler |
| `get_registered_tools` | -- | `list[dict]` | Return copy of registered tool definitions |
| `execute_tool_call` | `tool_name, tool_input` | `Any` | Dispatch to registered handler; raises `ClaudeError` on failure |
| `execute_with_tools` | `request, auto_execute=True, max_tool_rounds=10` | `AgentResponse` | Multi-round tool execution loop |

### `SessionMixin`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `execute_with_session` | `request, session=None, session_id=None` | `AgentResponse` | Execute with conversation history context |
| `create_session` | `session_id=None` | `AgentSession` | Create new conversation session |

### `FileOpsMixin`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `edit_file` | `file_path, instructions, language=None` | `dict` | AI-guided editing with auto language detection |
| `create_file` | `file_path, description, language="python"` | `dict` | Generate new file from natural-language description |

### `CodeIntelMixin`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `review_code` | `code, language, analysis_type` | `dict` | Code review returning issues and recommendations |
| `explain_code` | `code, language, detail_level` | `dict` | Explanation with summary, concepts, and full text |
| `generate_diff` | `original, modified, filename` | `dict` | Unified diff with addition/deletion counts |
| `suggest_tests` | `code, language, framework` | `dict` | Test generation with case descriptions |

### `SystemOpsMixin`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `scan_directory` | `path, max_depth, include_patterns, exclude_patterns` | `dict` | Recursive directory scan with filtering |
| `run_command` | `command, cwd, timeout, capture_output` | `dict` | Shell command execution with timeout |
| `get_project_structure` | `path, max_depth, include_analysis` | `dict` | Directory scan plus language breakdown and optional AI analysis |

## Dependencies

- **Internal**: `codomyrmex.agents.core` (AgentRequest, AgentResponse, AgentSession, SessionManager, ClaudeError), `codomyrmex.logging_monitoring`
- **External**: `anthropic` (optional import; `None` if not installed), `difflib` (stdlib)

## Constraints

- `ExecutionMixin` retries only on `RateLimitError` and server errors (500, 502, 503, 529); all other API errors propagate immediately.
- `ToolsMixin` caps tool execution at `max_tool_rounds` to prevent infinite loops; raises `ClaudeError` if exceeded.
- `FileOpsMixin.edit_file` reads files with UTF-8 encoding; binary files will fail with an explicit error dict (not an exception).
- `SystemOpsMixin.run_command` uses `shell=True` intentionally as an agent shell executor -- this is documented and expected.
- Zero-mock: real API calls only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `ClaudeError` raised on API failures, tool dispatch failures, and max-retry exhaustion.
- `_handle_retryable_error` logs warning per retry attempt with delay and error details.
- All errors logged before propagation via structured `logging_monitoring` loggers.
