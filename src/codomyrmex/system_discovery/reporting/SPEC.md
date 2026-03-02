# Reporting -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides system status reporting and hardware/environment profiling for the
Codomyrmex ecosystem. Generates comprehensive diagnostic reports covering
Python environment, project structure, dependency availability, git repository
state, and external tool detection.

## Architecture

`StatusReporter` aggregates results from five independent check methods into a
unified dict. Each check is isolated so a failure in one (e.g., git not
available) does not block the others. `HardwareProfiler` and
`EnvironmentProfiler` are stateless utility classes using `psutil` and
environment-variable inspection respectively.

## Key Classes

### `StatusReporter`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `check_python_environment` | -- | `dict[str, Any]` | Python version, executable, venv status, platform |
| `check_project_structure` | -- | `dict[str, Any]` | Presence of src, testing, docs dirs and config files |
| `check_dependencies` | -- | `dict[str, Any]` | Importability of 14 packages with success rate |
| `check_git_status` | -- | `dict[str, Any]` | Branch, remotes, recent commits, staged/unstaged counts |
| `check_external_tools` | -- | `dict[str, bool]` | Availability of git, npm, node, docker, uv |
| `generate_comprehensive_report` | -- | `dict[str, Any]` | Aggregated report from all checks above |
| `display_status_report` | -- | `None` | Pretty-prints the report to stdout with colour |
| `export_report` | `filename: str \| None` | `str` | Export report as JSON file; returns path |

### `HardwareProfiler`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `get_hardware_info` | -- | `dict[str, Any]` | CPU count, frequency, RAM (GB), OS, architecture |

### `EnvironmentProfiler`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `get_environment_type` | -- | `str` | One of: `ci_github`, `ci_travis`, `docker`, `kubernetes`, `local` |
| `get_python_info` | -- | `dict[str, Any]` | Python version string, executable path, `sys.path` |

## Dependencies

- **Internal**: `logging_monitoring.core.logger_config`, `terminal_interface.utils.terminal_utils`
- **External**: `psutil` (hardware profiling), `subprocess` (git and tool detection)

## Constraints

- Git subprocess calls use a 10-second timeout to avoid blocking.
- `check_dependencies` tests 14 specific packages; the list is not auto-discovered.
- `HardwareProfiler` requires `psutil`; guard with `@pytest.mark.skipif` in tests.
- `TerminalFormatter` is optional; `format_message` degrades to plain text if unavailable.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- All git subprocess errors are caught and logged; partial results are returned.
- Import failures in `check_dependencies` return `False` per package, not exceptions.
- All errors logged before propagation.
