# Paperclip Agent — Agent Coordination

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Agent coordination document for the `paperclip/` submodule within `agents/`. Defines operating contracts for AI agents interacting with the Paperclip zero-human company orchestration platform.

## Module Structure

| File | Role |
| :--- | :--- |
| `paperclip_client.py` | CLI client — wraps `paperclipai` binary |
| `paperclip_api_client.py` | REST API client — stdlib `urllib.request` |
| `paperclip_integration.py` | Codomyrmex integration adapter |
| `mcp_tools.py` | MCP tool definitions (5 tools) |

## Key Classes

- `PaperclipClient(CLIAgentBase)`: CLI agent for heartbeat, doctor, onboard, configure, company/agent/issue operations.
- `PaperclipAPIClient`: HTTP client for health, companies, agents, issues, approvals, activity, dashboard.
- `PaperclipIntegrationAdapter(AgentIntegrationAdapter)`: Bridges Paperclip into code editing, LLM, and execution modules.

## MCP Tools

| Tool | Category | Description |
| :--- | :--- | :--- |
| `paperclip_execute` | paperclip | Execute heartbeat run |
| `paperclip_list_companies` | paperclip | List companies via REST API |
| `paperclip_create_issue` | paperclip | Create issue via REST API |
| `paperclip_trigger_heartbeat` | paperclip | Trigger heartbeat via REST API |
| `paperclip_doctor` | paperclip | Run CLI diagnostics |

## Operating Contracts

1. **Zero-Mock Policy**: All tests use real CLI/API when available; skip when unavailable.
2. **Config-Driven**: All behavior configured via `paperclip_*` config keys.
3. **Error Handling**: All errors raise `PaperclipError(AgentError)`.
4. **Logging**: Uses `codomyrmex.logging_monitoring.get_logger`.

## Dependencies

- `codomyrmex.agents.core` — Base classes, exceptions
- `codomyrmex.agents.generic` — `CLIAgentBase`
- `codomyrmex.logging_monitoring` — Structured logging

## Signposting

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [../AGENTS.md](../AGENTS.md)
- **README**: [README.md](README.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **PAI**: [PAI.md](PAI.md)
