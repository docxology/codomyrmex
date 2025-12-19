# Codomyrmex Agents — src/codomyrmex/logging_monitoring

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Foundation module providing centralized logging infrastructure for the Codomyrmex platform. This module implements a unified logging system that ensures consistent log formatting, configurable output destinations, and proper log level management across all platform components.

The logging_monitoring module serves as the backbone for observability, enabling debugging, monitoring, and troubleshooting throughout the entire Codomyrmex ecosystem.

## Module Overview

### Key Capabilities
- **Centralized Configuration**: Unified logging setup via environment variables and configuration files
- **Multiple Output Formats**: Support for text and JSON log formats
- **Flexible Destinations**: Console and file output with configurable paths
- **Structured Logging**: JSON formatter for machine-readable logs
- **Logger Factory**: Consistent logger instantiation across modules

### Key Features
- Environment-based configuration (log level, format, output type)
- Custom JSON formatter with timestamps and structured data
- Hierarchical logger naming for clear source identification
- Performance-optimized logging with minimal overhead
- Integration with Python's standard logging framework

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `logger_config.py` – Main logging configuration and utilities

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `MCP_TOOL_SPECIFICATION.md` – AI agent tool specifications
- `SECURITY.md` – Security considerations and best practices
- `CHANGELOG.md` – Version history and updates

### Supporting Files
- `requirements.txt` – Module dependencies
- `docs/` – Additional documentation
- `tests/` – Comprehensive test suite

## Operating Contracts

### Universal Logging Protocols

All logging within the Codomyrmex platform must:

1. **Use Centralized Configuration** - All modules obtain loggers via `get_logger(__name__)` from this module
2. **Follow Consistent Naming** - Logger names should match module hierarchy for clear identification
3. **Respect Log Levels** - Appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) for different message types
4. **Include Context** - Log messages should provide sufficient context for debugging and monitoring
5. **Handle Sensitive Data** - Never log passwords, API keys, or other sensitive information

### Module-Specific Guidelines

#### Logger Usage
- Import logger at module level: `logger = get_logger(__name__)`
- Use appropriate log levels for different scenarios
- Include relevant context in log messages
- Avoid excessive logging in performance-critical paths

#### Configuration Management
- Configure logging once at application startup via `setup_logging()`
- Use environment variables for runtime configuration
- Support both development and production logging needs
- Enable JSON logging for production monitoring systems

## Navigation Links

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Practical usage demonstrations

### Related Modules
- **Environment Setup**: [../environment_setup/](../../environment_setup/) - Environment configuration
- **Terminal Interface**: [../terminal_interface/](../../terminal_interface/) - Console output formatting

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation

## Agent Coordination

### Integration Points

When integrating with other modules:

1. **Logger Dependencies** - Ensure logging is configured before other modules initialize
2. **Configuration Sharing** - Coordinate log level settings across related modules
3. **Output Coordination** - Align log destinations and formats with monitoring systems
4. **Performance Monitoring** - Monitor logging performance impact on other modules

### Quality Gates

Before logging changes are accepted:

1. **Configuration Tested** - All environment configurations properly tested
2. **Format Validated** - Both text and JSON formats produce expected output
3. **Performance Verified** - Logging overhead remains within acceptable limits
4. **Security Reviewed** - No sensitive data logging introduced
5. **Integration Confirmed** - Changes work correctly with existing module loggers

## Version History

- **v0.1.0** (December 2025) - Initial centralized logging system with JSON and text format support
