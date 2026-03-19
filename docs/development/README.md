# Development Guide

**Version**: v1.2.3 | **Status**: Active | **Last Updated**: March 2026

## Overview

Developer-facing documentation covering environment setup, testing strategy, coding standards, multi-agent Git workflows, uv package management, and Cursor ↔ Codomyrmex wiring.

## Contents

| Document | Description |
|:---|:---|
| [cursor-integration.md](cursor-integration.md) | Cursor editor rules, MCP tools (`ide_cursor_*`), `CODOMYRMEX_CURSOR_WORKSPACE` |
| [cursor-mcp.json.example](cursor-mcp.json.example) | Example `~/.cursor/mcp.json` for full PAI MCP stdio server |
| [cursor-mcp-troubleshooting.md](cursor-mcp-troubleshooting.md) | `ENOENT` / PATH issues for `uv`, `codex`, extension MCP servers |
| [documentation.md](documentation.md) | Documentation standards, AGENTS/README/SPEC parity |
| [environment-setup.md](environment-setup.md) | Development environment prerequisites and configuration |
| [google-integration.md](google-integration.md) | Google Cloud and Workspace integration for development |
| [multi-agent-git.md](multi-agent-git.md) | Git workflows for concurrent multi-agent development |
| [testing-strategy.md](testing-strategy.md) | Zero-Mock testing philosophy, coverage targets (≥35%), test organization |
| [uv-usage-guide.md](uv-usage-guide.md) | uv package manager usage for Python dependency management |

## Coordination

- [AGENTS.md](AGENTS.md) — Agent coordination for this section
- [SPEC.md](SPEC.md) — Functional specification
- [PAI.md](PAI.md) — PAI infrastructure integration

## Navigation

- **Parent**: [docs/](../README.md)
- **Project Root**: [README.md](../../README.md)
