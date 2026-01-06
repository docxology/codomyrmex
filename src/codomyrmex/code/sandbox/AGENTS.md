# Codomyrmex Agents — code/sandbox

## Signposting
- **Parent**: [Code Module](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Siblings**: [execution](../execution/AGENTS.md), [review](../review/AGENTS.md), [monitoring](../monitoring/AGENTS.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Sandbox submodule providing isolated code execution environments with Docker containerization, resource limits, and security controls.

## Key Components

- `container.py` – Docker container management
- `isolation.py` – Process isolation utilities
- `resource_limits.py` – Resource limit definitions
- `security.py` – Security policies and access controls

## Function Signatures

```python
def run_code_in_docker(code: str, language: str, limits: ExecutionLimits = None) -> ExecutionResult
def check_docker_available() -> bool
```


## Active Components

### Core Files
- `__init__.py` – Package initialization
- Other module-specific implementation files

## Operating Contracts

### Universal Execution Protocols
1. **Container Isolation** - Execute code in isolated containers
2. **Resource Limits** - Enforce CPU, memory, and time limits
3. **Security Policies** - Apply security restrictions
4. **Cleanup** - Remove containers after execution

## Navigation Links
- **Parent**: [Code AGENTS](../AGENTS.md)
- **Human Documentation**: [README.md](README.md)
