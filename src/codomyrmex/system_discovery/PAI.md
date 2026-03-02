# Personal AI Infrastructure — System Discovery Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The System Discovery module provides capability scanning, system context gathering, and status reporting for the codomyrmex ecosystem. It is the primary tool for the PAI Algorithm's OBSERVE phase, enabling agents to understand what modules are available, their health status, and the current environment.

## PAI Capabilities

### Capability Scanning

```python
from codomyrmex.system_discovery import CapabilityScanner

scanner = CapabilityScanner()
capabilities = scanner.scan()
# Returns: available modules, their exports, health status, versions
```

### System Context

```python
from codomyrmex.system_discovery import get_system_context

context = get_system_context()
# Returns: OS, Python version, installed packages, env vars, available services
```

### Discovery Engine

```python
from codomyrmex.system_discovery import SystemDiscovery

discovery = SystemDiscovery()
modules = discovery.discover_modules()
# Auto-discovers all codomyrmex modules via pkgutil scan
# Reports RASP documentation coverage, MCP tool specs, test status
```

### Status Reporting

```python
from codomyrmex.system_discovery import StatusReporter

reporter = StatusReporter()
report = reporter.generate()
# Comprehensive health report: module count, test pass rate, doc coverage
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `CapabilityScanner` | Class | Scan and catalog available capabilities |
| `get_system_context` | Function | Gather current system environment context |
| `SystemDiscovery` | Class | Auto-discover codomyrmex modules |
| `StatusReporter` | Class | Generate health and status reports |

## PAI Algorithm Phase Mapping

| Phase | System Discovery Contribution |
|-------|-------------------------------|
| **OBSERVE** | Primary module: scans capabilities, gathers context, discovers modules |
| **THINK** | Context data informs capability selection and ISC expansion |
| **PLAN** | Module discovery data helps plan which tools to use in workflows |
| **VERIFY** | Status reports verify system health after changes |

## MCP Tools

| Tool | Description | Key Parameters | PAI Phase |
|------|-------------|----------------|-----------|
| `health_check` | Run health checks across all codomyrmex modules | `module: str \| None` | OBSERVE |
| `list_modules` | List all available codomyrmex modules with metadata | -- | OBSERVE |
| `dependency_tree` | Generate module dependency tree | `module: str \| None` | OBSERVE |

## Architecture Role

**Foundation Layer** — First module invoked in any PAI session. Zero dependencies on other codomyrmex modules. Consumed by `maintenance/`, `documentation/`, and the MCP server startup.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
