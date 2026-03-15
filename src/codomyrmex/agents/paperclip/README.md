# Paperclip

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Integrates [Paperclip](https://github.com/paperclipai/paperclip) — an open-source Node.js platform for orchestrating zero-human companies — into the Codomyrmex agent subsystem. Paperclip manages AI agent teams with org charts, budgets, governance, heartbeats, and goal alignment.

## Capabilities

- **CLI Client** (`PaperclipClient`): Wraps the `paperclipai` CLI for heartbeat runs, doctor diagnostics, onboarding, configuration, company/agent/issue management.
- **REST API Client** (`PaperclipAPIClient`): HTTP client for the Paperclip server at `localhost:3100` — companies, agents, issues, approvals, activity, dashboard.
- **Integration Adapter** (`PaperclipIntegrationAdapter`): Bridges Paperclip into Codomyrmex's code editing, LLM, and execution modules.
- **MCP Tools**: 5 tools (`paperclip_execute`, `paperclip_list_companies`, `paperclip_create_issue`, `paperclip_trigger_heartbeat`, `paperclip_doctor`).

## Prerequisites

```bash
npx paperclipai onboard --yes   # CLI setup
# or
npm install -g paperclipai
```

Server runs at `http://localhost:3100` with embedded PostgreSQL.

## Directory Contents

| File | Purpose |
| :--- | :--- |
| `__init__.py` | Public exports |
| `paperclip_client.py` | CLI client (`CLIAgentBase`) |
| `paperclip_api_client.py` | REST API client (stdlib `urllib`) |
| `paperclip_integration.py` | Codomyrmex integration adapter |
| `mcp_tools.py` | MCP tool definitions |
| `py.typed` | PEP 561 marker |

## Navigation

- **Parent**: [agents/](../README.md)
- **Spec**: [SPEC.md](SPEC.md)
- **Agent Coordination**: [AGENTS.md](AGENTS.md)
- **PAI Bridge**: [PAI.md](PAI.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
