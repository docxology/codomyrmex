# Agentic Memory Tests - Agent Coordination
**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for the `agentic_memory/tests` package. This directory contains zero-mock tests for the agentic_memory module, primarily the `rules/` sub-module test suite.

## Key Files

| File | Purpose |
|------|---------|
| `rules/test_rules.py` | 40+ tests for RuleLoader, RuleEngine, RuleRegistry, RuleSet, and MCP tools |
| `rules/__init__.py` | Test package marker |

## MCP Tools Available

No MCP tools. This is a test-only package.

## Agent Instructions

1. Run tests with `uv run pytest src/codomyrmex/agentic_memory/tests/ -v` before modifying any rules module code.
2. All tests use real `.cursorrules` files from the `rules/` package -- never introduce mocks or stubs.
3. When adding new MCP tools to `rules/mcp_tools.py`, add corresponding tests in `rules/test_rules.py`.
4. Tests validate the full rule hierarchy: FILE_SPECIFIC > MODULE > CROSS_MODULE > GENERAL.
5. Verify the expected rule count (75 total) if adding or removing `.cursorrules` files.

## Operating Contracts

- **Zero-Mock Policy**: All tests operate against real `.cursorrules` files on disk.
- **Explicit Failure**: Tests use `pytest.raises` for expected errors (FileNotFoundError, ValueError).
- **No Silent Fallbacks**: Missing rules cause assertion failures, not silent degradation.

## Common Patterns

```python
# Standard test setup: locate rules root directory
RULES_ROOT = Path(__file__).parent.parent.parent / "rules"

# Load and validate a rule
rule = RuleLoader.load(RULES_ROOT / "modules" / "agentic_memory.cursorrules")
assert rule.name == "agentic_memory"
assert rule.priority == RulePriority.MODULE
```

## PAI Agent Role Access Matrix

| Agent Role | Access Level | Notes |
|------------|-------------|-------|
| QATester | Full | Primary consumer -- runs and extends tests |
| Engineer | Full | Modifies tests when changing rules module code |
| Architect | Read | Reviews test coverage and structure |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Parent](../README.md)
