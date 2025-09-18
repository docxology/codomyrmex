# System Discovery

## Overview

The System Discovery module provides comprehensive introspection and analysis capabilities for the Codomyrmex ecosystem. It enables automatic discovery, scanning, and analysis of modules, functions, capabilities, and system health across the entire project.

## Key Components

- **Discovery Engine**: Core system for scanning and analyzing the Codomyrmex module ecosystem
- **Capability Scanner**: Identifies and catalogs available functions, tools, and features
- **Status Reporter**: Provides system health monitoring and status reporting
- **Health Monitoring**: Real-time monitoring of module availability and functionality

## Integration Points

This module serves as the central nervous system for Codomyrmex:

**Provides:**
- **System Inventory**: Complete catalog of available modules and their capabilities
- **Health Monitoring**: Real-time status of all system components
- **Capability Mapping**: Detailed function and tool discovery across modules
- **System Diagnostics**: Comprehensive health checks and troubleshooting

**Consumes:**
- **All Modules**: Scans every module in the Codomyrmex ecosystem
- **Environment Setup**: Uses environment configuration for system analysis
- **Logging Monitoring**: Comprehensive logging of discovery and health operations

## Getting Started

```python
from codomyrmex.system_discovery import SystemDiscovery

# Initialize system discovery
discovery = SystemDiscovery()

# Run comprehensive system scan
discovery.run_full_discovery()

# Get system health status
health_status = discovery.check_system_health()

# Generate capability inventory
capabilities = discovery.get_capability_inventory()
```

## Key Features

### Comprehensive Module Scanning
- Automatic discovery of all Codomyrmex modules
- Function and method inventory across the entire codebase
- API endpoint and tool identification
- Dependency analysis and relationship mapping

### Health Monitoring
- Real-time system health assessment
- Module availability checking
- Performance monitoring integration
- Automated health reporting

### Capability Analysis
- Function signature analysis
- Tool and API cataloging
- Cross-module integration mapping
- System-wide capability inventory

## Usage Examples

### Basic System Discovery
```python
from codomyrmex.system_discovery import SystemDiscovery

discovery = SystemDiscovery()

# Discover all modules
modules = discovery.discover_modules()
print(f"Found {len(modules)} modules")

# Check system health
health = discovery.check_system_health()
if health['status'] == 'healthy':
    print("✅ All systems operational")
```

### Capability Analysis
```python
# Get detailed capability inventory
capabilities = discovery.get_capability_inventory()

# Find modules with specific functionality
ai_modules = [m for m in capabilities if 'ai' in m['capabilities']]
print(f"Found {len(ai_modules)} AI-enabled modules")

# Analyze function signatures
functions = discovery.analyze_function_signatures()
print(f"Analyzed {len(functions)} functions across all modules")
```

### Health Monitoring
```python
# Continuous health monitoring
while True:
    health_report = discovery.generate_health_report()
    if health_report['issues']:
        print(f"⚠️  Found {len(health_report['issues'])} system issues")

    time.sleep(60)  # Check every minute
```

## API Reference

See [API_SPECIFICATION.md](API_SPECIFICATION.md) for detailed programmatic interfaces.

## MCP Tools

This module provides the following MCP tools:
- `system_discovery.scan_modules`: Comprehensive module scanning
- `system_discovery.health_check`: System health assessment
- `system_discovery.capability_inventory`: Capability cataloging

See [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) for complete tool specifications.

## Security Considerations

See [SECURITY.md](SECURITY.md) for security implications and best practices.

## Dependencies

- `logging_monitoring`: For comprehensive logging
- `environment_setup`: For system environment analysis
- Standard Python libraries for introspection and analysis
