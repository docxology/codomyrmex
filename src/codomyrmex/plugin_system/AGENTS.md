# Codomyrmex Agents — src/codomyrmex/plugin_system

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Plugin System Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Plugin system module providing extensible architecture for loading and managing plugins in the Codomyrmex platform. This module enables dynamic extension of platform capabilities through a well-defined plugin interface and lifecycle management.

The plugin_system module serves as the foundation for platform extensibility, allowing third-party developers and internal modules to extend functionality without modifying core code.

## Module Overview

### Key Capabilities
- **Plugin Loading**: Dynamic loading of plugin modules
- **Plugin Validation**: Security and compatibility validation
- **Plugin Registry**: Centralized plugin discovery and management
- **Lifecycle Management**: Plugin initialization, execution, and cleanup

### Key Features
- Secure plugin isolation and sandboxing
- Version compatibility checking
- Dependency resolution and management
- Plugin metadata and configuration
- Hot-reload capabilities for development

## Function Signatures

### Plugin Management Functions

```python
def get_plugin_manager() -> PluginManager
```

Get the global plugin manager instance.

**Returns:** `PluginManager` - Global plugin manager instance

```python
def discover_plugins() -> List[PluginInfo]
```

Discover available plugins in the system.

**Returns:** `List[PluginInfo]` - List of discovered plugin information

```python
def load_plugin(plugin_name: str, config: Optional[Dict[str, Any]] = None) -> LoadResult
```

Load and initialize a plugin by name.

**Parameters:**
- `plugin_name` (str): Name of the plugin to load
- `config` (Optional[Dict[str, Any]]): Plugin configuration dictionary

**Returns:** `LoadResult` - Result of the plugin loading operation

```python
def unload_plugin(plugin_name: str) -> bool
```

Unload a previously loaded plugin.

**Parameters:**
- `plugin_name` (str): Name of the plugin to unload

**Returns:** `bool` - True if successfully unloaded, False otherwise

### Plugin Discovery Functions

```python
def discover_plugins() -> List[PluginInfo]
```

Discover available plugins from configured paths.

**Returns:** `List[PluginInfo]` - List of discovered plugin information objects

### Plugin Validation Functions

```python
def validate_plugin(plugin_path: str) -> ValidationResult
```

Validate a plugin for security and compatibility requirements.

**Parameters:**
- `plugin_path` (str): Path to the plugin to validate

**Returns:** `ValidationResult` - Validation result with status and issues

```python
def check_plugin_security(plugin_path: str) -> List[str]
```

Perform security checks on a plugin.

**Parameters:**
- `plugin_path` (str): Path to the plugin to check

**Returns:** `List[str]` - List of security issues found

```python
def validate_plugin_metadata(metadata: Dict[str, Any]) -> List[str]
```

Validate plugin metadata for required fields and formats.

**Parameters:**
- `metadata` (Dict[str, Any]): Plugin metadata dictionary

**Returns:** `List[str]` - List of validation errors

### Plugin Registry Functions

```python
def create_plugin_info(**kwargs) -> PluginInfo
```

Create a PluginInfo object from keyword arguments.

**Parameters:**
- `**kwargs` - Plugin information attributes

**Returns:** `PluginInfo` - Created plugin information object

```python
def get_registry() -> PluginRegistry
```

Get the global plugin registry instance.

**Returns:** `PluginRegistry` - Global plugin registry instance

## Data Structures

### PluginState Enum
```python
class PluginState(Enum):
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"
    DISABLED = "disabled"
```

Enumeration of possible plugin states during lifecycle.

### PluginType Enum
```python
class PluginType(Enum):
    ANALYSIS = "analysis"
    UTILITY = "utility"
    INTEGRATION = "integration"
    EXTENSION = "extension"
```

Enumeration of plugin types for categorization.

### PluginInfo Class
```python
@dataclass
class PluginInfo:
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    entry_point: str
    dependencies: List[str]
    metadata: Dict[str, Any]
    state: PluginState = PluginState.UNLOADED
```

Information about a plugin including metadata and current state.

### PluginHook Class
```python
@dataclass
class PluginHook:
    name: str
    description: str
    parameters: Dict[str, str]
    return_type: str
```

Definition of a plugin hook point for extension.

### Plugin Abstract Base Class
```python
class Plugin(ABC):
    @property
    def name(self) -> str: ...

    @property
    def version(self) -> str: ...

    @property
    def description(self) -> str: ...

    def initialize(self, config: Dict[str, Any]) -> bool: ...

    def execute(self, **kwargs) -> Any: ...

    def cleanup(self) -> bool: ...

    def get_info(self) -> PluginInfo: ...
```

Abstract base class defining the plugin interface that all plugins must implement.

### ValidationResult Class
```python
@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]
```

Result of plugin validation including errors and warnings.

### LoadResult Class
```python
@dataclass
class LoadResult:
    success: bool
    plugin: Optional[Plugin]
    error_message: Optional[str]
    load_time: float
```

Result of plugin loading operation with timing and error information.

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `plugin_loader.py` – Plugin loading and initialization logic
- `plugin_manager.py` – Plugin lifecycle and execution management
- `plugin_registry.py` – Plugin discovery and registration
- `plugin_validator.py` – Plugin security and compatibility validation

## Operating Contracts

### Universal Plugin Protocols

All plugin handling within the Codomyrmex platform must:

1. **Security First** - Validate plugins before loading and execution
2. **Isolation** - Plugins run in isolated contexts to prevent interference
3. **Version Compatibility** - Ensure plugin compatibility with platform versions
4. **Resource Limits** - Enforce resource constraints on plugin execution

### Module-Specific Guidelines

#### Plugin Development
- Follow defined plugin interface contracts
- Include error handling
- Provide clear documentation and metadata
- Test plugins across supported platforms

#### Plugin Loading
- Validate plugins before loading in production
- Provide clear error messages for loading failures
- Support both development and production loading modes
- Monitor plugin resource usage

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Source Root**: [src](../../README.md) - Source code documentation