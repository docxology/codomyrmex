# Codomyrmex Agents — docs/getting-started

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Purpose

User onboarding documentation. Covers installation, quick start, environment setup, and step-by-step tutorials for new users.

## Active Components

| File | Priority | Description |
|------|----------|-------------|
| [quickstart.md](quickstart.md) | **Critical** | 5-minute quick start |
| [installation.md](installation.md) | **Critical** | Complete installation guide |
| [setup.md](setup.md) | High | Environment configuration |
| [tutorials/](tutorials/) | High | Step-by-step learning |
| [README.md](README.md) | Medium | Directory overview |
| [SPEC.md](SPEC.md) | Medium | Functional specification |

## Agent Guidelines

### Onboarding Quality Standards

1. **Accuracy**: Installation commands must work on fresh systems
2. **Clarity**: Write for users new to the platform
3. **Speed**: Quick start should complete in <5 minutes
4. **Completeness**: Cover all supported platforms

### When Modifying Getting Started Docs

- Test installation on Mac, Linux, and Windows (WSL)
- Update uv/pip commands when versions change
- Verify all quick start examples are runnable
- Keep tutorials relevant to current module APIs

### User Journey

1. **Quick Start**: First successful interaction
2. **Installation**: Complete environment setup
3. **Configuration**: API keys, preferences
4. **Tutorials**: Deeper learning paths

## Operating Contracts

- Maintain alignment between docs and installation scripts
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Record outcomes in shared telemetry and update TODO queues when necessary

## Navigation Links

- **📁 Parent Directory**: [docs/](../README.md)
- **🏠 Project Root**: [../../README.md](../../README.md)
- **📦 Related**: [Examples](../examples/) | [API Reference](../reference/api.md)
