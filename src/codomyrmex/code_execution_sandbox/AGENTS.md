# Codomyrmex Agents — src/codomyrmex/code_execution_sandbox

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Code Execution Sandbox Agents](AGENTS.md)
- **Children**:
    - [docs](docs/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Core module providing secure code execution capabilities within isolated sandboxed environments for the Codomyrmex platform. This module enables safe execution of untrusted code across multiple programming languages using Docker containerization to prevent system compromise.

The code_execution_sandbox module serves as a critical security boundary, allowing dynamic code execution while maintaining platform integrity.

## Module Overview

### Key Capabilities
- **Multi-Language Support**: Execute code in Python, JavaScript, Bash, and other languages
- **Container Isolation**: Docker-based sandboxing for security and resource control
- **Timeout Protection**: Configurable execution time limits to prevent infinite loops
- **Input/Output Handling**: Support for stdin input and stdout/stderr capture
- **Session Management**: Optional persistent execution environments
- **Security Validation**: Input sanitization and execution restrictions

### Key Features
- Docker container isolation with resource limits
- Support for multiple programming languages
- Configurable execution timeouts and memory limits
- Structured execution results with timing and status information
- Integration with logging system for execution tracking
- Error handling and recovery mechanisms

## Function Signatures

### Core Functions

```python
def execute_code(
    language: str,
    code: str,
    stdin: Optional[str] = None,
    timeout: Optional[int] = None,
    session_id: Optional[str] = None,
) -> dict[str, Any]
```

Executes code in a sandboxed Docker environment with security isolation.

**Parameters:**
- `language` (str): Programming language of the code ("python", "javascript", "bash", etc.)
- `code` (str): Source code to execute
- `stdin` (Optional[str]): Standard input to provide to the program
- `timeout` (Optional[int]): Maximum execution time in seconds (default: 30)
- `session_id` (Optional[str]): Session identifier for persistent execution environments

**Returns:** Dictionary containing execution results with keys: "stdout", "stderr", "exit_code", "execution_time", "status"

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `code_executor.py` – Main execution engine and sandbox management

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `MCP_TOOL_SPECIFICATION.md` – AI agent tool specifications
- `SECURITY.md` – Security considerations and sandboxing details
- `CHANGELOG.md` – Version history and updates

### Supporting Files
- `requirements.txt` – Module dependencies (docker, security libraries)
- `docs/` – Additional documentation
- `tests/` – Comprehensive test suite

## Operating Contracts

### Universal Execution Protocols

All code execution within the Codomyrmex platform must:

1. **Security First** - All execution occurs within sandboxed environments
2. **Resource Limits** - Enforce CPU, memory, and time constraints on execution
3. **Input Validation** - Sanitize and validate all code and input data
4. **Error Containment** - Prevent execution errors from compromising the platform
5. **Audit Logging** - Log all execution attempts and results for monitoring

### Module-Specific Guidelines

#### Sandbox Management
- Use Docker containers for complete isolation
- Configure appropriate resource limits for each language
- Implement timeout mechanisms to prevent runaway execution
- Validate container images for security and compatibility

#### Code Execution
- Support multiple programming languages with appropriate runtimes
- Provide clear execution results with stdout, stderr, and exit codes
- Handle compilation and runtime errors gracefully
- Support both one-off execution and persistent sessions

#### Security Controls
- Restrict network access from sandboxed environments
- Limit file system access to necessary directories
- Prevent execution of potentially harmful system commands
- Validate and sanitize all user-provided code

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification (if applicable)
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Practical usage demonstrations (if applicable)

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Source Root**: [src](../../README.md) - Source code documentation