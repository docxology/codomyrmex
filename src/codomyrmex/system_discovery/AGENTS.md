# Codomyrmex Agents — src/codomyrmex/system_discovery

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides system discovery and orchestration capabilities for the Codomyrmex ecosystem. Scans all modules, discovers capabilities, reports on system status, and provides interactive exploration tools for understanding the system structure.

## Active Components

- `discovery_engine.py` - Core system discovery and module scanning
- `capability_scanner.py` - Scans modules for exposed capabilities
- `status_reporter.py` - Reports on module and system status
- `health_checker.py` - Checks module health and availability
- `health_reporter.py` - Generates health reports
- `context.py` - System context management
- `__init__.py` - Module exports
- `MCP_TOOL_SPECIFICATION.md` - MCP tool definitions

## Key Classes and Functions

### discovery_engine.py
- **`SystemDiscovery`** - Main class for system-wide discovery
  - `scan_modules()` - Discovers all installed modules
  - `get_module_info(module_name)` - Gets detailed module information
  - `list_capabilities()` - Lists all available capabilities
  - `search(query)` - Searches across modules and capabilities

### capability_scanner.py
- **`CapabilityScanner`** - Scans modules for capabilities
  - `scan(module)` - Extracts capabilities from a module
  - `get_functions(module)` - Lists public functions
  - `get_classes(module)` - Lists public classes
  - `get_mcp_tools(module)` - Finds MCP tool definitions

### status_reporter.py
- **`StatusReporter`** - Reports system and module status
  - `get_system_status()` - Overall system health
  - `get_module_status(module_name)` - Individual module status
  - `generate_report()` - Creates comprehensive status report

### health_checker.py / health_reporter.py
- Health check execution and reporting
- Availability verification
- Performance baseline checks

### context.py
- **`get_system_context()`** - Returns current system context
  - Environment information
  - Loaded modules
  - Active configurations

## Operating Contracts

- Discovery is non-invasive (read-only inspection)
- Module scanning respects __all__ exports
- Status checks have configurable timeouts
- Reports are JSON-serializable
- MCP tools follow standard protocol

## Signposting

- **Dependencies**: Uses `logging_monitoring` for logging
- **Parent Directory**: [codomyrmex](../README.md) - Parent module documentation
- **Related Modules**:
  - All modules are discovery targets
  - `logging_monitoring/` - Log integration
  - `cli/` - CLI commands for discovery
- **Project Root**: [../../../README.md](../../../README.md) - Main project documentation
