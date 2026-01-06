# Codomyrmex Agents — src/codomyrmex/system_discovery

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [System Discovery Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Specialized Layer module providing system discovery and orchestration capabilities for the Codomyrmex platform. This module enables exploration of the platform's modules, capabilities, and status through automated scanning, analysis, and reporting.

The system_discovery module serves as the platform introspection layer, providing self-awareness and exploration capabilities for the entire Codomyrmex ecosystem.

## Module Overview

### Key Capabilities
- **Module Discovery**: Automatic discovery and analysis of all platform modules
- **Capability Scanning**: Detailed analysis of module capabilities and functions
- **Health Monitoring**: System-wide health checks and status reporting
- **Interactive Exploration**: Command-line tools for exploring the system
- **Status Reporting**: Comprehensive system status and capability reports
- **Dependency Analysis**: Module dependency mapping and validation

### Key Features
- AST-based code analysis for function signature extraction
- Module capability classification and tagging
- Health check automation with configurable thresholds
- Interactive status dashboard with real-time updates
- Comprehensive system inventory and reporting
- Dependency relationship analysis

## Function Signatures

### SystemDiscovery Class Methods

```python
def __init__(self, project_root: Optional[Path] = None) -> None
```

Initialize the system discovery engine.

**Parameters:**
- `project_root` (Optional[Path]): Root path of the project. If None, auto-detects

**Returns:** None

```python
def run_full_discovery(self) -> None
```

Run complete system discovery including modules, capabilities, and status.

**Returns:** None - Displays discovery results interactively

```python
def show_status_dashboard(self) -> None
```

Display interactive status dashboard with system overview.

**Returns:** None - Shows interactive dashboard

```python
def run_demo_workflows(self) -> None
```

Execute demonstration workflows to showcase system capabilities.

**Returns:** None - Runs demo workflows interactively

```python
def export_full_inventory(self) -> None
```

Export complete system inventory to files.

**Returns:** None - Creates inventory files

```python
def check_git_repositories(self) -> None
```

Check status of Git repositories in the system.

**Returns:** None - Displays Git status information

### CapabilityScanner Class Methods

```python
def __init__(self, project_root: Optional[Path] = None) -> None
```

Initialize the capability scanner.

**Parameters:**
- `project_root` (Optional[Path]): Root path of the project

**Returns:** None

```python
def scan_all_modules(self) -> dict[str, ModuleCapability]
```

Scan all modules in the system for capabilities.

**Returns:** `dict[str, ModuleCapability]` - Dictionary mapping module names to capabilities

```python
def scan_module(
    self, module_path: Path, include_functions: bool = True, include_classes: bool = True
) -> ModuleCapability
```

Scan a specific module for capabilities.

**Parameters:**
- `module_path` (Path): Path to the module to scan
- `include_functions` (bool): Whether to include function analysis. Defaults to True
- `include_classes` (bool): Whether to include class analysis. Defaults to True

**Returns:** `ModuleCapability` - Capability analysis for the module

```python
def analyze_capability_relationships(
    self, capabilities: dict[str, ModuleCapability]
) -> dict[str, list[str]]
```

Analyze relationships between module capabilities.

**Parameters:**
- `capabilities` (dict[str, ModuleCapability]): Module capabilities to analyze

**Returns:** `dict[str, list[str]]` - Capability relationship mapping

```python
def export_capabilities_report(
    self, capabilities: dict[str, ModuleCapability], output_path: Path
) -> None
```

Export capabilities analysis to a report file.

**Parameters:**
- `capabilities` (dict[str, ModuleCapability]): Capabilities to export
- `output_path` (Path): Path for the output report

**Returns:** None

### StatusReporter Class Methods

```python
def __init__(self, project_root: Optional[Path] = None) -> None
```

Initialize the status reporter.

**Parameters:**
- `project_root` (Optional[Path]): Root path of the project

**Returns:** None

```python
def generate_full_report(self) -> str
```

Generate a system status report.

**Returns:** `str` - Formatted status report

```python
def get_module_status(self, module_name: str) -> dict[str, Any]
```

Get status information for a specific module.

**Parameters:**
- `module_name` (str): Name of the module to check

**Returns:** `dict[str, Any]` - Module status information

```python
def check_system_health(self) -> dict[str, Any]
```

Perform system-wide health check.

**Returns:** `dict[str, Any]` - Health check results

```python
def get_dependency_graph(self) -> dict[str, list[str]]
```

Generate system dependency graph.

**Returns:** `dict[str, list[str]]` - Module dependency relationships

### Health Check Functions

```python
def perform_health_check(module_name: str) -> HealthCheckResult
```

Perform health check on a specific module.

**Parameters:**
- `module_name` (str): Name of the module to check

**Returns:** `HealthCheckResult` - Health check results

```python
def check_module_dependencies(module_name: str) -> Dict[str, HealthStatus]
```

Check dependencies for a specific module.

**Parameters:**
- `module_name` (str): Name of the module to check

**Returns:** `Dict[str, HealthStatus]` - Dependency health status

```python
def check_module_performance(module_name: str) -> Dict[str, Any]
```

Check performance metrics for a specific module.

**Parameters:**
- `module_name` (str): Name of the module to check

**Returns:** `Dict[str, Any]` - Performance metrics

```python
def check_module_availability(module_name: str) -> bool
```

Check if a module is available and importable.

**Parameters:**
- `module_name` (str): Name of the module to check

**Returns:** `bool` - True if module is available

### Health Reporting Functions

```python
def generate_health_report(modules: List[str]) -> HealthReport
```

Generate health report for specified modules.

**Parameters:**
- `modules` (List[str]): List of module names to include

**Returns:** `HealthReport` - Comprehensive health report

```python
def format_health_report(report: HealthReport, format: str = "text") -> str
```

Format health report in specified format.

**Parameters:**
- `report` (HealthReport): Health report to format
- `format` (str): Output format ("text", "json", "html"). Defaults to "text"

**Returns:** `str` - Formatted health report

```python
def export_health_report(report: HealthReport, filepath: str) -> None
```

Export health report to file.

**Parameters:**
- `report` (HealthReport): Health report to export
- `filepath` (str): Path to export file

**Returns:** None

## Data Structures

### ModuleCapability
```python
@dataclass
class ModuleCapability:
    name: str
    path: Path
    description: str
    version: str
    functions: list[FunctionInfo]
    classes: list[ClassInfo]
    dependencies: list[str]
    has_tests: bool
    has_docs: bool
    last_modified: str
    capabilities: list[str]
    complexity_score: int
```

Represents the capabilities of a discovered module.

### FunctionInfo
```python
@dataclass
class FunctionInfo:
    name: str
    signature: str
    parameters: list[dict[str, Any]]
    return_annotation: str
    decorators: list[str]
    is_async: bool
    is_generator: bool
    docstring: Optional[str]
    complexity: int
```

Information about a function extracted from code analysis.

### ClassInfo
```python
@dataclass
class ClassInfo:
    name: str
    methods: list[FunctionInfo]
    properties: list[str]
    base_classes: list[str]
    docstring: Optional[str]
    decorators: list[str]
```

Information about a class extracted from code analysis.

### HealthCheckResult
```python
@dataclass
class HealthCheckResult:
    module_name: str
    status: HealthStatus
    checks_passed: int
    checks_failed: int
    failed_checks: list[str]
    performance_metrics: dict[str, Any]
    recommendations: list[str]
    timestamp: datetime
```

Results of a health check on a module.

### HealthReport
```python
@dataclass
class HealthReport:
    modules_checked: int
    healthy_modules: int
    unhealthy_modules: int
    overall_status: HealthStatus
    module_results: list[HealthCheckResult]
    system_metrics: dict[str, Any]
    recommendations: list[str]
    generated_at: datetime
```

Comprehensive health report for the system.

## Enums

### HealthStatus
```python
class HealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
```

Health status levels for modules and systems.

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `discovery_engine.py` – Main system discovery and analysis engine
- `capability_scanner.py` – Module capability scanning and AST analysis
- `status_reporter.py` – System status reporting and dashboard
- `health_checker.py` – Module health checking and validation
- `health_reporter.py` – Health report generation and formatting

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `MCP_TOOL_SPECIFICATION.md` – AI agent tool specifications
- `SECURITY.md` – Security considerations for system discovery

## Operating Contracts

### Universal System Discovery Protocols

All system discovery operations within the Codomyrmex platform must:

1. **Non-Intrusive** - Discovery operations don't interfere with system operation
2. **Comprehensive Coverage** - All modules and capabilities are discoverable
3. **Accurate Analysis** - Code analysis produces correct function signatures and capabilities
4. **Real-Time Updates** - Discovery results reflect current system state
5. **Performance Conscious** - Discovery operations complete within reasonable time limits

### Module-Specific Guidelines

#### Module Discovery
- Scan all module directories systematically
- Extract accurate metadata from module files
- Handle import errors gracefully
- Provide progress feedback for long operations

#### Capability Analysis
- Use AST parsing for accurate code analysis
- Extract complete function signatures with type hints
- Identify module capabilities and classifications
- Calculate complexity metrics accurately

#### Health Monitoring
- Check module importability and basic functionality
- Monitor performance metrics where available
- Validate dependencies and compatibility
- Provide actionable health recommendations

#### Status Reporting
- Generate system overviews
- Provide both summary and detailed views
- Support multiple output formats
- Include historical trends where applicable

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification (if applicable)

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Source Root**: [src](../../README.md) - Source code documentation