# Codomyrmex Agents — code/tests

## Signposting
- **Parent**: [Code Module](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [execution](execution/AGENTS.md)
    - [sandbox](sandbox/AGENTS.md)
    - [review](review/AGENTS.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Test suite coordination for the code module, organizing tests for execution, sandboxing, review, and monitoring components.

## Test Organization

| Category | Purpose | Key Tests |
|----------|---------|-----------|
| **execution/** | Execution engine tests | Language support, sessions |
| **sandbox/** | Sandbox tests | Isolation, containers, limits |
| **review/** | Review tests | Analysis, metrics |


## Active Components

### Core Files
- `__init__.py` – Package initialization
- Other module-specific implementation files

## Operating Contracts

### Universal Test Protocols
1. **Isolation** - Tests must not affect other tests
2. **Reproducibility** - Tests must produce consistent results
3. **Speed** - Unit tests should complete quickly
4. **Coverage** - Maintain high code coverage

## Navigation Links

- **Parent**: [Code AGENTS](../AGENTS.md)
- **Human Documentation**: [README.md](README.md)
