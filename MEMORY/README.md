# MEMORY

**Version**: v1.0.8 | **Last Updated**: March 2026

## Overview

This directory is the project-local persistent memory store for Codomyrmex agents. It follows the PAI memory hierarchy:

| Subdirectory | Purpose |
| :--- | :--- |
| `WORK/` | Active task workspaces and PRD documents |
| `STATE/` | Persistent state snapshots and session bridges |
| `LEARNING/` | Accumulated insights and error-fix records |

## Usage

Memory entries are created automatically by CogniLayer, the PAI session bridge, and agent workflows. They can also be created manually via:

```bash
codomyrmex memory add --type work --content "..."
```

## Signposting

- **Parent**: [README.md](../README.md) — Project root
- **Agentic Memory Module**: [src/codomyrmex/agentic_memory/](../src/codomyrmex/agentic_memory/) — Programmatic memory API
- **PAI Bridge**: [PAI.md](../PAI.md) — PAI system integration
