# execution

## Signposting
- **Parent**: [coding](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Code execution capabilities including language support and session management. Provides execution of code snippets in sandboxed environments with support for multiple programming languages, session management for persistent environments, and timeout handling.

## Directory Contents
- `README.md` – File
- `__init__.py` – File
- `executor.py` – File
- `language_support.py` – File
- `session_manager.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [coding](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.coding.execution import (
    execute_code,
    SUPPORTED_LANGUAGES,
    validate_language,
    validate_session_id,
)

# Execute Python code
result = execute_code(
    code="print('Hello, World!')",
    language="python",
    session_id="session_123",
    timeout=30
)
print(f"Output: {result.output}")
print(f"Error: {result.error}")

# Check supported languages
print(f"Supported: {SUPPORTED_LANGUAGES}")

# Validate language
if validate_language("python"):
    print("Python is supported")
```

