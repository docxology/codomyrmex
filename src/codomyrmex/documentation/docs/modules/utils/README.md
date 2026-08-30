<!-- readme: generated -->

# utils

**Version**: v1.2.8 | **Status**: Active | **Source**: `src/codomyrmex/utils/`

## Overview

Utilities Package.

Common utility functions and helpers used across the codomyrmex codebase.

This package provides:
- Subprocess execution utilities (run_command, run_command_async, etc.)
- JSON handling utilities (safe_json_loads, safe_json_dumps)
- File/path utilities (ensure_directory, hash_file)
- Retry decorators and timing utilities
- Script execution base classes

## Submodules

| Submodule | Description |
|-----------|-------------|
| `i18n:` | Consolidated i18n capabilities. |

## Public Exports

`utils` exports 44 public symbols via `__all__`:

`CommandError`, `CommandErrorType`, `ConfigurableScript`, `HealthChecker`, `HealthStatus`, `ModuleRegistry`, `RefinedUtilities`, `RetryConfig`, `ScriptBase`, `ScriptConfig`, `ScriptResult`, `SubprocessResult`, `async_retry`, `async_timed_operation`, `check_command_available`, `deep_merge`, `ensure_directory`, `flatten_dict`, `gather_with_concurrency`, `get_command_version`, `get_env`, `get_timestamp`, `hash_content`, `hash_file` …

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../utils/](../../../../utils/)
