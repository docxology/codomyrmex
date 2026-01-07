# utils

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Shared utilities for Codomyrmex orchestrator scripts. This module provides common functions and patterns used across all orchestrator scripts to ensure consistency and reduce code duplication.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `cli_helpers.py` – Shared CLI utilities and helpers

## Key Features

- **Progress Reporting**: Progress bars and status updates for long-running operations
- **Error Handling**: Consistent error reporting with context and correlation IDs
- **Output Formatting**: Table formatting, JSON/text output, colored messages
- **File Operations**: JSON file loading/saving with validation
- **CLI Utilities**: Common argument parsing and dry-run support
- **Path Validation**: File and directory path validation utilities

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.utils.cli_helpers import (
    ProgressReporter,
    format_table,
    print_success,
    print_error,
    validate_file_path,
    load_json_file,
    save_json_file
)

# Example: Progress reporting
reporter = ProgressReporter(total=100, prefix="Processing")
for i in range(100):
    reporter.update(1, f"Item {i}")
reporter.complete("Done")

# Example: Table formatting
data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
table = format_table(data, headers=["name", "age"])
print(table)

# Example: File operations
config = load_json_file("config.json")
save_json_file({"result": "success"}, "output.json")
```

