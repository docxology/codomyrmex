# Paperclip — Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

The `paperclip` module integrates the Paperclip zero-human company orchestration platform into Codomyrmex's agent subsystem. Paperclip is a Node.js server and React UI that orchestrates teams of AI agents with org charts, budgets, governance, and goal alignment.

## Design Principles

### Modularity

- **Dual-Client Architecture**: `PaperclipClient` (CLI via `CLIAgentBase`) and `PaperclipAPIClient` (REST via `urllib.request`).
- **Config Driven**: All behavior configurable via `paperclip_command`, `paperclip_timeout`, `paperclip_working_dir`, `paperclip_agent_id`, `paperclip_api_base`, `paperclip_config_path`.

### Functionality

- **Agent Heartbeat**: `paperclipai heartbeat run --agent-id <id>` — wake agent, check work, act.
- **Company Management**: List, create, and inspect companies.
- **Issue Tracking**: Create and list tickets/issues.
- **Approval Governance**: List, approve, and reject pending approvals.
- **Health Diagnostics**: `paperclipai doctor` with optional `--repair`.
- **Onboarding**: `paperclipai onboard --yes` for first-run setup.

## Functional Requirements

### Core Capabilities

1. **Execute**: Run agent heartbeat via `_execute_impl`.
2. **Stream**: Stream heartbeat output via `_stream_impl`.
3. **Doctor**: Health check via `run_doctor`.
4. **Onboard**: Setup via `onboard`.
5. **Configure**: Section configuration via `configure`.
6. **Company List**: List companies via `list_companies`.
7. **Agent List**: List agents via `list_agents`.
8. **Issue Create**: Create tickets via `create_issue`.
9. **Heartbeat**: Trigger heartbeat via `trigger_heartbeat`.
10. **API Client**: Full REST API coverage via `PaperclipAPIClient`.

## Interface Contracts

### Public API

- `PaperclipClient(config: dict)`: CLI client constructor.
- `PaperclipClient.execute(request: AgentRequest) -> AgentResponse`: Execute heartbeat.
- `PaperclipClient.stream(request: AgentRequest) -> Iterator[str]`: Stream output.
- `PaperclipAPIClient(base_url, api_key, timeout)`: REST API client constructor.
- `PaperclipIntegrationAdapter(agent)`: Integration adapter constructor.

### Dependencies

- `codomyrmex.agents.core`
- `codomyrmex.agents.generic`
- `codomyrmex.logging_monitoring`

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent**: [../SPEC.md](../SPEC.md)
