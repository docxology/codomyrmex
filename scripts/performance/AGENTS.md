# Codomyrmex Agents — scripts/performance

## Signposting
- **Parent**: [Parent](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Performance monitoring automation scripts providing command-line interfaces for performance tracking, caching management, and system metrics collection. This script module enables automated performance monitoring and optimization workflows.

The performance scripts serve as the primary interface for system administrators and developers monitoring and optimizing Codomyrmex performance.

## Module Overview

### Key Capabilities
- **Performance Monitoring**: Real-time performance metrics collection
- **Cache Management**: Caching system monitoring and optimization
- **Resource Tracking**: System resource usage monitoring
- **Performance Analysis**: Bottleneck identification and optimization recommendations
- **Metrics Reporting**: Structured performance reports and dashboards

### Key Features
- Command-line interface with argument parsing
- Integration with core performance monitoring modules
- Structured output formatting (JSON, text, verbose)
- Error handling and validation
- Logging integration for monitoring tracking

## Function Signatures

### Core CLI Functions

```python
def main() -> None
```

Main CLI entry point for the performance monitoring orchestrator.

**Command-line Usage:**
```bash
python orchestrate.py [command] [options]
```

**Available Commands:**
- `monitor-stats` - Monitor performance statistics
- `cache-info` - Display cache information and statistics

**Global Options:**
- `--verbose, -v` - Enable verbose output
- `--interval, -i` - Monitoring interval in seconds

```python
def handle_monitor_stats(args) -> None
```

Handle performance monitoring commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `monitor_type` (str, optional): Type of monitoring ("cpu", "memory", "disk", "all"). Defaults to "all"
  - `duration` (int, optional): Monitoring duration in seconds. Defaults to 60
  - `output_file` (str, optional): Path to save monitoring results

**Returns:** None (monitors performance and outputs statistics)

```python
def handle_cache_info(args) -> None
```

Handle cache information commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `cache_type` (str, optional): Type of cache to analyze ("function", "module", "all"). Defaults to "all"
  - `show_stats` (bool, optional): Show detailed cache statistics. Defaults to True
  - `clear_cache` (bool, optional): Clear specified cache. Defaults to False

**Returns:** None (displays cache information and optionally clears cache)

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `orchestrate.py` – Main CLI orchestrator script

### Documentation
- `README.md` – Script usage and overview
- `AGENTS.md` – This coordination document

### Supporting Files
- Integration with `_orchestrator_utils.py` for shared utilities

## Operating Contracts

### Universal Script Protocols

All scripts in this module must:

1. **CLI Standards**: Follow consistent command-line argument patterns
2. **Error Handling**: Provide clear error messages and exit codes
3. **Performance Impact**: Minimize monitoring overhead on system performance
4. **Data Accuracy**: Ensure accurate collection of performance metrics
5. **Resource Efficiency**: Use system resources efficiently during monitoring

### Module-Specific Guidelines

#### Performance Monitoring
- Support real-time and historical performance data
- Provide configurable monitoring intervals and thresholds
- Handle high-frequency data collection efficiently
- Include system and application-level metrics

#### Cache Management
- Monitor cache hit/miss ratios and performance
- Provide cache size and memory usage statistics
- Support cache clearing and optimization operations
- Include cache configuration validation

#### Resource Tracking
- Monitor CPU, memory, disk, and network usage
- Provide resource utilization trends and alerts
- Support different monitoring timeframes
- Include resource allocation and optimization recommendations

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Script Overview**: [README.md](README.md) - Complete script documentation

### Related Scripts

### Platform Navigation
- **Scripts Directory**: [../README.md](../README.md) - Scripts directory overview

## Agent Coordination

### Integration Points

When integrating with other scripts:

1. **Shared Utilities**: Use `_orchestrator_utils.py` for common CLI patterns
2. **System Monitoring**: Coordinate with logging_monitoring scripts
3. **Resource Management**: Share data with physical_management scripts
4. **Alerting**: Integrate with notification and alerting systems

### Quality Gates

Before script changes are accepted:

1. **CLI Testing**: All command-line options work correctly
2. **Monitoring Testing**: Performance monitoring works accurately
3. **Resource Testing**: Scripts don't impact system performance significantly
4. **Data Testing**: Performance data is accurate and actionable
5. **Integration Testing**: Scripts work with core performance monitoring modules

## Version History

- **v0.1.0** (December 2025) - Initial performance monitoring automation scripts with metrics collection and cache management