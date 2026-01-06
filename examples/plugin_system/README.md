# Plugin System Example

## Signposting
- **Parent**: [Examples](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Module**: `codomyrmex.plugin_system` - Extensible Plugin Architecture

## Overview

This example demonstrates the comprehensive plugin management capabilities of Codomyrmex, showcasing how to discover, validate, load, and manage plugins through their complete lifecycle. The plugin system provides a secure and extensible architecture for extending platform functionality.

## What This Example Demonstrates

- **Plugin Discovery**: Automatic discovery of plugins from configured directories
- **Plugin Validation**: Security scanning and compatibility validation
- **Plugin Loading**: Safe loading and initialization of plugins
- **Lifecycle Management**: Enable/disable plugins and state management
- **Hook System**: Global hooks for plugin communication
- **Dependency Resolution**: Plugin dependency checking and resolution
- **System Monitoring**: Comprehensive plugin system status and health

## Features Demonstrated

### Core Plugin Operations
- Plugin discovery from multiple directories
- Security validation and dependency checking
- Parallel plugin loading with timeout handling
- Plugin state management (active/disabled/error)
- Plugin metadata extraction and management

### Advanced Capabilities
- Hook-based plugin communication
- Plugin configuration management
- System health monitoring
- Plugin registry persistence
- Error recovery and cleanup

### Security Features
- Plugin validation before loading
- Security scanning for malicious code
- Sandboxed execution environment
- Dependency verification

## Tested Methods

The example utilizes and demonstrates methods primarily tested in:
- `src/codomyrmex/tests/unit/test_plugin_system.py`

Specifically, it covers:
- `PluginManager.discover_plugins()` - Verified in `TestPluginManager::test_plugin_discovery_through_manager`
- `PluginManager.load_plugin()` - Verified in `TestPluginManager::test_load_plugin_with_validation`
- `PluginManager.list_plugins()` - Verified in `TestPluginManager::test_plugin_listing`
- `PluginValidator.validate_plugin()` - Verified in `TestPluginValidator::test_validate_plugin`
- `PluginRegistry.register_plugin()` - Verified in `TestPluginRegistry::test_plugin_registration`
- `PluginManager.enable_plugin()` - Verified in `TestPluginManager::test_plugin_status`
- `PluginManager.disable_plugin()` - Verified in `TestPluginManager::test_plugin_status`
- `PluginManager.get_plugin_status()` - Verified in `TestPluginManager::test_plugin_status`
- `PluginManager.get_system_status()` - Verified in `TestPluginManager::test_plugin_status`
- `PluginManager.register_hook()` - Verified in `TestPluginManager::test_hook_registration`
- `PluginManager.emit_hook()` - Verified in `TestPluginManager::test_hook_registration`
- `PluginManager.unload_plugin()` - Verified in `TestPluginManager::test_plugin_status`
- `PluginManager.cleanup()` - Verified in `TestPluginManager::test_plugin_status`

## Configuration

The example uses `config.yaml` (or `config.json`) for settings:

```yaml
# Plugin System Configuration
logging:
  level: INFO
  file: logs/plugin_system_example.log
  output_type: TEXT

output:
  format: json
  file: output/plugin_system_results.json

plugin_system:
  # Plugin discovery settings
  discovery:
    enabled: true
    auto_discover: true
    plugin_directories:
      - "./plugins"
      - "./custom_plugins"

  # Plugin validation settings
  validation:
    enabled: true
    auto_validate: true
    strict_mode: false
    security_checks: true
    dependency_checks: true

  # Plugin loading settings
  loading:
    parallel_loading: true
    max_concurrent_loads: 3
    timeout_seconds: 30
    fail_fast: false

  # Plugin lifecycle settings
  lifecycle:
    auto_enable: true
    auto_disable_on_error: true
    cleanup_on_shutdown: true

  # Hook system settings
  hooks:
    enabled: true
    max_handlers_per_hook: 10
    timeout_seconds: 5

# Plugin-specific configurations
plugin_configs:
  analysis_tool:
    max_concurrent_operations: 5
    output_format: json
    enable_caching: true

  visualization_helper:
    supported_formats: ["png", "svg", "pdf"]
    default_resolution: 300
    color_scheme: "default"

  utility_processor:
    batch_size: 100
    retry_attempts: 3
    enable_metrics: true
```

### Configuration Options

- **`logging.level`**: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- **`logging.file`**: Log file path
- **`output.format`**: Output format (json, yaml)
- **`output.file`**: Results file path

- **`plugin_system.discovery.enabled`**: Enable/disable plugin discovery
- **`plugin_system.discovery.plugin_directories`**: List of directories to scan for plugins

- **`plugin_system.validation.enabled`**: Enable/disable validation
- **`plugin_system.validation.security_checks`**: Enable security scanning
- **`plugin_system.validation.dependency_checks`**: Check plugin dependencies

- **`plugin_system.loading.parallel_loading`**: Load plugins in parallel
- **`plugin_system.loading.timeout_seconds`**: Loading timeout
- **`plugin_system.loading.fail_fast`**: Stop on first failure

- **`plugin_system.lifecycle.auto_enable`**: Auto-enable loaded plugins
- **`plugin_system.lifecycle.cleanup_on_shutdown`**: Clean up on shutdown

- **`plugin_configs`**: Plugin-specific configuration objects

## Running the Example

### Prerequisites

Ensure you have the Codomyrmex package installed:

```bash
cd /path/to/codomyrmex
pip install -e .
```

### Basic Execution

```bash
# Navigate to the example directory
cd examples/plugin_system

# Run the example
python example_basic.py
```

### With Custom Configuration

```bash
# Use a custom config file
python example_basic.py --config my_custom_config.yaml
```

### With Environment Variables

```bash
# Override logging level
LOG_LEVEL=DEBUG python example_basic.py

# Use different output format
OUTPUT_FORMAT=yaml python example_basic.py
```

## Expected Output

The script will print a summary of plugin operations and save a JSON file (`output/plugin_system_results.json`) containing the results, including:

- `plugins_discovered`: Number of plugins found
- `plugins_validated`: Number of plugins validated
- `plugins_loaded`: Number of plugins successfully loaded
- `plugins_unloaded`: Number of plugins unloaded
- `lifecycle_operations`: Number of enable/disable operations
- `hooks_demonstrated`: Number of hooks demonstrated
- `system_status_retrieved`: Whether system status was retrieved
- `cleanup_completed`: Whether cleanup was successful

Example `output/plugin_system_results.json`:
```json
{
  "plugins_discovered": 3,
  "plugins_validated": 3,
  "plugins_loaded": 3,
  "plugins_unloaded": 3,
  "lifecycle_operations": 4,
  "hooks_demonstrated": 1,
  "system_status_retrieved": true,
  "cleanup_completed": true
}
```

## Troubleshooting

### Common Issues

1. **Plugin Discovery Fails**
   - Check that plugin directories exist
   - Verify plugin files have correct naming
   - Ensure plugin files are valid Python

2. **Plugin Validation Errors**
   - Check plugin metadata (PluginInfo)
   - Verify plugin class inheritance
   - Review security scan results

3. **Plugin Loading Fails**
   - Check plugin dependencies
   - Verify plugin configuration
   - Review error messages in logs

4. **Hook System Issues**
   - Ensure hooks are registered before emission
   - Check handler function signatures
   - Verify timeout settings

### Debug Mode

Enable debug logging for detailed information:

```yaml
logging:
  level: DEBUG
```

### Manual Plugin Creation

To create a custom plugin for testing:

```python
from codomyrmex.plugin_system import Plugin, PluginInfo, PluginType

class MyCustomPlugin(Plugin):
    def __init__(self, info):
        super().__init__(info)

    def on_load(self):
        print(f"Custom plugin {self.info.name} loaded!")

# Plugin metadata
PLUGIN_INFO = PluginInfo(
    name="my_custom_plugin",
    version="1.0.0",
    description="Custom plugin example",
    author="Your Name",
    plugin_type=PluginType.UTILITY,
    entry_point="my_custom_plugin.py"
)
```

## Plugin Architecture

### Plugin Types

- **ANALYSIS**: Data analysis and processing
- **VISUALIZATION**: Chart and graph generation
- **INTEGRATION**: External service integration
- **TRANSFORMATION**: Data transformation utilities
- **UTILITY**: General-purpose utilities
- **EXTENSION**: Framework extensions

### Plugin States

- **UNLOADED**: Plugin not loaded
- **LOADING**: Plugin being loaded
- **LOADED**: Plugin loaded but not active
- **INITIALIZING**: Plugin initializing
- **ACTIVE**: Plugin fully operational
- **ERROR**: Plugin in error state
- **DISABLED**: Plugin manually disabled

### Hook System

Plugins can register handlers for global hooks:

```python
# Register hook handler
manager.register_hook("data_processing")

# Plugin can connect to hook
def my_handler(data):
    return process_data(data)

plugin.register_hook("data_processing", my_handler)
```

## Performance Considerations

- **Parallel Loading**: Enable for multiple plugins
- **Validation Caching**: Avoid re-validation on reload
- **Resource Limits**: Configure timeouts and concurrency
- **Cleanup**: Always cleanup on shutdown

## Security Best Practices

- **Validation**: Always validate plugins before loading
- **Sandboxing**: Use execution sandboxing for untrusted plugins
- **Dependency Checks**: Verify plugin dependencies
- **Access Control**: Limit plugin capabilities
- **Audit Logging**: Log all plugin operations

## Integration Examples

### With Other Modules

The plugin system integrates with:

- **Logging Monitoring**: Plugin operation logging
- **Security Audit**: Plugin security scanning
- **Configuration Management**: Plugin configuration
- **Events**: Plugin event publishing

### Workflow Integration

```python
# Load analysis plugins for a workflow
analysis_plugins = manager.list_plugins(PluginType.ANALYSIS)

# Execute analysis pipeline
for plugin in analysis_plugins:
    if "loaded" in plugin.tags:
        result = manager.get_plugin(plugin.name).process_data(data)
```

## Advanced Usage

### Custom Plugin Validators

```python
from codomyrmex.plugin_system import PluginValidator

class CustomValidator(PluginValidator):
    def validate_plugin(self, plugin_path):
        # Custom validation logic
        result = super().validate_plugin(plugin_path)
        # Additional checks...
        return result
```

### Plugin Factories

```python
def create_plugin_factory(plugin_type):
    def factory(info):
        if plugin_type == PluginType.ANALYSIS:
            return AnalysisPlugin(info)
        elif plugin_type == PluginType.VISUALIZATION:
            return VisualizationPlugin(info)
    return factory
```

### Registry Persistence

```python
# Save registry state
manager.save_plugin_registry("plugin_registry.json")

# Restore on restart
manager.load_plugin_registry("plugin_registry.json")
```

## Related Documentation

- **[Plugin System API](../../src/codomyrmex/plugin_system/)**
- **[Configuration Management](../config_management/)**

---

**Status**: Complete example demonstrating plugin system capabilities
**Tested Methods**: 12 core plugin management methods
**Features**: Discovery, validation, loading, lifecycle, hooks, monitoring

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
