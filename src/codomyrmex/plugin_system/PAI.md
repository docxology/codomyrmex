# Personal AI Infrastructure — Plugin System Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Plugin System module provides dynamic capability extension through plugin discovery, loading, dependency resolution, and lifecycle management. It serves as the Foundation Layer extensibility infrastructure that enables third-party and custom modules to integrate seamlessly into the codomyrmex ecosystem. When PAI needs to extend its capabilities at runtime — loading a new analyzer, registering a workflow hook, or scanning for available tools — the Plugin System is the mechanism that makes it possible.

## PAI Capabilities

### Plugin Discovery

Discover available plugins from entry points and configured scan paths:

```python
from codomyrmex.plugin_system import PluginManager, PluginRegistry

# Initialize the plugin manager with custom scan directories
manager = PluginManager(plugin_directories=["./plugins", "./extensions"])

# Discover all available plugins across configured paths
available = manager.discover_plugins()
for plugin_info in available:
    print(f"Found: {plugin_info.name} v{plugin_info.version} [{plugin_info.plugin_type.value}]")

# Entry-point based discovery (uses setuptools entry_points)
from codomyrmex.plugin_system.discovery import PluginDiscovery
discovery = PluginDiscovery(entry_point_group="codomyrmex.plugins")
result = discovery.scan_entry_points()
for p in result.plugins:
    print(f"  Entry point: {p.name} -> {p.module_path} ({p.state.value})")
```

### Dependency Resolution

Resolve plugin load order using topological sort to guarantee dependencies are satisfied before dependents load:

```python
from codomyrmex.plugin_system.dependency_resolver import DependencyResolver, DependencyNode

resolver = DependencyResolver()

# Define plugins with their dependency chains
resolver.add(DependencyNode(name="code_formatter", dependencies=[]))
resolver.add(DependencyNode(name="linter", dependencies=["code_formatter"]))
resolver.add(DependencyNode(name="auto_fix", dependencies=["linter", "code_formatter"]))

result = resolver.resolve()

# result.load_order: ["code_formatter", "linter", "auto_fix"]
# result.missing: [] (empty if all deps satisfied)
# result.circular: [] (empty if no cycles detected)
print(f"Resolution: {result.status.value}")
print(f"Load order: {result.load_order}")
```

### Plugin Lifecycle

Plugins follow a strict lifecycle with four hook stages:

- **init** — Plugin is loaded into memory and its metadata is registered with the `PluginRegistry`. Configuration is applied via `Plugin.initialize(config)`. State transitions: `UNLOADED` -> `INITIALIZING` -> `LOADED`.
- **activate** — Plugin is enabled and ready to serve requests. State transitions: `LOADED` -> `ACTIVE`. The manager calls `PluginManager.enable_plugin(name)`.
- **deactivate** — Plugin is temporarily disabled but remains in memory. State transitions: `ACTIVE` -> `DISABLED`. Reversible via re-activation without a full reload.
- **cleanup** — Plugin is fully unloaded and unregistered. State transitions: any -> `SHUTTING_DOWN` -> `UNLOADED`. The manager calls `PluginManager.unload_plugin(name)`, which invokes `Plugin.shutdown()` and removes the plugin from the registry.

```python
from codomyrmex.plugin_system import PluginManager

manager = PluginManager()

# Full lifecycle demonstration
result = manager.load_plugin("my_analyzer", config={"depth": 3})  # init
if result.success:
    manager.enable_plugin("my_analyzer")                           # activate

    # ... use the plugin ...

    manager.disable_plugin("my_analyzer")                          # deactivate
    manager.unload_plugin("my_analyzer")                           # cleanup
```

### Plugin Types and Registration

The registry supports nine plugin type categories, each serving a distinct architectural role:

```python
from codomyrmex.plugin_system import PluginType

# Available types:
# PluginType.ANALYZER   — Code analysis and inspection
# PluginType.FORMATTER  — Code formatting and style
# PluginType.EXPORTER   — Data export to external formats
# PluginType.IMPORTER   — Data import from external sources
# PluginType.PROCESSOR  — Data transformation pipelines
# PluginType.HOOK       — Event-driven extension points
# PluginType.UTILITY    — General-purpose utilities
# PluginType.ADAPTER    — Bridge to external systems
# PluginType.AGENT      — AI agent integrations
```

### Hook System

Plugins can register and emit hooks for event-driven coordination:

```python
from codomyrmex.plugin_system import PluginManager

manager = PluginManager()

# Register a global hook for cross-plugin events
hook = manager.register_hook(
    "on_analysis_complete",
    description="Fired when code analysis finishes"
)

# Any plugin can subscribe to the hook
hook.register(lambda result: print(f"Analysis done: {result}"))

# Emit the hook from any plugin or the manager
results = manager.emit_hook("on_analysis_complete", {"files": 42, "issues": 3})
```

## MCP Tools

The Plugin System exposes two MCP tools via `@mcp_tool` decorators in `mcp_tools.py`. Both are read-only and safe to call without trust elevation.

| Tool | Description | Trust Level | Parameters |
|------|-------------|-------------|------------|
| `plugin_scan_entry_points` | Scan for installed plugins via Python package entry points. Returns plugin names, module paths, and states. | READ-ONLY | `entry_point_group` (default: `"codomyrmex.plugins"`) |
| `plugin_resolve_dependencies` | Resolve plugin dependencies using topological sort. Returns load order, missing deps, and circular references. | READ-ONLY | `plugins` (list of `{"name": str, "dependencies": [str]}`) |

### MCP Tool Usage Examples

```python
# Via MCP bridge — scan for available plugins
result = plugin_scan_entry_points(entry_point_group="codomyrmex.plugins")
# Returns: {"status": "ok", "plugin_count": 5, "plugins": [...], "errors": []}

# Via MCP bridge — resolve load order for a set of plugins
result = plugin_resolve_dependencies(plugins=[
    {"name": "base_tools", "dependencies": []},
    {"name": "git_plugin", "dependencies": ["base_tools"]},
    {"name": "review_plugin", "dependencies": ["git_plugin", "base_tools"]},
])
# Returns: {"status": "ok", "load_order": ["base_tools", "git_plugin", "review_plugin"], ...}
```

## PAI Algorithm Phase Mapping

| Phase | Plugin System Contribution |
|-------|----------------------------|
| **OBSERVE** | Discover available plugins and their capabilities via `plugin_scan_entry_points`. Enumerate installed extensions to understand what tools and analyzers are available in the current environment. |
| **THINK** | Evaluate plugin dependencies and compatibility. Use `plugin_resolve_dependencies` to determine if required plugins are available and what gaps exist before selecting a strategy. |
| **PLAN** | Compute plugin load order via topological sort. Plan which plugins to activate for a given workflow, ensuring dependencies are loaded first and conflicts are identified early. |
| **BUILD** | Register new plugin hooks and extension points. When building new capabilities, use the Plugin base class and PluginInfo decorator to create conforming extensions. |
| **EXECUTE** | Load and activate plugins dynamically at runtime. The `PluginManager` orchestrates the full init/activate lifecycle, enabling dynamic capability extension during workflow execution. |
| **VERIFY** | Validate plugin health and compatibility. Use `PluginValidator` to check plugin structure, security, and metadata. Verify all dependencies are satisfied via `PluginRegistry.check_dependencies()`. |
| **LEARN** | Capture plugin usage patterns and performance. Plugin state transitions (load, activate, error) are logged through `logging_monitoring` for post-hoc analysis of what worked and what failed. |

## PAI Configuration

### Environment Variables

```bash
# Plugin scan paths (colon-separated directories to search for plugins)
export CODOMYRMEX_PLUGIN_SCAN_PATHS="./plugins:./extensions:~/.codomyrmex/plugins"

# Entry point group name for setuptools-based discovery
export CODOMYRMEX_PLUGIN_ENTRY_POINT_GROUP="codomyrmex.plugins"

# Enable or disable automatic plugin validation before loading
export CODOMYRMEX_PLUGIN_AUTO_VALIDATE="true"

# Enable parallel plugin loading (default: true)
export CODOMYRMEX_PLUGIN_PARALLEL_LOAD="true"
```

### Plugin Registry Location

The global plugin registry is a singleton managed by `get_registry()` in `core/plugin_registry.py`. Plugin metadata is stored in-memory during the process lifetime. For persistent plugin state across sessions, the registry integrates with codomyrmex's config management module.

### Version Constraints

Plugin version compatibility is checked during the validation phase. The `PluginInfo.version` field follows semantic versioning. The `PluginValidator` ensures that plugin metadata is well-formed and that declared dependencies reference plugins that exist in the registry.

## PAI Best Practices

### 1. Discover Custom PAI Capability Plugins

When PAI needs to know what extensions are available, scan entry points before planning:

```python
from codomyrmex.plugin_system import PluginManager

manager = PluginManager()
available = manager.discover_plugins()

# Filter by type to find specific capabilities
analyzers = [p for p in available if p.plugin_type.value == "analyzer"]
agents = [p for p in available if p.plugin_type.value == "agent"]
```

### 2. Resolve Dependencies for Workflow Plugins

Before executing a multi-plugin workflow, resolve the dependency graph to ensure correct load order:

```python
from codomyrmex.plugin_system.dependency_resolver import DependencyResolver, DependencyNode

resolver = DependencyResolver()
for plugin_info in required_plugins:
    resolver.add(DependencyNode(
        name=plugin_info.name,
        dependencies=plugin_info.dependencies,
    ))

result = resolver.resolve()
if result.missing:
    raise RuntimeError(f"Cannot start workflow: missing plugins {result.missing}")
if result.circular:
    raise RuntimeError(f"Circular dependency detected: {result.circular}")

# Load in resolved order
for name in result.load_order:
    manager.load_plugin(name)
```

### 3. Integrate with MCP Auto-Discovery

The Plugin System's entry-point scanning is the foundation for `model_context_protocol`'s auto-discovery of `@mcp_tool` decorators. When a new module exposes an `mcp_tools.py` submodule, the plugin system's discovery mechanism (via `pkgutil` scan) finds it and the MCP bridge surfaces those tools automatically with a 5-minute TTL cache.

```python
# The MCP bridge uses plugin-system-style discovery internally:
# 1. pkgutil scans all codomyrmex submodules for mcp_tools.py
# 2. Each @mcp_tool decorated function is registered
# 3. Tools are cached with CODOMYRMEX_MCP_CACHE_TTL (default 300s)
# 4. No manual registration needed — just add @mcp_tool decorator
```

### 4. Validate Before Loading in Production

Always validate plugins before loading to prevent untrusted code from compromising the host:

```python
from codomyrmex.plugin_system import PluginManager

manager = PluginManager()
manager.auto_validate = True  # Enabled by default

# Validation checks: metadata completeness, security scan, version format
result = manager.load_plugin("untrusted_plugin")
if not result.success:
    print(f"Rejected: {result.error_message}")
```

## Architecture Role

**Foundation Layer** — The Plugin System sits at the Foundation Layer of codomyrmex's architecture, providing extensibility infrastructure that higher layers depend on.

**Dependencies** (what Plugin System uses):
- `logging_monitoring/` — Structured logging for plugin lifecycle events
- `validation/` — `PluginValidator` for security and metadata validation

**Consumed by** (what depends on Plugin System):
- `system_discovery/` — Capability scanning to enumerate available modules and tools
- `orchestrator/` — Dynamic tool loading for workflow execution
- `model_context_protocol/` — Auto-discovery of `@mcp_tool` decorated functions across all modules

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
