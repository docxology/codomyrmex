# Hermes Tools System

**Version**: v0.4.0 | **Last Updated**: March 2026 (73-commit update + v0.4.0)

## Overview

Hermes provides a rich set of built-in tools organized into categories. Tools are self-registering implementations managed by a central registry, and can be extended via MCP servers.

## Toolsets Configuration

```yaml
toolsets:
    - all # enable everything
```

Available toolset presets:

- `all` — all tool categories enabled
- Individual categories can be specified for restricted access

## Tool Categories

| Category            | Key Tools                                  | Description                                                                 |
| :------------------ | :----------------------------------------- | :-------------------------------------------------------------------------- |
| **Terminal**        | `terminal_tool.py`                         | Execute shell commands via configurable backends (local, Docker, SSH, etc.) |
| **Browser**         | `web_tools.py`                             | `web_search`, `web_extract` — browse, extract, and analyze web content      |
| **File Operations** | `file_operations.py`, `file_tools.py`      | Read, write, search, and patch files                                        |
| **Code Execution**  | `code_execution_tool.py`                   | Sandboxed Python code execution                                             |
| **Memory**          | `session_search_tool.py`, `memory_tool.py` | FTS5 cross-session recall and long-term storage                             |
| **Skills**          | `skills_tool.py`, `skill_manager_tool.py`  | Invoke, create, and manage reusable skills                                  |
| **Delegation**      | `delegate_tool.py`                         | Spawn isolated subagents for parallel work                                  |
| **Cron**            | `cronjob_tools.py`                         | Create and manage scheduled jobs                                            |
| **Checkpoint**      | `checkpoint_manager.py`                    | Save and restore conversation states                                        |
| **Vision**          | Part of `web_tools.py`                     | Image analysis and OCR                                                      |
| **TTS/Audio**       | Voice tools                                | Text-to-speech and audio processing                                         |

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

```text
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

| File                           | Purpose                                |
| :----------------------------- | :------------------------------------- |
| `tools/registry.py`            | Central tool schema/handler registry   |
| `model_tools.py`               | Thin dispatch layer for tool execution |
| `tools/terminal_tool.py`       | Terminal command execution             |
| `tools/web_tools.py`           | Web search and browsing                |
| `tools/file_operations.py`     | File system operations                 |
| `tools/code_execution_tool.py` | Sandboxed code execution               |
| `tools/approval.py`            | Safety approval system                 |

## Codomyrmex MCP Tools (v1.5.x+)

Hermes is exposed to other agents through `@mcp_tool` decorated functions in
`src/codomyrmex/agents/hermes/mcp_tools.py`. As of March 2026 there are **48** such tools (verify with `rg '^@mcp_tool' mcp_tools.py` if the count drifts).

**Distinction**: Hermes’s runtime **tool** registry (`tools/registry.py`, categories above) is not the same as Codomyrmex’s **skill preload** registry (stable ids → `hermes chat -s` names). The latter is documented in [skills.md](skills.md).

These MCP tools bridge internal Hermes capabilities to the broader PAI ecosystem. Grouped samples below; knowledge codification, swarm orchestration, worktrees, vault, and task tools are summarized in [codomyrmex_integration.md](codomyrmex_integration.md).

### Session Management Tools

| Tool | Description |
| :--- | :---------- |
| `hermes_session_list` | List all session IDs |
| `hermes_session_stats` | DB stats: count, size, oldest/newest timestamps |
| `hermes_session_fork` | Fork a session into an independent child |
| `hermes_session_export_md` | Export a session as formatted Markdown |
| `hermes_session_detail` | Rich session detail: `message_count`, `has_system_prompt`, etc. |
| `hermes_session_clear` | Delete a session by ID |
| `hermes_session_search` | Substring search by session name |
| `hermes_set_system_prompt` | Upsert a persistent system message at position 0 |
| `hermes_prune_sessions` | Archive+delete sessions older than N days |
| `hermes_recall_memory` | FTS5 BM25-ranked full-text search across all sessions |

### Execution Tools

| Tool | Description |
| :--- | :---------- |
| `hermes_execute` | Single-turn prompt execution |
| `hermes_stream` | Streaming prompt execution |
| `hermes_chat_session` | Stateful multi-turn session |
| `hermes_batch_execute` | Submit a list of prompts; sequential or parallel |
| `hermes_sampling` | Server-initiated MCP sampling protocol |
| `hermes_run_coverage_loop` | Autonomous pytest heal-and-retry loop |

### Skill preload & validation

| Tool | Description |
| :--- | :---------- |
| `hermes_skills_list` | Wraps `hermes skills list` when the Hermes CLI is available |
| `hermes_skills_resolve` | Resolve registry skill ids to Hermes preload names and metadata |
| `hermes_skills_validate_registry` | Compare bundled/overlay registry entries to installed Hermes skills |

### Diagnostics & Utility Tools

| Tool | Description |
| :--- | :---------- |
| `hermes_status` | Backend availability check |
| `hermes_version` | CLI version string |
| `hermes_doctor` | Full `hermes doctor` output |
| `hermes_system_health` | CPU/RAM/Swap realtime metrics |
| `hermes_insights` | Usage analytics (token cost, tool patterns) |
| `hermes_provider_status` | Multi-provider credential status |
| `hermes_mcp_reload` | Hot-reload MCP server configuration |

### Script Orchestrations

```bash
# Batch execution from file
uv run python -m codomyrmex.agents.hermes.scripts.run_batch --file prompts.txt

# Session export (list all)
uv run python -m codomyrmex.agents.hermes.scripts.run_session_export --list

# Export specific session to markdown
uv run python -m codomyrmex.agents.hermes.scripts.run_session_export --session-id abc123

# Prune old sessions (dry run)
uv run python -m codomyrmex.agents.hermes.scripts.run_prune --days 30 --dry-run
```

## Related Documents

- [Architecture](architecture.md) — Tool dispatch in agent loop
- [Skills](skills.md) — Skill-based tools
- [Configuration](configuration.md) — Toolset configuration
- [Sessions](sessions.md) — Session management and storage
