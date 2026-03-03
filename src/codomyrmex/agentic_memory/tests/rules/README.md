# Agentic Memory Rules Tests
**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Zero-mock test suite for the `agentic_memory.rules` sub-module. Tests validate the `.cursorrules` coding governance system including rule loading, priority-based resolution, section parsing, registry caching, and all 8 MCP tools. All tests operate against real `.cursorrules` files shipped in the `rules/` package directory.

## Key Exports

| Export | Type | Description |
|--------|------|-------------|
| `test_rules.py` | Test module | 40+ test functions covering RuleLoader, RuleEngine, RuleRegistry, RuleSet, and MCP tools |

## Quick Start

```bash
# Run all rules tests
uv run pytest src/codomyrmex/agentic_memory/tests/rules/test_rules.py -v

# Run only MCP tool tests
uv run pytest src/codomyrmex/agentic_memory/tests/rules/test_rules.py -k "mcp" -v

# Run only edge case tests
uv run pytest src/codomyrmex/agentic_memory/tests/rules/test_rules.py -k "cache or path or extension" -v
```

## Architecture

```
rules/
  __init__.py         # Package marker
  test_rules.py       # All test functions (500 lines)
  README.md
  AGENTS.md
  SPEC.md
```

## Test Categories

| Category | Count | Description |
|----------|-------|-------------|
| Sanity checks | 5 | Directory structure and file presence validation |
| RuleLoader | 8 | Load rules, parse sections, serialize, error handling |
| RuleEngine lists | 4 | Module/cross-module/file-specific listing and sorting |
| RuleEngine applicable | 7 | Priority-based rule resolution with various contexts |
| MCP tools | 10 | All 8 MCP tool functions plus edge cases |
| Edge cases | 10 | Caching, path normalization, extension mapping, exports |

## Testing

```bash
uv run pytest src/codomyrmex/agentic_memory/tests/rules/ -v
```

## Navigation

- [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [Parent](../README.md)
