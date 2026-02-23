# Personal AI Infrastructure — CLI Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The CLI module provides the unified command-line interface for all codomyrmex operations. It aggregates CLI commands from all modules into a single `codomyrmex` CLI with subcommands for each capability domain.

## PAI Capabilities

- Unified CLI entry point for all codomyrmex operations
- Module auto-discovery of CLI commands via `cli_commands()` convention
- Rich formatting with progress bars and color output
- Interactive prompts for guided workflows
- Shell completion generation

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| CLI app | Various | Main CLI application and subcommand routing |

## PAI Algorithm Phase Mapping

| Phase | CLI Contribution |
|-------|-------------------|
| **OBSERVE** | CLI provides human-readable system status and inspection |
| **EXECUTE** | CLI commands execute module operations from terminal |

## Architecture Role

**Interface Layer** — Top-level user interaction. Aggregates `cli_commands()` from all modules. No MCP tools — CLI operates through direct terminal I/O.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
