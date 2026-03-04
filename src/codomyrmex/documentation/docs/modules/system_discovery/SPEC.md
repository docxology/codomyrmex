# System Discovery Module - Technical Specification

**Version**: v1.1.0 | **Last Updated**: March 2026

## Overview

The System Discovery module provides programmatic discovery of all Codomyrmex modules, their exported capabilities (functions, classes, methods, constants), dependency relationships, health status, and documentation completeness. It operates at both AST level (static analysis) and runtime level (dynamic import inspection).

## Design Principles

- **Zero-Mock Policy**: Tests use real module imports and actual filesystem scanning.
- **Explicit Failure**: ImportErrors and missing modules are reported with full tracebacks.
- **Dual-Mode Scanning**: Combines AST parsing with runtime inspection for comprehensive discovery.

## Architecture

```
system_discovery/
  __init__.py              # Exports: SystemDiscovery, CapabilityScanner, StatusReporter, get_system_context
  mcp_tools.py             # 3 MCP tools
  core/
    capability_scanner.py  # CapabilityScanner class + dataclasses
    context.py             # get_system_context()
    dependency_analyzer.py # DependencyAnalyzer
    discovery_engine.py    # SystemDiscovery + ModuleInfo + ModuleCapability
    health_checker.py      # SystemHealthChecker
  health/                  # Health check implementations
  reporting/
    status_reporter.py     # StatusReporter
```

## Functional Requirements

1. Discover all Codomyrmex modules by scanning the `src/codomyrmex/` directory tree.
2. Extract per-module metadata: name, path, description, version, capabilities, dependencies, importability.
3. Scan modules for function capabilities (signature, docstring, parameters, decorators, complexity).
4. Scan modules for class capabilities (methods, properties, inheritance, abstract flag).
5. Analyze dependency graphs between modules.
6. Run health checks on individual modules or the entire system.
7. Generate system status reports.
8. Expose discovery capabilities as MCP tools.

## Interface Contracts

```python
@dataclass
class FunctionCapability:
    name: str
    signature: str
    docstring: str
    parameters: list[dict[str, Any]]
    return_annotation: str
    file_path: str
    line_number: int
    is_async: bool
    is_generator: bool
    decorators: list[str]
    complexity_score: int

@dataclass
class ModuleInfo:
    name: str
    path: str
    description: str
    version: str
    capabilities: list[ModuleCapability]
    dependencies: list[str]
    is_importable: bool
    has_tests: bool
    has_docs: bool
    last_modified: str

class SystemDiscovery:
    def __init__(self, project_root: Path | None = None): ...
    def discover_all(self) -> list[ModuleInfo]: ...
```

## Dependencies

**Internal**: `codomyrmex.logging_monitoring`, `codomyrmex.validation.schemas` (optional)

**External**: `ast` (stdlib), `importlib` (stdlib), `inspect` (stdlib)

## Constraints

- Module scanning requires filesystem access to `src/codomyrmex/`.
- Runtime inspection via `importlib.import_module` may trigger module-level side effects.
- `validation.schemas` import is optional; `Result`/`ResultStatus` gracefully degrade to `None`.

## Navigation

- [readme.md](readme.md) -- Module overview
- [AGENTS.md](AGENTS.md) -- Agent coordination
- [Source Module](../../../../system_discovery/)
