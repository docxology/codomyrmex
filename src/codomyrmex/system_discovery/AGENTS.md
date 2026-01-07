# Codomyrmex Agents — src/codomyrmex/system_discovery

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
System Discovery Engine for Codomyrmex. Provides comprehensive system discovery capabilities, scanning all modules, methods, classes, and functions to create a complete map of the Codomyrmex ecosystem capabilities. Includes health checking, capability scanning, and system status reporting.

## Active Components
- `API_SPECIFICATION.md` – Project file
- `MCP_TOOL_SPECIFICATION.md` – Project file
- `README.md` – Project file
- `SECURITY.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `capability_scanner.py` – Capability scanning and analysis
- `discovery_engine.py` – Main system discovery engine
- `health_checker.py` – Health checking and validation
- `health_reporter.py` – Health status reporting
- `status_reporter.py` – System status reporting

## Key Classes and Functions

### SystemDiscovery (`discovery_engine.py`)
- `SystemDiscovery(project_root: Optional[Path] = None)` – Initialize the system discovery engine
- `run_full_discovery() -> None` – Run complete system discovery and display results
- `_discover_modules() -> None` – Discover all modules in the system
- `_display_discovery_results() -> None` – Display discovery results

### ModuleInfo (`discovery_engine.py`)
- `ModuleInfo` (dataclass) – Complete information about a discovered module:
  - `name: str` – Module name
  - `path: str` – Module path
  - `description: str` – Module description
  - `version: str` – Module version
  - `capabilities: list[ModuleCapability]` – List of module capabilities
  - `dependencies: list[str]` – Module dependencies
  - `is_importable: bool` – Whether module can be imported
  - `has_tests: bool` – Whether module has tests
  - `has_docs: bool` – Whether module has documentation
  - `last_modified: str` – Last modification timestamp

### ModuleCapability (`discovery_engine.py`)
- `ModuleCapability` (dataclass) – Represents a discovered capability:
  - `name: str` – Capability name
  - `module_path: str` – Module path
  - `type: str` – Type ('function', 'class', 'method', 'constant')
  - `signature: str` – Function/class signature
  - `docstring: str` – Documentation string
  - `file_path: str` – Source file path
  - `line_number: int` – Line number in source
  - `is_public: bool` – Whether capability is public
  - `dependencies: list[str]` – Capability dependencies

### HealthChecker (`health_checker.py`)
- `HealthStatus` (Enum) – Health status enumeration (HEALTHY, DEGRADED, UNHEALTHY, UNKNOWN)
- `HealthCheckResult` (dataclass) – Result of a health check:
  - `module_name: str` – Module name
  - `status: HealthStatus` – Health status
  - `timestamp: float` – Check timestamp
  - `checks_performed: List[str]` – List of checks performed
  - `issues: List[str]` – List of issues found
  - `recommendations: List[str]` – List of recommendations
  - `metrics: Dict[str, Any]` – Health metrics
  - `dependencies: Dict[str, HealthStatus]` – Dependency health statuses
- `HealthChecker()` – Comprehensive health checker for Codomyrmex modules
- `check_module(module_name: str) -> HealthCheckResult` – Check health of a specific module
- `check_all_modules() -> Dict[str, HealthCheckResult]` – Check health of all modules

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation