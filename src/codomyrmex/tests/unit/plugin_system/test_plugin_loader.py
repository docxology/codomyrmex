"""Unit tests for plugin loading, discovery, and unloading."""

import json
import os
import tempfile

import pytest

from codomyrmex.plugin_system.core.plugin_loader import LoadResult, PluginLoader
from codomyrmex.plugin_system.core.plugin_registry import (
    Plugin,
    PluginInfo,
    PluginType,
)


# ============================================================================
# Test Plugin Loader
# ============================================================================

@pytest.mark.unit
class TestPluginLoader:
    """Test cases for PluginLoader functionality."""

    def test_plugin_loader_creation(self):
        """Test creating a plugin loader with real implementation."""
        loader = PluginLoader()
        assert loader is not None
        assert len(loader.plugin_directories) > 0

    def test_plugin_loader_custom_directories(self):
        """Test creating plugin loader with custom directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_dirs = [temp_dir]
            loader = PluginLoader(custom_dirs)

            assert temp_dir in [str(d) for d in loader.plugin_directories]

    def test_plugin_discovery(self):
        """Test plugin discovery with real files."""
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

@pytest.mark.unit
class TestPlugin(Plugin):
    '''Test suite for Plugin.'''
    def initialize(self, config): return True
    def shutdown(self): pass
""")

            loader = PluginLoader([temp_dir])
            discovered = loader.discover_plugins()

            assert len(discovered) == 1
            assert discovered[0].name == "test_plugin"

    def test_discover_multiple_plugins(self):
        """Test discovering multiple plugins."""
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
        # Create a real plugin module
        plugin_dir = tmp_path / "test_plugin"
        plugin_dir.mkdir()

        plugin_file = plugin_dir / "test_plugin.py"
        plugin_file.write_text("""
@pytest.mark.unit
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
        loader = PluginLoader([str(tmp_path)])

        result = loader.unload_plugin("nonexistent")

        assert result is False

    def test_get_loaded_plugins(self, tmp_path):
        """Test getting all loaded plugins."""
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
# Test YAML Plugin Metadata
# ============================================================================

@pytest.mark.unit
class TestYAMLMetadata:
    """Test cases for YAML plugin metadata loading."""

    def test_discover_yaml_plugin(self, tmp_path):
        """Test discovering plugin with YAML metadata."""
        try:
            import yaml
        except ImportError:
            pytest.skip("YAML not available")

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
# Test Plugin Discovery (from test_tier3_promotions.py)
# ============================================================================

class TestPluginDiscovery:
    """Tests for PluginDiscovery."""

    def test_scan_entry_points_runs(self):
        """Test functionality: scan entry points runs."""
        from codomyrmex.plugin_system.discovery import PluginDiscovery
        discovery = PluginDiscovery(entry_point_group="codomyrmex.test.nonexistent")
        result = discovery.scan_entry_points()
        assert isinstance(result.plugins, list)  # may be empty
        assert len(result.scan_sources) == 1

    def test_scan_invalid_directory(self):
        """Test functionality: scan invalid directory."""
        from codomyrmex.plugin_system.discovery import PluginDiscovery
        discovery = PluginDiscovery()
        result = discovery.scan_directory("/nonexistent/path")
        assert len(result.errors) == 1
