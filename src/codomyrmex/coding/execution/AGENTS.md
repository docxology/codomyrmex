# Codomyrmex Agents — src/codomyrmex/coding/execution

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides code execution capabilities for running code snippets in sandboxed Docker environments. This module handles multi-language code execution with configurable timeouts, session management, and validation of supported languages.

## Active Components

- `executor.py` - Main execution engine with `execute_code()` function
- `language_support.py` - Language configuration and validation with `SUPPORTED_LANGUAGES`
- `session_manager.py` - Session tracking with `ACTIVE_SESSIONS` and `validate_session_id()`
- `__init__.py` - Module exports

## Key Classes and Functions

### executor.py
- **`execute_code(language, code, stdin, timeout, session_id)`** - Main entry point for executing code in a sandboxed Docker environment. Returns execution results including stdout, stderr, exit_code, execution_time, and status.
- **`validate_timeout(timeout)`** - Validates and normalizes timeout values within allowed range (1-300 seconds, default 30).
- **Constants**: `DEFAULT_TIMEOUT=30`, `MAX_TIMEOUT=300`, `MIN_TIMEOUT=1`

### language_support.py
- **`SUPPORTED_LANGUAGES`** - Dictionary mapping language names to their Docker images, file extensions, commands, and timeout factors. Supported languages:
  - `python` (python:3.9-slim)
  - `javascript` (node:14-alpine)
  - `java` (openjdk:11-jre-slim)
  - `cpp` (gcc:9)
  - `c` (gcc:9)
  - `go` (golang:1.19-alpine)
  - `rust` (rust:1.65-slim)
  - `bash` (bash:5.1)
- **`validate_language(language)`** - Checks if a language is supported.

### session_manager.py
- **`ACTIVE_SESSIONS`** - Dictionary tracking active execution session containers.
- **`validate_session_id(session_id)`** - Validates session ID format (alphanumeric, underscores, hyphens; max 64 chars).

## Operating Contracts

- All code execution occurs in isolated Docker containers with network disabled.
- Timeout validation ensures execution time remains within safe limits.
- Language validation prevents unsupported language execution attempts.
- Session IDs are validated to prevent injection attacks.
- Docker availability is checked before execution attempts.
- Temporary files are cleaned up after execution completes.

## Signposting

- **Dependencies**: Requires `sandbox` submodule for Docker container management and security utilities.
- **Parent Directory**: [coding](../README.md) - Parent module documentation.
- **Related Modules**:
  - `sandbox/` - Container execution and resource limits.
  - `monitoring/` - Execution monitoring and metrics.
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation.
