# Hermes Agent Documentation

**Version**: v0.3.0 | **Status**: Active | **Last Updated**: March 2026 (73-commit update)

> **Official Docs**: [hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)
> **GitHub**: [github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)

## Overview

Hermes 3.0 is an open-source, self-improving AI agent developed by [Nous Research](https://nousresearch.com). It features autonomous skill creation, cross-session memory recall, multi-platform messaging gateways (Telegram, WhatsApp, Discord, Slack), and flexible model routing through OpenRouter, Nous Portal, or direct providers. Hermes 3.0 brings advanced reasoning, agentic autonomy, multi-turn interactions and 40+ built-in tools.

This documentation suite captures architecture, operational patterns, troubleshooting, and first-hand deployment learnings from running Hermes in production at Codomyrmex.

## Documentation Index

### Getting Started

| Document                             | Description                                                                |
| :----------------------------------- | :------------------------------------------------------------------------- |
| [setup_guide.md](setup_guide.md)     | **Complete new-instance setup** — installation, config, gateway, multi-bot |
| [cli_reference.md](cli_reference.md) | All CLI commands and slash commands (from official docs)                   |

### Architecture & Configuration

| Document                                               | Description                                                                  |
| :----------------------------------------------------- | :--------------------------------------------------------------------------- |
| [architecture.md](architecture.md)                     | Core agent loop, components, LLM provider backends                           |
| [copilot_acp.md](copilot_acp.md)                       | **GitHub Copilot ACP backend** — free GPT-4o via Copilot subscription        |
| [codomyrmex_integration.md](codomyrmex_integration.md) | **Deep dive into Codomyrmex bidirectional interfaces and MCP augmentations** |
| [configuration.md](configuration.md)                   | `config.yaml` structure, YAML pitfalls, precedence                           |
| [environment.md](environment.md)                       | `.env` file, `HERMES_HOME`, API key management                               |
| [models.md](models.md)                                 | Model selection, OpenRouter, provider config, rate limits                    |
| [personalities.md](personalities.md)                   | Personality system and custom personas                                       |

### Platform Integration

| Document                               | Description                                        |
| :------------------------------------- | :------------------------------------------------- |
| [gateway.md](gateway.md)               | Gateway system, platform adapters, message routing |
| [telegram.md](telegram.md)             | Telegram bot setup, polling, troubleshooting       |
| [launchd.md](launchd.md)               | macOS launchd service management                   |
| [multi_instance.md](multi_instance.md) | Running multiple Hermes bots on one machine        |

### Agent Capabilities

| Document                   | Description                                      |
| :------------------------- | :----------------------------------------------- |
| [sessions.md](sessions.md) | Session lifecycle, `state.db`, FTS5, compression |
| [skills.md](skills.md)     | Skills system, self-improvement, agentskills.io  |
| [tools.md](tools.md)       | Tool registry, categories, MCP integration       |
| [cron.md](cron.md)         | Scheduled jobs, cron ticker, proactive messaging |

### Operations

| Document                                 | Description                                    |
| :--------------------------------------- | :--------------------------------------------- |
| [troubleshooting.md](troubleshooting.md) | 9 common issue patterns with diagnosis & fixes |
| [security.md](security.md)               | API key hygiene, access control, hardening     |

## Quick Start

```bash
# Install (via official installer)
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
source ~/.zshrc

# Configure provider
hermes model

# (Optional) Use GitHub Copilot as backend (free with subscription)
hermes copilot login

# Run interactive chat
hermes

# Check health
hermes doctor

# Start gateway (Telegram/WhatsApp/Discord)
hermes gateway setup
hermes gateway run
```

## Key Concepts

- **Gateway**: Unified daemon routing messages from Telegram, WhatsApp, Discord, Slack
- **HERMES_HOME**: Environment variable controlling config/data directory (default: `~/.hermes/`)
- **Skills**: Self-improving modules compatible with [agentskills.io](https://agentskills.io)
- **Sessions**: Persistent conversation state with FTS5-indexed SQLite and LLM summarization
- **Terminal Backends**: 6 execution environments — local, Docker, SSH, Daytona, Singularity, Modal
- **Honcho**: Dialectic user modeling for personalized interactions
- **Smart Routing**: Auto-routes simple messages to cheap model; complex tasks to strong model
- **Copilot ACP**: GitHub Copilot as an LLM backend (free with GitHub subscription) via `copilot --acp --stdio`
- **Pairing**: Dynamic user access management without gateway restart

## Codomyrmex Scripts

Thin orchestrator scripts in [`scripts/agents/hermes/`](../../../scripts/agents/hermes/):

| Script                      | Purpose                                            |
| :-------------------------- | :------------------------------------------------- |
| `new_instance.py`           | **Create and configure new Hermes instances**      |
| `setup_hermes.py`           | Validate environment, config, and backends         |
| `run_hermes.py`             | Send prompt, get response (CLI or Ollama fallback) |
| `dispatch_hermes.py`        | Sweep-and-dispatch improvement orchestrator        |
| `observe_hermes.py`         | Session observability and telemetry viewer         |
| `evaluate_orchestrators.py` | Evaluate scripts against thin orchestrator pattern |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source Module**: [src/codomyrmex/agents/hermes/](../../../src/codomyrmex/agents/hermes/)
- **Project Root**: [README.md](../../../README.md)
