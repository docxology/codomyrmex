# Codomyrmex Agents — src/codomyrmex/coding/sandbox

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides sandboxing and isolation mechanisms for secure code execution. This module manages Docker container lifecycle, enforces resource limits, handles file preparation, and ensures security constraints are applied to all executed code.

## Active Components

- `container.py` - Docker container management with `run_code_in_docker()`
- `isolation.py` - Process isolation and resource enforcement with `ExecutionLimits`
- `resource_limits.py` - Default Docker security arguments configuration
- `security.py` - File preparation and cleanup utilities
- `__init__.py` - Module exports

## Key Classes and Functions

### container.py
- **`run_code_in_docker(language, code_file_path, temp_dir, stdin_file, timeout, session_id)`** - Executes code in a Docker container with security constraints. Manages container lifecycle including timeout handling and cleanup.
- **`check_docker_available()`** - Verifies Docker is installed and running on the system.

### isolation.py
- **`ExecutionLimits`** - Dataclass for configuring execution resource limits:
  - `time_limit` (default: 30 seconds)
  - `memory_limit` (default: 256 MB)
  - `cpu_limit` (default: 0.5 cores)
  - `max_output_chars` (default: 100000)
- **`resource_limits_context(limits)`** - Context manager for setting and restoring resource limits.
- **`execute_with_limits(language, code, limits, stdin, session_id)`** - Executes code with resource monitoring.
- **`sandbox_process_isolation(language, code, limits, stdin)`** - Executes code in a completely isolated subprocess environment.

### resource_limits.py
- **`DEFAULT_DOCKER_ARGS`** - List of default Docker run arguments for security:
  - `--network=none` - No network access
  - `--cap-drop=ALL` - Drop all capabilities
  - `--security-opt=no-new-privileges` - Prevent privilege escalation
  - `--read-only` - Read-only container filesystem
  - `--memory=256m` - Memory limit
  - `--memory-swap=256m` - Disable swap
  - `--cpus=0.5` - CPU limit
  - `--pids-limit=50` - Process limit

### security.py
- **`prepare_code_file(code, language)`** - Creates temporary file with code content and appropriate extension. Returns tuple of (temp_dir, relative_file_path).
- **`prepare_stdin_file(stdin, temp_dir)`** - Prepares stdin content file if needed.
- **`cleanup_temp_files(temp_dir)`** - Safely removes temporary directory and files after execution.

## Operating Contracts

- All code execution is isolated in Docker containers with no network access.
- Resource limits are enforced to prevent resource exhaustion attacks.
- Privilege escalation is prevented through capability dropping and security options.
- Temporary files are created in isolated directories and cleaned up after execution.
- Output is truncated to prevent memory exhaustion from large outputs (max 100KB).
- Containers are configured as read-only to prevent filesystem modifications.

## Signposting

- **Dependencies**: Requires Docker to be installed and running.
- **Parent Directory**: [coding](../README.md) - Parent module documentation.
- **Related Modules**:
  - `execution/` - Uses sandbox for code execution.
  - `monitoring/` - Resource monitoring during execution.
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation.
