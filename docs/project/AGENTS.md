# Codomyrmex Agents — docs/project

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Project-level documentation for architecture, contributing guidelines, and project governance.

## Active Components

| File | Priority | Description |
|------|----------|-------------|
| [architecture.md](architecture.md) | **Critical** | System architecture and design |
| [contributing.md](contributing.md) | **Critical** | Contribution guidelines |

## Agent Guidelines

### Project Documentation Standards

1. **Architecture**: Keep architecture docs in sync with code structure
2. **Contributing**: Ensure contribution guides are accurate and welcoming
3. **RASP Compliance**: Every directory maintains README, AGENTS, SPEC, PAI

### When Modifying Project Docs

- Update architecture diagrams when structure changes
- Verify contributing steps work for new contributors
- Keep module count references at 104 (or update if modules are added/removed)

### Key Architectural Components

- **Layered Architecture**: Foundation → Core → Service → Application
- **Module System**: 104 independent, composable modules
- **Secure Cognitive Layer**: Identity, Wallet, Defense, Market, Privacy

## Operating Contracts

- Maintain alignment between project docs and codebase reality
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Record outcomes in shared telemetry when necessary

## Navigation Links

- **📁 Parent Directory**: [docs/](../README.md)
- **🏠 Project Root**: [../../README.md](../../README.md)
- **📦 Related**: [Getting Started](../getting-started/) | [Development](../development/)
