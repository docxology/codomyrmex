# Pi Coding Agent — Agent Coordination

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Agent coordination document for the Pi coding agent integration within Codomyrmex. Pi is a minimal, extensible terminal coding harness that supports 15+ LLM providers via a unified CLI.

## Operating Contracts

### Dependencies

| Dependency | Type | Purpose |
| :--- | :--- | :--- |
| `pi` CLI | External (npm) | `@mariozechner/pi-coding-agent` v0.57+ |
| Node.js | Runtime | Required for pi CLI execution |
| `model_context_protocol/` | Internal | MCP tool registration |

### Interface

- **RPC**: JSONL over stdin/stdout (`pi --mode rpc`)
- **Print**: `pi -p <message>` for one-shot queries
- **SDK**: TypeScript API via `createAgentSession()`

### Capabilities

| MCP Tool | Description |
| :--- | :--- |
| `pi_status` | Check pi installation and version |
| `pi_prompt` | Execute a one-shot prompt |
| `pi_list_models` | List available models |
| `pi_start_rpc` | Start an RPC session |
| `pi_install_package` | Install pi packages |
| `pi_list_packages` | List installed packages |

## Signposting

- **Parent**: [agents/AGENTS.md](../AGENTS.md)
- **Siblings**: [claude/](../claude/), [codex/](../codex/), [hermes/](../hermes/), [mission_control/](../mission_control/)
- **Upstream**: [github.com/badlogic/pi-mono](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent)
