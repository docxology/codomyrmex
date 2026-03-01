"""Unit tests for the plugin registry -- registration, discovery, hooks, and lifecycle."""

import time
from typing import Any

import pytest

from codomyrmex.plugin_system.core.plugin_registry import (
    Hook,
    Plugin,
    PluginInfo,
    PluginRegistry,
    PluginState,
    PluginType,
    create_plugin_info,
    get_registry,
)


# ============================================================================
# Test Plugin Helper Classes
# ============================================================================

class MockPlugin:
    """Mock plugin for testing purposes."""

    def __init__(self, info=None):
        self.info = info
        self.initialized = False
        self.shutdown_called = False
        self.config = {}
        self.state = "unloaded"
        self.hooks = {}
        self._info = info

    def initialize(self, config: dict[str, Any] | None = None) -> bool:
        self.config = config or {}
        self.initialized = True
        self.state = "active"
        return True

    def shutdown(self) -> bool:
        self.shutdown_called = True
        self.state = "shutdown"
        return True

    def get_state(self):
        return self.state

    def get_config(self):
        return self.config

    def set_config(self, config: dict[str, Any]):
        self.config = config


class FaultyInitPlugin(MockPlugin):
    """Plugin that fails during initialization."""

    def initialize(self, config: dict[str, Any] | None = None) -> bool:
        raise RuntimeError("Initialization failed intentionally")


class FaultyShutdownPlugin(MockPlugin):
    """Plugin that fails during shutdown."""

    def shutdown(self) -> bool:
        raise RuntimeError("Shutdown failed intentionally")


class SlowInitPlugin(MockPlugin):
    """Plugin with slow initialization."""

    def initialize(self, config: dict[str, Any] | None = None) -> bool:
        time.sleep(0.1)  # Simulate slow init
        return super().initialize(config)


class ResourceLeakPlugin(MockPlugin):
    """Plugin that simulates resource management."""

    resources_acquired = []

    def initialize(self, config: dict[str, Any] | None = None) -> bool:
        ResourceLeakPlugin.resources_acquired.append(f"resource_{id(self)}")
        return super().initialize(config)

    def shutdown(self) -> bool:
        if ResourceLeakPlugin.resources_acquired:
            ResourceLeakPlugin.resources_acquired.pop()
        return super().shutdown()


# ============================================================================
# Test Plugin Registry
# ============================================================================

@pytest.mark.unit
class TestPluginRegistry:
    """Test cases for PluginRegistry functionality."""

    def test_plugin_registry_creation(self):
        """Test creating a plugin registry."""
        registry = PluginRegistry()
        assert registry is not None
        assert registry._plugins == {}
        assert registry.categories == {}

    def test_plugin_info_creation(self):
        """Test creating PluginInfo."""
        info = PluginInfo(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin",
            author="Test Author",
            plugin_type=PluginType.UTILITY,
            entry_point="test_plugin.py"
        )

        assert info.name == "test_plugin"
        assert info.version == "1.0.0"
        assert info.plugin_type == PluginType.UTILITY

    def test_plugin_info_to_dict(self):
        """Test PluginInfo serialization to dictionary."""
        info = PluginInfo(
            name="serialization_test",
            version="2.0.0",
            description="Test serialization",
            author="Author",
            plugin_type=PluginType.ANALYZER,
            entry_point="test.py",
            dependencies=["dep1", "dep2"],
            tags=["test", "serialization"]
        )

        info_dict = info.to_dict()

        assert info_dict["name"] == "serialization_test"
        assert info_dict["version"] == "2.0.0"
        assert info_dict["plugin_type"] == "analyzer"
        assert info_dict["dependencies"] == ["dep1", "dep2"]
        assert info_dict["tags"] == ["test", "serialization"]

    def test_plugin_registration(self):
        """Test plugin registration."""
        registry = PluginRegistry()
        plugin = Plugin(PluginInfo(
            name="test_plugin",
            version="1.0.0",
            description="Test",
            author="Test",
            plugin_type=PluginType.UTILITY,
            entry_point="test.py"
        ))

        result = registry.register(plugin)

        assert result is True
        assert "test_plugin" in registry._plugins
        assert PluginType.UTILITY.value in registry.categories
        assert "test_plugin" in registry.categories[PluginType.UTILITY.value]

    def test_duplicate_registration_rejected(self):
        """Test that duplicate plugin registration is rejected."""
        registry = PluginRegistry()
        plugin1 = Plugin(PluginInfo(
            name="duplicate_test",
            version="1.0.0",
            description="First",
            author="Author",
            plugin_type=PluginType.UTILITY,
            entry_point="test.py"
        ))
        plugin2 = Plugin(PluginInfo(
            name="duplicate_test",
            version="2.0.0",
            description="Second",
            author="Author",
            plugin_type=PluginType.UTILITY,
            entry_point="test2.py"
        ))

        result1 = registry.register(plugin1)
        result2 = registry.register(plugin2)

        assert result1 is True
        assert result2 is False
        # First plugin should remain registered
        assert registry.get_plugin_info("duplicate_test").version == "1.0.0"

    def test_plugin_unregistration(self):
        """Test plugin unregistration."""
        registry = PluginRegistry()
        plugin = Plugin(PluginInfo(
            name="unregister_test",
            version="1.0.0",
            description="Test",
            author="Author",
            plugin_type=PluginType.UTILITY,
            entry_point="test.py"
        ))

        registry.register(plugin)
        assert "unregister_test" in registry._plugins

        result = registry.unregister("unregister_test")

        assert result is True
        assert "unregister_test" not in registry._plugins
        assert registry.get("unregister_test") is None

    def test_unregister_nonexistent_plugin(self):
        """Test unregistering a non-existent plugin."""
        registry = PluginRegistry()
        result = registry.unregister("nonexistent_plugin")

        assert result is False

    def test_plugin_listing(self):
        """Test plugin listing and filtering."""
        registry = PluginRegistry()

        plugins = [
            Plugin(PluginInfo("analyzer_plugin", "1.0.0", "Analysis", "Author", PluginType.ANALYZER, "a.py")),
            Plugin(PluginInfo("utility_plugin", "1.0.0", "Utility", "Author", PluginType.UTILITY, "u.py")),
            Plugin(PluginInfo("another_utility", "1.0.0", "Utility 2", "Author", PluginType.UTILITY, "u2.py"))
        ]

        for plugin in plugins:
            registry.register(plugin)

        # Test listing all
        all_plugins = registry.list_plugins()
        assert len(all_plugins) == 3

        # Test filtering by type
        analysis_plugins = registry.list_plugins(PluginType.ANALYZER)
        assert len(analysis_plugins) == 1
        assert analysis_plugins[0].name == "analyzer_plugin"

        utility_plugins = registry.list_plugins(PluginType.UTILITY)
        assert len(utility_plugins) == 2

    def test_get_plugin_by_name(self):
        """Test retrieving a plugin by name."""
        registry = PluginRegistry()
        plugin = Plugin(PluginInfo(
            name="get_test",
            version="1.0.0",
            description="Test",
            author="Author",
            plugin_type=PluginType.UTILITY,
            entry_point="test.py"
        ))

        registry.register(plugin)

        retrieved = registry.get("get_test")
        assert retrieved is not None
        assert retrieved.info.name == "get_test"

        # Test non-existent plugin
        non_existent = registry.get("nonexistent")
        assert non_existent is None

    def test_dependency_checking(self):
        """Test dependency validation."""
        registry = PluginRegistry()

        # Register plugin with dependencies
        plugin = Plugin(PluginInfo(
            name="dependent_plugin",
            version="1.0.0",
            description="Dependent",
            author="Author",
            plugin_type=PluginType.UTILITY,
            entry_point="dep.py",
            dependencies=["base_plugin"]
        ))
        registry.register(plugin)

        # Check dependencies (base_plugin not registered)
        missing = registry.check_dependencies("dependent_plugin")
        assert "base_plugin" in missing

        # Register base plugin
        base_plugin = Plugin(PluginInfo(
            name="base_plugin",
            version="1.0.0",
            description="Base",
            author="Author",
            plugin_type=PluginType.UTILITY,
            entry_point="base.py"
        ))
        registry.register(base_plugin)

        # Check dependencies again
        missing = registry.check_dependencies("dependent_plugin")
        assert len(missing) == 0

    def test_multiple_dependencies(self):
        """Test checking multiple dependencies."""
        registry = PluginRegistry()

        plugin = Plugin(PluginInfo(
            name="multi_dep_plugin",
            version="1.0.0",
            description="Multi-dependency",
            author="Author",
            plugin_type=PluginType.UTILITY,
            entry_point="multi.py",
            dependencies=["dep1", "dep2", "dep3"]
        ))
        registry.register(plugin)

        missing = registry.check_dependencies("multi_dep_plugin")
        assert len(missing) == 3
        assert "dep1" in missing
        assert "dep2" in missing
        assert "dep3" in missing

        # Register one dependency
        registry.register(Plugin(PluginInfo("dep1", "1.0.0", "", "", PluginType.UTILITY, "d1.py")))

        missing = registry.check_dependencies("multi_dep_plugin")
        assert len(missing) == 2
        assert "dep1" not in missing

    def test_hook_system(self):
        """Test plugin hook system."""
        registry = PluginRegistry()

        # Register a hook
        hook = registry.register_global_hook("test_hook", description="Test hook")
        assert hook.name == "test_hook"

        # Register handler
        results = []
        def test_handler(data):
            """Test functionality: handler."""
            results.append(f"processed_{data}")
            return f"result_{data}"

        hook.register(test_handler)

        # Emit hook
        emitted_results = registry.emit_global_hook("test_hook", "test_data")
        assert len(emitted_results) == 1
        assert emitted_results[0] == "result_test_data"
        assert results == ["processed_test_data"]

    def test_multiple_hook_handlers(self):
        """Test multiple handlers on the same hook."""
        registry = PluginRegistry()
        hook = registry.register_global_hook("multi_handler_hook")

        results = []

        def handler1(data):
            results.append(f"handler1_{data}")
            return f"result1_{data}"

        def handler2(data):
            results.append(f"handler2_{data}")
            return f"result2_{data}"

        def handler3(data):
            results.append(f"handler3_{data}")
            return f"result3_{data}"

        hook.register(handler1)
        hook.register(handler2)
        hook.register(handler3)

        emitted_results = registry.emit_global_hook("multi_handler_hook", "test")

        assert len(emitted_results) == 3
        assert "result1_test" in emitted_results
        assert "result2_test" in emitted_results
        assert "result3_test" in emitted_results
        assert len(results) == 3

    def test_hook_error_handling(self):
        """Test that hook errors don't prevent other handlers from running."""
        registry = PluginRegistry()
        hook = registry.register_global_hook("error_hook")

        call_order = []

        def good_handler1(data):
            call_order.append("good1")
            return "good1"

        def bad_handler(data):
            call_order.append("bad")
            raise ValueError("Intentional error")

        def good_handler2(data):
            call_order.append("good2")
            return "good2"

        hook.register(good_handler1)
        hook.register(bad_handler)
        hook.register(good_handler2)

        # Should not raise, even with bad handler
        results = registry.emit_global_hook("error_hook", "test")

        # All handlers should have been called
        assert "good1" in call_order
        assert "bad" in call_order
        assert "good2" in call_order

    def test_emit_nonexistent_hook(self):
        """Test emitting a non-existent hook."""
        registry = PluginRegistry()
        results = registry.emit_global_hook("nonexistent_hook", "data")

        assert results == []

    def test_initialize_all_plugins(self):
        """Test initializing all registered plugins."""
        registry = PluginRegistry()

        plugins = [
            Plugin(PluginInfo("init_test1", "1.0.0", "", "", PluginType.UTILITY, "t1.py")),
            Plugin(PluginInfo("init_test2", "1.0.0", "", "", PluginType.UTILITY, "t2.py")),
            Plugin(PluginInfo("init_test3", "1.0.0", "", "", PluginType.UTILITY, "t3.py")),
        ]

        for p in plugins:
            registry.register(p)

        results = registry.initialize_all()

        assert len(results) == 3
        assert all(v is True for v in results.values())

    def test_shutdown_all_plugins(self):
        """Test shutting down all registered plugins."""
        registry = PluginRegistry()

        plugins = [
            Plugin(PluginInfo("shutdown_test1", "1.0.0", "", "", PluginType.UTILITY, "t1.py")),
            Plugin(PluginInfo("shutdown_test2", "1.0.0", "", "", PluginType.UTILITY, "t2.py")),
        ]

        for p in plugins:
            registry.register(p)
            p.initialize()

        results = registry.shutdown_all()

        assert len(results) == 2
        assert all(v is True for v in results.values())

    def test_global_registry_singleton(self):
        """Test global registry is a singleton."""
        registry1 = get_registry()
        registry2 = get_registry()

        assert registry1 is registry2


# ============================================================================
# Test Plugin Base Class
# ============================================================================

@pytest.mark.unit
class TestPluginBaseClass:
    """Test cases for the Plugin base class."""

    def test_plugin_base_creation(self):
        """Test creating a plugin base class."""
        info = PluginInfo(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin",
            author="Test Author",
            plugin_type=PluginType.UTILITY,
            entry_point="test_plugin.py"
        )

        plugin = Plugin(info)

        assert plugin.info == info
        assert plugin.state == PluginState.UNLOADED
        assert plugin.config == {}
        assert plugin.hooks == {}

    def test_plugin_creation_without_info(self):
        """Test creating plugin without explicit info."""
        plugin = Plugin()

        assert plugin.info is not None
        assert plugin.state == PluginState.UNLOADED

    def test_plugin_hook_registration(self):
        """Test plugin hook registration."""
        plugin = Plugin(PluginInfo(
            "test", "1.0.0", "Test", "Author", PluginType.UTILITY, "test.py"
        ))

        # Register hook
        def test_handler():
            """Test functionality: handler."""
            return "handled"

        plugin.register_hook("test_hook", test_handler)

        assert "test_hook" in plugin.hooks
        hook = plugin.hooks["test_hook"]

        # Emit hook
        results = plugin.emit_hook("test_hook")
        assert len(results) == 1
        assert results[0] == "handled"

    def test_emit_nonexistent_hook(self):
        """Test emitting a non-existent hook returns empty list."""
        plugin = Plugin(PluginInfo("test", "1.0.0", "", "", PluginType.UTILITY, "t.py"))

        results = plugin.emit_hook("nonexistent")
        assert results == []

    def test_plugin_lifecycle(self):
        """Test plugin lifecycle methods."""
        plugin = Plugin(PluginInfo(
            "test", "1.0.0", "Test", "Author", PluginType.UTILITY, "test.py"
        ))

        # Test state changes
        assert plugin.get_state() == PluginState.UNLOADED

        plugin.state = PluginState.ACTIVE
        assert plugin.get_state() == PluginState.ACTIVE

        # Test config management
        config = {"key": "value"}
        plugin.set_config(config)
        assert plugin.get_config() == config

    def test_plugin_initialize_with_config(self):
        """Test plugin initialization with configuration."""
        plugin = Plugin(PluginInfo("config_test", "1.0.0", "", "", PluginType.UTILITY, "t.py"))

        config = {"setting1": "value1", "setting2": 42}
        result = plugin.initialize(config)

        assert result is True
        assert plugin.state == PluginState.ACTIVE
        assert plugin.config["setting1"] == "value1"
        assert plugin.config["setting2"] == 42

    def test_plugin_shutdown(self):
        """Test plugin shutdown."""
        plugin = Plugin(PluginInfo("shutdown_test", "1.0.0", "", "", PluginType.UTILITY, "t.py"))
        plugin.initialize()

        result = plugin.shutdown()

        assert result is True
        assert plugin.state == PluginState.SHUTTING_DOWN


# ============================================================================
# Test Plugin Types
# ============================================================================

@pytest.mark.unit
class TestPluginTypes:
    """Test cases for different plugin types."""

    def test_all_plugin_types_exist(self):
        """Test that all expected plugin types are defined."""
        expected_types = [
            "ANALYZER", "FORMATTER", "EXPORTER", "IMPORTER",
            "PROCESSOR", "HOOK", "UTILITY", "ADAPTER", "AGENT"
        ]

        for type_name in expected_types:
            assert hasattr(PluginType, type_name)

    def test_plugin_type_values(self):
        """Test plugin type enum values."""
        assert PluginType.ANALYZER.value == "analyzer"
        assert PluginType.UTILITY.value == "utility"
        assert PluginType.AGENT.value == "agent"


# ============================================================================
# Test Plugin States
# ============================================================================

@pytest.mark.unit
class TestPluginStates:
    """Test cases for plugin state management."""

    def test_all_plugin_states_exist(self):
        """Test that all expected plugin states are defined."""
        expected_states = [
            "UNKNOWN", "REGISTERED", "LOADED", "ACTIVE",
            "DISABLED", "ERROR", "INITIALIZING", "SHUTTING_DOWN",
            "LOADING", "UNLOADED"
        ]

        for state_name in expected_states:
            assert hasattr(PluginState, state_name)

    def test_plugin_state_transitions(self):
        """Test plugin state transitions."""
        plugin = Plugin(PluginInfo("state_test", "1.0.0", "", "", PluginType.UTILITY, "t.py"))

        # Initial state
        assert plugin.state == PluginState.UNLOADED

        # After initialization
        plugin.initialize()
        assert plugin.state == PluginState.ACTIVE

        # After shutdown
        plugin.shutdown()
        assert plugin.state == PluginState.SHUTTING_DOWN


# ============================================================================
# Test Plugin Isolation
# ============================================================================

@pytest.mark.unit
class TestPluginIsolation:
    """Test cases for plugin isolation."""

    def test_plugins_have_separate_state(self):
        """Test that plugins maintain separate state."""
        plugin1 = Plugin(PluginInfo("isolation1", "1.0.0", "", "", PluginType.UTILITY, "t.py"))
        plugin2 = Plugin(PluginInfo("isolation2", "1.0.0", "", "", PluginType.UTILITY, "t.py"))

        plugin1.set_config({"key": "value1"})
        plugin2.set_config({"key": "value2"})

        assert plugin1.get_config()["key"] == "value1"
        assert plugin2.get_config()["key"] == "value2"

    def test_plugins_have_separate_hooks(self):
        """Test that plugins have separate hook registrations."""
        plugin1 = Plugin(PluginInfo("hook_iso1", "1.0.0", "", "", PluginType.UTILITY, "t.py"))
        plugin2 = Plugin(PluginInfo("hook_iso2", "1.0.0", "", "", PluginType.UTILITY, "t.py"))

        plugin1.register_hook("shared_hook", lambda: "plugin1")
        plugin2.register_hook("shared_hook", lambda: "plugin2")

        results1 = plugin1.emit_hook("shared_hook")
        results2 = plugin2.emit_hook("shared_hook")

        assert results1 == ["plugin1"]
        assert results2 == ["plugin2"]

    def test_registry_isolation(self):
        """Test that separate registries are isolated."""
        registry1 = PluginRegistry()
        registry2 = PluginRegistry()

        plugin = Plugin(PluginInfo("shared_name", "1.0.0", "", "", PluginType.UTILITY, "t.py"))

        registry1.register(plugin)

        assert registry1.get("shared_name") is not None
        assert registry2.get("shared_name") is None


# ============================================================================
# Test Hook Class
# ============================================================================

@pytest.mark.unit
class TestHookClass:
    """Test cases for the Hook class."""

    def test_hook_creation(self):
        """Test creating a hook."""
        hook = Hook("test_hook", description="Test description")

        assert hook.name == "test_hook"
        assert hook.description == "Test description"
        assert hook.handlers == []

    def test_hook_register_handler(self):
        """Test registering handlers with a hook."""
        hook = Hook("test")

        def handler1(): pass
        def handler2(): pass

        hook.register(handler1)
        hook.register(handler2)

        assert len(hook.handlers) == 2
        assert handler1 in hook.handlers
        assert handler2 in hook.handlers

    def test_hook_emit_with_args(self):
        """Test emitting hook with arguments."""
        hook = Hook("args_test")

        def handler(a, b, c=None):
            return f"{a}-{b}-{c}"

        hook.register(handler)

        results = hook.emit("x", "y", c="z")

        assert results == ["x-y-z"]
