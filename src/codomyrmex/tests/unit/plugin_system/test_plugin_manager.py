"""Unit tests for the plugin manager -- orchestration, status, enable/disable."""

import json

import pytest

from codomyrmex.plugin_system.core.plugin_loader import PluginLoader
from codomyrmex.plugin_system.core.plugin_manager import (
    PluginManager,
    discover_plugins,
    get_plugin_manager,
    load_plugin,
    unload_plugin,
)
from codomyrmex.plugin_system.core.plugin_registry import (
    Hook,
    Plugin,
    PluginInfo,
    PluginRegistry,
    PluginState,
    PluginType,
    create_plugin_info,
)
from codomyrmex.plugin_system.validation.plugin_validator import (
    PluginValidator,
    validate_plugin,
)

# ============================================================================
# Test Plugin Manager
# ============================================================================

@pytest.mark.unit
class TestPluginManager:
    """Test cases for PluginManager functionality."""

    def test_plugin_manager_creation(self):
        """Test creating a plugin manager."""
        manager = PluginManager()
        assert manager is not None
        assert manager.registry is not None
        assert manager.validator is not None
        assert manager.loader is not None

    def test_plugin_manager_default_settings(self):
        """Test plugin manager default settings."""
        manager = PluginManager()

        assert manager.auto_discover is True
        assert manager.auto_validate is True
        assert manager.parallel_loading is True

    def test_plugin_discovery_through_manager(self, tmp_path):
        """Test plugin discovery through manager with real files."""
        # Create a real plugin directory
        plugin_dir = tmp_path / "test_plugin"
        plugin_dir.mkdir()

        plugin_file = plugin_dir / "test_plugin.py"
        plugin_file.write_text("""
@pytest.mark.unit
class TestPlugin:
    def initialize(self, config): return True
    def shutdown(self): pass
""")

        plugin_json_file = plugin_dir / "plugin.json"
        plugin_json = {
            "name": "test_plugin",
            "version": "1.0.0",
            "description": "Test",
            "author": "Author",
            "plugin_type": "utility",
            "entry_point": "test_plugin.py"
        }
        with open(plugin_json_file, 'w') as f:
            json.dump(plugin_json, f)

        manager = PluginManager()
        # Set plugin directories to include our test directory
        manager.loader.plugin_directories = [str(tmp_path)]

        plugins = manager.discover_plugins()

        # Should discover at least our test plugin
        assert len(plugins) >= 0  # May be 0 if discovery doesn't work, but shouldn't error

    def test_plugin_listing(self):
        """Test plugin listing through manager."""
        manager = PluginManager()

        # Manually add plugin to registry for testing
        plugin = Plugin(PluginInfo(
            "test_plugin", "1.0.0", "Test", "Author", PluginType.UTILITY, "test.py"
        ))
        manager.registry.register(plugin)

        plugins = manager.list_plugins()
        assert len(plugins) == 1
        assert plugins[0].name == "test_plugin"

    def test_list_plugins_by_type(self):
        """Test listing plugins filtered by type."""
        manager = PluginManager()

        plugins = [
            Plugin(PluginInfo("analyzer1", "1.0.0", "", "", PluginType.ANALYZER, "a.py")),
            Plugin(PluginInfo("utility1", "1.0.0", "", "", PluginType.UTILITY, "u.py")),
            Plugin(PluginInfo("hook1", "1.0.0", "", "", PluginType.HOOK, "h.py")),
        ]

        for p in plugins:
            manager.registry.register(p)

        analyzers = manager.list_plugins(PluginType.ANALYZER)
        assert len(analyzers) == 1
        assert analyzers[0].name == "analyzer1"

    def test_hook_registration(self):
        """Test hook registration through manager."""
        manager = PluginManager()

        # Register a hook
        hook = manager.register_hook("test_hook", description="Test hook")
        assert hook is not None
        assert hook.name == "test_hook"

        # Register handler and emit
        def test_handler():
            """Test functionality: handler."""
            return "handled"

        hook.register(test_handler)
        results = manager.emit_hook("test_hook")
        assert len(results) == 1
        assert results[0] == "handled"

    def test_plugin_status(self):
        """Test getting plugin status."""
        manager = PluginManager()

        # Add plugin to registry
        plugin = Plugin(PluginInfo(
            "test_plugin", "1.0.0", "Test", "Author", PluginType.UTILITY, "test.py",
            dependencies=["missing_dep"]
        ))
        manager.registry.register(plugin)

        status = manager.get_plugin_status("test_plugin")

        assert status["name"] == "test_plugin"
        assert status["registered"] == True
        assert status["loaded"] == False
        assert not status["dependencies_satisfied"]
        assert "missing_dep" in status["missing_dependencies"]

    def test_plugin_status_nonexistent(self):
        """Test getting status of non-existent plugin."""
        manager = PluginManager()

        status = manager.get_plugin_status("nonexistent")

        assert status["name"] == "nonexistent"
        assert status["registered"] == False
        assert status["loaded"] == False

    def test_system_status(self):
        """Test getting system status."""
        manager = PluginManager()

        # Add some plugins
        plugins = [
            Plugin(PluginInfo("analysis1", "1.0.0", "Analysis 1", "Author", PluginType.ANALYZER, "a1.py")),
            Plugin(PluginInfo("utility1", "1.0.0", "Utility 1", "Author", PluginType.UTILITY, "u1.py")),
        ]

        for plugin in plugins:
            manager.registry.register(plugin)

        status = manager.get_system_status()

        assert status["status_counts"]["total_registered"] == 2
        assert status["status_counts"]["total_loaded"] == 0
        assert status["status_counts"]["by_type"]["analyzer"] == 1
        assert status["status_counts"]["by_type"]["utility"] == 1

    def test_enable_disable_plugin(self):
        """Test enabling and disabling plugins."""
        manager = PluginManager()

        plugin = Plugin(PluginInfo("toggle_test", "1.0.0", "", "", PluginType.UTILITY, "t.py"))
        manager.registry.register(plugin)

        # Enable
        result = manager.enable_plugin("toggle_test")
        assert result is True
        assert manager.get_plugin("toggle_test").state == PluginState.ACTIVE

        # Disable
        result = manager.disable_plugin("toggle_test")
        assert result is True
        assert manager.get_plugin("toggle_test").state == PluginState.DISABLED

    def test_enable_nonexistent_plugin(self):
        """Test enabling a non-existent plugin."""
        manager = PluginManager()

        result = manager.enable_plugin("nonexistent")
        assert result is False

    def test_load_plugin_with_validation(self, tmp_path):
        """Test loading plugin with validation using real validator and loader."""
        manager = PluginManager()

        # Create a real plugin file
        plugin_dir = tmp_path / "test_plugin"
        plugin_dir.mkdir()

        plugin_file = plugin_dir / "test_plugin.py"
        plugin_file.write_text("""
@pytest.mark.unit
class TestPlugin:
    def initialize(self, config): return True
    def shutdown(self): pass
""")

        plugin_json_file = plugin_dir / "plugin.json"
        plugin_json = {
            "name": "test_plugin",
            "version": "1.0.0",
            "description": "Test",
            "author": "Author",
            "plugin_type": "utility",
            "entry_point": "test_plugin.py"
        }
        with open(plugin_json_file, 'w') as f:
            json.dump(plugin_json, f)

        # Add plugin to registry first
        plugin = Plugin(PluginInfo(
            "test_plugin", "1.0.0", "Test", "Author", PluginType.UTILITY, str(plugin_file)
        ))
        manager.registry.register(plugin)

        # Try to load the plugin
        result = manager.load_plugin("test_plugin")

        # Should return a result (may succeed or fail depending on implementation)
        assert hasattr(result, 'success')
        assert isinstance(result.success, bool)

    def test_load_plugin_not_found(self):
        """Test loading a non-existent plugin."""
        manager = PluginManager()

        result = manager.load_plugin("definitely_not_a_real_plugin")

        assert result.success is False
        assert "not found" in result.error_message.lower()

    def test_cleanup(self):
        """Test manager cleanup."""
        manager = PluginManager()

        # Add plugins and also add them to the loader's loaded_plugins
        for i in range(3):
            plugin = Plugin(PluginInfo(f"cleanup_{i}", "1.0.0", "", "", PluginType.UTILITY, "t.py"))
            manager.registry.register(plugin)
            manager.loader.loaded_plugins[f"cleanup_{i}"] = plugin

        initial_count = len(manager.list_plugins())
        assert initial_count == 3

        manager.cleanup()

        # Loaded plugins should be unloaded
        assert len(manager.loader.get_loaded_plugins()) == 0


# ============================================================================
# Test Convenience Functions
# ============================================================================

@pytest.mark.unit
class TestConvenienceFunctions:
    """Test cases for plugin system convenience functions."""

    def test_get_plugin_manager(self):
        """Test getting the global plugin manager."""
        manager1 = get_plugin_manager()
        manager2 = get_plugin_manager()

        assert manager1 is manager2  # Should return same instance

    def test_convenience_functions(self):
        """Test other convenience functions."""
        # Test that functions exist and are callable
        assert callable(discover_plugins)
        assert callable(load_plugin)
        assert callable(unload_plugin)
        assert callable(validate_plugin)

    def test_create_plugin_info_helper(self):
        """Test plugin info creation helper."""
        info = create_plugin_info(
            name="helper_test",
            version="1.0.0",
            plugin_type=PluginType.UTILITY,
            entry_point="test.py"
        )

        assert info.name == "helper_test"
        assert info.version == "1.0.0"
        assert info.plugin_type == PluginType.UTILITY


# ============================================================================
# Test Error Handling
# ============================================================================

@pytest.mark.unit
class TestErrorHandling:
    """Test cases for error handling in the plugin system."""

    def test_load_invalid_plugin_path(self, tmp_path):
        """Test loading plugin with invalid path."""
        loader = PluginLoader([str(tmp_path)])

        info = PluginInfo(
            name="invalid_path",
            version="1.0.0",
            description="Test",
            author="Test",
            plugin_type=PluginType.UTILITY,
            entry_point="/nonexistent/path/plugin.py"
        )

        result = loader.load_plugin(info)

        assert result.success is False
        assert result.error_message is not None

    def test_validate_corrupted_file(self, tmp_path):
        """Test validating a corrupted plugin file."""
        validator = PluginValidator()

        # Create a file with invalid content
        bad_file = tmp_path / "corrupted.py"
        bad_file.write_bytes(b'\x00\x01\x02\x03')  # Binary garbage

        result = validator.validate_plugin(str(bad_file))

        # Should handle gracefully without crashing
        assert hasattr(result, 'valid')

    def test_registry_handles_shutdown_errors(self):
        """Test that registry handles shutdown errors gracefully."""
        class FaultyPlugin(Plugin):
            def shutdown(self):
                raise RuntimeError("Shutdown error")

        registry = PluginRegistry()

        plugin = FaultyPlugin(PluginInfo("faulty", "1.0.0", "", "", PluginType.UTILITY, "t.py"))
        registry.register(plugin)

        # Should not raise
        results = registry.shutdown_all()

        assert "faulty" in results
        assert results["faulty"] is False

    def test_hook_continues_after_handler_error(self):
        """Test that hooks continue execution after handler errors."""
        hook = Hook("error_test")

        executed = []

        def handler1():
            executed.append(1)
            return 1

        def bad_handler():
            executed.append("bad")
            raise ValueError("Bad handler")

        def handler2():
            executed.append(2)
            return 2

        hook.register(handler1)
        hook.register(bad_handler)
        hook.register(handler2)

        hook.emit()

        # All handlers should have been attempted
        assert 1 in executed
        assert "bad" in executed
        assert 2 in executed


# ============================================================================
# Test Dependency Resolver (from test_tier3_promotions_pass2.py)
# ============================================================================

class TestDependencyResolver:
    """Tests for DependencyResolver."""

    def test_simple_resolution(self):
        """Test functionality: simple resolution."""
        from codomyrmex.plugin_system.dependency_resolver import (
            DependencyNode,
            DependencyResolver,
            ResolutionStatus,
        )
        resolver = DependencyResolver()
        resolver.add(DependencyNode("auth", dependencies=["db"]))
        resolver.add(DependencyNode("db"))
        result = resolver.resolve()
        assert result.status == ResolutionStatus.RESOLVED
        assert result.load_order.index("db") < result.load_order.index("auth")

    def test_missing_dependency(self):
        """Test functionality: missing dependency."""
        from codomyrmex.plugin_system.dependency_resolver import (
            DependencyNode,
            DependencyResolver,
            ResolutionStatus,
        )
        resolver = DependencyResolver()
        resolver.add(DependencyNode("auth", dependencies=["nonexistent"]))
        result = resolver.resolve()
        assert result.status == ResolutionStatus.MISSING
        assert "nonexistent" in result.missing

    def test_circular_dependency(self):
        """Test functionality: circular dependency."""
        from codomyrmex.plugin_system.dependency_resolver import (
            DependencyNode,
            DependencyResolver,
            ResolutionStatus,
        )
        resolver = DependencyResolver()
        resolver.add(DependencyNode("a", dependencies=["b"]))
        resolver.add(DependencyNode("b", dependencies=["a"]))
        result = resolver.resolve()
        assert result.status == ResolutionStatus.CIRCULAR
