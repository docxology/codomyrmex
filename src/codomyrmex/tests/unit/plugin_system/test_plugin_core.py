"""Comprehensive tests for plugin_system/core — registry, loader, manager, and dependency resolver.

Covers:
- PluginRegistry: register, unregister, get, list, categories, hooks, check_dependencies,
  initialize_all, shutdown_all, global hooks
- PluginLoader: discover from temp directories, load real .py plugin files, unload, reload,
  get_plugin, validate_plugin_dependencies, duplicate detection
- PluginManager: lifecycle orchestration, enable/disable, plugin/system status, hooks, cleanup
- Plugin base class: hook registration/emission, config, state, info property
- PluginInfo: to_dict, default values, all PluginType and PluginState enums
- DependencyResolver: multi-level chains, conflicts, add_many, clear, optional deps, node_count
- PluginDiscovery: scan real temp directory with PLUGIN_INFO dict and Plugin class patterns
- LoadResult: dataclass defaults, warnings list
- Parametrized: PluginType values, PluginState values, valid/invalid plugin specs

Zero-mock policy: all tests use real objects, real temp files, real imports.
"""

import json
import os
import tempfile
from typing import Any

import pytest

from codomyrmex.plugin_system.core.plugin_loader import LoadResult, PluginLoader
from codomyrmex.plugin_system.core.plugin_manager import PluginManager
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
from codomyrmex.plugin_system.dependency_resolver import (
    DependencyNode,
    DependencyResolver,
    ResolutionResult,
    ResolutionStatus,
)
from codomyrmex.plugin_system.discovery import (
    DiscoveryResult,
    PluginDiscovery,
)
from codomyrmex.plugin_system.discovery import (
    PluginState as DiscoveryPluginState,
)

# ---------------------------------------------------------------------------
# Helpers -- real Plugin subclasses (not mocks)
# ---------------------------------------------------------------------------


class SamplePlugin(Plugin):
    """A real Plugin subclass for testing loading from files."""

    def initialize(self, config: dict[str, Any] | None = None) -> bool:
        if config:
            self.config.update(config)
        self.state = PluginState.ACTIVE
        return True


class FailingInitPlugin(Plugin):
    """Plugin whose initialize always returns False."""

    def initialize(self, config: dict[str, Any] | None = None) -> bool:
        self.state = PluginState.ERROR
        return False


class ExplodingShutdownPlugin(Plugin):
    """Plugin whose shutdown raises."""

    def shutdown(self) -> bool:
        raise RuntimeError("shutdown explosion")


# ---------------------------------------------------------------------------
# PluginInfo and enums
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPluginInfoDataclass:
    """Tests for PluginInfo creation, defaults, and serialization."""

    def test_default_values(self):
        info = PluginInfo()
        assert info.name == ""
        assert info.version == "0.0.0"
        assert info.description == ""
        assert info.author is None
        assert info.plugin_type == PluginType.UTILITY
        assert info.entry_point == ""
        assert info.dependencies == []
        assert info.enabled is True
        assert info.tags == []
        assert info.config_schema is None
        assert info.homepage is None
        assert info.license is None

    def test_to_dict_round_trip(self):
        info = PluginInfo(
            name="rt",
            version="3.1.4",
            description="Round-trip test",
            author="Tester",
            plugin_type=PluginType.AGENT,
            entry_point="rt.py",
            dependencies=["dep_a"],
            enabled=True,
            tags=["tag1"],
            config_schema={"type": "object"},
            homepage="https://example.com",
            license="MIT",
        )
        d = info.to_dict()
        assert d["name"] == "rt"
        assert d["version"] == "3.1.4"
        assert d["plugin_type"] == "agent"
        assert d["dependencies"] == ["dep_a"]
        assert d["tags"] == ["tag1"]
        assert d["config_schema"] == {"type": "object"}
        assert d["homepage"] == "https://example.com"
        assert d["license"] == "MIT"

    def test_create_plugin_info_helper(self):
        info = create_plugin_info(name="helper", version="0.1.0")
        assert isinstance(info, PluginInfo)
        assert info.name == "helper"

    @pytest.mark.parametrize(
        "ptype",
        [
            PluginType.ANALYZER,
            PluginType.FORMATTER,
            PluginType.EXPORTER,
            PluginType.IMPORTER,
            PluginType.PROCESSOR,
            PluginType.HOOK,
            PluginType.UTILITY,
            PluginType.ADAPTER,
            PluginType.AGENT,
        ],
    )
    def test_all_plugin_types_in_enum(self, ptype):
        """Every PluginType enum value is a non-empty string."""
        assert isinstance(ptype.value, str)
        assert len(ptype.value) > 0

    @pytest.mark.parametrize(
        "state",
        list(PluginState),
    )
    def test_all_plugin_states_in_enum(self, state):
        """Every PluginState enum value is a non-empty string."""
        assert isinstance(state.value, str)
        assert len(state.value) > 0


# ---------------------------------------------------------------------------
# Plugin base class
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPluginBaseClass:
    """Tests for the Plugin base class."""

    def test_default_construction(self):
        p = Plugin()
        assert p.info.name == ""
        assert p.state == PluginState.UNLOADED
        assert p.config == {}
        assert p.hooks == {}

    def test_construction_with_plugin_info(self):
        info = PluginInfo(name="myp", version="1.0.0")
        p = Plugin(info)
        assert p.info.name == "myp"
        assert p.info.version == "1.0.0"

    def test_initialize_sets_active(self):
        p = Plugin()
        result = p.initialize({"key": "val"})
        assert result is True
        assert p.state == PluginState.ACTIVE
        assert p.config == {"key": "val"}

    def test_initialize_without_config(self):
        p = Plugin()
        assert p.initialize() is True
        assert p.state == PluginState.ACTIVE

    def test_shutdown(self):
        p = Plugin()
        p.initialize()
        result = p.shutdown()
        assert result is True
        assert p.state == PluginState.SHUTTING_DOWN

    def test_get_state(self):
        p = Plugin()
        assert p.get_state() == PluginState.UNLOADED
        p.initialize()
        assert p.get_state() == PluginState.ACTIVE

    def test_set_and_get_config(self):
        p = Plugin()
        p.set_config({"a": 1})
        assert p.get_config() == {"a": 1}

    def test_register_and_emit_hook(self):
        p = Plugin()
        results_collector = []

        def handler(x):
            results_collector.append(x * 2)
            return x * 2

        p.register_hook("double", handler)
        returned = p.emit_hook("double", 5)
        assert returned == [10]
        assert results_collector == [10]

    def test_emit_unregistered_hook_returns_empty(self):
        p = Plugin()
        assert p.emit_hook("nonexistent", 1, 2) == []

    def test_multiple_handlers_on_one_hook(self):
        p = Plugin()
        p.register_hook("multi", lambda x: x + 1)
        p.register_hook("multi", lambda x: x + 2)
        results = p.emit_hook("multi", 10)
        assert results == [11, 12]


# ---------------------------------------------------------------------------
# Hook class
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestHookClass:
    """Tests for the Hook class directly."""

    def test_hook_creation(self):
        h = Hook("test_hook", description="A test hook")
        assert h.name == "test_hook"
        assert h.description == "A test hook"
        assert h.handlers == []

    def test_hook_register_and_emit(self):
        h = Hook("adder")
        h.register(lambda a, b: a + b)
        results = h.emit(3, 4)
        assert results == [7]

    def test_hook_handler_exception_is_caught(self):
        h = Hook("boom")

        def bad_handler():
            raise ValueError("kaboom")

        h.register(bad_handler)
        # Should not raise; error is logged
        results = h.emit()
        assert results == []


# ---------------------------------------------------------------------------
# PluginRegistry
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPluginRegistryCore:
    """Tests for PluginRegistry internals."""

    def test_register_and_get(self):
        reg = PluginRegistry()
        info = PluginInfo(name="alpha", version="1.0.0", plugin_type=PluginType.ANALYZER)
        p = Plugin(info)
        assert reg.register(p) is True
        assert reg.get("alpha") is p

    def test_duplicate_registration_returns_false(self):
        reg = PluginRegistry()
        info = PluginInfo(name="dup", version="1.0.0")
        p1 = Plugin(info)
        p2 = Plugin(info)
        assert reg.register(p1) is True
        assert reg.register(p2) is False

    def test_unregister_calls_shutdown(self):
        reg = PluginRegistry()
        info = PluginInfo(name="unreg", version="1.0.0")
        p = Plugin(info)
        p.initialize()
        reg.register(p)
        assert reg.unregister("unreg") is True
        assert p.state == PluginState.SHUTTING_DOWN
        assert reg.get("unreg") is None

    def test_unregister_nonexistent_returns_false(self):
        reg = PluginRegistry()
        assert reg.unregister("ghost") is False

    def test_get_plugin_info(self):
        reg = PluginRegistry()
        info = PluginInfo(name="infotest", version="2.0.0", description="desc")
        p = Plugin(info)
        reg.register(p)
        retrieved = reg.get_plugin_info("infotest")
        assert retrieved is not None
        assert retrieved.version == "2.0.0"
        assert retrieved.description == "desc"

    def test_get_plugin_info_missing(self):
        reg = PluginRegistry()
        assert reg.get_plugin_info("nope") is None

    def test_list_plugins_all(self):
        reg = PluginRegistry()
        for name, ptype in [("a", PluginType.ANALYZER), ("b", PluginType.FORMATTER)]:
            reg.register(Plugin(PluginInfo(name=name, plugin_type=ptype)))
        listed = reg.list_plugins()
        assert len(listed) == 2

    def test_list_plugins_filtered_by_type(self):
        reg = PluginRegistry()
        reg.register(Plugin(PluginInfo(name="x", plugin_type=PluginType.ANALYZER)))
        reg.register(Plugin(PluginInfo(name="y", plugin_type=PluginType.FORMATTER)))
        analyzers = reg.list_plugins(plugin_type=PluginType.ANALYZER)
        assert len(analyzers) == 1
        assert analyzers[0].name == "x"

    def test_categories_tracking(self):
        reg = PluginRegistry()
        reg.register(Plugin(PluginInfo(name="c1", plugin_type=PluginType.HOOK)))
        reg.register(Plugin(PluginInfo(name="c2", plugin_type=PluginType.HOOK)))
        assert "hook" in reg.categories
        assert sorted(reg.categories["hook"]) == ["c1", "c2"]

    def test_unregister_removes_from_categories(self):
        reg = PluginRegistry()
        reg.register(Plugin(PluginInfo(name="rm", plugin_type=PluginType.EXPORTER)))
        assert "rm" in reg.categories.get("exporter", [])
        reg.unregister("rm")
        assert "rm" not in reg.categories.get("exporter", [])

    def test_check_dependencies_all_present(self):
        reg = PluginRegistry()
        reg.register(Plugin(PluginInfo(name="base")))
        reg.register(Plugin(PluginInfo(name="child", dependencies=["base"])))
        missing = reg.check_dependencies("child")
        assert missing == []

    def test_check_dependencies_some_missing(self):
        reg = PluginRegistry()
        reg.register(Plugin(PluginInfo(name="orphan", dependencies=["missing_dep"])))
        missing = reg.check_dependencies("orphan")
        assert missing == ["missing_dep"]

    def test_check_dependencies_unknown_plugin(self):
        reg = PluginRegistry()
        assert reg.check_dependencies("ghost") == []

    def test_initialize_all(self):
        reg = PluginRegistry()
        for n in ["i1", "i2", "i3"]:
            reg.register(Plugin(PluginInfo(name=n)))
        results = reg.initialize_all()
        assert all(v is True for v in results.values())
        assert set(results.keys()) == {"i1", "i2", "i3"}

    def test_shutdown_all(self):
        reg = PluginRegistry()
        for n in ["s1", "s2"]:
            p = Plugin(PluginInfo(name=n))
            p.initialize()
            reg.register(p)
        results = reg.shutdown_all()
        assert all(v is True for v in results.values())

    def test_global_hooks(self):
        reg = PluginRegistry()
        hook = reg.register_global_hook("on_start", description="Startup hook")
        assert isinstance(hook, Hook)
        assert hook.name == "on_start"

        collected = []
        hook.register(lambda: collected.append("fired"))
        reg.emit_global_hook("on_start")
        assert collected == ["fired"]

    def test_emit_unregistered_global_hook(self):
        reg = PluginRegistry()
        assert reg.emit_global_hook("nope") == []

    def test_get_registry_singleton(self):
        r1 = get_registry()
        r2 = get_registry()
        assert r1 is r2


# ---------------------------------------------------------------------------
# LoadResult dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestLoadResult:
    """Tests for LoadResult."""

    def test_defaults(self):
        lr = LoadResult(plugin_name="test", success=True)
        assert lr.plugin_name == "test"
        assert lr.success is True
        assert lr.plugin_instance is None
        assert lr.error_message is None
        assert lr.warnings == []

    def test_warnings_mutable_default(self):
        lr1 = LoadResult(plugin_name="a", success=True)
        lr2 = LoadResult(plugin_name="b", success=False)
        lr1.warnings.append("w1")
        assert lr2.warnings == []  # no shared mutable default


# ---------------------------------------------------------------------------
# PluginLoader with real temp directories
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPluginLoaderCore:
    """Tests for PluginLoader using real temp directories and .py files."""

    def test_init_creates_directories(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = os.path.join(tmpdir, "plugins_new")
            PluginLoader(plugin_directories=[plugin_dir])
            assert os.path.isdir(plugin_dir)

    def test_discover_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = PluginLoader(plugin_directories=[tmpdir])
            discovered = loader.discover_plugins()
            assert discovered == []

    def test_discover_plugin_from_json_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = os.path.join(tmpdir, "my_plugin")
            os.makedirs(plugin_dir)
            metadata = {
                "name": "my_plugin",
                "version": "1.2.3",
                "entry_point": "my_plugin.py",
                "description": "A test plugin",
                "author": "Tester",
            }
            with open(os.path.join(plugin_dir, "plugin.json"), "w") as f:
                json.dump(metadata, f)
            loader = PluginLoader(plugin_directories=[tmpdir])
            discovered = loader.discover_plugins()
            assert len(discovered) == 1
            assert discovered[0].name == "my_plugin"
            assert discovered[0].version == "1.2.3"

    def test_discover_plugin_from_inline_comment_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_content = (
                '# plugin: {"name": "inline_p", "version": "0.5.0", "type": "analyzer"}\n'
                "class InlinePPlugin:\n"
                "    pass\n"
            )
            plugin_file = os.path.join(tmpdir, "inline_p.py")
            with open(plugin_file, "w") as f:
                f.write(plugin_content)
            loader = PluginLoader(plugin_directories=[tmpdir])
            discovered = loader.discover_plugins()
            assert len(discovered) == 1
            assert discovered[0].name == "inline_p"
            assert discovered[0].version == "0.5.0"

    def test_load_real_plugin_from_file(self):
        """Load a real .py file containing a Plugin subclass."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_code = (
                "from codomyrmex.plugin_system.core.plugin_registry import Plugin, PluginState\n"
                "from typing import Any\n\n"
                "class GreeterPlugin(Plugin):\n"
                "    def initialize(self, config=None):\n"
                "        if config:\n"
                "            self.config.update(config)\n"
                "        self.state = PluginState.ACTIVE\n"
                "        return True\n"
            )
            plugin_file = os.path.join(tmpdir, "greeter.py")
            with open(plugin_file, "w") as f:
                f.write(plugin_code)

            info = PluginInfo(
                name="greeter",
                version="1.0.0",
                entry_point="greeter.py",
            )
            loader = PluginLoader(plugin_directories=[tmpdir])
            result = loader.load_plugin(info, config={"greeting": "hello"})
            assert result.success is True
            assert result.plugin_instance is not None
            assert result.plugin_instance.config.get("greeting") == "hello"
            assert result.plugin_instance.state == PluginState.ACTIVE

    def test_load_already_loaded_returns_warning(self):
        """Loading the same plugin twice returns a warning but succeeds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_code = (
                "from codomyrmex.plugin_system.core.plugin_registry import Plugin, PluginState\n"
                "class DupPlugin(Plugin):\n"
                "    def initialize(self, config=None):\n"
                "        self.state = PluginState.ACTIVE\n"
                "        return True\n"
            )
            with open(os.path.join(tmpdir, "dup.py"), "w") as f:
                f.write(plugin_code)

            info = PluginInfo(name="dup_load", version="1.0.0", entry_point="dup.py")
            loader = PluginLoader(plugin_directories=[tmpdir])
            r1 = loader.load_plugin(info)
            assert r1.success is True
            r2 = loader.load_plugin(info)
            assert r2.success is True
            assert any("already loaded" in w for w in r2.warnings)

    def test_load_missing_module_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            info = PluginInfo(name="ghost", version="1.0.0", entry_point="nonexistent.py")
            loader = PluginLoader(plugin_directories=[tmpdir])
            result = loader.load_plugin(info)
            assert result.success is False
            assert result.error_message is not None

    def test_unload_plugin(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_code = (
                "from codomyrmex.plugin_system.core.plugin_registry import Plugin, PluginState\n"
                "class UnloadMe(Plugin):\n"
                "    def initialize(self, config=None):\n"
                "        self.state = PluginState.ACTIVE\n"
                "        return True\n"
            )
            with open(os.path.join(tmpdir, "unload_me.py"), "w") as f:
                f.write(plugin_code)

            info = PluginInfo(name="unload_test", version="1.0.0", entry_point="unload_me.py")
            loader = PluginLoader(plugin_directories=[tmpdir])
            loader.load_plugin(info)
            assert loader.get_plugin("unload_test") is not None
            assert loader.unload_plugin("unload_test") is True
            assert loader.get_plugin("unload_test") is None

    def test_unload_nonexistent_returns_false(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = PluginLoader(plugin_directories=[tmpdir])
            assert loader.unload_plugin("never_loaded") is False

    def test_get_loaded_plugins(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_code = (
                "from codomyrmex.plugin_system.core.plugin_registry import Plugin, PluginState\n"
                "class ListMe(Plugin):\n"
                "    def initialize(self, config=None):\n"
                "        self.state = PluginState.ACTIVE\n"
                "        return True\n"
            )
            with open(os.path.join(tmpdir, "list_me.py"), "w") as f:
                f.write(plugin_code)

            info = PluginInfo(name="listed", version="1.0.0", entry_point="list_me.py")
            loader = PluginLoader(plugin_directories=[tmpdir])
            loader.load_plugin(info)
            loaded = loader.get_loaded_plugins()
            assert "listed" in loaded
            # Ensure it returns a copy
            loaded.pop("listed")
            assert "listed" in loader.get_loaded_plugins()

    def test_validate_plugin_dependencies_all_importable(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = PluginLoader(plugin_directories=[tmpdir])
            info = PluginInfo(name="v", dependencies=["os", "sys", "json"])
            missing = loader.validate_plugin_dependencies(info)
            assert missing == []

    def test_validate_plugin_dependencies_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = PluginLoader(plugin_directories=[tmpdir])
            info = PluginInfo(name="v", dependencies=["nonexistent_pkg_abc123"])
            missing = loader.validate_plugin_dependencies(info)
            assert len(missing) == 1
            assert "nonexistent_pkg_abc123" in missing[0]

    def test_load_plugin_via_python_module_path(self):
        """Test loading a plugin via dotted module path (not .py file)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            info = PluginInfo(
                name="json_module",
                version="1.0.0",
                entry_point="codomyrmex.plugin_system.core.plugin_registry",
            )
            loader = PluginLoader(plugin_directories=[tmpdir])
            # This should load the module but may not find a suitable subclass
            # (Plugin itself is excluded). The point is: the code path runs.
            result = loader.load_plugin(info)
            # It loads the module but Plugin is the only class, so no subclass found
            assert result.success is False
            assert "class not found" in (result.error_message or "").lower()


# ---------------------------------------------------------------------------
# PluginManager
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPluginManagerCore:
    """Tests for PluginManager lifecycle orchestration."""

    def test_creation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = PluginManager(plugin_directories=[tmpdir])
            assert mgr.registry is not None
            assert mgr.loader is not None
            assert mgr.auto_discover is True
            assert mgr.auto_validate is True

    def test_get_plugin_returns_none_for_unknown(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = PluginManager(plugin_directories=[tmpdir])
            assert mgr.get_plugin("nonexistent") is None

    def test_enable_and_disable_plugin(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = PluginManager(plugin_directories=[tmpdir])
            info = PluginInfo(name="toggle", version="1.0.0")
            p = Plugin(info)
            p.initialize()
            mgr.registry.register(p)
            assert mgr.enable_plugin("toggle") is True
            assert p.state == PluginState.ACTIVE
            assert mgr.disable_plugin("toggle") is True
            assert p.state == PluginState.DISABLED

    def test_enable_nonexistent_returns_false(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = PluginManager(plugin_directories=[tmpdir])
            assert mgr.enable_plugin("ghost") is False

    def test_disable_nonexistent_returns_false(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = PluginManager(plugin_directories=[tmpdir])
            assert mgr.disable_plugin("ghost") is False

    def test_list_plugins(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = PluginManager(plugin_directories=[tmpdir])
            mgr.registry.register(Plugin(PluginInfo(name="lp1", plugin_type=PluginType.ANALYZER)))
            mgr.registry.register(Plugin(PluginInfo(name="lp2", plugin_type=PluginType.FORMATTER)))
            all_list = mgr.list_plugins()
            assert len(all_list) == 2
            analyzers = mgr.list_plugins(filter_type=PluginType.ANALYZER)
            assert len(analyzers) == 1

    def test_get_plugin_status_registered_only(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = PluginManager(plugin_directories=[tmpdir])
            info = PluginInfo(name="stat", version="2.0.0", dependencies=["missing_dep"])
            mgr.registry.register(Plugin(info))
            status = mgr.get_plugin_status("stat")
            assert status["registered"] is True
            assert status["loaded"] is False
            assert status["dependencies_satisfied"] is False
            assert "missing_dep" in status["missing_dependencies"]

    def test_get_plugin_status_unknown(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = PluginManager(plugin_directories=[tmpdir])
            status = mgr.get_plugin_status("no_such")
            assert status["registered"] is False
            assert status["loaded"] is False

    def test_get_system_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = PluginManager(plugin_directories=[tmpdir])
            mgr.registry.register(Plugin(PluginInfo(name="sys1", plugin_type=PluginType.HOOK)))
            status = mgr.get_system_status()
            assert status["status_counts"]["total_registered"] == 1
            assert status["system_health"] == "healthy"

    def test_register_and_emit_hook(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = PluginManager(plugin_directories=[tmpdir])
            hook = mgr.register_hook("test_hook", description="Test")
            assert isinstance(hook, Hook)
            results_box = []
            hook.register(lambda v: results_box.append(v))
            mgr.emit_hook("test_hook", 42)
            assert results_box == [42]

    def test_cleanup_attempts_unload_for_all_registered(self):
        """cleanup() iterates all registered plugins and attempts unload.
        Plugins only in the registry (not loaded via loader) will remain
        because PluginManager.unload_plugin requires loader.unload to succeed
        before it unregisters from the registry.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = PluginManager(plugin_directories=[tmpdir])
            mgr.registry.register(Plugin(PluginInfo(name="clean1")))
            mgr.registry.register(Plugin(PluginInfo(name="clean2")))
            # cleanup does not raise even when unload returns False
            mgr.cleanup()
            # Plugins stay registered because they were never loaded via loader
            assert len(mgr.list_plugins()) == 2

    def test_cleanup_removes_loaded_plugins(self):
        """When plugins are loaded via loader, cleanup fully removes them."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_code = (
                "from codomyrmex.plugin_system.core.plugin_registry import Plugin, PluginState\n"
                "class CleanPlugin(Plugin):\n"
                "    def initialize(self, config=None):\n"
                "        self.state = PluginState.ACTIVE\n"
                "        return True\n"
            )
            with open(os.path.join(tmpdir, "cleanp.py"), "w") as f:
                f.write(plugin_code)

            mgr = PluginManager(plugin_directories=[tmpdir])
            info = PluginInfo(name="cleanp", version="1.0.0", entry_point="cleanp.py")
            mgr.registry.register(Plugin(info))
            # Load via loader so it is tracked there
            mgr.loader.load_plugin(info)
            assert "cleanp" in mgr.loader.get_loaded_plugins()
            mgr.cleanup()
            assert "cleanp" not in mgr.loader.get_loaded_plugins()


# ---------------------------------------------------------------------------
# DependencyResolver
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDependencyResolverCore:
    """Extended tests for DependencyResolver."""

    def test_empty_resolver(self):
        resolver = DependencyResolver()
        result = resolver.resolve()
        assert result.status == ResolutionStatus.RESOLVED
        assert result.load_order == []

    def test_single_node_no_deps(self):
        resolver = DependencyResolver()
        resolver.add(DependencyNode("solo"))
        result = resolver.resolve()
        assert result.status == ResolutionStatus.RESOLVED
        assert result.load_order == ["solo"]

    def test_linear_chain(self):
        resolver = DependencyResolver()
        resolver.add(DependencyNode("c", dependencies=["b"]))
        resolver.add(DependencyNode("b", dependencies=["a"]))
        resolver.add(DependencyNode("a"))
        result = resolver.resolve()
        assert result.status == ResolutionStatus.RESOLVED
        order = result.load_order
        assert order.index("a") < order.index("b") < order.index("c")

    def test_diamond_dependency(self):
        resolver = DependencyResolver()
        resolver.add(DependencyNode("top", dependencies=["left", "right"]))
        resolver.add(DependencyNode("left", dependencies=["bottom"]))
        resolver.add(DependencyNode("right", dependencies=["bottom"]))
        resolver.add(DependencyNode("bottom"))
        result = resolver.resolve()
        assert result.status == ResolutionStatus.RESOLVED
        order = result.load_order
        assert order.index("bottom") < order.index("left")
        assert order.index("bottom") < order.index("right")
        assert order.index("left") < order.index("top")
        assert order.index("right") < order.index("top")

    def test_conflict_detection(self):
        resolver = DependencyResolver()
        resolver.add(DependencyNode("pg", conflicts=["mysql"]))
        resolver.add(DependencyNode("mysql"))
        result = resolver.resolve()
        assert result.status == ResolutionStatus.CONFLICT
        assert len(result.conflicts) >= 1

    def test_add_many(self):
        resolver = DependencyResolver()
        resolver.add_many([
            DependencyNode("x", dependencies=["y"]),
            DependencyNode("y"),
        ])
        result = resolver.resolve()
        assert result.status == ResolutionStatus.RESOLVED
        assert result.load_order.index("y") < result.load_order.index("x")

    def test_get_node(self):
        resolver = DependencyResolver()
        node = DependencyNode("fetched", version="2.0.0")
        resolver.add(node)
        assert resolver.get("fetched") is node
        assert resolver.get("missing") is None

    def test_node_count(self):
        resolver = DependencyResolver()
        assert resolver.node_count == 0
        resolver.add(DependencyNode("a"))
        resolver.add(DependencyNode("b"))
        assert resolver.node_count == 2

    def test_clear(self):
        resolver = DependencyResolver()
        resolver.add(DependencyNode("clearme"))
        assert resolver.node_count == 1
        resolver.clear()
        assert resolver.node_count == 0

    def test_three_node_cycle(self):
        resolver = DependencyResolver()
        resolver.add(DependencyNode("a", dependencies=["b"]))
        resolver.add(DependencyNode("b", dependencies=["c"]))
        resolver.add(DependencyNode("c", dependencies=["a"]))
        result = resolver.resolve()
        assert result.status == ResolutionStatus.CIRCULAR
        assert len(result.circular) >= 1

    def test_partial_order_with_cycle(self):
        """Nodes not in the cycle still appear in load_order."""
        resolver = DependencyResolver()
        resolver.add(DependencyNode("free"))
        resolver.add(DependencyNode("x", dependencies=["y"]))
        resolver.add(DependencyNode("y", dependencies=["x"]))
        result = resolver.resolve()
        assert result.status == ResolutionStatus.CIRCULAR
        assert "free" in result.load_order

    def test_optional_dependencies_field(self):
        node = DependencyNode("opt", optional_dependencies=["nice_to_have"])
        assert node.optional_dependencies == ["nice_to_have"]


# ---------------------------------------------------------------------------
# PluginDiscovery with real temp directories
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPluginDiscoveryCore:
    """Tests for PluginDiscovery scanning real temp directories."""

    def test_scan_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            discovery = PluginDiscovery(plugin_dirs=[tmpdir])
            result = discovery.scan_directory(tmpdir)
            assert result.plugins == []
            assert result.errors == []

    def test_scan_directory_with_plugin_info_dict(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            code = (
                'PLUGIN_INFO = {\n'
                '    "name": "dir_scanner",\n'
                '    "version": "3.0.0",\n'
                '    "author": "TestBot",\n'
                '    "description": "Found by directory scan",\n'
                '    "dependencies": ["dep_x"],\n'
                '}\n'
            )
            with open(os.path.join(tmpdir, "scanner_plugin.py"), "w") as f:
                f.write(code)

            discovery = PluginDiscovery(plugin_dirs=[tmpdir])
            result = discovery.scan_directory(tmpdir)
            assert len(result.plugins) == 1
            pi = result.plugins[0]
            assert pi.name == "dir_scanner"
            assert pi.version == "3.0.0"
            assert pi.author == "TestBot"
            assert pi.dependencies == ["dep_x"]
            assert pi.state == DiscoveryPluginState.DISCOVERED

    def test_scan_directory_with_plugin_class(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            code = (
                'class Plugin:\n'
                '    name = "class_based"\n'
                '    version = "0.9.0"\n'
                '    description = "Class-based discovery"\n'
            )
            with open(os.path.join(tmpdir, "class_plugin.py"), "w") as f:
                f.write(code)

            discovery = PluginDiscovery(plugin_dirs=[tmpdir])
            result = discovery.scan_directory(tmpdir)
            assert len(result.plugins) == 1
            assert result.plugins[0].name == "class_based"

    def test_scan_skips_underscore_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "__init__.py"), "w") as f:
                f.write("PLUGIN_INFO = {'name': 'hidden'}\n")
            with open(os.path.join(tmpdir, "_private.py"), "w") as f:
                f.write("PLUGIN_INFO = {'name': 'private'}\n")

            discovery = PluginDiscovery()
            result = discovery.scan_directory(tmpdir)
            assert len(result.plugins) == 0

    def test_scan_nonexistent_directory(self):
        discovery = PluginDiscovery()
        result = discovery.scan_directory("/no/such/dir/anywhere")
        assert len(result.errors) == 1

    def test_full_scan_combines_sources(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            code = 'PLUGIN_INFO = {"name": "combined", "version": "1.0.0"}\n'
            with open(os.path.join(tmpdir, "combined.py"), "w") as f:
                f.write(code)

            discovery = PluginDiscovery(
                entry_point_group="codomyrmex.test.nonexistent_group",
                plugin_dirs=[tmpdir],
            )
            result = discovery.scan()
            # At minimum we get the directory-scanned plugin
            names = [p.name for p in result.plugins]
            assert "combined" in names
            # Scan sources should include both entry_point and directory
            assert any("entry_point" in s for s in result.scan_sources)
            assert any("directory" in s for s in result.scan_sources)

    def test_scan_directory_with_syntax_error_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "broken.py"), "w") as f:
                f.write("def oops(\n")  # syntax error
            discovery = PluginDiscovery()
            result = discovery.scan_directory(tmpdir)
            assert len(result.errors) >= 1
            assert result.plugins == []


# ---------------------------------------------------------------------------
# Parametrized: valid and invalid plugin specs
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestParametrizedPluginSpecs:
    """Parametrized tests for valid and invalid plugin info combinations."""

    @pytest.mark.parametrize(
        "name,version,entry_point,expected_valid",
        [
            ("valid_plugin", "1.0.0", "valid.py", True),
            ("another", "0.0.1", "another.py", True),
            ("", "1.0.0", "e.py", True),   # empty name is allowed by dataclass
            ("p", "0.0.0", "", True),       # empty entry_point is allowed
        ],
    )
    def test_plugin_info_creation_variants(self, name, version, entry_point, expected_valid):
        info = PluginInfo(name=name, version=version, entry_point=entry_point)
        assert isinstance(info, PluginInfo)
        assert info.name == name
        assert info.version == version

    @pytest.mark.parametrize(
        "ptype_str",
        ["analyzer", "formatter", "exporter", "importer", "processor", "hook", "utility", "adapter", "agent"],
    )
    def test_plugin_type_from_string(self, ptype_str):
        ptype = PluginType(ptype_str)
        assert ptype.value == ptype_str

    def test_invalid_plugin_type_raises(self):
        with pytest.raises(ValueError):
            PluginType("nonexistent_type")

    def test_invalid_plugin_state_raises(self):
        with pytest.raises(ValueError):
            PluginState("nonexistent_state")


# ---------------------------------------------------------------------------
# DiscoveryResult and ResolutionResult dataclasses
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDataclassDefaults:
    """Tests for dataclass default factories."""

    def test_discovery_result_defaults(self):
        dr = DiscoveryResult()
        assert dr.plugins == []
        assert dr.errors == []
        assert dr.scan_sources == []

    def test_resolution_result_defaults(self):
        rr = ResolutionResult(status=ResolutionStatus.RESOLVED)
        assert rr.load_order == []
        assert rr.missing == []
        assert rr.circular == []
        assert rr.conflicts == []

    def test_dependency_node_defaults(self):
        dn = DependencyNode(name="dn")
        assert dn.version == "0.0.0"
        assert dn.dependencies == []
        assert dn.optional_dependencies == []
        assert dn.conflicts == []
