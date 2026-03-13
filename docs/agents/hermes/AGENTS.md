# Hermes Agent Documentation — Agent Coordination

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Agent coordination document for the Hermes documentation subfolder. This directory contains modular documentation for the Hermes AI Agent (Nous Research), covering architecture, deployment, operations, and troubleshooting.

## Directory Contents

| File | Description |
|:---|:---|
| `README.md` | Documentation index and quick start |
| `architecture.md` | Core agent loop, gateway system, component overview |
| `configuration.md` | `config.yaml` structure, YAML pitfalls |
| `environment.md` | `.env` file, `HERMES_HOME`, API keys |
| `gateway.md` | Gateway daemon, platform adapters, message routing |
| `telegram.md` | Telegram bot setup, polling, 409 Conflict resolution |
| `multi_instance.md` | Multiple bots on one machine |
| `launchd.md` | macOS service management with launchd |
| `sessions.md` | Session lifecycle, `state.db`, compression |
| `skills.md` | Skills system, agentskills.io integration |
| `tools.md` | Tool registry, categories, MCP extension |
| `cron.md` | Scheduled jobs and proactive messaging |
| `troubleshooting.md` | Common issues and diagnostic procedures |
| `security.md` | API key hygiene, access control |
| `models.md` | Model selection, OpenRouter, reasoning effort |
| `personalities.md` | Custom persona definitions |

## Operating Contracts

- All content reflects **Hermes Agent v0.2.0** (2026.3.12)
- Documentation includes first-hand production learnings from Codomyrmex deployments
- Cross-references use relative links within the `hermes/` directory
- Content was enriched by Perplexity research and verified against running instances

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Root**: [AGENTS.md](../../../AGENTS.md)
