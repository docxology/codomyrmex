# Code Execution Submodule

## Signposting
- **Parent**: [Code Module](../README.md)
- **Siblings**: [sandbox](../sandbox/), [review](../review/), [monitoring](../monitoring/)
- **Key Artifacts**: [AGENTS.md](AGENTS.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

The execution submodule provides core code execution capabilities for the Codomyrmex code module. It handles language detection, session management, and safe code execution across multiple programming languages.

## Key Components

### executor.py
Main code execution engine supporting multiple languages with configurable timeouts and resource limits.

### language_support.py
Language detection and validation utilities. Supports Python, JavaScript, Go, Rust, and more.

### session_manager.py
Execution session lifecycle management for stateful code execution scenarios.

## Usage

```python
from codomyrmex.coding.execution import execute_code
from codomyrmex.coding.execution.language_support import SUPPORTED_LANGUAGES

# Execute Python code
result = execute_code("print('Hello, World!')", language="python")

# Check supported languages
print(SUPPORTED_LANGUAGES)
```

## Navigation Links

- **Parent**: [Code Module](../README.md)
- **Code AGENTS**: [../AGENTS.md](../AGENTS.md)
- **Source Root**: [src/codomyrmex](../../README.md)
