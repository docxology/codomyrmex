# Codomyrmex Agents — cursorrules

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Coding standards and automation rules for consistent code quality across the repository. Defines style guidelines, naming conventions, and automated checks for AI-assisted development.

## Directory Structure

```
cursorrules/
├── general.cursorrules   # Universal coding standards
├── cross-module/         # Rules for cross-module operations
├── file-specific/        # Rules for specific file types
└── modules/              # Module-specific rule overrides
```

## Active Components

| Component | Type | Description |
|-----------|------|-------------|
| `general.cursorrules` | Rules | Universal coding standards |
| `cross-module/` | Directory | Cross-cutting concerns |
| `file-specific/` | Directory | File type specific rules |
| `modules/` | Directory | Per-module overrides |

## Rule Hierarchy

Rules follow a specificity hierarchy (most specific wins):

1. **File-specific** (`file-specific/`) - Rules for specific file patterns
2. **Module-specific** (`modules/`) - Per-module overrides
3. **Cross-module** (`cross-module/`) - Cross-cutting patterns
4. **General** (`general.cursorrules`) - Universal defaults

## Agent Guidelines

### Coding Standards

1. **Python**: PEP 8, type hints, docstrings
2. **Naming**: snake_case for variables/functions, PascalCase for classes
3. **Imports**: Group by standard library, third-party, local
4. **Documentation**: Google-style docstrings

### When Modifying Rules

- Document rationale for rule changes
- Ensure backward compatibility where possible
- Test rules against existing codebase
- Update related documentation

### Key Rules Summary

| Rule | Description |
|------|-------------|
| **No mocks** | Use real implementations, not mock methods |
| **Type hints** | All functions must have type annotations |
| **Docstrings** | All public APIs must be documented |
| **Test coverage** | ≥80% coverage required |
| **RASP compliance** | Every directory needs README, AGENTS, SPEC, PAI |

## Operating Contracts

- Rules apply to all code modifications
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Conflicts resolved by specificity hierarchy
- Document exceptions with rationale

## Navigation Links

- **📁 Parent**: [../README.md](../README.md) - Project root
- **📖 Dev Docs**: [../docs/development/](../docs/development/) - Development guides
- **🧪 Testing**: [../docs/development/testing-strategy.md](../docs/development/testing-strategy.md) - Test patterns
