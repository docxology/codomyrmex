# coding/sandbox

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Sandboxing and isolation mechanisms for secure code execution. Provides Docker container execution, process-level resource limits, and temporary file management for safely running untrusted code.

## Key Exports

### Container Execution

- **`run_code_in_docker()`** -- Execute code inside a Docker container with configurable image and limits
- **`check_docker_available()`** -- Check if Docker daemon is accessible

### Resource Isolation

- **`ExecutionLimits`** -- Data class defining CPU, memory, and time limits for execution
- **`resource_limits_context()`** -- Context manager that enforces resource limits during execution
- **`execute_with_limits()`** -- Execute a callable with resource limits applied
- **`sandbox_process_isolation()`** -- Apply process-level isolation (namespaces, seccomp, etc.)

### Docker Configuration

- **`DEFAULT_DOCKER_ARGS`** -- Default Docker run arguments for sandboxed execution

### Temporary File Security

- **`prepare_code_file()`** -- Securely write code to a temporary file for execution
- **`prepare_stdin_file()`** -- Securely write stdin data to a temporary file
- **`cleanup_temp_files()`** -- Remove temporary files after execution

## Directory Contents

- `__init__.py` - Package init; re-exports from container, isolation, resource_limits, and security
- `container.py` - Docker container execution logic
- `isolation.py` - ExecutionLimits and process-level isolation
- `resource_limits.py` - Default Docker argument configuration
- `security.py` - Temporary file preparation and cleanup
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [coding](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
