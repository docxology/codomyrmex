# Codomyrmex Agents — src/codomyrmex/coding/execution

## Signposting
- **Parent**: [coding](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Code execution capabilities including language support and session management. Provides execution of code snippets in sandboxed environments with support for multiple programming languages, session management for persistent environments, and timeout handling.

## Active Components
- `README.md` – Project file
- `__init__.py` – Module exports and public API
- `executor.py` – Code execution engine
- `language_support.py` – Programming language support definitions
- `session_manager.py` – Session management for persistent environments

## Key Classes and Functions

### execute_code (`executor.py`)
- `execute_code(language: str, code: str, stdin: Optional[str] = None, timeout: Optional[int] = None, session_id: Optional[str] = None) -> dict[str, Any]` – Execute a code snippet in a sandboxed environment
- Returns dictionary with: stdout, stderr, exit_code, execution_time, status

### validate_timeout (`executor.py`)
- `validate_timeout(timeout: Optional[int]) -> int` – Validate and normalize timeout value (default: 30, max: 300, min: 1)

### Language Support (`language_support.py`)
- `SUPPORTED_LANGUAGES` – Dictionary of supported programming languages and their configurations
- `validate_language(language: str) -> bool` – Validate if language is supported

### Session Management (`session_manager.py`)
- `validate_session_id(session_id: str | None) -> str | None` – Validate session ID format

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [coding](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation