# Codomyrmex Agents — docs

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Central documentation hub for the Codomyrmex platform. Contains user guides, developer documentation, API references, and module-specific documentation for 78 specialized modules.

## Documentation Organization

| Section | Scope | Agent Priority |
|---------|-------|----------------|
| [**getting-started/**](getting-started/) | Installation, setup, tutorials | High - user onboarding |
| [**development/**](development/) | Dev environment, testing | Medium - dev workflows |
| [**reference/**](reference/) | API, CLI, troubleshooting | High - technical reference |
| [**deployment/**](deployment/) | Production deployment | Medium - operations |
| [**modules/**](modules/) | Per-module docs (78) | High - module details |
| [**integration/**](integration/) | External integrations | Medium - integrations |
| [**examples/**](examples/) | Code examples | Medium - learning |
| [**project/**](project/) | Architecture, contributing | Low - project info |
| [**project_orchestration/**](project_orchestration/) | Multi-project workflows | Low - advanced |

### Secure Cognitive Agent Documentation

| Directory | Scope | Agent Priority |
|-----------|-------|----------------|
| [**src/codomyrmex/identity/**](../src/codomyrmex/identity/) | Identity & Verification | Critical - Security Core |
| [**src/codomyrmex/wallet/**](../src/codomyrmex/wallet/) | Self-Custody & Recovery | Critical - Security Core |
| [**src/codomyrmex/defense/**](../src/codomyrmex/defense/) | Active Defense | Critical - Security Core |
| [**src/codomyrmex/market/**](../src/codomyrmex/market/) | Anonymous Markets | High - Economic Layer |
| [**src/codomyrmex/privacy/**](../src/codomyrmex/privacy/) | Privacy & Mixnets | Critical - Privacy Core |

## Agent Guidelines

### Documentation Quality Standards

1. **Accuracy**: Keep documentation synchronized with code changes
2. **Completeness**: Ensure all public APIs are documented
3. **Clarity**: Use clear, concise language
4. **Examples**: Include working code examples where applicable

### When Modifying Documentation

- Update corresponding source code docstrings if applicable
- Verify all links are valid after changes
- Run spell-check on modified content
- Ensure code examples are runnable

### Cross-Reference Patterns

```markdown
# Link to module source
[llm module](../src/codomyrmex/llm/)

# Link to API reference
[API Reference](reference/api.md)

# Link to sibling doc
[Installation Guide](getting-started/installation.md)
```

## Operating Contracts

- Maintain alignment between documentation and source code
- All modules must have corresponding documentation in `modules/`
- Ensure RASP compliance (README, AGENTS, SPEC, PAI) in each directory
- Update documentation when API changes are made

## Navigation Links

- **🏠 Project Root**: [../README.md](../README.md) - Main project entry
- **📦 Source Code**: [../src/codomyrmex/](../src/codomyrmex/) - Implementation
- **🔧 Scripts**: [../scripts/](../scripts/) - Automation utilities
- **📋 Examples**: [../examples/](../examples/) - Executable examples
