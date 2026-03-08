# Agentic Memory Tests
**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Test package for the `agentic_memory` module. Contains the `rules/` subdirectory with 500 lines of zero-mock tests covering the `.cursorrules` coding governance system including `RuleLoader`, `RuleEngine`, `RuleRegistry`, `RuleSet`, and all 8 MCP tools.

## Architecture

```
tests/
  rules/               # Tests for the rules sub-module
    __init__.py
    test_rules.py       # 40+ zero-mock tests for rules engine, loader, registry, MCP tools
  README.md
  AGENTS.md
  SPEC.md
```

## Running Tests

```bash
# Run all agentic_memory tests (including rules/)
uv run pytest src/codomyrmex/agentic_memory/tests/ -v

# Run only rules tests
uv run pytest src/codomyrmex/agentic_memory/tests/rules/test_rules.py -v
```

## Test Coverage

Tests validate against real `.cursorrules` files in the `rules/` package directory (75 total rules: 1 general + 8 cross-module + 60 module + 6 file-specific). No mocks, stubs, or fake data are used, following the project zero-mock policy.

## Navigation

- [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [Parent](../README.md)
