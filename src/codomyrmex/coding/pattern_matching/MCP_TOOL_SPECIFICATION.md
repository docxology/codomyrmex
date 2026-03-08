# Pattern Matching -- MCP Tool Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `coding/pattern_matching` module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `pattern_matching` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `match_pattern`

**Description**: Match a named pattern or detect all design patterns in Python code.
**Trust Level**: Safe
**Category**: analysis

When a specific pattern name is given (e.g. 'singleton', 'factory', 'decorator', 'context_manager'),
searches for that structural pattern using the ASTMatcher. When the pattern is empty or 'all',
runs the full PatternDetector to find all recognised design patterns.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `code` | `str` | Yes | -- | Python source code to analyse |
| `pattern` | `str` | No | `""` | Pattern name to search for. Use empty string or 'all' to detect every known pattern. |

**Returns**: `dict[str, Any]` -- Dictionary with matched patterns including pattern_name, node_type, line, col, name, and details per match.

**Example**:
```python
from codomyrmex.coding.pattern_matching.mcp_tools import match_pattern

result = match_pattern(
    code="class Singleton:\n    _instance = None\n    def __new__(cls):\n        if cls._instance is None:\n            cls._instance = super().__new__(cls)\n        return cls._instance",
    pattern="singleton",
)
```

---

### `list_patterns`

**Description**: List all available code patterns that can be detected.
**Trust Level**: Safe
**Category**: data-retrieval

Returns both the design patterns from PatternDetector (singleton, factory, observer, etc.)
and the structural patterns from ASTMatcher (singleton, factory, decorator, context_manager).

**Parameters**: No parameters required.

**Returns**: `dict[str, Any]` -- Dictionary with design_patterns, ast_patterns, anti_patterns, and total_count.

**Example**:
```python
from codomyrmex.coding.pattern_matching.mcp_tools import list_patterns

result = list_patterns()
```

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe -- read-only code analysis
- **PAI Phases**: OBSERVE (code pattern discovery), VERIFY (code quality checks)
- **Dependencies**: Internal `ast_matcher` module (ASTMatcher) and `code_patterns` module (PatternDetector, PATTERNS)

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
