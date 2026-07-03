# AGENTS.md — docs/modules/agents/open_gauss

**Version**: v1.3.0 | **Status**: Mirror Stub | **Last Updated**: July 2026

> Technical reference for AI agents working in this directory.

## Purpose
Documentation module mirror for `codomyrmex.agents.open_gauss` — navigation entry and operating notes for agents and contributors working on the open_gauss agent subpackage.

## Source of Truth
All implementation details live in the source package:
- Implementation: [`src/codomyrmex/agents/open_gauss/`](../../../../src/codomyrmex/agents/open_gauss/)
- Mirror README: [README.md](README.md)
- Mirror SPEC: [SPEC.md](SPEC.md)

## Module Summary
`codomyrmex.agents.open_gauss` is the embedded gauss-agent — a full-featured AI coding and task agent with 90+ tools, persistent memory, multi-platform messaging gateway (Telegram, Discord, WhatsApp, Slack, Signal), ACP IDE integration, cron scheduling, RL training environments (Atropos), and a data-driven CLI skin/theme engine.

## Subpackages
| Subpackage | Purpose |
|-----------|---------|
| `acp_adapter/` | ACP server exposing Gauss to IDE integrations |
| `agent/` | Internals extracted from `run_agent.py` |
| `acp_registry/` | ACP manifest and icon |
| `cron/` | Cron job scheduling |
| `environments/` | Atropos RL training environments |
| `gateway/` | Multi-platform messaging gateway |
| `gauss_cli/` | Unified `gauss` CLI |
| `optional-skills/` | Optional skills not activated by default |
| `scripts/` | Maintenance and release utilities |
| `skills/` | Bundled skills |
| `tests/` | Full pytest suite (~3000 tests) |
| `tools/` | Tool registry and 38+ tool implementations |

## Key Files

- `src/codomyrmex/agents/open_gauss/__init__.py` — Public module API.
- `src/codomyrmex/agents/open_gauss/run_agent.py` — Main agent entry point.
- `src/codomyrmex/agents/open_gauss/tools/` — Tool registry and implementations.

## Dependencies

- `logging_monitoring` — Structured logging.
- `model_context_protocol` — MCP interfaces.
- `environment_setup` — Dependency validation.

## Development Guidelines

- Keep tool definitions in `tools/` and register them via the tool registry.
- Use the gateway abstraction for all messaging platform integrations.
- Never hardcode platform-specific credentials; use environment variables.

## Navigation
- **Parent Directory**: [agents](../README.md)
- **README**: [README.md](README.md)
- **Specification**: [SPEC.md](SPEC.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
