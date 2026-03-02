# Personal AI Infrastructure - Rules Submodule

**Module**: `agentic_memory/rules/`
**Status**: Active | **Last Updated**: March 2026

## Overview

The `rules/` submodule contains **75 `.cursorrules` files** for AI-assisted development, organized hierarchically by specificity, plus a Python API (`RuleEngine`, `RuleLoader`, `RuleRegistry`) and three MCP tools for programmatic access. Rules encode mandatory project policies (Zero-Mock, UV, RASP, Python ≥ 3.10) alongside coding standards and best practices.

## Statistics

| Category | Count |
|----------|-------|
| Module-specific rules | 60 |
| Cross-module rules | 8 |
| File-specific rules | 6 |
| General rules | 1 |
| **Total** | **75** |

## Mandatory Policies

These policies are encoded in `general.cursorrules §2` and enforced globally:

| Policy | Key Implication |
|--------|----------------|
| **Zero-Mock** | All `.cursorrules` testing sections use real implementations |
| **UV-Only** | All Key Files sections reference `pyproject.toml`, not `requirements.txt` |
| **RASP** | All subdirectories contain README.md, AGENTS.md, SPEC.md, PAI.md |
| **Python ≥ 3.10** | Type hints, match statements, and modern syntax expected |

## AI Context

When working with cursor rules:

1. **Rule Hierarchy**: Apply rules in order of specificity:
   - File-specific rules (highest priority)
   - Module-specific rules
   - Cross-module rules
   - General rules (lowest priority)

2. **Mandatory policies cannot be overridden** by any rule level — they apply universally.

3. **Module-Specific Rules**: Check `modules/{module_name}.cursorrules` first when editing a module.

4. **File-Specific Rules**: Check `file-specific/` for Python, YAML, JSON, and documentation files.

5. **Python API available**: Use `RuleEngine` to query rules programmatically.

## MCP Tools

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `rules_list_modules` | List all Codomyrmex module names with a defined coding rule | Safe |
| `rules_get_module_rule` | Get full rule (sections, raw content) for a specific module | Safe |
| `rules_get_applicable` | Get all applicable rules for a file path and/or module, ordered FILE_SPECIFIC → GENERAL | Safe |

## PAI Algorithm Phase Mapping

| Phase | Rules Contribution |
|-------|-------------------|
| **OBSERVE** | `rules_get_applicable` retrieves coding standards relevant to the current file/module context |
| **THINK** | Agents consult `rules_get_module_rule` to understand constraints before reasoning about changes |
| **PLAN** | `rules_get_applicable` surfaces mandatory policies (Zero-Mock, RASP) that constrain the plan |
| **BUILD** | `rules_get_module_rule` provides coding standards to enforce during implementation |
| **VERIFY** | `rules_get_applicable` supplies the verification checklist (§7 Final Check) for the file/module |
| **LEARN** | Rule usage patterns inform which standards are most consulted |

## Key Files

- `engine.py`: `RuleEngine` — hierarchy-aware rule resolution
- `loader.py`: `RuleLoader` — parses `.cursorrules` files into `Rule` objects
- `registry.py`: `RuleRegistry` — indexed access to all rules
- `models.py`: `Rule`, `RuleSet`, `RulePriority`, `RuleSection` dataclasses
- `mcp_tools.py`: MCP tool definitions
- `general.cursorrules`: Default coding standards + mandatory policies for the repository
- `modules/`: 60 module-specific rule files
- `cross-module/`: 8 cross-cutting concern rules
- `file-specific/`: 6 file-type specific rules

## Navigation

- **Parent**: [../README.md](../README.md) — Agentic Memory module
- **Related Spec**: [SPEC.md](SPEC.md)
- **Agent Guidelines**: [AGENTS.md](AGENTS.md)
- **Modules Directory**: [modules/](modules/)
