# Agentic Memory Tests Specification
**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Technical specification for the `agentic_memory/tests` package. Contains the test suite for the rules sub-module, validating the `.cursorrules` coding governance system against real rule files.

## Design Principles

- **Zero-Mock**: All tests use real `.cursorrules` files on disk. No `unittest.mock`, `MagicMock`, or `monkeypatch`.
- **Explicit Failure**: Missing files trigger `FileNotFoundError`; invalid extensions trigger `ValueError`.
- **Integration-First**: Tests exercise the full chain from file loading through engine resolution to MCP tool output.

## Architecture

```
tests/
  rules/
    __init__.py          # Package marker
    test_rules.py        # 40+ test functions covering all rules module components
  README.md
  AGENTS.md
  SPEC.md
```

## Functional Requirements

1. **Sanity Checks**: Verify the rules directory structure exists with expected subdirectories (`modules/`, `cross-module/`, `file-specific/`) and `general.cursorrules`.
2. **RuleLoader Tests**: Validate loading of rules at each priority level, section parsing and numbering, `to_dict()` serialization, and error handling for missing files and wrong extensions.
3. **RuleEngine Tests**: Verify `list_module_names()` returns 60 sorted modules, `list_cross_module_names()` returns 8 names, `get_applicable_rules()` returns correctly ordered rules by priority, and `list_all_rules()` returns all 75 rules with no duplicates.
4. **MCP Tool Tests**: Validate all 8 MCP tools (`rules_list_modules`, `rules_get_module_rule`, `rules_get_applicable`, `rules_get_section`, `rules_search`, `rules_list_cross_module`, `rules_list_file_specific`, `rules_list_all`) return correct types and expected data.
5. **Edge Cases**: Verify caching behavior, path normalization (absolute/relative/bare filename), `.yml` to `yaml` extension mapping, CHANGELOG/SPEC filename-based rules, empty RuleSet handling, and no-duplicate invariants.

## Interface Contracts

```python
# Primary test fixture
RULES_ROOT = Path(__file__).parent.parent.parent / "rules"  # Absolute path to rules/ package

# Expected invariants
assert len(engine.list_module_names()) == 60
assert len(engine.list_cross_module_names()) == 8
assert len(engine.list_all_rules()) == 75
```

## Dependencies

- `pytest` -- test runner
- `codomyrmex.agentic_memory.rules` -- RuleEngine, RuleLoader, RulePriority, RuleSet, RuleRegistry, RuleSection
- `codomyrmex.agentic_memory.rules.mcp_tools` -- all 8 MCP tool functions

## Constraints

- Tests depend on the actual `.cursorrules` file corpus being present. The files are shipped in the `rules/` package directory.
- Rule counts (60 modules, 8 cross-module, 6 file-specific, 1 general = 75 total) are asserted as invariants. Adding or removing `.cursorrules` files requires updating these counts.

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Parent](../README.md)
