# system_discovery

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Application-layer module providing runtime introspection and orchestration capabilities for the Codomyrmex ecosystem. Scans all modules to discover functions, classes, and capabilities via AST analysis and dynamic import; performs health checks on dependencies and services; generates detailed status reports with terminal formatting; profiles hardware and environment; and aggregates system context into a standardized format consumable by AI agents.

## Key Exports

- **`SystemDiscovery`** -- Main discovery engine that scans all Codomyrmex modules, methods, classes, and functions to create a complete capability map of the ecosystem
- **`StatusReporter`** -- Generates detailed status reports including health checks, dependency analysis, and system diagnostics with formatted terminal output via `TerminalFormatter`
- **`CapabilityScanner`** -- Scans and catalogs individual module capabilities using AST parsing, producing `FunctionCapability` metadata records for discovered functions and classes
- **`get_system_context(root_dir)`** -- Aggregates system structure, available modules, and health status into a dictionary suitable for agent consumption

## Internal Components

These are not exported but support the main classes:

- **`HealthChecker`** -- Validates system dependencies (Docker, git, Python packages) and service availability
- **`HardwareProfiler`** -- Detects CPU, RAM, OS, and architecture information via `psutil`
- **`EnvironmentProfiler`** -- Detects execution environment (CI, Docker, virtualenv, etc.)

## Directory Contents

- `discovery_engine.py` -- `SystemDiscovery` class for full ecosystem capability mapping
- `capability_scanner.py` -- `CapabilityScanner` with AST-based function and class introspection
- `status_reporter.py` -- `StatusReporter` for health checks and formatted diagnostics output
- `health_checker.py` -- `HealthChecker` for dependency and service health validation
- `health_reporter.py` -- Health report generation and formatting utilities
- `profilers.py` -- `HardwareProfiler` and `EnvironmentProfiler` for system profiling
- `context.py` -- `get_system_context()` function aggregating system state for agents

## Navigation

- **Full Documentation**: [docs/modules/system_discovery/](../../../docs/modules/system_discovery/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
