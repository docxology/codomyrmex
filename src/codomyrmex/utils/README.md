# Utilities Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Common utility functions and helpers used across the entire Codomyrmex codebase. Provides subprocess execution with error handling and retry, safe JSON serialization/deserialization, file hashing, directory management, retry decorators with exponential backoff, timing measurement, environment variable access, dictionary operations (flatten, deep merge), string truncation, and script execution base classes.

## Key Exports

### Core Utilities

- **`ensure_directory()`** -- Create a directory (and parents) if it does not exist, returns the Path
- **`safe_json_loads()`** -- Parse JSON with a fallback default value on failure
- **`safe_json_dumps()`** -- Serialize to JSON with a fallback string on failure; uses `default=str` for non-serializable types
- **`hash_content()`** -- Generate a hex digest hash (sha256/sha512/md5) of string or bytes content
- **`hash_file()`** -- Generate a hex digest hash of a file's contents, returns None if file not found
- **`timing_decorator`** -- Decorator that measures function execution time in milliseconds; injects `execution_time_ms` into dict results
- **`retry()`** -- Decorator for retrying failed operations with configurable max attempts, delay, exponential backoff, and exception filter
- **`get_timestamp()`** -- Get current timestamp as a formatted string (default: `%Y-%m-%d_%H-%M-%S`)
- **`truncate_string()`** -- Truncate a string to a maximum length with a configurable suffix
- **`get_env()`** -- Get an environment variable with optional default and required-or-raise behavior
- **`flatten_dict()`** -- Flatten a nested dictionary into dot-separated keys
- **`deep_merge()`** -- Deep merge two dictionaries with override semantics

### Script Base Classes

- **`ScriptBase`** -- Abstract base class for runnable scripts with lifecycle hooks
- **`ScriptConfig`** -- Configuration dataclass for script execution parameters
- **`ScriptResult`** -- Result container for script execution output and status
- **`ConfigurableScript`** -- Script base with built-in configuration loading
- **`run_script()`** -- Execute a ScriptBase instance with config

### Subprocess Utilities

- **`run_command()`** -- Run a shell command synchronously with timeout and error handling
- **`run_command_async()`** -- Run a shell command asynchronously
- **`stream_command()`** -- Run a command with real-time output streaming
- **`run_with_retry()`** -- Run a command with automatic retry on failure
- **`SubprocessResult`** -- Result of subprocess execution with stdout, stderr, return code
- **`CommandError`** -- Exception for command execution failures
- **`CommandErrorType`** -- Classification of command errors (timeout, permission, not_found, etc.)
- **`check_command_available()`** -- Check whether a command exists on the system PATH
- **`get_command_version()`** -- Get the version string of an installed command
- **`quote_command()`** -- Safely quote a command string for shell execution
- **`split_command()`** -- Split a command string into arguments list

### Refined Utilities

- **`RefinedUtilities`** -- Extended utility class with additional refined helper methods

## Directory Contents

- `__init__.py` - Module exports combining core utilities, subprocess, script base, and refined utilities
- `subprocess.py` - Subprocess execution: run_command, streaming, retry, error types
- `script_base.py` - ScriptBase ABC, ScriptConfig, ScriptResult, ConfigurableScript
- `refined.py` - RefinedUtilities class with extended helpers
- `cli_helpers.py` - CLI-specific helper functions
- `AGENTS.md` - Agent integration specification
- `API_SPECIFICATION.md` - Detailed API documentation
- `SPEC.md` - Module specification
- `PAI.md` - PAI integration notes

## Quick Start

```python
from codomyrmex.utils import ensure_directory, safe_json_loads

# Ensure a directory exists, creating it if necessary.
result = ensure_directory()

# Safely parse JSON with a fallback default.
output = safe_json_loads()
```

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k utils -v
```

## Consolidated Sub-modules

The following modules have been consolidated into this module as sub-packages:

| Sub-module | Description |
|------------|-------------|
| **`i18n/`** | Internationalization support (babel, gettext) |

Original standalone modules remain as backward-compatible re-export wrappers.

## Navigation

- **Full Documentation**: [docs/modules/utils/](../../../docs/modules/utils/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
