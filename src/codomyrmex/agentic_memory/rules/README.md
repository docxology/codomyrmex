# Agentic Memory — Rules Submodule

**Version**: v0.3.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Hierarchical coding standards and automation rules for AI-assisted development across the Codomyrmex platform. Rules are organized by specificity level and applied in order of precedence.

This submodule exposes the 75 `.cursorrules` files via a Python API and three MCP tools, enabling AI agents to programmatically query which coding standards apply to any given file or module.

## Python API

```python
from codomyrmex.agentic_memory.rules import RuleEngine, RulePriority

engine = RuleEngine()

# Which rules apply when editing src/codomyrmex/agents/memory.py?
rule_set = engine.get_applicable_rules(
    file_path="memory.py",
    module_name="agentic_memory",
)
for rule in rule_set.resolved():  # FILE_SPECIFIC first, GENERAL last
    print(f"[{rule.priority.name}] {rule.name}")

# Get a specific module's rule
rule = engine.get_module_rule("agents")
section = rule.get_section(3)  # "Coding Standards & Practices for agents"
print(section.content)

# List all modules with rules
print(engine.list_module_names())  # ['agents', 'agentic_memory', 'cloud', ...]
```

## MCP Tools

Three tools are auto-discovered by the PAI MCP bridge:

| Tool | Description |
|------|-------------|
| `rules_list_modules` | List all module names with defined rules |
| `rules_get_module_rule` | Get the full rule for a specific module |
| `rules_get_applicable` | Get all applicable rules for a file/module context |

## Rule Hierarchy

Rules follow a specificity hierarchy (most specific wins):

| Priority | Category | Location | Count |
|----------|----------|----------|-------|
| 1 (Highest) | File-specific | `file-specific/` | 6 rules |
| 2 | Module-specific | `modules/` | 60 rules |
| 3 | Cross-module | `cross-module/` | 8 rules |
| 4 (Lowest) | General | `general.cursorrules` | 1 rule |
| | **Total** | | **75 rules** |

## Mandatory Policies (Cannot Be Overridden)

These policies are defined in `general.cursorrules §2` and enforced at all levels:

| Policy | Summary |
|--------|---------|
| **Zero-Mock** | Never use mocks — real implementations, data factories, environment-gated tests |
| **UV-Only** | `pyproject.toml` + `uv sync` for all dependencies — no `pip install` or `requirements.txt` |
| **RASP** | Every directory needs `README.md`, `AGENTS.md`, `SPEC.md`, `PAI.md` |
| **Python ≥ 3.10** | All code compatible with Python 3.10+ |

## Directory Structure

```
src/codomyrmex/agentic_memory/rules/
├── __init__.py               # Public API (RuleEngine, RuleLoader, Rule, RuleSet, RulePriority)
├── engine.py                 # RuleEngine — hierarchy-aware resolution
├── loader.py                 # RuleLoader — parses .cursorrules files
├── registry.py               # RuleRegistry — indexed access by module/extension/cross-module
├── models.py                 # Rule, RuleSet, RulePriority, RuleSection dataclasses
├── mcp_tools.py              # MCP tools (rules_list_modules, rules_get_module_rule, rules_get_applicable)
├── general.cursorrules       # Universal coding standards + mandatory policies
├── cross-module/             # Rules for cross-cutting concerns (8 rules)
│   ├── logging_monitoring.cursorrules
│   ├── model_context_protocol.cursorrules
│   ├── static_analysis.cursorrules
│   └── ... (5 more)
├── file-specific/            # Rules for specific file types (6 rules)
│   ├── python.cursorrules
│   ├── yaml.cursorrules
│   ├── json.cursorrules
│   └── ... (3 more)
└── modules/                  # Module-specific rules (60 rules)
    ├── security.cursorrules
    ├── agents.cursorrules
    ├── cloud.cursorrules
    └── ... (57 more)
```

## Standard Rule Template (8 Sections)

All `.cursorrules` files follow this structure:
0. **Preamble**: Relationship to general.cursorrules

1. **Purpose & Context**: Core functionality, key technologies
2. **Key Files & Structure**: Important files to monitor
3. **Coding Standards**: Language and style requirements
4. **Testing**: Test requirements and strategies (Zero-Mock enforced)
5. **Documentation**: Documentation maintenance (RASP enforced)
6. **Specific Considerations**: Module-specific notes
7. **Final Check**: Verification steps before finalizing

## Quick Reference

| Need | File |
|------|------|
| Python code standards | `file-specific/python.cursorrules` |
| Security guidelines | `modules/security.cursorrules` |
| Logging patterns | `cross-module/logging_monitoring.cursorrules` |
| MCP tool specs | `cross-module/model_context_protocol.cursorrules` |
| General principles + policies | `general.cursorrules` |

## Companion Files

- [**AGENTS.md**](AGENTS.md) - AI agent guidelines for rule application
- [**SPEC.md**](SPEC.md) - Functional specification with architecture diagram
- [**PAI.md**](PAI.md) - Personal AI Infrastructure context

## Navigation

- **Parent Module**: [../README.md](../README.md) — Agentic Memory module
- **Source Code**: [../](../) — agentic_memory/ package root
- **Documentation**: [../../../../../docs/](../../../../../docs/)
