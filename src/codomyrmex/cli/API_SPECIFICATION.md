# CLI Module API Specification

**Version**: v1.1.9 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview

The `cli` module is the command-line interface entry point for Codomyrmex. It processes user commands, dispatches to handlers, and manages interactive sessions.

## 2. Core Components

### 2.1 Entry Point

- **`main(argv: list[str] | None = None) -> int`**: The entry point invoked by the `codomyrmex` command. It runs the command (``argv`` defaults to `sys.argv[1:]`) and returns the process exit status; the console script passes it to `sys.exit`.
- **`exit_code(result) -> int`** (in `codomyrmex.cli.core`): Maps a command's return value to that status. `False` is 1, an `int` is used as-is (out-of-range values become 1), anything else is 0. Bool and int results are not printed.

### 2.2 Handlers

The module exports numerous handlers for specific command groups:

- **Project**: `handle_project_create`, `handle_project_list`, `handle_project_build`.
- **Workflow**: `handle_workflow_create`, `list_workflows`, `run_workflow`.
- **AI**: `handle_ai_generate`, `handle_ai_refactor`.
- **FPF**: `handle_fpf_fetch`, `handle_fpf_parse`, `handle_fpf_visualize`.
- **System**: `check_environment`, `show_system_status`.

### 2.3 Demonstration

- `demo_data_visualization`
- `demo_ai_code_editing`
- `demo_code_execution`

## 3. Usage Example

```bash
# General usage
codomyrmex <command> [options]

# Interactive mode
codomyrmex shell
```

```python
# Programmatic invocation: returns the exit status instead of exiting
from codomyrmex.cli import main

status = main(["workflow", "list"])
```
