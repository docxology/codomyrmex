# Qwen Agent — Agent Coordination

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Agent guidelines for the `codomyrmex.agents.qwen` module.

## Agent-Accessible Resources

| Resource | Path | Description |
|----------|------|-------------|
| QwenClient | `qwen_client.py` | DashScope API client with tool calling |
| Agent Wrapper | `qwen_agent_wrapper.py` | Native qwen-agent framework |
| MCP Tools | `mcp_tools.py` | 5 MCP tools for AI consumption |
| Model Registry | `qwen_client.QWEN_MODELS` | 14 model variants |

## Key Capabilities

1. **Chat**: Single/multi-turn via `qwen_chat` MCP tool
2. **Tool Calling**: `chat_with_tools()` for function calling loops
3. **Code Review**: `qwen_code_review` with language/focus targeting
4. **Agent Framework**: Create qwen-agent Assistants with MCP servers
5. **Streaming**: Both DashScope and qwen-agent streaming

## Agent Guidelines

- Use `DASHSCOPE_API_KEY` or `QWEN_API_KEY` for authentication
- Default model is `qwen-coder-turbo` (code-specialized)
- For reasoning tasks, prefer `qwen3-max`
- For long documents, use `qwen-long` (1M context)
- For vision tasks, use `qwen-vl-max`

## Zero-Mock Compliance

All tests use real client construction (guarded by API key availability).
No mocks or stubs.

## Navigation

- **README**: [README.md](README.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **PAI**: [PAI.md](PAI.md)
- **Parent**: [agents/](../README.md)
