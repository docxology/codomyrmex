# Codomyrmex Agents — docs/development

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Development environment documentation and best practices for contributing to Codomyrmex. Covers environment setup, testing, documentation standards, and tooling.

## Active Components

| File | Priority | Description |
|------|----------|-------------|
| [environment-setup.md](environment-setup.md) | **Critical** | Complete dev environment setup |
| [testing-strategy.md](testing-strategy.md) | **Critical** | Testing patterns and requirements |
| [documentation.md](documentation.md) | High | Documentation standards |
| [uv-usage-guide.md](uv-usage-guide.md) | High | UV package manager guide |
| [README.md](README.md) | Medium | Directory overview |
| [SPEC.md](SPEC.md) | Medium | Functional specification |

## Agent Guidelines

### Development Quality Standards

1. **Environment**: Keep setup docs working across Mac/Linux/Windows
2. **Testing**: Maintain >80% test coverage requirement
3. **Documentation**: Enforce RASP compliance in all modules
4. **Tooling**: Keep uv/pip instructions current

### When Modifying Development Docs

- Test all installation commands on a clean environment
- Update Python version requirements when changed
- Verify test commands with current test suite
- Update IDE configuration for new VS Code/PyCharm versions

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Record outcomes in shared telemetry and update TODO queues when necessary

## Navigation Links

- **📁 Parent Directory**: [docs/](../README.md)
- **🏠 Project Root**: [../../README.md](../../README.md)
- **📦 Related**: [Deployment](../deployment/) | [Contributing](../project/contributing.md)
