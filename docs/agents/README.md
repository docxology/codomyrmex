# Agent Documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Agent rules, coordination directives, and governance for autonomous agents operating within the Codomyrmex ecosystem. This directory defines how AI agents should interact with, modify, and reason about the codebase.

## Contents

| File | Description |
|------|-------------|
| [rules/](rules/) | General agent rules and behavioral guidelines |
| [rules/general.md](rules/general.md) | Core agent operating rules |

## Principles

- **Functional Integrity**: All agent-generated code must be fully operational and production-ready
- **Zero-Mock Policy**: Agents must ensure all tests run against real logic, never mocks
- **RASP Compliance**: Agents must maintain README.md, AGENTS.md, SPEC.md, and PAI.md in every directory
- **Documentation Sync**: Agents must keep documentation synchronized with actual code capabilities

## Related Documentation

- [Main AGENTS.md](../AGENTS.md) — Docs-level agent coordination
- [Root AGENTS.md](../../AGENTS.md) — Project-level agent coordination
- [Skills Documentation](../skills/) — Skill system for agents

## Navigation

- **Parent**: [docs/](../README.md)
- **Root**: [Project Root](../../README.md)
