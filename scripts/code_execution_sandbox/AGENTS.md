# Codomyrmex Agents — scripts/code_execution_sandbox

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Code execution sandbox automation scripts providing command-line interfaces for secure code execution in isolated environments. This script module enables safe testing and execution of untrusted code across multiple programming languages.

The code_execution_sandbox scripts serve as the primary interface for developers and automated systems to execute code securely within Docker sandboxed environments.

## Module Overview

### Key Capabilities
- **Secure Code Execution**: Execute code in isolated Docker containers
- **Multi-Language Support**: Support for Python, JavaScript, Bash, and other languages
- **Timeout Management**: Configurable execution time limits
- **Input/Output Handling**: Support for stdin input and stdout/stderr capture
- **Session Management**: Optional persistent execution environments

### Key Features
- Command-line interface with argument parsing
- Integration with core code execution sandbox modules
- Structured output formatting (JSON, text, verbose)
- Error handling and validation
- Logging integration for execution tracking

## Function Signatures

### Core CLI Functions

```python
def main() -> None
```

Main CLI entry point for the code execution sandbox orchestrator.

**Command-line Usage:**
```bash
python orchestrate.py [command] [options]
```

**Available Commands:**
- `execute` - Execute code in sandboxed environment

**Global Options:**
- `--verbose, -v` - Enable verbose output
- `--timeout, -t` - Execution timeout in seconds

```python
def handle_execute(args) -> None
```

Handle code execution commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `language` (str): Programming language ("python", "javascript", "bash", etc.)
  - `code` (str): Code to execute (can be file path or inline code)
  - `input` (str, optional): Standard input to provide to the program
  - `timeout` (int, optional): Maximum execution time in seconds. Defaults to 30
  - `session_id` (str, optional): Session identifier for persistent environments
  - `output_format` (str, optional): Output format ("json", "text"). Defaults to "text"

**Returns:** None (executes code and outputs results to stdout)

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `orchestrate.py` – Main CLI orchestrator script

### Documentation
- `README.md` – Script usage and overview
- `AGENTS.md` – This coordination document

### Supporting Files
- Integration with `_orchestrator_utils.py` for shared utilities

## Operating Contracts

### Universal Script Protocols

All scripts in this module must:

1. **CLI Standards**: Follow consistent command-line argument patterns
2. **Error Handling**: Provide clear error messages and exit codes
3. **Logging Integration**: Use centralized logging for all operations
4. **Security First**: Ensure all execution occurs in sandboxed environments
5. **Resource Limits**: Enforce CPU, memory, and time constraints

### Module-Specific Guidelines

#### Code Execution
- Validate all code and input before execution
- Execute only in properly configured Docker containers
- Provide clear execution results and error messages
- Support both file-based and inline code execution

#### Sandbox Management
- Ensure Docker containers are properly isolated
- Clean up containers after execution
- Monitor resource usage during execution
- Handle execution timeouts gracefully

#### Input Validation
- Validate programming language support
- Sanitize input data and code
- Check file paths and permissions
- Prevent execution of potentially harmful code

## Navigation Links

### Module Documentation
- **Script Overview**: [README.md](README.md) - Complete script documentation

### Related Scripts

### Platform Navigation
- **Scripts Directory**: [../README.md](../README.md) - Scripts directory overview

## Agent Coordination

### Integration Points

When integrating with other scripts:

1. **Shared Utilities**: Use `_orchestrator_utils.py` for common CLI patterns
2. **Security Coordination**: Coordinate with security_audit for code validation
3. **Output Consistency**: Maintain consistent output formats
4. **Resource Monitoring**: Share execution metrics and limits

### Quality Gates

Before script changes are accepted:

1. **CLI Testing**: All command-line options work correctly
2. **Execution Testing**: Code executes successfully in sandboxed environment
3. **Security Testing**: Sandbox properly isolates execution
4. **Integration Testing**: Scripts work with core code execution modules

## Version History

- **v0.1.0** (December 2025) - Initial code execution sandbox automation scripts with secure CLI interface
