# Agentic Memory Rules Tests - Agent Coordination
**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for the `agentic_memory/tests/rules` test package. Contains 40+ zero-mock tests validating the `.cursorrules` coding governance engine, loader, registry, and MCP tools.

## Key Files

| File | Purpose |
|------|---------|
| `test_rules.py` | Complete test suite -- sanity, loader, engine, MCP tools, edge cases |
| `__init__.py` | Package marker (empty) |

## MCP Tools Available

No MCP tools. This is a test-only package.

## Agent Instructions

1. Always run the full test suite after modifying any file in `agentic_memory/rules/` (engine, loader, registry, models, or mcp_tools).
2. Tests reference `RULES_ROOT` as the absolute path to the `rules/` package directory -- all assertions depend on real files.
3. When adding a new MCP tool to `rules/mcp_tools.py`, add at least one test function in `test_rules.py` under the MCP tools section.
4. Rule count invariants (60 modules, 8 cross-module, 6 file-specific, 75 total) are hardcoded assertions. Update them when adding or removing `.cursorrules` files.

## Operating Contracts

- **Zero-Mock**: Tests import from `codomyrmex.agentic_memory.rules` and `codomyrmex.agentic_memory.rules.mcp_tools` directly -- no mocking of any kind.
- **Explicit Failure**: `pytest.raises(FileNotFoundError)` for missing files, `pytest.raises(ValueError)` for wrong extensions.
- **Caching Verification**: Tests verify `RuleRegistry` returns the same object on repeated loads (`r1 is r2`).

## Common Patterns

```python
# Standard test pattern: create engine, get rules, assert structure
engine = RuleEngine(RULES_ROOT)
rule_set = engine.get_applicable_rules(file_path="memory.py", module_name="agentic_memory")
resolved = rule_set.resolved()
assert resolved[0].priority == RulePriority.FILE_SPECIFIC

# MCP tool test pattern: import tool, call, assert return type
from codomyrmex.agentic_memory.rules.mcp_tools import rules_list_modules
modules = rules_list_modules()
assert isinstance(modules, list)
assert "agentic_memory" in modules
```

## PAI Agent Role Access Matrix

| Agent Role | Access Level | Notes |
|------------|-------------|-------|
| QATester | Full | Runs and extends test suite |
| Engineer | Full | Updates tests when modifying rules module |
| Architect | Read | Reviews coverage and invariants |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Parent](../README.md)
