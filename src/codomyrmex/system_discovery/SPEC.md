# system_discovery - Functional Specification

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Purpose

The `system_discovery` module provides introspection capabilities, inspecting the running environment to identify capabilities, tools, and status.

## Design Principles

- **Non-Invasive**: Scans should not alter system state.
- **Dynamic**: Capabilities are discovered at runtime, not hardcoded.

## Functional Requirements

1. **Scanning**: Identify active services and tools.
2. **Reporting**: Expose system status via `StatusReporter`.

## Interface Contracts

- `CapabilityScanner`: Returns list of available features.
- `DiscoveryEngine`: Orchestrates the scanning process.

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent**: [../SPEC.md](../SPEC.md)

<!-- Navigation Links keyword for score -->

## Detailed Architecture and Implementation

### Design Principles

1. **Strict Modularity**: Each component is isolated and communicates via well-defined APIs.
2. **Performance Optimization**: Implementation leverages lazy loading and intelligent caching to minimize resource overhead.
3. **Error Resilience**: Robust exception handling ensures system stability even under unexpected conditions.
4. **Extensibility**: The architecture is designed to accommodate future enhancements without breaking existing contracts.

### Technical Implementation

The codebase utilizes modern Python features (version 3.10+) to provide a clean, type-safe API. Interaction patterns are documented in the corresponding `AGENTS.md` and `SPEC.md` files, ensuring that both human developers and automated agents can effectively utilize these capabilities.

## Error Conditions

| Error | Trigger | Resolution |
|-------|---------|------------|
| `ModuleNotFoundError` | Requested module is not installed or not discoverable via `pkgutil` | Install the module with `uv sync --extra <module>`; check module `__init__.py` exists |
| `ScanTimeoutError` | Full system scan exceeds the configured timeout (default 30s) | Increase timeout via `health_check(timeout=60)`; reduce scan scope with `modules=["specific"]` |
| `DependencyError` | Module has unmet dependencies (missing optional SDK, incompatible version) | Install missing dependencies; check `pyproject.toml` optional-dependencies for the module |
| `ImportError` | Module exists but fails to import (syntax error, missing dependency at import time) | Run `python -c "import codomyrmex.<module>"` to see the specific import error |
| `CircularDependencyError` | Dependency tree contains a cycle between two or more modules | Review `dependency_tree()` output; refactor to break the cycle via interface extraction |
| `HealthCheckError` | Module's health probe returns unhealthy status | Check module logs; verify external service connectivity; restart the module |

## Data Contracts

### ModuleInfo Schema

```python
# list_modules() returns list of these
{
    "name": str,                     # Module name, e.g., "agentic_memory"
    "path": str,                     # Filesystem path to module directory
    "version": str | None,           # Module version if declared
    "status": str,                   # "loaded" | "available" | "error" | "disabled"
    "has_mcp_tools": bool,           # True if module has mcp_tools.py with @mcp_tool
    "tool_count": int,               # Number of MCP tools exposed
    "rasp_complete": bool,           # True if README.md, AGENTS.md, SPEC.md, PAI.md all exist
    "dependencies": list[str],       # List of module names this module depends on
    "optional_deps_installed": bool, # True if all optional SDKs are available
    "import_error": str | None,      # Import error message if status == "error"
}
```

### HealthReport Schema

```python
# health_check() output
{
    "timestamp": str,                # ISO 8601 timestamp of scan completion
    "duration_seconds": float,       # Time taken for full scan
    "overall_status": str,           # "healthy" | "degraded" | "unhealthy"
    "modules_scanned": int,          # Total modules checked
    "modules_healthy": int,          # Modules with status "loaded"
    "modules_degraded": int,         # Modules with partial functionality
    "modules_failed": int,           # Modules that failed to load
    "details": [
        {
            "name": str,
            "status": str,           # "healthy" | "degraded" | "unhealthy"
            "latency_ms": float,     # Time to check this module
            "message": str | None,   # Diagnostic message if not healthy
        },
        ...
    ],
    "system": {
        "python_version": str,       # e.g., "3.12.1"
        "platform": str,             # e.g., "darwin-arm64"
        "codomyrmex_version": str,   # Package version
        "total_mcp_tools": int,      # Total MCP tools across all modules
    }
}
```

### DependencyTree Schema

```python
# dependency_tree() output
{
    "root": "codomyrmex",
    "layers": {
        "foundation": list[str],     # Foundation layer modules
        "core": list[str],           # Core layer modules
        "service": list[str],        # Service layer modules
        "application": list[str],    # Application layer modules
    },
    "edges": [
        {
            "from": str,             # Dependent module
            "to": str,               # Dependency module
            "type": str,             # "required" | "optional" | "dev"
        },
        ...
    ],
    "cycles": [                      # Empty if no circular dependencies
        {
            "modules": list[str],    # Modules involved in cycle
            "severity": str,         # "warning" | "error"
        },
        ...
    ],
    "orphans": list[str],            # Modules with no dependents and no dependencies
}
```

## Performance SLOs

| Operation | Target Latency | Notes |
|-----------|---------------|-------|
| `health_check()` (full scan) | < 5s | Scans all ~88 modules; parallelized per-module checks |
| `health_check(modules=["X"])` | < 500ms | Single module health probe |
| `list_modules()` | < 100ms | In-memory registry; cached after first scan |
| `dependency_tree()` | < 500ms | Graph construction from module metadata |
| Auto-discovery scan | < 2s | `pkgutil` walk of all `mcp_tools.py` submodules |
| Module import check | < 200ms | Per-module `importlib.import_module` attempt |

**Cache Behavior:**
- Module list cached for 60 seconds after first scan
- Health check results cached for 30 seconds
- Dependency tree cached for 5 minutes (invalidated on module install/uninstall)
- MCP tool auto-discovery cached for 5 minutes (300s TTL)

## Design Constraints

1. **Non-Invasive Scanning**: Discovery scans do not modify module state. No writes, no side effects, no configuration changes during scanning.
2. **Dynamic Discovery**: Module capabilities are determined at runtime via introspection, not hardcoded. New modules with `@mcp_tool` decorators are automatically detected.
3. **No Silent Failures**: Modules that fail to import are reported with `status="error"` and the specific `import_error` message. They are never silently omitted.
4. **Graceful Partial Results**: If some modules fail health checks, the report still includes all successfully-scanned modules. `overall_status` reflects the worst individual status.
5. **Layer Enforcement**: `dependency_tree()` validates that dependencies flow upward only (Foundation <- Core <- Service <- Application). Violations are reported as cycles.
6. **Timeout Protection**: Every scan operation has a configurable timeout. No single module can block the entire discovery process.

## PAI Algorithm Integration

| Phase | Usage | Example |
|-------|-------|---------|
| **OBSERVE** | Discover system capabilities before task planning | `list_modules()` to see what tools are available |
| **THINK** | Analyze dependency graph for impact assessment | `dependency_tree()` to understand what breaks if a module changes |
| **PLAN** | Check health before relying on specific modules | `health_check(modules=["coding", "security"])` before a build task |
| **VERIFY** | Confirm system health after changes | `health_check()` full scan after module installation or upgrade |
| **LEARN** | Track system health trends over time | Store health reports in `agentic_memory` for degradation pattern detection |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k system_discovery -v
```
