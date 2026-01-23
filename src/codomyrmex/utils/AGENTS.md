# Codomyrmex Agents - src/codomyrmex/utils

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The Utils module provides common utility functions and helpers used across the Codomyrmex codebase. It includes functions for file operations, JSON handling, hashing, timing, retries, environment variables, and dictionary manipulation, as well as comprehensive CLI helper utilities.

## Active Components

- `__init__.py` - Core utility functions (ensure_directory, JSON operations, hashing, decorators)
- `cli_helpers.py` - CLI-specific utilities (formatting, progress bars, error handling, file validation)
- `refined.py` - RefinedUtilities class with additional helper methods
- `API_SPECIFICATION.md` - API documentation
- `SPEC.md` - Technical specification

## Key Classes

- **RefinedUtilities** - Collection of refined utility methods

- **ProgressReporter** (cli_helpers) - Progress reporting for long-running operations
  - `update(increment, message)` - Advance progress with optional status
  - `set_current(current, message)` - Set absolute progress value
  - `complete(message)` - Mark progress as complete

## Operating Contracts

### Core Utilities (__init__.py)
- `ensure_directory(path)` - Create directory if needed, return Path
- `safe_json_loads(text, default)` - Parse JSON with fallback
- `safe_json_dumps(obj, indent, default)` - Serialize to JSON safely
- `hash_content(content, algorithm)` - Generate hash (sha256 default)
- `hash_file(path, algorithm)` - Hash file contents
- `timing_decorator` - Measure function execution time
- `retry(max_attempts, delay, backoff, exceptions)` - Retry with exponential backoff
- `get_timestamp(fmt)` - Get formatted timestamp
- `truncate_string(s, max_length, suffix)` - Truncate with suffix
- `get_env(key, default, required)` - Get environment variable with validation
- `flatten_dict(d, parent_key, sep)` - Flatten nested dictionary
- `deep_merge(base, override)` - Deep merge dictionaries

### CLI Helpers (cli_helpers.py)
- `format_table(data, headers)` - Format data as ASCII table
- `print_progress_bar(current, total, prefix)` - Simple progress bar
- `print_with_color(message, color)` - Colored terminal output
- `format_output(data, format_type, indent)` - Format as JSON or text
- `validate_file_path(path, must_exist, must_be_file, must_be_dir)` - Path validation
- `load_json_file(path)` - Load JSON with error handling
- `save_json_file(data, path, indent, create_parents)` - Save JSON file
- `print_section(title, separator, width, prefix)` - Section headers
- `print_success/error/warning/info(message)` - Consistent status messages
- `handle_common_exceptions(operation_name)` - Exception handling decorator
- `add_common_arguments(parser)` - Add --dry-run, --format, --verbose, --quiet
- `enhanced_error_context(operation, context)` - Context manager for error reporting

## Signposting

- **Parent Directory**: [codomyrmex](../README.md) - Main package documentation
- **Related Modules**:
  - [cli/](../cli/README.md) - CLI module using these utilities
  - [logging_monitoring/](../logging_monitoring/README.md) - Logging integration
- **Project Root**: [../../../README.md](../../../README.md) - Main project documentation
