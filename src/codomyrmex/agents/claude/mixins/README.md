# Claude Client Mixins
**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Claude Client Mixins package provides modular, composable mixin classes that extend the Claude API client with specialized capabilities. Each mixin encapsulates a distinct domain of functionality -- code intelligence, API execution with retry logic, file operations, session management, system operations, and tool/function calling -- allowing the ClaudeClient to be assembled from focused, testable components.

## PAI Integration

| PAI Phase | Mixin | Usage |
|-----------|-------|-------|
| BUILD | CodeIntelMixin | AI-powered code review, explanation, diff generation, test suggestion |
| EXECUTE | ExecutionMixin | Claude API request execution with exponential backoff retry |
| EXECUTE | FileOpsMixin | AI-guided file editing and creation |
| EXECUTE | SessionMixin | Multi-turn conversation session management |
| EXECUTE | SystemOpsMixin | Directory scanning, shell command execution, project analysis |
| EXECUTE | ToolsMixin | Tool registration, execution, and agentic tool-use loops |

## Key Exports

| Export | Type | Source File |
|--------|------|-------------|
| (mixins are imported by ClaudeClient directly) | - | `__init__.py` |

## Mixin Summary

| Mixin | File | Key Methods |
|-------|------|-------------|
| CodeIntelMixin | `code_intel.py` | `review_code`, `explain_code`, `suggest_tests`, `generate_diff` |
| ExecutionMixin | `execution.py` | `_execute_impl`, `_execute_with_retry`, `_stream_impl`, `_calculate_cost` |
| FileOpsMixin | `file_ops.py` | `edit_file`, `create_file`, `_extract_code_block` |
| SessionMixin | `session.py` | `execute_with_session`, `create_session` |
| SystemOpsMixin | `system_ops.py` | `scan_directory`, `run_command`, `get_project_structure` |
| ToolsMixin | `tools.py` | `register_tool`, `execute_tool_call`, `execute_with_tools`, `get_registered_tools` |

## Quick Start

```python
# Mixins are consumed by ClaudeClient -- not used standalone.
# Example via the assembled client:
from codomyrmex.agents.claude import ClaudeClient

client = ClaudeClient(model="claude-3-5-sonnet-20241022")

# CodeIntelMixin
result = client.review_code("def add(a, b): return a + b", language="python")

# FileOpsMixin
edit = client.edit_file("/path/to/file.py", "Add type hints to all parameters")

# ToolsMixin
client.register_tool(
    name="calculator",
    description="Perform arithmetic",
    input_schema={"type": "object", "properties": {"expression": {"type": "string"}}},
    handler=lambda expression: eval(expression),
)
```

## Architecture

```
agents/claude/mixins/
    __init__.py          # Package marker
    code_intel.py        # CodeIntelMixin -- review, explain, diff, test suggestions
    execution.py         # ExecutionMixin -- API calls, retry, streaming, cost calc
    file_ops.py          # FileOpsMixin -- edit_file, create_file
    session.py           # SessionMixin -- multi-turn session management
    system_ops.py        # SystemOpsMixin -- directory scan, shell exec, project analysis
    tools.py             # ToolsMixin -- tool registration and agentic tool-use loop
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/agents/claude/ -v
```

## Navigation

- Parent: [`agents/claude/`](../README.md)
- Grandparent: [`agents/`](../../README.md)
- Project root: [`/`](../../../../../README.md)
