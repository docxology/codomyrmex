# Codomyrmex Agents — src/codomyrmex/agents/claude

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Anthropic Claude-based agent implementation for AI-assisted coding with advanced reasoning and Claude Code agentic capabilities.

## Active Components

| File | Description |
|------|-------------|
| `__init__.py` | Public API exports (`ClaudeClient`, `ClaudeIntegrationAdapter`) |
| `claude_client.py` | Full-featured API client (1595 lines) |
| `claude_integration.py` | Codomyrmex module adapters (468 lines) |
| `API_SPECIFICATION.md` | Complete API reference |
| `MCP_TOOL_SPECIFICATION.md` | Model Context Protocol tools |

## Method Inventory

### ClaudeClient (claude_client.py)

| Method | Lines | Description |
|--------|-------|-------------|
| `execute(request)` | Inherited | Main execution entry point |
| `stream(request)` | 372-445 | Streaming response generator |
| `register_tool()` | 124-154 | Register tool for function calling |
| `execute_tool_call()` | 607-638 | Execute registered tool handler |
| `execute_with_tools()` | 640-740 | Automatic tool execution loop |
| `execute_with_session()` | 544-590 | Multi-turn conversation |
| `create_session()` | 592-603 | Create conversation session |
| `edit_file()` | (new) | AI-guided file editing |
| `create_file()` | (new) | Generate new file from description |
| `review_code()` | (new) | Code review with suggestions |
| `scan_directory()` | (new) | Scan project structure for context |
| `generate_diff()` | (new) | Generate unified diff output |

### ClaudeIntegrationAdapter (claude_integration.py)

| Method | Lines | Description |
|--------|-------|-------------|
| `adapt_for_ai_code_editing()` | 47-143 | Code generation with style hints |
| `adapt_for_ai_code_editing_stream()` | 145-174 | Streaming code generation |
| `adapt_for_llm()` | 176-243 | OpenAI-compatible message format |
| `adapt_for_code_execution()` | 245-318 | Security/bug/performance analysis |
| `adapt_for_code_refactoring()` | 320-373 | Refactoring with instructions |

## Operating Contracts

1. **API Key Management**: Use `ANTHROPIC_API_KEY` env var or config dict
2. **Error Handling**: All methods wrap API errors in `ClaudeError`
3. **Logging**: Use `logging_monitoring.get_logger()` for structured logs
4. **Cost Tracking**: Methods return `cost_usd` in metadata
5. **Retry Logic**: Exponential backoff with jitter for transient failures
6. **MCP Compliance**: Maintain Model Context Protocol interfaces for sibling agents

## Related Components

- **ClaudeTaskMaster**: [`../ai_code_editing/claude_task_master.py`](../ai_code_editing/claude_task_master.py) - Advanced task orchestration (815 lines)
- **Core Agents**: [`../core/`](../core/) - Base classes and session management
- **Generic Agent**: [`../generic/api_agent_base.py`](../generic/api_agent_base.py) - API agent base class

## Navigation Links

- **� README**: [README.md](README.md) - Human documentation
- **📋 SPEC**: [SPEC.md](SPEC.md) - Technical specification  
- **🔧 API**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - API reference
- **📡 MCP**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) - MCP tools
- **📁 Parent**: [agents](../README.md) - Parent directory
- **🏠 Root**: [../../../../README.md](../../../../README.md) - Project root
