# System Discovery API Specification

## Overview

The System Discovery module provides programmatic interfaces for comprehensive system analysis and introspection of the Codomyrmex ecosystem.

## Core Classes

### SystemDiscovery

Main class for system discovery operations.

```python
class SystemDiscovery:
    def __init__(self, scan_depth: int = 2, include_private: bool = False)
    def run_full_discovery(self) -> Dict[str, Any]
    def discover_modules(self) -> List[Dict[str, Any]]
    def check_system_health(self) -> Dict[str, Any]
    def get_capability_inventory(self) -> List[Dict[str, Any]]
    def analyze_function_signatures(self) -> Dict[str, Any]
    def generate_health_report(self) -> Dict[str, Any]
    def export_full_inventory(self, output_path: str = None) -> str
```

### CapabilityScanner

Scans and catalogs system capabilities.

```python
class CapabilityScanner:
    def scan_module_capabilities(self, module_name: str) -> Dict[str, Any]
    def scan_all_capabilities(self) -> Dict[str, Any]
    def identify_tools(self, module_path: str) -> List[str]
    def identify_functions(self, module_path: str) -> List[Dict[str, Any]]
    def analyze_dependencies(self, module_path: str) -> Dict[str, Any]
```

### StatusReporter

Provides system status and health reporting.

```python
class StatusReporter:
    def generate_status_report(self) -> Dict[str, Any]
    def check_module_health(self, module_name: str) -> Dict[str, Any]
    def monitor_system_resources(self) -> Dict[str, Any]
    def log_health_metrics(self) -> None
    def alert_on_issues(self, issues: List[str]) -> None
```

## Key Functions

### Discovery Operations

```python
def run_full_discovery(scan_depth: int = 2) -> Dict[str, Any]:
    """
    Perform comprehensive system discovery.

    Args:
        scan_depth: Depth of module scanning (1-3)

    Returns:
        Complete system discovery report
    """

def discover_modules() -> List[Dict[str, Any]]:
    """
    Discover all available Codomyrmex modules.

    Returns:
        List of module information dictionaries
    """
```

### Health Monitoring

```python
def check_system_health() -> Dict[str, Any]:
    """
    Check overall system health status.

    Returns:
        Health status report with issues and recommendations
    """

def check_module_health(module_name: str) -> Dict[str, Any]:
    """
    Check health of specific module.

    Args:
        module_name: Name of module to check

    Returns:
        Module health status
    """
```

### Capability Analysis

```python
def get_capability_inventory() -> List[Dict[str, Any]]:
    """
    Get complete inventory of system capabilities.

    Returns:
        List of capability definitions
    """

def analyze_function_signatures() -> Dict[str, Any]:
    """
    Analyze function signatures across all modules.

    Returns:
        Function signature analysis report
    """
```

## Data Structures

### ModuleInfo
```python
ModuleInfo = TypedDict('ModuleInfo', {
    'name': str,
    'path': str,
    'version': str,
    'capabilities': List[str],
    'dependencies': List[str],
    'health_status': str,
    'documentation_complete': bool,
    'test_coverage': float
})
```

### HealthReport
```python
HealthReport = TypedDict('HealthReport', {
    'overall_status': str,  # 'healthy', 'warning', 'critical'
    'module_count': int,
    'healthy_modules': int,
    'issues': List[str],
    'recommendations': List[str],
    'last_checked': str,
    'scan_duration_seconds': float
})
```

### CapabilityDefinition
```python
CapabilityDefinition = TypedDict('CapabilityDefinition', {
    'module': str,
    'capability_type': str,  # 'function', 'tool', 'service'
    'name': str,
    'signature': str,
    'description': str,
    'parameters': List[Dict[str, Any]],
    'return_type': str,
    'complexity': str
})
```

## Usage Examples

### Basic System Discovery
```python
from codomyrmex.system_discovery import SystemDiscovery

discovery = SystemDiscovery()
report = discovery.run_full_discovery()

print(f"Discovered {len(report['modules'])} modules")
print(f"System health: {report['health']['status']}")
```

### Module Analysis
```python
# Analyze specific module
module_info = discovery.discover_modules()
for module in module_info:
    if module['name'] == 'ai_code_editing':
        print(f"AI module capabilities: {module['capabilities']}")
        break
```

### Health Monitoring
```python
health = discovery.check_system_health()
if health['issues']:
    print("System issues found:")
    for issue in health['issues']:
        print(f"  - {issue}")
```

## Error Handling

All functions include comprehensive error handling:

```python
try:
    result = discovery.run_full_discovery()
except DiscoveryError as e:
    logger.error(f"Discovery failed: {e}")
    # Handle discovery-specific errors
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle general errors
```

## Configuration

### Environment Variables
- `SYSTEM_DISCOVERY_SCAN_DEPTH`: Default scan depth (default: 2)
- `SYSTEM_DISCOVERY_INCLUDE_PRIVATE`: Include private functions (default: false)
- `SYSTEM_DISCOVERY_CACHE_RESULTS`: Cache discovery results (default: true)
- `SYSTEM_DISCOVERY_LOG_LEVEL`: Logging verbosity (default: INFO)

### Configuration File
```json
{
  "scan_depth": 2,
  "include_private": false,
  "cache_enabled": true,
  "excluded_modules": ["test", "example"],
  "health_check_interval": 60
}
```

## Performance Considerations

- **Caching**: Discovery results are cached to improve performance
- **Incremental Scanning**: Only changed modules are re-scanned
- **Resource Limits**: Memory and CPU limits prevent system impact
- **Async Operations**: Non-blocking discovery operations available

## Security Considerations

- **Safe Execution**: All code analysis is performed in restricted environments
- **Permission Checks**: Proper access controls for system introspection
- **Data Sanitization**: Sensitive information is filtered from reports
- **Audit Logging**: All discovery operations are logged for security review

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
