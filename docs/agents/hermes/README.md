# Hermes Agent Documentation

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Hermes is an open-source, self-improving AI agent developed by [Nous Research](https://nousresearch.com). It features autonomous skill creation, cross-session memory recall, multi-platform messaging gateways, and flexible model routing through OpenRouter or direct providers.

This documentation suite captures architecture, operational patterns, troubleshooting, and first-hand deployment learnings from running Hermes in production at Codomyrmex.

## Documentation Index

| Document | Description |
|:---|:---|
| [architecture.md](architecture.md) | Core agent loop, gateway system, and component overview |
| [configuration.md](configuration.md) | `config.yaml` structure, YAML pitfalls, and best practices |
| [environment.md](environment.md) | `.env` file, `HERMES_HOME`, and API key management |
| [gateway.md](gateway.md) | Gateway system, platform adapters, and message routing |
| [telegram.md](telegram.md) | Telegram bot setup, polling, and troubleshooting |
| [multi_instance.md](multi_instance.md) | Running multiple Hermes bots on one machine |
| [launchd.md](launchd.md) | macOS launchd service management |
| [sessions.md](sessions.md) | Session lifecycle, `state.db`, and compression |
| [skills.md](skills.md) | Skills system, discovery, and community sharing |
| [tools.md](tools.md) | Tool registry, categories, and `toolsets` config |
| [cron.md](cron.md) | Scheduled jobs, cron ticker, and proactive messaging |
| [troubleshooting.md](troubleshooting.md) | Common issues, error patterns, and fixes |
| [security.md](security.md) | API key hygiene, access control, and hardening |
| [models.md](models.md) | Model selection, OpenRouter, and provider config |
| [personalities.md](personalities.md) | Personality system and custom persona definitions |

## Quick Start

```bash
# Install
pip install hermes-agent

# Setup
hermes setup

# Run interactive chat
hermes chat

# Start gateway (Telegram, WhatsApp, etc.)
hermes gateway run

# Check health
hermes doctor
```

## Key Concepts

- **Gateway**: Unified daemon that routes messages from Telegram, WhatsApp, Discord, and more
- **HERMES_HOME**: Environment variable controlling the config/data directory (default: `~/.hermes/`)
- **Skills**: Reusable, self-improving modules compatible with [agentskills.io](https://agentskills.io)
- **Sessions**: Persistent conversation state with FTS5-indexed SQLite and LLM summarization

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Codomyrmex Hermes Module**: [src/codomyrmex/agents/hermes/](../../../src/codomyrmex/agents/)
- **Project Root**: [README.md](../../../README.md)
