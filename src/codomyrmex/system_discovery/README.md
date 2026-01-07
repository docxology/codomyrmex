# system_discovery

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

System Discovery Engine for Codomyrmex. Provides comprehensive system discovery capabilities, scanning all modules, methods, classes, and functions to create a complete map of the Codomyrmex ecosystem capabilities. Includes health checking, capability scanning, and system status reporting.

## Directory Contents
- `API_SPECIFICATION.md` – File
- `MCP_TOOL_SPECIFICATION.md` – File
- `README.md` – File
- `SECURITY.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `capability_scanner.py` – File
- `discovery_engine.py` – File
- `health_checker.py` – File
- `health_reporter.py` – File
- `status_reporter.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.system_discovery import (
    SystemDiscovery,
    CapabilityScanner,
    StatusReporter,
)

# Run full system discovery
discovery = SystemDiscovery()
discovery.run_full_discovery()

# Scan module capabilities
scanner = CapabilityScanner()
capabilities = scanner.scan_all_capabilities()
print(f"Found {len(capabilities)} capabilities")

# Check system health
reporter = StatusReporter()
health_report = reporter.generate_status_report()
print(f"System health: {health_report['status']}")
```

