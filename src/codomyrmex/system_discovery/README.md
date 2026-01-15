# System Discovery

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview
The `system_discovery` module provides introspection capabilities for the Codomyrmex runtime. It allows the system to identify available resources, active agents, connected services, and system capabilities dynamically. This module is essential for the self-healing and adaptive behaviors of the platform, as well as for generating system health reports.

## Key Features
- **Capability Scanning**: `capability_scanner.py` detects features supported by the current environment (e.g., GPU availability, specific toolsets).
- **Service Discovery**: `discovery_engine.py` identifies running services and active agent instances.
- **Health Monitoring**: `health_checker.py` runs diagnostic probes against system components.
- **Reporting**: `health_reporter.py` and `status_reporter.py` aggregate findings into human-readable or machine-parsable formats.

## Quick Start

```python
from codomyrmex.system_discovery.discovery_engine import DiscoveryEngine
from codomyrmex.system_discovery.health_checker import SystemHealthChecker

# Discover active components
engine = DiscoveryEngine()
components = engine.scan_components()
print(f"Found {len(components)} active components.")

# Check system health
checker = SystemHealthChecker()
status = checker.run_full_check()
if status.is_healthy:
    print("System is healthy.")
else:
    print(f"Degraded: {status.issues}")
```

## Module Structure

- `discovery_engine.py`: Core logic for component identification.
- `capability_scanner.py`: Hardware and software feature detection.
- `health_checker.py`: Diagnostic logic.
- `health_reporter.py`: Report formatting.
- `status_reporter.py`: Real-time status updates.

## Navigation Links
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **MCP Tool Specification**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **📁 Parent Directory**: [codomyrmex](../README.md)
- **🏠 Project Root**: [README](../../../README.md)
