# Code Sandbox Submodule

## Signposting
- **Parent**: [Code Module](../README.md)
- **Siblings**: [execution](../execution/), [review](../review/), [monitoring](../monitoring/)
- **Key Artifacts**: [AGENTS.md](AGENTS.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

The sandbox submodule provides isolated code execution environments with Docker containerization, resource limits, and security controls. It ensures safe execution of untrusted code.

## Key Components

### container.py
Docker container management for isolated code execution environments.

### isolation.py
Process isolation and sandboxing utilities for secure code execution.

### resource_limits.py
Resource limit definitions and enforcement (CPU, memory, time limits).

### security.py
Security policies and access controls for sandboxed execution.

## Usage

```python
from codomyrmex.coding.sandbox import run_code_in_docker, check_docker_available
from codomyrmex.coding.sandbox.resource_limits import ExecutionLimits

# Check Docker availability
if check_docker_available():
    result = run_code_in_docker("print('Safe execution')", language="python")

# Custom resource limits
limits = ExecutionLimits(timeout=30, memory_limit="512m")
```

## Navigation Links

- **Parent**: [Code Module](../README.md)
- **Code AGENTS**: [../AGENTS.md](../AGENTS.md)
- **Source Root**: [src/codomyrmex](../../README.md)
