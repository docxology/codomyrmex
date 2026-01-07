# Codomyrmex Agents — src/codomyrmex/coding/sandbox

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
Sandboxing and isolation for secure code execution. Provides Docker container management, process isolation, resource limits enforcement, and security measures for safe code execution.

## Active Components
- `README.md` – Project file
- `__init__.py` – Module exports and public API
- `container.py` – Docker container management
- `isolation.py` – Process isolation
- `resource_limits.py` – Resource limits enforcement
- `security.py` – Security measures and file preparation

## Key Classes and Functions

### Container Management (`container.py`)
- `run_code_in_docker(language: str, code_file_path: str, temp_dir: str, stdin_file: Optional[str] = None, timeout: int = 30, session_id: Optional[str] = None) -> dict[str, Any]` – Execute code in Docker container
- `check_docker_available() -> bool` – Check if Docker is available

### Resource Limits (`resource_limits.py`)
- `ExecutionLimits` (dataclass) – Resource limits configuration
- `resource_limits_context(limits: ExecutionLimits)` – Context manager for resource limits
- `execute_with_limits(code: str, language: str, limits: ExecutionLimits) -> ExecutionResult` – Execute with resource limits

### Security (`security.py`)
- `prepare_code_file(code: str, language: str) -> Path` – Prepare code file for execution
- `prepare_stdin_file(stdin: str) -> Path` – Prepare stdin file
- `cleanup_temp_files() -> None` – Clean up temporary files

### Isolation (`isolation.py`)
- `sandbox_process_isolation(code: str, language: str, limits: Optional[ExecutionLimits] = None) -> ExecutionResult` – Execute code with process isolation

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [coding](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation