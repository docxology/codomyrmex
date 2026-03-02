# cli - Functional Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

The `cli` module provides a unified, structured command-line interface for the Codomyrmex ecosystem. It enables both human users and AI agents to interact with the platform's diverse capabilities through a consistent API.

## Architecture

The CLI uses a "Thin Dispatcher" pattern:

1. **Entry Point (`core.py`)**: Defines the `Cli` class which maps methods to CLI commands using `google-fire`.
2. **Handlers (`handlers/`)**: Logic for each command group is isolated in dedicated modules.
3. **Utilities (`utils.py`)**: Common formatting, logging, and capability detection.
4. **Doctor (`doctor.py`)**: Specialized diagnostic logic for system health.

## Core Components

### `Cli` Class
The central hub for all commands. Methods are automatically exposed as subcommands.
- Uses `fire.Fire(Cli)` for automatic CLI generation.
- Handles global flags like `--verbose` and `--performance`.

### Command Handlers
Located in `src/codomyrmex/cli/handlers/`:
- `system.py`: Environment checks, info, and status.
- `ai.py`: LLM-powered code editing.
- `analysis.py`: Static analysis and module testing.
- `orchestration.py`: Project and workflow management.
- `fpf.py`: First Principles Framework operations.
- `skills.py`: Skill registry management.
- `quick.py`: Composable orchestration primitives (`run`, `pipe`, `batch`).

## Behavioral Requirements

- **Module Independence**: The CLI must start even if optional dependencies are missing.
- **Clear Feedback**: Errors must be descriptive and actionable.
- **Exit Codes**:
  - `0`: Success.
  - `1`: Functional error or invalid arguments.
  - `2`: System-level failure.
- **Interactivity**: Support for interactive shells and dashboards.

## Testing Strategy

- **Zero-Mock Policy**: All CLI tests must use real functional components. No mocking of internal logic or subprocesses (unless strictly necessary for environment isolation).
- **Integrated Verification**: Tests in `test_cli_integrated.py` verify the end-to-end command flow.

## Dependencies

- **Core**: `fire`, `fire-python` (built-in)
- **Optional**: `matplotlib`, `docker`, `jsonschema`, and various Codomyrmex internal modules.

## Navigation

- [README](README.md)
- [Agent Guidelines](AGENTS.md)
- [Project Root](../../../README.md)
