# Codomyrmex Agents — src/codomyrmex/environment_setup

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Foundation Layer module providing environment validation, dependency checking, and setup verification for the Codomyrmex platform. Ensures all required tools and dependencies are available before operations.

## Active Components

### Environment Checker

- `env_checker.py` - Main environment validation
  - Key Classes: `EnvironmentChecker`, `DependencyValidator`
  - Key Functions: `check_environment()`, `validate_dependencies()`, `get_python_version()`

### Scripts

- `scripts/` - Setup and validation scripts
  - Setup automation and environment configuration

## Key Classes and Functions

| Class/Function | Purpose |
| :--- | :--- |
| `EnvironmentChecker` | Main class for environment validation |
| `DependencyValidator` | Validate required dependencies |
| `check_environment()` | Comprehensive environment check |
| `validate_dependencies()` | Check required package versions |
| `get_python_version()` | Get current Python version |
| `check_tool_available()` | Check if external tool is installed |

## Operating Contracts

1. **Foundation Status**: No dependencies on other Codomyrmex modules
2. **Early Execution**: Should be called early in application startup
3. **Fail Fast**: Raises clear errors for missing dependencies
4. **Logging**: Uses standard Python logging (not logging_monitoring)
5. **MCP Tools**: Exposes environment check tools via MCP

## Usage Example

```python
from codomyrmex.environment_setup import (
    EnvironmentChecker,
    check_environment,
    validate_dependencies
)

# Quick check
check_environment()

# Detailed validation
checker = EnvironmentChecker()
result = checker.validate_all()
if not result.is_valid:
    print(f"Missing: {result.missing_dependencies}")
```

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules (Foundation Layer)

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| logging_monitoring | [../logging_monitoring/AGENTS.md](../logging_monitoring/AGENTS.md) | Logging infrastructure |
| terminal_interface | [../terminal_interface/AGENTS.md](../terminal_interface/AGENTS.md) | Terminal UI |
| model_context_protocol | [../model_context_protocol/AGENTS.md](../model_context_protocol/AGENTS.md) | MCP standards |

### Related Documentation

- [README.md](README.md) - User documentation
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) - MCP tools
- [SPEC.md](SPEC.md) - Functional specification
