# Codomyrmex Agents — src/codomyrmex/ide/cursor

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Coordinate agent work for the Cursor IDE integration module.  
This module provides a real, filesystem-backed `CursorClient` implementation of the shared `IDEClient` contract.

## Active Components

- `__init__.py` — Defines `CursorClient` and all Cursor command/rules/model behaviors.
- `README.md` — Human-facing usage and verification guide.
- `SPEC.md` — Functional contracts and behaviors.
- `PAI.md` — AI integration context.
- `AGENTS.md` — This coordination document.

## Implementation Contracts

- `CursorClient` must honor the `IDEClient` interface from `codomyrmex.ide`.
- `connect()` and `disconnect()` must keep `IDEStatus` accurate (`CONNECTING`, `CONNECTED`, `DISCONNECTED`, `ERROR`).
- `execute_command()` must reject unknown commands with `CommandExecutionError`.
- Rules updates must write UTF-8 content to workspace `.cursorrules`.
- Model selection must update internal active-model state only for known models.

## Testing Contracts

- Use zero-mock tests with real filesystem state (`tmp_path` / temp directories).
- Keep these suites green after changes:
  - `src/codomyrmex/tests/unit/ide/test_cursor_impl.py`
  - `src/codomyrmex/tests/unit/ide/test_cursor_settings.py`
  - `src/codomyrmex/tests/unit/ide/test_ide.py` (Cursor sections)

## Navigation

- **Parent Directory**: [ide](../README.md)
- **Project Root**: [README](../../../../README.md)
- **Sibling Docs**: [README](README.md) · [SPEC](SPEC.md) · [PAI](PAI.md)
