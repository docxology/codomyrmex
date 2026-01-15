# CLI Module API Specification

**Version**: v0.1.0 | **Status**: Stable | **Last Updated**: January 2026

## 1. Overview
The `cli` module is the command-line interface entry point for Codomyrmex. It processes user commands, dispatches to handlers, and manages interactive sessions.

## 2. Core Components

### 2.1 Entry Point
- **`main()`**: The primary execution function invoked by the `codomyrmex` command.

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
# Programmatic invocation
from codomyrmex.cli import main
main()
```
