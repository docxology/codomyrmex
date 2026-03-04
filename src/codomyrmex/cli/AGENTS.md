# Agent Guidelines - CLI

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

The `cli` module is the primary user interface for the Codomyrmex platform. Uses `google-fire` to
map a Python `Cli` class to command-line sub-commands. Handlers live in `handlers/` and are
dispatched via the `Cli` class in `core.py`. No MCP tools — the CLI is consumed by human operators
and shell scripts, not PAI agents via MCP.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Module entry point |
| `core.py` | `Cli` class — main `fire` entrypoint; all top-level commands |
| `handlers/` | Handler functions by domain (`ai.py`, `workflow.py`, `project.py`, etc.) |
| `handlers/__init__.py` | Exports all handler functions |
| `utils.py` | `print_success()`, `print_error()`, `print_warning()` — consistent output helpers |
| `formatters.py` | Output formatting helpers for tables and JSON |
| `doctor.py` | `DoctorCheck` — environment health diagnostics |

## Key Classes

- **`Cli`** (`core.py`) — Root `fire` class; all `codomyrmex` sub-commands are methods
- **`DoctorCheck`** (`doctor.py`) — Environment diagnostics and health reporting
- **`print_success()`**, **`print_error()`**, **`print_warning()`** — Consistent output helpers

## Agent Instructions

1. **Zero-Mock Policy** — When writing tests for the CLI, **do not use mocks**; exercise real handlers
2. **Graceful Imports** — Use lazy imports or `try-except ImportError` in handlers; CLI must remain usable without optional modules
3. **Consistent Formatting** — Use `print_success`, `print_error`, `print_warning` from `utils.py`
4. **Method Documentation** — Every `Cli` method needs a docstring; `fire` uses them for help text
5. **Subcommand Grouping** — Group related functionality into logical subcommands (`ai`, `workflow`, `fpf`)

## Operating Contracts

- All handler functions must return `True` on success, `False` on failure — never raise unhandled exceptions
- `print_success()`, `print_error()`, and `print_warning()` are the only permitted output paths in handlers
- The `Cli` class is the sole entrypoint — no direct calls to handler functions from outside `cli/`
- New commands must use lazy imports: `from codomyrmex.my_module import X` inside the function body
- **DO NOT** import heavy modules at module-level in `core.py` — this slows CLI startup

## Common Patterns

### Adding a New Command Group

1. Create a new handler file in `handlers/` (e.g., `my_feature.py`)
2. Implement handler functions with proper error handling
3. Export them in `handlers/__init__.py`
4. Add a method to the `Cli` class in `core.py` that dispatches to these handlers

### Robust Handler Implementation

```python
def handle_my_command(param):
    try:
        from codomyrmex.my_module import real_logic
        result = real_logic(param)
        print_success("Operation completed")
        return True
    except ImportError:
        print_error("My Module not available")
        return False
    except Exception as e:
        print_error(f"Failed: {e}")
        return False
```

## Testing Patterns

```python
def test_my_command_integrated():
    from codomyrmex.cli.core import Cli
    cli = Cli()
    # Exercise real command logic — no mocks
    result = cli.my_command(param="value")
    assert result is True
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | None — Python import / shell execution only | TRUSTED |
| **Architect** | Read + Design | None — design command hierarchy and API specs | OBSERVED |
| **QATester** | Validation | None — run integrated CLI tests and doctor checks | OBSERVED |
| **Researcher** | Read-only | None — inspect CLI command structure | SAFE |

### Engineer Agent
**Use Cases**: Building and maintaining CLI handlers during BUILD, adding new command groups.

### Architect Agent
**Use Cases**: Defining command hierarchy, reviewing API specs, planning subcommand taxonomy.

### QATester Agent
**Use Cases**: Running integrated CLI tests during VERIFY, confirming doctor check results.

### Researcher Agent
**Use Cases**: Inspecting CLI command structure and handler implementations for analysis.

## Navigation

- [README](README.md) | [SPEC](SPEC.md)


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/cli.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/cli.cursorrules)
