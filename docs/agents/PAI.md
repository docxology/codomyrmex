# Agent Documentation — Personal AI Infrastructure

**Version**: v1.2.3 | **Status**: Active | **Last Updated**: March 2026

## Overview

PAI agents operating within the Codomyrmex ecosystem integrate through the agent documentation here. This directory governs **38 AI agent frameworks** spanning CLI-based, API-based, local, and infrastructure agents.

## AI Capabilities

1. **Behavioral guidelines** — Core operating rules for all AI agents (see `rules/`)
2. **Coordination patterns** — How 38 agents collaborate within and across modules
3. **Quality enforcement** — Zero-Mock policy and functional integrity across all agent integrations
4. **Multi-agent orchestration** — Pooling, load balancing, and mission control

## Agent-PAI Integration Points

| Integration | Agent Module | Purpose |
|:---|:---|:---|
| Dashboard coordination | [pai/](pai/) | Admin :8787 + PM :8888 dual-interface |
| WebSocket push | [pai/](pai/) | Real-time updates via :8890 |
| Agent observability | [history/](history/) | Audit logs, replay, telemetry |
| Task management | [droid/](droid/) | Priority queues, cross-agent tasks |
| Memory systems | [memory/](memory/) | Vector recall, episodic storage |
| Agent pooling | [pooling/](pooling/) | Load balancing, circuit breakers |

## Key Agents with PAI Deep Integration

- **Hermes** — [hermes/](hermes/) — 21 modular docs; MCP can preload CLI skills (`hermes_skill` / `hermes_skills`) for packs such as [PrediHermes](https://github.com/nativ3ai/hermes-geopolitical-market-sim); see [skills.md](hermes/skills.md#codomyrmex-mcp-preloading-skills)
- **Claude** — [claude/](claude/) — Anthropic integration with advanced reasoning
- **Gemini** — [gemini/](gemini/) — Google CLI with file operations and session management
- **Jules** — [jules/](jules/) — Swarm orchestration (113+ concurrent sessions)
- **Mission Control** — [mission_control/](mission_control/) — Multi-agent mission coordination

## Related PAI Documentation

- [docs/PAI.md](../PAI.md) — Documentation-level PAI index
- [docs/PAI_DASHBOARD.md](../PAI_DASHBOARD.md) — Dashboard functionality matrix
- [Root PAI.md](../../PAI.md) — Project-level PAI bridge
- [docs/pai/](../pai/) — Detailed PAI-Codomyrmex reference
- [src/codomyrmex/agents/pai/](../../src/codomyrmex/agents/pai/) — PAI source module
