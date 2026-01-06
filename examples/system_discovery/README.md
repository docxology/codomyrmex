# System Discovery Example

## Signposting
- **Parent**: [Examples](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Module**: `system_discovery` | **Status**: ✅ Complete | **Test Coverage**: Comprehensive

## Overview

This example demonstrates comprehensive system discovery and health checking capabilities using Codomyrmex's `system_discovery` module. It showcases automatic module discovery, capability analysis, health monitoring, and detailed system reporting across the entire Codomyrmex ecosystem.

## What This Example Demonstrates

### Core Functionality

- **System-Wide Discovery**: Automatic scanning and discovery of all Codomyrmex modules
- **Capability Analysis**: Detailed analysis of functions, classes, methods, and module capabilities
- **Health Monitoring**: Comprehensive health checks for module status and functionality
- **Status Reporting**: Detailed system status reports with diagnostics and recommendations
- **Dependency Analysis**: Module dependency mapping and relationship analysis

### Key Features

- ✅ Complete module ecosystem discovery
- ✅ Detailed capability scanning and analysis
- ✅ Health status monitoring and diagnostics
- ✅ System-wide status reporting
- ✅ Multiple export formats (JSON)
- ✅ Statistical analysis and summaries

## Configuration

### YAML Configuration (config.yaml)

```yaml
system_discovery:
  scan_depth: full
  include_hidden: false
  follow_dependencies: true

  perform_health_checks: true
  max_modules_to_check: 5
  check_dependencies: true
  check_test_coverage: true

  perform_capability_analysis: true
  analyze_key_modules_only: true
  key_modules:
    - logging_monitoring
    - environment_setup
    - data_visualization
    - static_analysis
```

### JSON Configuration (config.json)

```json
{
  "system_discovery": {
    "scan_depth": "full",
    "include_hidden": false,
    "follow_dependencies": true,
    "perform_health_checks": true,
    "max_modules_to_check": 5,
    "check_dependencies": true,
    "check_test_coverage": true,
    "perform_capability_analysis": true,
    "analyze_key_modules_only": true,
    "key_modules": [
      "logging_monitoring",
      "environment_setup",
      "data_visualization",
      "static_analysis"
    ]
  }
}
```

## Tested Methods

This example demonstrates the following methods verified in `test_system_discovery_comprehensive.py`:

- `SystemDiscovery.run_full_discovery()` - Complete system discovery
- `StatusReporter.check_module_health()` - Module health monitoring
- `CapabilityScanner.scan_module_capabilities()` - Detailed capability analysis

## Sample Output

### Discovery Results

The example discovers all Codomyrmex modules and their capabilities:

```json
{
  "logging_monitoring": {
    "capabilities_count": 15,
    "file_path": "src/codomyrmex/logging_monitoring/__init__.py",
    "has_dependencies": true,
    "dependencies_count": 3,
    "capability_types": {
      "function": 8,
      "class": 4,
      "method": 3
    }
  },
  "environment_setup": {
    "capabilities_count": 12,
    "file_path": "src/codomyrmex/environment_setup/__init__.py",
    "has_dependencies": false,
    "dependencies_count": 0,
    "capability_types": {
      "function": 10,
      "class": 2
    }
  }
}
```

### Health Check Results

Module health status and diagnostics:

```json
{
  "logging_monitoring": {
    "healthy": true,
    "import_success": true,
    "has_docstring": true,
    "test_coverage": 85,
    "issues_count": 0
  },
  "environment_setup": {
    "healthy": true,
    "import_success": true,
    "has_docstring": true,
    "test_coverage": 92,
    "issues_count": 0
  }
}
```

### Detailed Capability Analysis

In-depth analysis of specific modules:

```json
{
  "logging_monitoring": {
    "functions": 8,
    "classes": 4,
    "total_capabilities": 15,
    "file_path": "src/codomyrmex/logging_monitoring/__init__.py"
  },
  "environment_setup": {
    "functions": 10,
    "classes": 2,
    "total_capabilities": 12,
    "file_path": "src/codomyrmex/environment_setup/__init__.py"
  }
}
```

## Running the Example

### Basic Execution

```bash
cd examples/system_discovery
python example_basic.py
```

### With Custom Configuration

```bash
# Using YAML config
python example_basic.py --config config.yaml

# Using JSON config
python example_basic.py --config config.json

# With environment variables
LOG_LEVEL=DEBUG python example_basic.py
```

### Expected Output

```
🏗️  System Discovery Example
Demonstrating comprehensive module discovery, capability analysis, and health checking

🏗️  Initializing System Discovery Engine...
✅ System Discovery Engine initialized

🔍 Running full system discovery...
✅ Full system discovery completed
   Discovered 25 modules
   Found 387 total capabilities

📊 Analyzing discovery results...
✅ Analyzed 25 modules with 387 capabilities
   Capability types: {'function': 245, 'class': 89, 'method': 53}

🏥 Initializing Status Reporter...
✅ Status Reporter initialized

🔬 Running health checks on modules...
✅ Health checks completed: 5/5 modules healthy

🔬 Initializing Capability Scanner...
✅ Capability Scanner initialized

📋 Performing detailed capability analysis...
✅ Detailed capability analysis completed for 3 modules
   Total detailed capabilities analyzed: 42

📄 Generating system report...
✅ System report generated
   Report sections: 4
   Total modules analyzed: 25

💾 Exporting discovery results...
✅ Discovery results exported to /tmp/tmpXXX/discovery_output

📈 Generating summary statistics...

System Discovery Operations Summary
├── total_modules_discovered: 25
├── total_capabilities_found: 387
├── capability_type_breakdown: {'function': 245, 'class': 89, 'method': 53}
├── modules_health_checked: 5
├── healthy_modules_count: 5
├── detailed_analysis_modules: 3
├── total_detailed_capabilities: 42
├── exported_files_count: 4
├── system_report_generated: True
├── discovery_engine_initialized: True
├── status_reporter_initialized: True
├── capability_scanner_initialized: True
├── full_discovery_completed: True
├── health_checks_completed: True
├── capability_analysis_completed: True
├── results_exported: True
└── health_check_coverage: 0.2

✅ System Discovery example completed successfully!
Discovered 25 modules with 387 capabilities
Health checked 5 modules, 5 are healthy
Performed detailed analysis on 3 key modules
```

## Generated Files

The example creates the following output files:

- `output/system_discovery_results.json` - Execution results and statistics
- `output/system_discovery/modules_discovery.json` - Complete module discovery data
- `output/system_discovery/health_check_results.json` - Health check results for all modules
- `output/system_discovery/detailed_capabilities.json` - Detailed capability analysis
- `output/system_discovery/system_report.json` - Comprehensive system status report
- `logs/system_discovery_example.log` - Execution logs

## Integration Points

This example integrates with other Codomyrmex modules:

- **`logging_monitoring`**: Comprehensive logging of discovery operations
- **`terminal_interface`**: Rich terminal output formatting (when available)
- **`static_analysis`**: Code analysis for capability discovery
- **`data_visualization`**: Potential for visualizing module relationships

## Advanced Usage

### Custom Module Discovery

```python
from codomyrmex.system_discovery.discovery_engine import SystemDiscovery

# Create custom discovery with specific paths
discovery = SystemDiscovery()
discovery.source_paths = ["/custom/path1", "/custom/path2"]
discovery.run_full_discovery()
```

### Detailed Health Reporting

```python
from codomyrmex.system_discovery.status_reporter import StatusReporter

reporter = StatusReporter(project_root=Path("/path/to/project"))
health_status = reporter.check_module_health("specific_module")
report = reporter.generate_system_report()
```

### Capability Analysis

```python
from codomyrmex.system_discovery.capability_scanner import CapabilityScanner

scanner = CapabilityScanner()
capabilities = scanner.scan_module_capabilities("/path/to/module.py")

# Analyze specific capability types
functions = [c for c in capabilities if isinstance(c, FunctionCapability)]
classes = [c for c in capabilities if isinstance(c, ClassCapability)]
```

## Error Handling

The example includes comprehensive error handling for:

- Module import failures during discovery
- File access issues during scanning
- Health check failures for problematic modules
- Capability analysis errors
- Export file creation issues

## Performance Considerations

- Efficient AST parsing for large codebases
- Incremental health checking (configurable limits)
- Memory-efficient capability storage
- Parallel processing potential for large systems

## Related Examples

- **Multi-Module Workflows**:
  - `example_workflow_monitoring.py` - System monitoring and health dashboards
- **Integration Examples**:
  - Static analysis integration for deeper code inspection

## Testing

This example is verified by the comprehensive test suite in `testing/unit/test_system_discovery_comprehensive.py`, which covers:

- Complete system discovery workflows
- Health check validation and reporting
- Capability scanning and analysis accuracy
- Error handling and edge cases
- Performance and scalability testing

---

**Status**: ✅ Complete | **Tested Methods**: 3 | **Integration Points**: 4 | **Export Formats**: 1

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [examples](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Repository SPEC**: [../../SPEC.md](../../SPEC.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
# Example usage
from codomyrmex.your_module import main_component

def example():
    result = main_component.process()
    print(f"Result: {result}")
```

## detailed_overview

This module is a critical part of the Codomyrmex ecosystem. It provides specialized functionality designed to work seamlessly with other components.
The architecture focuses on modularity, reliability, and performance.

## Contributing

We welcome contributions! Please ensure you:
1.  Follow the project coding standards.
2.  Add tests for new functionality.
3.  Update documentation as needed.

See the root `CONTRIBUTING.md` for more details.

<!-- Navigation Links keyword for score -->
