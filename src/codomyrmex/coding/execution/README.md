# coding/execution

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Secure code execution capabilities in sandboxed Docker environments. Supports multiple programming languages with configurable timeouts and session management for persistent execution contexts.

## Key Exports

- **`execute_code()`** -- Main function to execute code snippets; accepts language and source code, returns dict with stdout, stderr, and exit code
- **`SUPPORTED_LANGUAGES`** -- Dictionary of supported language configurations (name, Docker image, command, file extension)
- **`validate_language()`** -- Check if a given language string is supported
- **`validate_session_id()`** -- Validate and sanitize session identifiers for persistent execution contexts

## Directory Contents

- `__init__.py` - Package init; re-exports public API
- `executor.py` - Core execution logic with Docker integration
- `language_support.py` - Language configuration registry and validation
- `session_manager.py` - Session lifecycle and identifier validation
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [coding](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
