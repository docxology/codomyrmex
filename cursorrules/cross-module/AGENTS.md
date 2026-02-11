# Codomyrmex Agents — cursorrules/cross-module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Cross-module cursor rules for multi-module interactions and shared patterns. Apply these rules when working across module boundaries or with infrastructure shared by multiple modules.

> **Mandatory Policies** (from `general.cursorrules §2`): Zero-Mock, UV-Only, RASP, Python ≥ 3.10 — these apply unconditionally at all levels.

## Active Rules (8)

| Rule | When to Apply |
|------|---------------|
| `logging_monitoring` | Adding logging, metrics, or observability |
| `model_context_protocol` | Defining MCP tools or resources |
| `static_analysis` | Configuring linters, security scanners |
| `build_synthesis` | Code generation, build processes |
| `data_visualization` | Charts, plots, visual output |
| `output_module` | Managing output directories, artifacts |
| `pattern_matching` | Code analysis, AST operations |
| `template_module` | Using or creating templates |

## Agent Guidelines

### When to Apply Cross-Module Rules

1. **Multi-Module Operations**: Working with 2+ modules simultaneously
2. **Shared Infrastructure**: Logging, metrics, output handling
3. **Code Generation**: Template-based or synthesized code
4. **Analysis Tools**: Static analysis, pattern matching

### Rule Application Order

```
1. Check file-specific rules (python.cursorrules, yaml.cursorrules, etc.)
2. Check module-specific rules (security.cursorrules, agents.cursorrules, etc.)
3. Check cross-module rules (this directory) ← Apply these
4. Fall back to general.cursorrules
```

### Key Patterns

**Logging**: Always use structured logging with the logging_monitoring patterns:

```python
logger.info("message", extra={"context": "value"})
```

**MCP Tools**: Follow model_context_protocol for tool definitions

**Output**: Use output_module patterns for artifact management

### Mandatory Policies (Always Apply)

- **Zero-Mock**: Cross-module tests must use real implementations
- **UV-Only**: Dependencies via `uv add` → `pyproject.toml` — no `requirements.txt`
- **RASP**: All directories need README.md, AGENTS.md, SPEC.md, PAI.md

## Operating Contracts

- Cross-module rules supplement module-specific rules
- When conflicts arise, module-specific rules take precedence
- Document cross-module dependency rationale
- Ensure MCP interfaces remain available for sibling agents

## Navigation Links

- **📁 Parent Directory**: [../README.md](../README.md) - cursorrules root
- **📦 Module Rules**: [../modules/](../modules/) - Per-module rules
- **📄 File Rules**: [../file-specific/](../file-specific/) - File type rules
- **📋 PAI Context**: [PAI.md](PAI.md) - AI infrastructure context
- **🏠 Project Root**: [../../README.md](../../README.md)
