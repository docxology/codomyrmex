# Agentic Memory Rules Tests Specification
**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Technical specification for the `agentic_memory/tests/rules` test package. Defines test structure, invariants, and coverage expectations for the `.cursorrules` coding governance system.

## Design Principles

- **Zero-Mock**: All tests exercise real code paths against real `.cursorrules` files. No `unittest.mock` or `monkeypatch`.
- **Explicit Failure**: Tests assert specific exceptions for error conditions rather than checking return codes.
- **Exhaustive MCP Coverage**: Every `@mcp_tool` function in `rules/mcp_tools.py` has at least one dedicated test.

## Architecture

```
rules/
  __init__.py         # Package marker
  test_rules.py       # 40+ test functions (500 lines)
```

## Functional Requirements

1. **Sanity checks**: Verify rules root directory exists, `general.cursorrules` is present, and `modules/`, `cross-module/`, `file-specific/` subdirectories exist.
2. **RuleLoader**: Load rules at each priority level (GENERAL, MODULE, CROSS_MODULE, FILE_SPECIFIC), parse sections with correct numbering, serialize to dict, and reject missing files or wrong extensions.
3. **RuleEngine listing**: `list_module_names()` returns exactly 60 sorted names, `list_cross_module_names()` returns 8, `list_file_rule_names()` includes `python`, `yaml`, `json`.
4. **RuleEngine resolution**: `get_applicable_rules()` returns rules ordered by priority (FILE_SPECIFIC first, GENERAL last), handles unknown modules gracefully, and produces no duplicates.
5. **MCP tools**: `rules_list_modules`, `rules_get_module_rule`, `rules_get_applicable`, `rules_get_section`, `rules_search`, `rules_list_cross_module`, `rules_list_file_specific`, `rules_list_all` all return correct types and expected data.
6. **Edge cases**: Registry caching (same object identity), `.yml` to `yaml` mapping, CHANGELOG/SPEC filename rules, absolute/relative/bare path resolution, empty RuleSet, `to_dict()` priority serialization.

## Interface Contracts

```python
# Test fixture -- immutable reference to rules root
RULES_ROOT: Path = Path(__file__).parent.parent.parent / "rules"

# Key invariants asserted by tests
len(engine.list_module_names()) == 60
len(engine.list_cross_module_names()) == 8
len(engine.list_all_rules()) == 75
engine.list_all_rules()[0].priority.value == 1   # FILE_SPECIFIC
engine.list_all_rules()[-1].priority.value == 4  # GENERAL
```

## Dependencies

- `pytest` -- test runner
- `pathlib.Path` -- path resolution
- `codomyrmex.agentic_memory.rules` -- RuleEngine, RuleLoader, RulePriority, RuleSet
- `codomyrmex.agentic_memory.rules.mcp_tools` -- all 8 MCP tool functions
- `codomyrmex.agentic_memory.rules.registry` -- RuleRegistry (caching tests)

## Constraints

- The 75 `.cursorrules` files must be present in the rules package directory for tests to pass.
- Count invariants must be updated when the `.cursorrules` corpus changes.
- No test should modify `.cursorrules` files on disk.

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Parent](../README.md)
