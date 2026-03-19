# getting-started - Functional Specification

**Version**: v1.2.3 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provide comprehensive onboarding documentation for Codomyrmex users, covering installation, environment setup, agent operations, and guided tutorials.

## Scope

### In Scope

- Quick start (5-minute path to first run)
- Full installation and `uv` environment setup
- Agent deployment and orchestration guide
- Tutorial series (modules, PAI, MCP tools, testing)
- CLI doctor diagnostics

### Out of Scope

- Module-specific API reference (see `docs/reference/`)
- Production deployment (see `docs/deployment/`)
- Security policies (see `docs/security/`)

## Components

| Component | File | Status |
|-----------|------|--------|
| Quick Start | `quickstart.md` | Active |
| Setup Guide | `setup.md` | Active |
| Agent Operations | `GETTING_STARTED_WITH_AGENTS.md` | Active (v1.2.3) |
| Tutorial Index | `tutorials/README.md` | Active (8 tutorials) |
| Installation Redirect | `installation.md` | Legacy redirect → `setup.md` |
| Full Setup | `full-setup.md` | Active |

## Success Criteria

1. User can install Codomyrmex in < 5 minutes following quickstart
2. User can run diagnostics (`doctor --all`) successfully
3. User understands agent architecture from GETTING_STARTED_WITH_AGENTS
4. All code examples are runnable and functional
5. No broken internal links

## Navigation

- **Parent**: [README.md](README.md)
- **Root**: [Project Root](../../README.md)
