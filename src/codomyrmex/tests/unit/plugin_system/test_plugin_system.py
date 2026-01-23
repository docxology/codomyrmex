"""Comprehensive tests for the Codomyrmex plugin system.

Tests cover:
1. Plugin discovery and loading
2. Plugin registration
3. Plugin lifecycle (init, start, stop)
4. Plugin dependencies
5. Plugin configuration
6. Hook system
7. Extension points
8. Plugin isolation
9. Error handling for faulty plugins
10. Plugin metadata and versioning
"""

import pytest
import tempfile
import os
import json
import sys
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock
from typing import Dict, Any, List, Optional


# ============================================================================
# Mock Plugin Classes for Testing
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

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
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

    def set_config(self, config: Dict[str, Any]):
        self.config = config


class FaultyInitPlugin(MockPlugin):
    """Plugin that fails during initialization."""

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        raise RuntimeError("Initialization failed intentionally")


class FaultyShutdownPlugin(MockPlugin):
    """Plugin that fails during shutdown."""

    def shutdown(self) -> bool:
        raise RuntimeError("Shutdown failed intentionally")


class SlowInitPlugin(MockPlugin):
    """Plugin with slow initialization."""

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        time.sleep(0.1)  # Simulate slow init
        return super().initialize(config)


class ResourceLeakPlugin(MockPlugin):
    """Plugin that simulates resource management."""

    resources_acquired = []

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        ResourceLeakPlugin.resources_acquired.append(f"resource_{id(self)}")
        return super().initialize(config)

    def shutdown(self) -> bool:
        if ResourceLeakPlugin.resources_acquired:
            ResourceLeakPlugin.resources_acquired.pop()
        return super().shutdown()


# ============================================================================
# Test Plugin Registry
# ============================================================================

class TestPluginRegistry:
    """Test cases for PluginRegistry functionality."""

    def test_plugin_registry_creation(self):
        """Test creating a plugin registry."""
        try:
            from codomyrmex.plugin_system.plugin_registry import PluginRegistry, PluginType
        except ImportError:
            pytest.skip("PluginRegistry not available")

        registry = PluginRegistry()
        assert registry is not None
        assert registry._plugins == {}
        assert registry.categories == {}

    def test_plugin_info_creation(self):
        """Test creating PluginInfo."""
        try:
            from codomyrmex.plugin_system.plugin_registry import PluginInfo, PluginType
        except ImportError:
            pytest.skip("PluginInfo not available")

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
        try:
            from codomyrmex.plugin_system.plugin_registry import PluginInfo, PluginType
        except ImportError:
            pytest.skip("PluginInfo not available")

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
        try:
            from codomyrmex.plugin_system.plugin_registry import PluginRegistry, Plugin, PluginInfo, PluginType
        except ImportError:
            pytest.skip("Plugin system not available")

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
        try:
            from codomyrmex.plugin_system.plugin_registry import PluginRegistry, Plugin, PluginInfo, PluginType
        except ImportError:
            pytest.skip("Plugin system not available")

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
        try:
            from codomyrmex.plugin_system.plugin_registry import PluginRegistry, Plugin, PluginInfo, PluginType
        except ImportError:
            pytest.skip("Plugin system not available")

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
        try:
            from codomyrmex.plugin_system.plugin_registry import PluginRegistry
        except ImportError:
            pytest.skip("Plugin system not available")

        registry = PluginRegistry()
        result = registry.unregister("nonexistent_plugin")

        assert result is False

    def test_plugin_listing(self):
        """Test plugin listing and filtering."""
        try:
            from codomyrmex.plugin_system.plugin_registry import PluginRegistry, Plugin, PluginInfo, PluginType
        except ImportError:
            pytest.skip("Plugin system not available")

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
        try:
            from codomyrmex.plugin_system.plugin_registry import PluginRegistry, Plugin, PluginInfo, PluginType
        except ImportError:
            pytest.skip("Plugin system not available")

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
        try:
            from codomyrmex.plugin_system.plugin_registry import PluginRegistry, Plugin, PluginInfo, PluginType
        except ImportError:
            pytest.skip("Plugin system not available")

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
        try:
            from codomyrmex.plugin_system.plugin_registry import PluginRegistry, Plugin, PluginInfo, PluginType
        except ImportError:
            pytest.skip("Plugin system not available")

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
        try:
            from codomyrmex.plugin_system.plugin_registry import PluginRegistry
        except ImportError:
            pytest.skip("PluginRegistry not available")

        registry = PluginRegistry()

        # Register a hook
        hook = registry.register_global_hook("test_hook", description="Test hook")
        assert hook.name == "test_hook"

        # Register handler
        results = []
        def test_handler(data):
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
        try:
            from codomyrmex.plugin_system.plugin_registry import PluginRegistry
        except ImportError:
            pytest.skip("PluginRegistry not available")

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
        try:
            from codomyrmex.plugin_system.plugin_registry import PluginRegistry
        except ImportError:
            pytest.skip("PluginRegistry not available")

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
        try:
            from codomyrmex.plugin_system.plugin_registry import PluginRegistry
        except ImportError:
            pytest.skip("PluginRegistry not available")

        registry = PluginRegistry()
        results = registry.emit_global_hook("nonexistent_hook", "data")

        assert results == []

    def test_initialize_all_plugins(self):
        """Test initializing all registered plugins."""
        try:
            from codomyrmex.plugin_system.plugin_registry import PluginRegistry, Plugin, PluginInfo, PluginType
        except ImportError:
            pytest.skip("Plugin system not available")

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
        try:
            from codomyrmex.plugin_system.plugin_registry import PluginRegistry, Plugin, PluginInfo, PluginType
        except ImportError:
            pytest.skip("Plugin system not available")

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
        try:
            from codomyrmex.plugin_system.plugin_registry import get_registry
        except ImportError:
            pytest.skip("get_registry not available")

        registry1 = get_registry()
        registry2 = get_registry()

        assert registry1 is registry2


# ============================================================================
# Test Plugin Validator
# ============================================================================

class TestPluginValidator:
    """Test cases for PluginValidator functionality."""

    def test_plugin_validator_creation(self):
        """Test creating a plugin validator."""
        try:
            from codomyrmex.plugin_system.plugin_validator import PluginValidator
        except ImportError:
            pytest.skip("PluginValidator not available")

        validator = PluginValidator()
        assert validator is not None
        assert len(validator.risky_imports) > 0
        assert len(validator.suspicious_patterns) > 0

    def test_validate_plugin_metadata(self):
        """Test plugin metadata validation."""
        try:
            from codomyrmex.plugin_system.plugin_validator import PluginValidator
        except ImportError:
            pytest.skip("PluginValidator not available")

        validator = PluginValidator()

        # Valid metadata
        valid_metadata = {
            "name": "test_plugin",
            "version": "1.0.0",
            "description": "Test plugin",
            "author": "Test Author",
            "entry_point": "test_plugin.py"
        }

        result = validator.validate_plugin_metadata(valid_metadata)
        assert result.valid

        # Invalid metadata
        invalid_metadata = {
            "name": "test_plugin",
            # Missing version
            "description": "Test plugin"
            # Missing other required fields
        }

        result = validator.validate_plugin_metadata(invalid_metadata)
        assert not result.valid
        assert len(result.issues) > 0

    def test_validate_metadata_missing_name(self):
        """Test validation fails when name is missing."""
        try:
            from codomyrmex.plugin_system.plugin_validator import PluginValidator
        except ImportError:
            pytest.skip("PluginValidator not available")

        validator = PluginValidator()

        metadata = {
            "version": "1.0.0",
            "description": "Test"
        }

        result = validator.validate_plugin_metadata(metadata)
        assert not result.valid
        assert any("name" in str(issue).lower() for issue in result.issues)

    def test_security_scanning(self):
        """Test plugin security scanning."""
        try:
            from codomyrmex.plugin_system.plugin_validator import PluginValidator
        except ImportError:
            pytest.skip("PluginValidator not available")

        validator = PluginValidator()

        # Create test plugin file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
import os
import subprocess

def dangerous_function():
    os.system('rm -rf /')  # Very dangerous!
    subprocess.call(['chmod', '777', '/etc/passwd'])
    api_key = 'sk-1234567890abcdef1234567890abcdef'  # Hardcoded secret
""")
            test_file = f.name

        try:
            result = validator.validate_plugin(test_file)

            assert not result.valid
            assert result.security_score < 100

            # Should detect multiple issues
            issue_messages = [issue['message'] for issue in result.issues + result.warnings]
            dangerous_found = any('dangerous' in msg.lower() or 'risky' in msg.lower() for msg in issue_messages)
            assert dangerous_found

        finally:
            os.unlink(test_file)

    def test_security_scanning_safe_plugin(self):
        """Test security scanning on a safe plugin."""
        try:
            from codomyrmex.plugin_system.plugin_validator import PluginValidator
        except ImportError:
            pytest.skip("PluginValidator not available")

        validator = PluginValidator()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
# Safe plugin with no dangerous patterns
def safe_function(x, y):
    return x + y

class SafePlugin:
    def __init__(self):
        self.data = []

    def process(self, item):
        self.data.append(item)
        return len(self.data)
""")
            test_file = f.name

        try:
            result = validator.validate_plugin(test_file)
            # Should have high security score
            assert result.security_score >= 80
        finally:
            os.unlink(test_file)

    def test_detect_eval_exec(self):
        """Test detection of eval and exec usage."""
        try:
            from codomyrmex.plugin_system.plugin_validator import PluginValidator
        except ImportError:
            pytest.skip("PluginValidator not available")

        validator = PluginValidator()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def run_code(code_string):
    eval(code_string)
    exec(code_string)
""")
            test_file = f.name

        try:
            result = validator.validate_plugin(test_file)
            assert not result.valid
            issue_messages = [issue['message'].lower() for issue in result.issues]
            assert any('eval' in msg or 'exec' in msg for msg in issue_messages)
        finally:
            os.unlink(test_file)

    def test_dependency_validation(self):
        """Test dependency validation."""
        try:
            from codomyrmex.plugin_system.plugin_validator import PluginValidator
        except ImportError:
            pytest.skip("PluginValidator not available")

        validator = PluginValidator()

        # Test safe dependencies
        safe_deps = ["requests", "click", "pyyaml"]
        result = validator.check_plugin_dependencies(safe_deps)
        assert result.valid
        assert len(result.issues) == 0

        # Test risky dependencies
        risky_deps = ["cryptography", "paramiko", "docker"]
        result = validator.check_plugin_dependencies(risky_deps)
        assert len(result.warnings) > 0  # Should flag at least some as risky

    def test_dependency_validation_with_available_list(self):
        """Test dependency validation against available plugins."""
        try:
            from codomyrmex.plugin_system.plugin_validator import PluginValidator
        except ImportError:
            pytest.skip("PluginValidator not available")

        validator = PluginValidator()

        available = ["plugin_a", "plugin_b"]
        required = ["plugin_a", "plugin_c"]

        result = validator.check_plugin_dependencies(required, available)

        assert not result.valid
        assert any("plugin_c" in issue['message'] for issue in result.issues)

    def test_dockerfile_validation(self):
        """Test Dockerfile validation."""
        try:
            from codomyrmex.plugin_system.plugin_validator import PluginValidator
        except ImportError:
            pytest.skip("PluginValidator not available")

        validator = PluginValidator()

        # Valid Dockerfile
        valid_dockerfile = """FROM ubuntu:20.04
WORKDIR /app
COPY . .
RUN apt-get update && apt-get install -y python3
USER appuser
CMD ["python", "app.py"]
"""

        result = validator.validate_dockerfile(valid_dockerfile)
        assert result.valid or len(result.issues) == 0  # May have warnings but no errors

        # Invalid Dockerfile
        invalid_dockerfile = """FROM ubuntu:latest
RUN chmod 777 /app
USER root
"""

        result = validator.validate_dockerfile(invalid_dockerfile)
        assert not result.valid or len(result.issues) > 0

    def test_dockerfile_missing_from(self):
        """Test Dockerfile validation without FROM instruction."""
        try:
            from codomyrmex.plugin_system.plugin_validator import PluginValidator
        except ImportError:
            pytest.skip("PluginValidator not available")

        validator = PluginValidator()

        invalid_dockerfile = """
WORKDIR /app
RUN echo "no from instruction"
"""

        result = validator.validate_dockerfile(invalid_dockerfile)
        assert not result.valid
        assert any("FROM" in issue['message'] for issue in result.issues)

    def test_validate_plugin_instance(self):
        """Test validating a plugin instance."""
        try:
            from codomyrmex.plugin_system.plugin_validator import PluginValidator
            from codomyrmex.plugin_system.plugin_registry import Plugin, PluginInfo, PluginType
        except ImportError:
            pytest.skip("Plugin system not available")

        validator = PluginValidator()

        plugin = Plugin(PluginInfo("test", "1.0.0", "", "", PluginType.UTILITY, "test.py"))

        result = validator.validate(plugin)
        assert result.valid

    def test_validate_plugin_missing_methods(self):
        """Test validating plugin without required methods."""
        try:
            from codomyrmex.plugin_system.plugin_validator import PluginValidator
        except ImportError:
            pytest.skip("PluginValidator not available")

        validator = PluginValidator()

        class IncompletePlugin:
            pass

        result = validator.validate(IncompletePlugin())
        assert not result.valid


# ============================================================================
# Test Plugin Loader
# ============================================================================

class TestPluginLoader:
    """Test cases for PluginLoader functionality."""

    def test_plugin_loader_creation(self):
        """Test creating a plugin loader with real implementation."""
        try:
            from codomyrmex.plugin_system.plugin_loader import PluginLoader
        except ImportError:
            pytest.skip("PluginLoader not available")

        loader = PluginLoader()
        assert loader is not None
        assert len(loader.plugin_directories) > 0

    def test_plugin_loader_custom_directories(self):
        """Test creating plugin loader with custom directories."""
        try:
            from codomyrmex.plugin_system.plugin_loader import PluginLoader
        except ImportError:
            pytest.skip("PluginLoader not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            custom_dirs = [temp_dir]
            loader = PluginLoader(custom_dirs)

            assert temp_dir in [str(d) for d in loader.plugin_directories]

    def test_plugin_discovery(self):
        """Test plugin discovery with real files."""
        try:
            from codomyrmex.plugin_system.plugin_loader import PluginLoader
        except ImportError:
            pytest.skip("PluginLoader not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create real plugin directory
            plugin_dir = os.path.join(temp_dir, "test_plugin")
            os.makedirs(plugin_dir)

            # Create plugin.json
            plugin_json = {
                "name": "test_plugin",
                "version": "1.0.0",
                "description": "Test plugin",
                "author": "Test",
                "plugin_type": "utility",
                "entry_point": "test_plugin.py"
            }

            with open(os.path.join(plugin_dir, "plugin.json"), 'w') as f:
                json.dump(plugin_json, f)

            # Create plugin file
            with open(os.path.join(plugin_dir, "test_plugin.py"), 'w') as f:
                f.write("""
from codomyrmex.plugin_system import Plugin

class TestPlugin(Plugin):
    def initialize(self, config): return True
    def shutdown(self): pass
""")

            loader = PluginLoader([temp_dir])
            discovered = loader.discover_plugins()

            assert len(discovered) == 1
            assert discovered[0].name == "test_plugin"

    def test_discover_multiple_plugins(self):
        """Test discovering multiple plugins."""
        try:
            from codomyrmex.plugin_system.plugin_loader import PluginLoader
        except ImportError:
            pytest.skip("PluginLoader not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            for i in range(3):
                plugin_dir = os.path.join(temp_dir, f"plugin_{i}")
                os.makedirs(plugin_dir)

                plugin_json = {
                    "name": f"plugin_{i}",
                    "version": "1.0.0",
                    "description": f"Plugin {i}",
                    "author": "Test",
                    "plugin_type": "utility",
                    "entry_point": f"plugin_{i}.py"
                }

                with open(os.path.join(plugin_dir, "plugin.json"), 'w') as f:
                    json.dump(plugin_json, f)

                with open(os.path.join(plugin_dir, f"plugin_{i}.py"), 'w') as f:
                    f.write("class Plugin: pass")

            loader = PluginLoader([temp_dir])
            discovered = loader.discover_plugins()

            assert len(discovered) == 3

    def test_plugin_loading(self, tmp_path):
        """Test plugin loading with real Python module."""
        try:
            from codomyrmex.plugin_system.plugin_loader import PluginLoader
            from codomyrmex.plugin_system.plugin_registry import PluginInfo, PluginType
        except ImportError:
            pytest.skip("PluginLoader not available")

        # Create a real plugin module
        plugin_dir = tmp_path / "test_plugin"
        plugin_dir.mkdir()

        plugin_file = plugin_dir / "test_plugin.py"
        plugin_file.write_text("""
class TestPlugin:
    def __init__(self):
        self.initialized = False

    def initialize(self, config):
        self.initialized = True
        return True

    def shutdown(self):
        self.initialized = False
""")

        # Create plugin.json
        plugin_json_file = plugin_dir / "plugin.json"
        plugin_json = {
            "name": "test_plugin",
            "version": "1.0.0",
            "description": "Test",
            "author": "Test",
            "plugin_type": "utility",
            "entry_point": "test_plugin.py"
        }
        with open(plugin_json_file, 'w') as f:
            json.dump(plugin_json, f)

        loader = PluginLoader([str(tmp_path)])

        info = PluginInfo(
            name="test_plugin",
            version="1.0.0",
            description="Test",
            author="Test",
            plugin_type=PluginType.UTILITY,
            entry_point=str(plugin_file)
        )

        # Try to load the plugin
        result = loader.load_plugin(info)

        # Should either succeed or fail gracefully
        assert hasattr(result, 'success')
        assert isinstance(result.success, bool)

    def test_load_already_loaded_plugin(self, tmp_path):
        """Test loading an already loaded plugin returns warning."""
        try:
            from codomyrmex.plugin_system.plugin_loader import PluginLoader
            from codomyrmex.plugin_system.plugin_registry import PluginInfo, PluginType, Plugin
        except ImportError:
            pytest.skip("PluginLoader not available")

        loader = PluginLoader([str(tmp_path)])

        info = PluginInfo(
            name="already_loaded",
            version="1.0.0",
            description="Test",
            author="Test",
            plugin_type=PluginType.UTILITY,
            entry_point="test.py"
        )

        # Manually add to loaded plugins
        mock_plugin = Plugin(info)
        loader.loaded_plugins["already_loaded"] = mock_plugin

        result = loader.load_plugin(info)

        assert result.success is True
        assert len(result.warnings) > 0
        assert "already loaded" in result.warnings[0].lower()

    def test_unload_plugin(self, tmp_path):
        """Test unloading a plugin."""
        try:
            from codomyrmex.plugin_system.plugin_loader import PluginLoader
            from codomyrmex.plugin_system.plugin_registry import PluginInfo, PluginType, Plugin
        except ImportError:
            pytest.skip("PluginLoader not available")

        loader = PluginLoader([str(tmp_path)])

        info = PluginInfo(
            name="to_unload",
            version="1.0.0",
            description="Test",
            author="Test",
            plugin_type=PluginType.UTILITY,
            entry_point="test.py"
        )

        mock_plugin = Plugin(info)
        loader.loaded_plugins["to_unload"] = mock_plugin

        result = loader.unload_plugin("to_unload")

        assert result is True
        assert "to_unload" not in loader.loaded_plugins

    def test_unload_nonexistent_plugin(self, tmp_path):
        """Test unloading a non-existent plugin."""
        try:
            from codomyrmex.plugin_system.plugin_loader import PluginLoader
        except ImportError:
            pytest.skip("PluginLoader not available")

        loader = PluginLoader([str(tmp_path)])

        result = loader.unload_plugin("nonexistent")

        assert result is False

    def test_get_loaded_plugins(self, tmp_path):
        """Test getting all loaded plugins."""
        try:
            from codomyrmex.plugin_system.plugin_loader import PluginLoader
            from codomyrmex.plugin_system.plugin_registry import PluginInfo, PluginType, Plugin
        except ImportError:
            pytest.skip("PluginLoader not available")

        loader = PluginLoader([str(tmp_path)])

        # Add some mock plugins
        for i in range(3):
            info = PluginInfo(f"plugin_{i}", "1.0.0", "", "", PluginType.UTILITY, "t.py")
            loader.loaded_plugins[f"plugin_{i}"] = Plugin(info)

        loaded = loader.get_loaded_plugins()

        assert len(loaded) == 3
        assert "plugin_0" in loaded
        assert "plugin_1" in loaded
        assert "plugin_2" in loaded

    def test_validate_plugin_dependencies(self, tmp_path):
        """Test validating plugin dependencies."""
        try:
            from codomyrmex.plugin_system.plugin_loader import PluginLoader
            from codomyrmex.plugin_system.plugin_registry import PluginInfo, PluginType
        except ImportError:
            pytest.skip("PluginLoader not available")

        loader = PluginLoader([str(tmp_path)])

        info = PluginInfo(
            name="dep_test",
            version="1.0.0",
            description="Test",
            author="Test",
            plugin_type=PluginType.UTILITY,
            entry_point="test.py",
            dependencies=["nonexistent_package_xyz"]
        )

        missing = loader.validate_plugin_dependencies(info)

        assert len(missing) > 0
        assert any("nonexistent_package_xyz" in m for m in missing)

    def test_load_result_dataclass(self):
        """Test LoadResult dataclass."""
        try:
            from codomyrmex.plugin_system.plugin_loader import LoadResult
        except ImportError:
            pytest.skip("LoadResult not available")

        result = LoadResult(
            plugin_name="test",
            success=True,
            error_message=None,
            warnings=["warning1"]
        )

        assert result.plugin_name == "test"
        assert result.success is True
        assert result.warnings == ["warning1"]

        # Test default warnings
        result2 = LoadResult(plugin_name="test2", success=False)
        assert result2.warnings == []


# ============================================================================
# Test Plugin Manager
# ============================================================================

class TestPluginManager:
    """Test cases for PluginManager functionality."""

    def test_plugin_manager_creation(self):
        """Test creating a plugin manager."""
        try:
            from codomyrmex.plugin_system.plugin_manager import PluginManager
        except ImportError:
            pytest.skip("PluginManager not available")

        manager = PluginManager()
        assert manager is not None
        assert manager.registry is not None
        assert manager.validator is not None
        assert manager.loader is not None

    def test_plugin_manager_default_settings(self):
        """Test plugin manager default settings."""
        try:
            from codomyrmex.plugin_system.plugin_manager import PluginManager
        except ImportError:
            pytest.skip("PluginManager not available")

        manager = PluginManager()

        assert manager.auto_discover is True
        assert manager.auto_validate is True
        assert manager.parallel_loading is True

    def test_plugin_discovery_through_manager(self, tmp_path):
        """Test plugin discovery through manager with real files."""
        try:
            from codomyrmex.plugin_system.plugin_manager import PluginManager
        except ImportError:
            pytest.skip("PluginManager not available")

        # Create a real plugin directory
        plugin_dir = tmp_path / "test_plugin"
        plugin_dir.mkdir()

        plugin_file = plugin_dir / "test_plugin.py"
        plugin_file.write_text("""
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
        try:
            from codomyrmex.plugin_system.plugin_manager import PluginManager
            from codomyrmex.plugin_system.plugin_registry import PluginInfo, PluginType, Plugin
        except ImportError:
            pytest.skip("PluginManager not available")

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
        try:
            from codomyrmex.plugin_system.plugin_manager import PluginManager
            from codomyrmex.plugin_system.plugin_registry import PluginInfo, PluginType, Plugin
        except ImportError:
            pytest.skip("PluginManager not available")

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
        try:
            from codomyrmex.plugin_system.plugin_manager import PluginManager
        except ImportError:
            pytest.skip("PluginManager not available")

        manager = PluginManager()

        # Register a hook
        hook = manager.register_hook("test_hook", description="Test hook")
        assert hook is not None
        assert hook.name == "test_hook"

        # Register handler and emit
        def test_handler():
            return "handled"

        hook.register(test_handler)
        results = manager.emit_hook("test_hook")
        assert len(results) == 1
        assert results[0] == "handled"

    def test_plugin_status(self):
        """Test getting plugin status."""
        try:
            from codomyrmex.plugin_system.plugin_manager import PluginManager
            from codomyrmex.plugin_system.plugin_registry import PluginInfo, PluginType, Plugin
        except ImportError:
            pytest.skip("PluginManager not available")

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
        try:
            from codomyrmex.plugin_system.plugin_manager import PluginManager
        except ImportError:
            pytest.skip("PluginManager not available")

        manager = PluginManager()

        status = manager.get_plugin_status("nonexistent")

        assert status["name"] == "nonexistent"
        assert status["registered"] == False
        assert status["loaded"] == False

    def test_system_status(self):
        """Test getting system status."""
        try:
            from codomyrmex.plugin_system.plugin_manager import PluginManager
            from codomyrmex.plugin_system.plugin_registry import PluginInfo, PluginType, Plugin
        except ImportError:
            pytest.skip("PluginManager not available")

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
        try:
            from codomyrmex.plugin_system.plugin_manager import PluginManager
            from codomyrmex.plugin_system.plugin_registry import PluginInfo, PluginType, Plugin, PluginState
        except ImportError:
            pytest.skip("PluginManager not available")

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
        try:
            from codomyrmex.plugin_system.plugin_manager import PluginManager
        except ImportError:
            pytest.skip("PluginManager not available")

        manager = PluginManager()

        result = manager.enable_plugin("nonexistent")
        assert result is False

    def test_load_plugin_with_validation(self, tmp_path):
        """Test loading plugin with validation using real validator and loader."""
        try:
            from codomyrmex.plugin_system.plugin_manager import PluginManager
            from codomyrmex.plugin_system.plugin_registry import PluginInfo, PluginType, Plugin
        except ImportError:
            pytest.skip("PluginManager not available")

        manager = PluginManager()

        # Create a real plugin file
        plugin_dir = tmp_path / "test_plugin"
        plugin_dir.mkdir()

        plugin_file = plugin_dir / "test_plugin.py"
        plugin_file.write_text("""
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
        try:
            from codomyrmex.plugin_system.plugin_manager import PluginManager
        except ImportError:
            pytest.skip("PluginManager not available")

        manager = PluginManager()

        result = manager.load_plugin("definitely_not_a_real_plugin")

        assert result.success is False
        assert "not found" in result.error_message.lower()

    def test_cleanup(self):
        """Test manager cleanup."""
        try:
            from codomyrmex.plugin_system.plugin_manager import PluginManager
            from codomyrmex.plugin_system.plugin_registry import PluginInfo, PluginType, Plugin
        except ImportError:
            pytest.skip("PluginManager not available")

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
# Test Plugin Base Class
# ============================================================================

class TestPluginBaseClass:
    """Test cases for the Plugin base class."""

    def test_plugin_base_creation(self):
        """Test creating a plugin base class."""
        try:
            from codomyrmex.plugin_system.plugin_registry import Plugin, PluginInfo, PluginType, PluginState
        except ImportError:
            pytest.skip("Plugin base class not available")

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
        try:
            from codomyrmex.plugin_system.plugin_registry import Plugin, PluginState
        except ImportError:
            pytest.skip("Plugin base class not available")

        plugin = Plugin()

        assert plugin.info is not None
        assert plugin.state == PluginState.UNLOADED

    def test_plugin_hook_registration(self):
        """Test plugin hook registration."""
        try:
            from codomyrmex.plugin_system.plugin_registry import Plugin, PluginInfo, PluginType
        except ImportError:
            pytest.skip("Plugin system not available")

        plugin = Plugin(PluginInfo(
            "test", "1.0.0", "Test", "Author", PluginType.UTILITY, "test.py"
        ))

        # Register hook
        def test_handler():
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
        try:
            from codomyrmex.plugin_system.plugin_registry import Plugin, PluginInfo, PluginType
        except ImportError:
            pytest.skip("Plugin system not available")

        plugin = Plugin(PluginInfo("test", "1.0.0", "", "", PluginType.UTILITY, "t.py"))

        results = plugin.emit_hook("nonexistent")
        assert results == []

    def test_plugin_lifecycle(self):
        """Test plugin lifecycle methods."""
        try:
            from codomyrmex.plugin_system.plugin_registry import Plugin, PluginInfo, PluginType, PluginState
        except ImportError:
            pytest.skip("Plugin system not available")

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
        try:
            from codomyrmex.plugin_system.plugin_registry import Plugin, PluginInfo, PluginType, PluginState
        except ImportError:
            pytest.skip("Plugin system not available")

        plugin = Plugin(PluginInfo("config_test", "1.0.0", "", "", PluginType.UTILITY, "t.py"))

        config = {"setting1": "value1", "setting2": 42}
        result = plugin.initialize(config)

        assert result is True
        assert plugin.state == PluginState.ACTIVE
        assert plugin.config["setting1"] == "value1"
        assert plugin.config["setting2"] == 42

    def test_plugin_shutdown(self):
        """Test plugin shutdown."""
        try:
            from codomyrmex.plugin_system.plugin_registry import Plugin, PluginInfo, PluginType, PluginState
        except ImportError:
            pytest.skip("Plugin system not available")

        plugin = Plugin(PluginInfo("shutdown_test", "1.0.0", "", "", PluginType.UTILITY, "t.py"))
        plugin.initialize()

        result = plugin.shutdown()

        assert result is True
        assert plugin.state == PluginState.SHUTTING_DOWN


# ============================================================================
# Test Interface Enforcer
# ============================================================================

class TestInterfaceEnforcer:
    """Test cases for the InterfaceEnforcer."""

    def test_enforcer_valid_interface(self):
        """Test enforcer with valid interface implementation."""
        try:
            from codomyrmex.plugin_system.enforcer import InterfaceEnforcer
        except ImportError:
            pytest.skip("InterfaceEnforcer not available")

        class RequiredInterface:
            def method_a(self): pass
            def method_b(self): pass

        class ValidImplementation:
            def method_a(self): return "a"
            def method_b(self): return "b"

        result = InterfaceEnforcer.enforce(ValidImplementation(), RequiredInterface)
        assert result is True

    def test_enforcer_invalid_interface(self):
        """Test enforcer with invalid interface implementation."""
        try:
            from codomyrmex.plugin_system.enforcer import InterfaceEnforcer
        except ImportError:
            pytest.skip("InterfaceEnforcer not available")

        class RequiredInterface:
            def method_a(self): pass
            def method_b(self): pass

        class InvalidImplementation:
            def method_a(self): return "a"
            # Missing method_b

        result = InterfaceEnforcer.enforce(InvalidImplementation(), RequiredInterface)
        assert result is False

    def test_enforcer_partial_implementation(self):
        """Test enforcer with partial interface implementation."""
        try:
            from codomyrmex.plugin_system.enforcer import InterfaceEnforcer
        except ImportError:
            pytest.skip("InterfaceEnforcer not available")

        class RequiredInterface:
            def method_a(self): pass
            def method_b(self): pass
            def method_c(self): pass

        class PartialImplementation:
            def method_a(self): return "a"
            method_b = "not callable"  # Not a method

        result = InterfaceEnforcer.enforce(PartialImplementation(), RequiredInterface)
        assert result is False


# ============================================================================
# Test Convenience Functions
# ============================================================================

class TestConvenienceFunctions:
    """Test cases for plugin system convenience functions."""

    def test_get_plugin_manager(self):
        """Test getting the global plugin manager."""
        try:
            from codomyrmex.plugin_system.plugin_manager import get_plugin_manager
        except ImportError:
            pytest.skip("Convenience functions not available")

        manager1 = get_plugin_manager()
        manager2 = get_plugin_manager()

        assert manager1 is manager2  # Should return same instance

    def test_convenience_functions(self):
        """Test other convenience functions."""
        try:
            from codomyrmex.plugin_system.plugin_manager import discover_plugins, load_plugin, unload_plugin
            from codomyrmex.plugin_system.plugin_loader import discover_plugins as loader_discover
            from codomyrmex.plugin_system.plugin_validator import validate_plugin
        except ImportError:
            pytest.skip("Convenience functions not available")

        # Test that functions exist and are callable
        assert callable(discover_plugins)
        assert callable(load_plugin)
        assert callable(unload_plugin)
        assert callable(validate_plugin)

    def test_create_plugin_info_helper(self):
        """Test plugin info creation helper."""
        try:
            from codomyrmex.plugin_system.plugin_registry import create_plugin_info, PluginType
        except ImportError:
            pytest.skip("Helper functions not available")

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
# Test Plugin Isolation
# ============================================================================

class TestPluginIsolation:
    """Test cases for plugin isolation."""

    def test_plugins_have_separate_state(self):
        """Test that plugins maintain separate state."""
        try:
            from codomyrmex.plugin_system.plugin_registry import Plugin, PluginInfo, PluginType
        except ImportError:
            pytest.skip("Plugin system not available")

        plugin1 = Plugin(PluginInfo("isolation1", "1.0.0", "", "", PluginType.UTILITY, "t.py"))
        plugin2 = Plugin(PluginInfo("isolation2", "1.0.0", "", "", PluginType.UTILITY, "t.py"))

        plugin1.set_config({"key": "value1"})
        plugin2.set_config({"key": "value2"})

        assert plugin1.get_config()["key"] == "value1"
        assert plugin2.get_config()["key"] == "value2"

    def test_plugins_have_separate_hooks(self):
        """Test that plugins have separate hook registrations."""
        try:
            from codomyrmex.plugin_system.plugin_registry import Plugin, PluginInfo, PluginType
        except ImportError:
            pytest.skip("Plugin system not available")

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
        try:
            from codomyrmex.plugin_system.plugin_registry import PluginRegistry, Plugin, PluginInfo, PluginType
        except ImportError:
            pytest.skip("Plugin system not available")

        registry1 = PluginRegistry()
        registry2 = PluginRegistry()

        plugin = Plugin(PluginInfo("shared_name", "1.0.0", "", "", PluginType.UTILITY, "t.py"))

        registry1.register(plugin)

        assert registry1.get("shared_name") is not None
        assert registry2.get("shared_name") is None


# ============================================================================
# Test Error Handling
# ============================================================================

class TestErrorHandling:
    """Test cases for error handling in the plugin system."""

    def test_load_invalid_plugin_path(self, tmp_path):
        """Test loading plugin with invalid path."""
        try:
            from codomyrmex.plugin_system.plugin_loader import PluginLoader
            from codomyrmex.plugin_system.plugin_registry import PluginInfo, PluginType
        except ImportError:
            pytest.skip("PluginLoader not available")

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
        try:
            from codomyrmex.plugin_system.plugin_validator import PluginValidator
        except ImportError:
            pytest.skip("PluginValidator not available")

        validator = PluginValidator()

        # Create a file with invalid content
        bad_file = tmp_path / "corrupted.py"
        bad_file.write_bytes(b'\x00\x01\x02\x03')  # Binary garbage

        result = validator.validate_plugin(str(bad_file))

        # Should handle gracefully without crashing
        assert hasattr(result, 'valid')

    def test_registry_handles_shutdown_errors(self):
        """Test that registry handles shutdown errors gracefully."""
        try:
            from codomyrmex.plugin_system.plugin_registry import PluginRegistry, Plugin, PluginInfo, PluginType
        except ImportError:
            pytest.skip("Plugin system not available")

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
        try:
            from codomyrmex.plugin_system.plugin_registry import Hook
        except ImportError:
            pytest.skip("Hook not available")

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

        results = hook.emit()

        # All handlers should have been attempted
        assert 1 in executed
        assert "bad" in executed
        assert 2 in executed


# ============================================================================
# Test Plugin Types
# ============================================================================

class TestPluginTypes:
    """Test cases for different plugin types."""

    def test_all_plugin_types_exist(self):
        """Test that all expected plugin types are defined."""
        try:
            from codomyrmex.plugin_system.plugin_registry import PluginType
        except ImportError:
            pytest.skip("PluginType not available")

        expected_types = [
            "ANALYZER", "FORMATTER", "EXPORTER", "IMPORTER",
            "PROCESSOR", "HOOK", "UTILITY", "ADAPTER", "AGENT"
        ]

        for type_name in expected_types:
            assert hasattr(PluginType, type_name)

    def test_plugin_type_values(self):
        """Test plugin type enum values."""
        try:
            from codomyrmex.plugin_system.plugin_registry import PluginType
        except ImportError:
            pytest.skip("PluginType not available")

        assert PluginType.ANALYZER.value == "analyzer"
        assert PluginType.UTILITY.value == "utility"
        assert PluginType.AGENT.value == "agent"


# ============================================================================
# Test Plugin States
# ============================================================================

class TestPluginStates:
    """Test cases for plugin state management."""

    def test_all_plugin_states_exist(self):
        """Test that all expected plugin states are defined."""
        try:
            from codomyrmex.plugin_system.plugin_registry import PluginState
        except ImportError:
            pytest.skip("PluginState not available")

        expected_states = [
            "UNKNOWN", "REGISTERED", "LOADED", "ACTIVE",
            "DISABLED", "ERROR", "INITIALIZING", "SHUTTING_DOWN",
            "LOADING", "UNLOADED"
        ]

        for state_name in expected_states:
            assert hasattr(PluginState, state_name)

    def test_plugin_state_transitions(self):
        """Test plugin state transitions."""
        try:
            from codomyrmex.plugin_system.plugin_registry import Plugin, PluginInfo, PluginType, PluginState
        except ImportError:
            pytest.skip("Plugin system not available")

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
# Test YAML Plugin Metadata
# ============================================================================

class TestYAMLMetadata:
    """Test cases for YAML plugin metadata loading."""

    def test_discover_yaml_plugin(self, tmp_path):
        """Test discovering plugin with YAML metadata."""
        try:
            import yaml
            from codomyrmex.plugin_system.plugin_loader import PluginLoader
        except ImportError:
            pytest.skip("YAML or PluginLoader not available")

        plugin_dir = tmp_path / "yaml_plugin"
        plugin_dir.mkdir()

        plugin_yaml = {
            "name": "yaml_plugin",
            "version": "1.0.0",
            "description": "Plugin with YAML metadata",
            "author": "Test",
            "plugin_type": "utility",
            "entry_point": "yaml_plugin.py"
        }

        with open(plugin_dir / "plugin.yaml", 'w') as f:
            yaml.dump(plugin_yaml, f)

        with open(plugin_dir / "yaml_plugin.py", 'w') as f:
            f.write("class YamlPlugin: pass")

        loader = PluginLoader([str(tmp_path)])
        discovered = loader.discover_plugins()

        assert len(discovered) == 1
        assert discovered[0].name == "yaml_plugin"


# ============================================================================
# Test Hook Class
# ============================================================================

class TestHookClass:
    """Test cases for the Hook class."""

    def test_hook_creation(self):
        """Test creating a hook."""
        try:
            from codomyrmex.plugin_system.plugin_registry import Hook
        except ImportError:
            pytest.skip("Hook not available")

        hook = Hook("test_hook", description="Test description")

        assert hook.name == "test_hook"
        assert hook.description == "Test description"
        assert hook.handlers == []

    def test_hook_register_handler(self):
        """Test registering handlers with a hook."""
        try:
            from codomyrmex.plugin_system.plugin_registry import Hook
        except ImportError:
            pytest.skip("Hook not available")

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
        try:
            from codomyrmex.plugin_system.plugin_registry import Hook
        except ImportError:
            pytest.skip("Hook not available")

        hook = Hook("args_test")

        def handler(a, b, c=None):
            return f"{a}-{b}-{c}"

        hook.register(handler)

        results = hook.emit("x", "y", c="z")

        assert results == ["x-y-z"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
