# Codomyrmex Agents — docs/project

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Project-level documentation for architecture, contributing, roadmap, and project management. Also contains documentation audit results and improvement tracking.

## Active Components

| File | Priority | Description |
|------|----------|-------------|
| [architecture.md](architecture.md) | **Critical** | System architecture |
| [contributing.md](contributing.md) | **Critical** | Contribution guidelines |
| [todo.md](todo.md) | High | Roadmap and todo items |
| [implementation-status.md](implementation-status.md) | High | Feature implementation status |
| [audit_results/](audit_results/) | Medium | Documentation audit results |
| [documentation-audit-report.md](documentation-audit-report.md) | Medium | Audit reports |

## Agent Guidelines

### Project Documentation Standards

1. **Architecture**: Keep architecture docs in sync with code structure
2. **Contributing**: Ensure contribution guides are accurate and welcoming
3. **Roadmap**: Update todo.md as features are completed
4. **Audits**: Record all documentation quality audits

### When Modifying Project Docs

- Update architecture diagrams when structure changes
- Verify contributing steps work for new contributors
- Mark completed items in todo.md
- Add new audit results to audit_results/

### Key Architectural Components

- **Layered Architecture**: Foundation → Core → Service → Application
- **Module System**: 80+ independent, composable modules
- **Secure Cognitive Layer**: Identity, Wallet, Defense, Market, Privacy

## Operating Contracts

- Maintain alignment between project docs and codebase reality
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Record outcomes in shared telemetry and update TODO queues when necessary

## Navigation Links

- **📁 Parent Directory**: [docs/](../README.md)
- **🏠 Project Root**: [../../README.md](../../README.md)
- **📦 Related**: [Getting Started](../getting-started/) | [Development](../development/)
