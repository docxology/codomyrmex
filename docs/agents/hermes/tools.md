# Hermes Tools System

**Version**: v0.2.0 | **Last Updated**: March 2026

## Overview

Hermes provides a rich set of built-in tools organized into categories. Tools are self-registering implementations managed by a central registry, and can be extended via MCP servers.

## Toolsets Configuration

```yaml
toolsets:
  - all          # enable everything
```

Available toolset presets:
- `all` — all tool categories enabled
- Individual categories can be specified for restricted access

## Tool Categories

| Category | Key Tools | Description |
|:---|:---|:---|
| **Terminal** | `terminal_tool.py` | Execute shell commands via configurable backends (local, Docker, SSH, etc.) |
| **Browser** | `web_tools.py` | `web_search`, `web_extract` — browse, extract, and analyze web content |
| **File Operations** | `file_operations.py`, `file_tools.py` | Read, write, search, and patch files |
| **Code Execution** | `code_execution_tool.py` | Sandboxed Python code execution |
| **Memory** | `session_search_tool.py`, `memory_tool.py` | FTS5 cross-session recall and long-term storage |
| **Skills** | `skills_tool.py`, `skill_manager_tool.py` | Invoke, create, and manage reusable skills |
| **Delegation** | `delegate_tool.py` | Spawn isolated subagents for parallel work |
| **Cron** | `cronjob_tools.py` | Create and manage scheduled jobs |
| **Checkpoint** | `checkpoint_manager.py` | Save and restore conversation states |
| **Vision** | Part of `web_tools.py` | Image analysis and OCR |
| **TTS/Audio** | Voice tools | Text-to-speech and audio processing |

## Tool Registration

Tools auto-register in `tools/registry.py` on import:

```python
# Each tool module registers its schema and handler
registry.register(
    name="web_search",
    schema={...},          # JSON schema for parameters
    handler=web_search_fn  # callable
)
```

The LLM receives tool schemas as JSON in the `<tools>` section of the prompt. When the model returns a `<tool_call>`, the registry dispatches to the appropriate handler.

## Approval System

Dangerous operations (file writes, terminal commands) go through `approval.py`:

```
Tool Call → approval.py check
  ├── Auto-approved (safe operations)
  └── Requires approval (destructive operations)
      ├── Terminal: sudo, rm, etc.
      └── File: write to sensitive paths
```

In gateway mode (Telegram, etc.), approvals are sent as interactive messages to the user.

## MCP Integration

Hermes supports Model Context Protocol (MCP) servers for tool extension:

```yaml
# In config.yaml (if supported)
mcp_servers:
  - url: http://localhost:8080
    name: custom_tools
```

## Key Implementation Files

| File | Purpose |
|:---|:---|
| `tools/registry.py` | Central tool schema/handler registry |
| `model_tools.py` | Thin dispatch layer for tool execution |
| `tools/terminal_tool.py` | Terminal command execution |
| `tools/web_tools.py` | Web search and browsing |
| `tools/file_operations.py` | File system operations |
| `tools/code_execution_tool.py` | Sandboxed code execution |
| `tools/approval.py` | Safety approval system |

## Related Documents

- [Architecture](architecture.md) — Tool dispatch in agent loop
- [Skills](skills.md) — Skill-based tools
- [Configuration](configuration.md) — Toolset configuration
