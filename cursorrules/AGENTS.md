# Codomyrmex Agents — cursorrules

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Coding standards and automation rules for consistent code quality across the repository. Defines style guidelines, naming conventions, mandatory policies, and automated checks for AI-assisted development.

## Directory Structure

```
cursorrules/                 # 75 rules total
├── general.cursorrules      # Universal coding standards (1)
├── cross-module/            # Cross-cutting concerns (8)
├── file-specific/           # File type specific rules (6)
└── modules/                 # Per-module standards (60)
```

## Active Components

| Component | Type | Description |
|-----------|------|-------------|
| `general.cursorrules` | Rules | Universal coding standards + mandatory policies |
| `cross-module/` | Directory | Cross-cutting concerns (8 rules) |
| `file-specific/` | Directory | File type specific rules (6 rules) |
| `modules/` | Directory | Per-module overrides (60 rules) |

## Rule Hierarchy

Rules follow a specificity hierarchy (most specific wins):

1. **File-specific** (`file-specific/`) - Rules for specific file patterns
2. **Module-specific** (`modules/`) - Per-module overrides
3. **Cross-module** (`cross-module/`) - Cross-cutting patterns
4. **General** (`general.cursorrules`) - Universal defaults

## Mandatory Policies

These policies are enforced globally and **cannot be overridden** by any rule level:

| Policy | Description |
|--------|-------------|
| **Zero-Mock** | Never use mocks, MagicMock, or test doubles — use real implementations |
| **UV-Only** | All dependencies via `pyproject.toml` + `uv sync` — never `pip install` |
| **RASP** | Every directory needs README.md, AGENTS.md, SPEC.md, PAI.md |
| **Python ≥ 3.10** | All code must be compatible with Python 3.10+ |
| **Type hints** | All functions must have type annotations |
| **Docstrings** | All public APIs must have Google-style docstrings |
| **Test coverage** | ≥80% coverage required |

## Agent Guidelines

### Coding Standards

1. **Python**: PEP 8, type hints, Google-style docstrings
2. **Naming**: snake_case for variables/functions, PascalCase for classes
3. **Imports**: Group by standard library, third-party, local
4. **Dependencies**: Add via `uv add <package>` — never edit `pyproject.toml` manually for deps

### Testing Standards

1. **Zero-Mock**: Use real data factories, environment-gated tests, simulation modes
2. **Execution**: Run via `uv run pytest` — never raw `pytest`
3. **External Services**: Gate behind `@pytest.mark.skipif(not os.getenv("API_KEY"))`
4. **File Operations**: Use `tmp_path` fixture with real filesystem operations

### When Modifying Rules

- Document rationale for rule changes
- Ensure backward compatibility where possible
- Test rules against existing codebase
- Update related documentation
- Never weaken mandatory policies (Zero-Mock, UV, RASP)

## Operating Contracts

- Rules apply to all code modifications
- Mandatory policies cannot be overridden at any level
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Conflicts resolved by specificity hierarchy (except mandatory policies)
- Document exceptions with rationale

## Navigation Links

- **📁 Parent**: [../README.md](../README.md) - Project root
- **📖 Dev Docs**: [../docs/development/](../docs/development/) - Development guides
- **🧪 Testing**: [../docs/development/testing-strategy.md](../docs/development/testing-strategy.md) - Test patterns
- **📋 PAI Context**: [PAI.md](PAI.md) - AI infrastructure context
