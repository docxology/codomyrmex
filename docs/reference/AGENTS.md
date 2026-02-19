# Codomyrmex Agents — docs/reference

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Technical reference documentation for APIs, CLI, troubleshooting, and performance optimization. The authoritative source for implementation details.

## Active Components

| File | Priority | Description |
|------|----------|-------------|
| [api.md](api.md) | **Critical** | Complete API reference |
| [api-complete.md](api-complete.md) | **Critical** | Extended API documentation |
| [cli.md](cli.md) | **Critical** | CLI command reference |
| [troubleshooting.md](troubleshooting.md) | High | Common issues and solutions |
| [performance.md](performance.md) | High | Performance optimization |
| [security.md](security.md) | High | Security best practices |
| [migration-guide.md](migration-guide.md) | Medium | Version migration |
| [changelog.md](changelog.md) | Medium | Version history |
| [orchestrator.md](orchestrator.md) | Medium | Orchestrator reference |

## Agent Guidelines

### Reference Quality Standards

1. **Accuracy**: API docs must match actual function signatures
2. **Completeness**: Document all public APIs
3. **Currency**: Update immediately when APIs change
4. **Examples**: Include working code snippets

### When Modifying Reference Docs

- Generate API docs from docstrings when possible
- Verify all code examples are runnable
- Update changelog for version changes
- Keep troubleshooting current with reported issues

### API Categories to Maintain

- **Python Module APIs**: Direct imports and function calls
- **CLI APIs**: Command-line interface commands
- **MCP Tool APIs**: AI/LLM integration interfaces
- **Secure Cognitive APIs**: Identity, Wallet, Defense, Market, Privacy

## Operating Contracts

- Maintain alignment between reference docs and source code
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Record outcomes in shared telemetry and update TODO queues when necessary

## Navigation Links

- **📁 Parent Directory**: [docs/](../README.md)
- **🏠 Project Root**: [../../README.md](../../README.md)
- **📦 Related**: [Getting Started](../getting-started/) | [Modules](../modules/)
