# Utils Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The Utils module provides a comprehensive collection of CLI helper utilities and common functions used throughout Codomyrmex. It includes progress reporting, table formatting, output handling, file operations, and enhanced error context management.

## Key Features

- **Progress Reporting**: Visual progress bars for long-running operations
- **Table Formatting**: Consistent, readable table output for CLI data display
- **Colored Output**: Terminal color support for status messages (success, error, warning)
- **File Operations**: JSON loading/saving with consistent error handling
- **Path Validation**: Flexible file and directory path validation
- **Dry-Run Support**: Execution planning and confirmation for destructive operations
- **Error Context**: Enhanced context managers for detailed error reporting
- **Common Arguments**: Standardized CLI argument patterns (verbose, dry-run, output format)

## Quick Start

```python
from codomyrmex.utils import (
    ProgressReporter,
    format_table,
    print_with_color,
    load_json_file,
    save_json_file,
    validate_file_path,
)

# Progress reporting
progress = ProgressReporter(total=100, prefix="Processing")
for i in range(100):
    progress.update(1, f"Step {i}")
progress.complete("All done!")

# Table formatting
data = [{"name": "Alice", "score": 95}, {"name": "Bob", "score": 87}]
print(format_table(data, headers=["name", "score"]))

# Colored output
print_with_color("Success!", color="green")
print_with_color("Warning: check configuration", color="yellow")

# File operations
config = load_json_file("config.json")
save_json_file({"result": "success"}, "output.json")

# Path validation
path = validate_file_path("./data", must_exist=True, must_be_dir=True)
```

## Module Structure

| File | Description |
|------|-------------|
| `__init__.py` | Module exports and public API |
| `cli_helpers.py` | CLI utility functions and classes |
| `AGENTS.md` | Technical documentation for AI agents |
| `SPEC.md` | Functional specification |

## Key Components

### ProgressReporter
A reusable progress bar class for tracking long-running operations with visual feedback.

### Output Formatting
- `format_table()`: Create aligned ASCII tables from list data
- `format_output()`: Format data as JSON or text with consistent styling
- `print_with_color()`: Emit colored terminal output when supported

### File Operations
- `load_json_file()`: Load and parse JSON with error handling
- `save_json_file()`: Write JSON with optional parent directory creation
- `validate_file_path()`: Validate paths with flexible existence/type requirements

### CLI Utilities
- `add_common_arguments()`: Add standard flags (--verbose, --dry-run, --output-format)
- `validate_dry_run()`: Confirm dry-run mode with user
- `create_dry_run_plan()`: Generate execution plan for review
- `enhanced_error_context()`: Context manager for rich error reporting

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)
