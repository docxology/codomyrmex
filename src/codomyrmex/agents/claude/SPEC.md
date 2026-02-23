# claude - Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

The `claude` submodule provides comprehensive integration with Anthropic's Claude API for AI-assisted coding. Includes full-featured API client, integration adapters, and Claude Code capabilities for agentic coding workflows.

## Core Capabilities

### API Integration

- **ClaudeClient**: Full-featured API client with retry logic, tool use, and session management
- **ClaudeIntegrationAdapter**: Bridges Claude with Codomyrmex modules (code editing, LLM, execution)
- **ClaudeTaskMaster**: Advanced task orchestration (see `ai_code_editing/claude_task_master.py`)

### Claude Code Features

- **File Operations**: `edit_file()`, `create_file()`, `review_code()`
- **Project Context**: `scan_directory()`, `get_project_structure()`
- **Diff Generation**: `generate_diff()`, unified patch output
- **Task Orchestration**: Decomposition, analysis, workflow planning

### Supported Models

| Model | Input $/1M | Output $/1M |
|-------|-----------|-------------|
| claude-sonnet-4-20250514 | $3.00 | $15.00 |
| claude-3-5-sonnet-20241022 | $3.00 | $15.00 |
| claude-3-5-haiku-20241022 | $1.00 | $5.00 |
| claude-3-opus-20240229 | $15.00 | $75.00 |
| claude-opus-4-5-20251101 | $15.00 | $75.00 |

## Method Inventory

### ClaudeClient Methods

| Method | Description |
|--------|-------------|
| `execute(request)` | Execute API request with retry |
| `stream(request)` | Stream response chunks |
| `register_tool(name, desc, schema, handler)` | Register tool for function calling |
| `execute_with_tools(request)` | Auto-execute tool calls |
| `execute_with_session(request, session)` | Multi-turn conversation |
| `create_session()` | Create conversation session |
| `edit_file(path, instructions)` | AI-guided file editing |
| `create_file(path, description)` | Generate new file |
| `review_code(code, language)` | Code review with suggestions |
| `scan_directory(path)` | Scan project structure |
| `generate_diff(original, modified)` | Generate unified diff |

### ClaudeIntegrationAdapter Methods

| Method | Description |
|--------|-------------|
| `adapt_for_ai_code_editing(prompt, language)` | Code generation |
| `adapt_for_llm(messages, model)` | OpenAI-compatible interface |
| `adapt_for_code_execution(code, analysis_type)` | Security/bug/performance analysis |
| `adapt_for_code_refactoring(code, instruction)` | Refactoring operations |

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Agent Documentation**: [AGENTS.md](AGENTS.md)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Parent SPEC**: [../SPEC.md](../SPEC.md)
- **Related**: [ClaudeTaskMaster](../ai_code_editing/claude_task_master.py)

## Design Principles

1. **Strict Modularity**: Components isolated with well-defined APIs
2. **Production-Ready Retry Logic**: Exponential backoff with jitter for transient failures
3. **Cost Transparency**: Automatic cost calculation and tracking
4. **Error Resilience**: Comprehensive exception handling
5. **Extensibility**: Tool registration for custom function calling

## Technical Implementation

The codebase utilizes Python 3.10+ features with type-safe APIs. Key patterns:

- **Lazy client initialization**: Anthropic client created on first use
- **Session management**: Multi-turn conversation context preservation
- **Tool execution loop**: Automatic tool call handling up to configurable max rounds
- **Vision support**: Image input via base64 encoding in messages
