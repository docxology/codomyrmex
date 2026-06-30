# AGENTS.md — docs/modules/agents/open_gauss

> Technical reference for AI agents working in this directory.

## Purpose
Documentation module mirror for `codomyrmex.agents.open_gauss` — navigation entry and operating notes for agents and contributors working on the open_gauss agent subpackage.

## Source of Truth
All implementation details live in the source package:
- Implementation: [`src/codomyrmex/agents/open_gauss/`](../../../../src/codomyrmex/agents/open_gauss/)
- Source AGENTS.md: [`src/codomyrmex/agents/open_gauss/AGENTS.md`](../../../../src/codomyrmex/agents/open_gauss/AGENTS.md)
- Source README: [`src/codomyrmex/agents/open_gauss/README.md`](../../../../src/codomyrmex/agents/open_gauss/README.md)

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

## Navigation
- **Parent Directory**: [agents](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
