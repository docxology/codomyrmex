# open_gauss — Documentation Module

**Version**: v1.3.0 | **Status**: Mirror Stub | **Last Updated**: July 2026

> Documentation mirror entry for the `codomyrmex.agents.open_gauss` subpackage.

## Overview
`open_gauss` is the embedded gauss-agent: a full-featured AI coding and task agent with 90+ tools, persistent memory, multi-platform messaging (Telegram, Discord, WhatsApp, Slack, Signal, Email, Home Assistant), ACP IDE integration (VS Code, Zed, JetBrains), cron scheduling, Atropos RL training environments, and a data-driven CLI skin engine. The source package lives under `src/codomyrmex/agents/open_gauss/`.

## Quick Links
- [Source implementation](../../../../src/codomyrmex/agents/open_gauss/)
- [Local SPEC.md](SPEC.md) — mirror contract and submodule boundary
- [Local AGENTS.md](AGENTS.md) — development reference for this docs mirror

## Key Subpackages
| Subpackage | Purpose |
|-----------|---------|
| `tools/` | Central registry and 38+ tool implementations |
| `gauss_cli/` | Unified `gauss` CLI (chat, gateway, setup, auth, skills) |
| `gateway/` | Multi-platform messaging gateway |
| `acp_adapter/` | ACP server for IDE integrations |
| `environments/` | Atropos RL training environments |
| `cron/` | Scheduled task execution |

## Navigation
- **Parent**: [agents](../README.md)
- **Specification**: [SPEC.md](SPEC.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
