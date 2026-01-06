# Codomyrmex Agents — code/execution

## Signposting
- **Parent**: [Code Module](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Siblings**: [sandbox](../sandbox/AGENTS.md), [review](../review/AGENTS.md), [monitoring](../monitoring/AGENTS.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Code execution submodule providing core execution capabilities for the Codomyrmex code module. Handles language detection, session management, and safe code execution.

## Key Components

- `executor.py` – Main execution engine
- `language_support.py` – Language detection and validation
- `session_manager.py` – Execution session lifecycle

## Function Signatures

```python
def execute_code(code: str, language: str, timeout: int = 30) -> ExecutionResult
```

Execute code in the specified language with optional timeout.


## Active Components

### Core Files
- `__init__.py` – Package initialization
- Other module-specific implementation files

## Operating Contracts

### Universal Execution Protocols
1. **Language Validation** - Validate language before execution
2. **Timeout Enforcement** - Respect timeout configurations
3. **Resource Management** - Clean up resources after execution
4. **Error Handling** - Return structured error information

## Navigation Links
- **Parent**: [Code AGENTS](../AGENTS.md)
- **Human Documentation**: [README.md](README.md)
