# Agentic Memory Rules — MCP Tool Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `agentic_memory/rules` submodule.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

The rules submodule provides programmatic access to the `.cursorrules` hierarchy,
allowing AI agents to query coding rules by module, file, or text search.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `agentic_memory` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `rules_list_modules`

**Description**: List all Codomyrmex module names that have a defined coding rule. Returns a sorted list of module names (e.g. 'agentic_memory', 'agents', 'cloud').
**Trust Level**: Safe
**Category**: data-retrieval

**Parameters**: No parameters required.

**Returns**: `list[str]` — Sorted list of module names with defined `.cursorrules` files.

**Example**:
```python
from codomyrmex.agentic_memory.rules.mcp_tools import rules_list_modules

modules = rules_list_modules()
# ["agentic_memory", "agents", "cloud", ...]
```

---

### `rules_get_module_rule`

**Description**: Get the full coding rule for a specific Codomyrmex module. Returns a dict with name, priority, sections, and raw_content, or null if no rule exists.
**Trust Level**: Safe
**Category**: data-retrieval

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `module_name` | `str` | Yes | -- | Codomyrmex module name, e.g. `"agentic_memory"` or `"agents"` |

**Returns**: `dict | None` — The module-specific Rule as a dict, or `None` if not found.

**Example**:
```python
from codomyrmex.agentic_memory.rules.mcp_tools import rules_get_module_rule

rule = rules_get_module_rule(module_name="agents")
```

---

### `rules_get_applicable`

**Description**: Get all applicable coding rules for a given file path and/or module name, ordered highest priority first (FILE_SPECIFIC -> MODULE -> CROSS_MODULE -> GENERAL). Pass file_path and/or module_name.
**Trust Level**: Safe
**Category**: data-retrieval

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | `str` | No | `""` | File path or filename to determine file-specific rules |
| `module_name` | `str` | No | `""` | Module name to include the module-specific rule |

**Returns**: `list[dict]` — Applicable rules as dicts, sorted FILE_SPECIFIC first.

**Example**:
```python
from codomyrmex.agentic_memory.rules.mcp_tools import rules_get_applicable

rules = rules_get_applicable(file_path="memory.py", module_name="agentic_memory")
```

---

### `rules_get_section`

**Description**: Get a specific numbered section (0-7) from a module's coding rule. Returns a dict with number, title, and content, or null if not found.
**Trust Level**: Safe
**Category**: data-retrieval

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `module_name` | `str` | Yes | -- | Codomyrmex module name, e.g. `"agentic_memory"` |
| `section_number` | `int` | Yes | -- | Section number 0-7 (section-0 Preamble through section-7 Final Check) |

**Returns**: `dict | None` — One section from a module rule as a dict, or `None` if not found.

**Example**:
```python
from codomyrmex.agentic_memory.rules.mcp_tools import rules_get_section

section = rules_get_section(module_name="agentic_memory", section_number=3)
```

---

### `rules_search`

**Description**: Search all 75 .cursorrules files for a text query (case-insensitive). Returns a list of matching rules with name, priority, and file path.
**Trust Level**: Safe
**Category**: data-retrieval

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | `str` | Yes | -- | Text to search for, e.g. `"Zero-Mock"` or `"pytest"` |

**Returns**: `list[dict]` — All rules whose raw content contains the query (case-insensitive). Each dict contains `name`, `priority`, and `file_path`.

**Example**:
```python
from codomyrmex.agentic_memory.rules.mcp_tools import rules_search

matches = rules_search(query="Zero-Mock")
```

---

### `rules_list_cross_module`

**Description**: List all cross-module rule names (8 rules governing inter-module concerns).
**Trust Level**: Safe
**Category**: data-retrieval

**Parameters**: No parameters required.

**Returns**: `list[str]` — Sorted list of all cross-module rule names.

**Example**:
```python
from codomyrmex.agentic_memory.rules.mcp_tools import rules_list_cross_module

cross_module_names = rules_list_cross_module()
```

---

### `rules_list_file_specific`

**Description**: List all file-specific rule names (6 rules for file types: .py, .yaml, .json, etc.).
**Trust Level**: Safe
**Category**: data-retrieval

**Parameters**: No parameters required.

**Returns**: `list[str]` — Sorted list of all file-specific rule names.

**Example**:
```python
from codomyrmex.agentic_memory.rules.mcp_tools import rules_list_file_specific

file_rule_names = rules_list_file_specific()
```

---

### `rules_list_all`

**Description**: List all 75 rules across all categories as summary dicts, sorted by priority. FILE_SPECIFIC rules come first, GENERAL last.
**Trust Level**: Safe
**Category**: data-retrieval

**Parameters**: No parameters required.

**Returns**: `list[dict]` — All rules as summary dicts sorted FILE_SPECIFIC first. Each dict contains `name`, `priority`, and `file_path`.

**Example**:
```python
from codomyrmex.agentic_memory.rules.mcp_tools import rules_list_all

all_rules = rules_list_all()
```

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe — no trust check required
- **PAI Phases**: OBSERVE (discover what rules apply), THINK (understand coding constraints), LEARN (index rule knowledge)
- **Dependencies**: `agentic_memory.rules.engine.RuleEngine` — reads `.cursorrules` files from the repository

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
