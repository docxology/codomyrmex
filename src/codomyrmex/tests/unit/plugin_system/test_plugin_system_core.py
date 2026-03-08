"""Zero-mock tests for plugin_system core: plugin_registry, dependency_resolver,
discovery, and mcp_tools.

No mocks, no monkeypatch, no MagicMock. Tests use real instances with real data.
Directory-scan tests write actual Python files into tempdir.
"""

from __future__ import annotations

import os
import tempfile

import pytest

from codomyrmex.plugin_system.core.plugin_registry import (
    Hook,
    Plugin,
    PluginInfo,
    PluginRegistry,
    PluginState,
    PluginType,
    create_plugin_info,
)
from codomyrmex.plugin_system.dependency_resolver import (
    DependencyNode,
    DependencyResolver,
    ResolutionStatus,
)
from codomyrmex.plugin_system.discovery import (
    DiscoveryResult,
    PluginDiscovery,
    PluginInfo as DiscoveryPluginInfo,
    PluginState as DiscoveryPluginState,
)


# ---------------------------------------------------------------------------
# TestPluginInfo
# ---------------------------------------------------------------------------


class TestPluginInfo:
    """Tests for the PluginInfo dataclass."""

    def test_default_values(self):
        info = PluginInfo()
        assert info.name == ""
        assert info.version == "0.0.0"
        assert info.enabled is True
        assert info.dependencies == []
        assert info.tags == []

    def test_to_dict_contains_name_and_version(self):
        info = PluginInfo(name="my_plugin", version="1.2.3")
        d = info.to_dict()
        assert d["name"] == "my_plugin"
        assert d["version"] == "1.2.3"

    def test_to_dict_contains_plugin_type_value(self):
        info = PluginInfo(plugin_type=PluginType.ANALYZER)
        d = info.to_dict()
        assert d["plugin_type"] == "analyzer"

    def test_to_dict_contains_dependencies(self):
        info = PluginInfo(name="dep_plugin", dependencies=["base_plugin"])
        d = info.to_dict()
        assert "base_plugin" in d["dependencies"]

    def test_to_dict_enabled_field(self):
        info = PluginInfo(enabled=False)
        d = info.to_dict()
        assert d["enabled"] is False

    def test_create_plugin_info_helper(self):
        info = create_plugin_info(name="helper_plugin", version="2.0.0")
        assert isinstance(info, PluginInfo)
        assert info.name == "helper_plugin"

    def test_all_plugin_types_have_string_value(self):
        for pt in PluginType:
            assert isinstance(pt.value, str)
            assert len(pt.value) > 0

    def test_plugin_info_tags(self):
        info = PluginInfo(tags=["ml", "inference"])
        assert "ml" in info.tags
        assert "inference" in info.tags


# ---------------------------------------------------------------------------
# TestHook
# ---------------------------------------------------------------------------


class TestHook:
    """Tests for the Hook class."""

    def test_hook_initializes_with_empty_handlers(self):
        hook = Hook("on_load")
        assert len(hook.handlers) == 0

    def test_register_adds_handler(self):
        hook = Hook("on_load")
        hook.register(lambda: None)
        assert len(hook.handlers) == 1

    def test_emit_calls_handler(self):
        hook = Hook("on_process")
        results = []
        hook.register(lambda x: results.append(x))
        hook.emit(42)
        assert results == [42]

    def test_emit_calls_all_handlers(self):
        hook = Hook("on_process")
        results = []
        hook.register(lambda x: results.append(f"h1:{x}"))
        hook.register(lambda x: results.append(f"h2:{x}"))
        hook.emit("data")
        assert "h1:data" in results
        assert "h2:data" in results

    def test_emit_returns_handler_results(self):
        hook = Hook("on_calc")
        hook.register(lambda x: x * 2)
        hook.register(lambda x: x + 1)
        results = hook.emit(5)
        assert 10 in results
        assert 6 in results

    def test_emit_captures_exception_and_continues(self):
        hook = Hook("on_error")
        results = []

        def bad_handler():
            raise ValueError("oops")

        def good_handler():
            results.append("ok")

        hook.register(bad_handler)
        hook.register(good_handler)
        hook.emit()
        assert "ok" in results

    def test_hook_name_stored(self):
        hook = Hook("my_hook", description="Does something")
        assert hook.name == "my_hook"
        assert hook.description == "Does something"


# ---------------------------------------------------------------------------
# TestPlugin
# ---------------------------------------------------------------------------


class TestPlugin:
    """Tests for the Plugin base class lifecycle."""

    def make_plugin(self, name: str = "test_plugin") -> Plugin:
        info = PluginInfo(name=name, version="1.0.0")
        return Plugin(info=info)

    def test_plugin_initial_state_is_unloaded(self):
        plugin = self.make_plugin()
        assert plugin.state == PluginState.UNLOADED

    def test_plugin_info_property(self):
        plugin = self.make_plugin("my_plugin")
        assert plugin.info.name == "my_plugin"

    def test_initialize_sets_state_to_active(self):
        plugin = self.make_plugin()
        result = plugin.initialize()
        assert result is True
        assert plugin.state == PluginState.ACTIVE

    def test_initialize_with_config_updates_config(self):
        plugin = self.make_plugin()
        plugin.initialize(config={"debug": True, "max_retries": 3})
        assert plugin.config["debug"] is True
        assert plugin.config["max_retries"] == 3

    def test_shutdown_sets_state_to_shutting_down(self):
        plugin = self.make_plugin()
        plugin.initialize()
        result = plugin.shutdown()
        assert result is True
        assert plugin.state == PluginState.SHUTTING_DOWN

    def test_get_state_returns_current_state(self):
        plugin = self.make_plugin()
        assert plugin.get_state() == PluginState.UNLOADED

    def test_set_config_and_get_config(self):
        plugin = self.make_plugin()
        plugin.set_config({"key": "value", "num": 42})
        cfg = plugin.get_config()
        assert cfg["key"] == "value"
        assert cfg["num"] == 42

    def test_register_hook_creates_hook(self):
        plugin = self.make_plugin()
        results = []
        plugin.register_hook("on_data", lambda d: results.append(d))
        assert "on_data" in plugin.hooks

    def test_emit_hook_calls_registered_handler(self):
        plugin = self.make_plugin()
        results = []
        plugin.register_hook("on_data", lambda d: results.append(d))
        plugin.emit_hook("on_data", "payload")
        assert "payload" in results

    def test_emit_hook_nonexistent_returns_empty(self):
        plugin = self.make_plugin()
        result = plugin.emit_hook("nonexistent_hook")
        assert result == []

    def test_plugin_with_none_info_uses_defaults(self):
        plugin = Plugin(info=None)
        assert plugin.info.name == ""

    def test_plugin_with_non_plugininfo_object(self):
        class FakeInfo:
            name = "fake"
            version = "0.1"
            description = "A fake"

        plugin = Plugin(info=FakeInfo())
        assert plugin.info.name == "fake"


# ---------------------------------------------------------------------------
# TestPluginRegistry
# ---------------------------------------------------------------------------


class TestPluginRegistry:
    """Tests for PluginRegistry."""

    def make_registry(self) -> PluginRegistry:
        return PluginRegistry()

    def make_plugin(self, name: str, plugin_type: PluginType = PluginType.UTILITY):
        info = PluginInfo(name=name, version="1.0.0", plugin_type=plugin_type)
        return Plugin(info=info)

    def test_register_returns_true_on_success(self):
        registry = self.make_registry()
        plugin = self.make_plugin("plug_a")
        result = registry.register(plugin)
        assert result is True

    def test_register_duplicate_returns_false(self):
        registry = self.make_registry()
        plugin = self.make_plugin("plug_dup")
        registry.register(plugin)
        result = registry.register(plugin)
        assert result is False

    def test_get_registered_plugin(self):
        registry = self.make_registry()
        plugin = self.make_plugin("plug_get")
        registry.register(plugin)
        retrieved = registry.get("plug_get")
        assert retrieved is plugin

    def test_get_nonexistent_returns_none(self):
        registry = self.make_registry()
        result = registry.get("nonexistent")
        assert result is None

    def test_unregister_removes_plugin(self):
        registry = self.make_registry()
        plugin = self.make_plugin("plug_del")
        registry.register(plugin)
        result = registry.unregister("plug_del")
        assert result is True
        assert registry.get("plug_del") is None

    def test_unregister_nonexistent_returns_false(self):
        registry = self.make_registry()
        result = registry.unregister("never_existed")
        assert result is False

    def test_list_plugins_returns_all(self):
        registry = self.make_registry()
        registry.register(self.make_plugin("p1"))
        registry.register(self.make_plugin("p2"))
        plugins = registry.list_plugins()
        names = [p.name for p in plugins]
        assert "p1" in names
        assert "p2" in names

    def test_list_plugins_filtered_by_type(self):
        registry = self.make_registry()
        registry.register(self.make_plugin("analyzer1", PluginType.ANALYZER))
        registry.register(self.make_plugin("formatter1", PluginType.FORMATTER))
        analyzers = registry.list_plugins(plugin_type=PluginType.ANALYZER)
        assert all(p.plugin_type == PluginType.ANALYZER for p in analyzers)
        assert len(analyzers) == 1

    def test_get_plugin_info(self):
        registry = self.make_registry()
        registry.register(self.make_plugin("info_plug"))
        info = registry.get_plugin_info("info_plug")
        assert info is not None
        assert info.name == "info_plug"

    def test_check_dependencies_no_deps(self):
        registry = self.make_registry()
        registry.register(self.make_plugin("nodep"))
        missing = registry.check_dependencies("nodep")
        assert missing == []

    def test_check_dependencies_missing_dep(self):
        registry = self.make_registry()
        info = PluginInfo(name="dep_plug", dependencies=["missing_dep"])
        plugin = Plugin(info=info)
        registry.register(plugin)
        missing = registry.check_dependencies("dep_plug")
        assert "missing_dep" in missing

    def test_check_dependencies_satisfied_dep(self):
        registry = self.make_registry()
        dep_plugin = self.make_plugin("dep_a")
        main_plugin = Plugin(
            info=PluginInfo(name="main_b", dependencies=["dep_a"])
        )
        registry.register(dep_plugin)
        registry.register(main_plugin)
        missing = registry.check_dependencies("main_b")
        assert missing == []

    def test_initialize_all(self):
        registry = self.make_registry()
        registry.register(self.make_plugin("init_p1"))
        registry.register(self.make_plugin("init_p2"))
        results = registry.initialize_all()
        assert all(v is True for v in results.values())

    def test_shutdown_all(self):
        registry = self.make_registry()
        registry.register(self.make_plugin("shut_p1"))
        registry.initialize_all()
        results = registry.shutdown_all()
        assert all(v is True for v in results.values())

    def test_categories_updated_on_register(self):
        registry = self.make_registry()
        registry.register(self.make_plugin("cat_plug", PluginType.ADAPTER))
        assert "adapter" in registry.categories
        assert "cat_plug" in registry.categories["adapter"]

    def test_categories_updated_on_unregister(self):
        registry = self.make_registry()
        registry.register(self.make_plugin("rm_plug", PluginType.HOOK))
        registry.unregister("rm_plug")
        assert "rm_plug" not in registry.categories.get("hook", [])

    def test_register_global_hook(self):
        registry = self.make_registry()
        hook = registry.register_global_hook("on_start", description="Startup hook")
        assert isinstance(hook, Hook)
        assert hook.name == "on_start"

    def test_emit_global_hook_calls_handler(self):
        registry = self.make_registry()
        results = []
        hook = registry.register_global_hook("on_event")
        hook.register(lambda x: results.append(x))
        registry.emit_global_hook("on_event", "fired")
        assert "fired" in results

    def test_emit_global_hook_nonexistent_returns_empty(self):
        registry = self.make_registry()
        result = registry.emit_global_hook("does_not_exist")
        assert result == []


# ---------------------------------------------------------------------------
# TestDependencyResolver
# ---------------------------------------------------------------------------


class TestDependencyResolver:
    """Tests for DependencyResolver — the topological sort engine."""

    def test_empty_resolver_resolves_successfully(self):
        resolver = DependencyResolver()
        result = resolver.resolve()
        assert result.status == ResolutionStatus.RESOLVED
        assert result.load_order == []

    def test_single_node_no_deps(self):
        resolver = DependencyResolver()
        resolver.add(DependencyNode("alpha"))
        result = resolver.resolve()
        assert result.status == ResolutionStatus.RESOLVED
        assert result.load_order == ["alpha"]

    def test_linear_dependency_chain(self):
        resolver = DependencyResolver()
        resolver.add(DependencyNode("c", dependencies=["b"]))
        resolver.add(DependencyNode("b", dependencies=["a"]))
        resolver.add(DependencyNode("a"))
        result = resolver.resolve()
        assert result.status == ResolutionStatus.RESOLVED
        order = result.load_order
        assert order.index("a") < order.index("b")
        assert order.index("b") < order.index("c")

    def test_missing_dependency_detected(self):
        resolver = DependencyResolver()
        resolver.add(DependencyNode("plugin_a", dependencies=["missing_dep"]))
        result = resolver.resolve()
        assert result.status == ResolutionStatus.MISSING
        assert "missing_dep" in result.missing

    def test_circular_dependency_detected(self):
        resolver = DependencyResolver()
        resolver.add(DependencyNode("a", dependencies=["b"]))
        resolver.add(DependencyNode("b", dependencies=["a"]))
        result = resolver.resolve()
        assert result.status == ResolutionStatus.CIRCULAR
        assert len(result.circular) > 0

    def test_conflict_detected(self):
        resolver = DependencyResolver()
        resolver.add(DependencyNode("a", conflicts=["b"]))
        resolver.add(DependencyNode("b"))
        result = resolver.resolve()
        assert result.status == ResolutionStatus.CONFLICT
        assert len(result.conflicts) > 0

    def test_multiple_independent_plugins(self):
        resolver = DependencyResolver()
        resolver.add(DependencyNode("x"))
        resolver.add(DependencyNode("y"))
        resolver.add(DependencyNode("z"))
        result = resolver.resolve()
        assert result.status == ResolutionStatus.RESOLVED
        assert len(result.load_order) == 3

    def test_add_many(self):
        resolver = DependencyResolver()
        nodes = [DependencyNode("n1"), DependencyNode("n2"), DependencyNode("n3")]
        resolver.add_many(nodes)
        assert resolver.node_count == 3

    def test_get_registered_node(self):
        resolver = DependencyResolver()
        node = DependencyNode("my_node", version="2.0.0")
        resolver.add(node)
        retrieved = resolver.get("my_node")
        assert retrieved is node

    def test_get_nonexistent_node_returns_none(self):
        resolver = DependencyResolver()
        result = resolver.get("no_such_node")
        assert result is None

    def test_clear_removes_all_nodes(self):
        resolver = DependencyResolver()
        resolver.add(DependencyNode("n1"))
        resolver.add(DependencyNode("n2"))
        resolver.clear()
        assert resolver.node_count == 0

    def test_diamond_dependency(self):
        # a -> b -> d and a -> c -> d  (diamond)
        resolver = DependencyResolver()
        resolver.add(DependencyNode("a", dependencies=["b", "c"]))
        resolver.add(DependencyNode("b", dependencies=["d"]))
        resolver.add(DependencyNode("c", dependencies=["d"]))
        resolver.add(DependencyNode("d"))
        result = resolver.resolve()
        assert result.status == ResolutionStatus.RESOLVED
        order = result.load_order
        assert order.index("d") < order.index("b")
        assert order.index("d") < order.index("c")

    def test_optional_dependencies_not_required(self):
        resolver = DependencyResolver()
        resolver.add(DependencyNode("main", optional_dependencies=["extra"]))
        # extra is not registered — but optional deps shouldn't block resolution
        result = resolver.resolve()
        assert result.status == ResolutionStatus.RESOLVED


# ---------------------------------------------------------------------------
# TestPluginDiscovery
# ---------------------------------------------------------------------------


class TestPluginDiscovery:
    """Tests for PluginDiscovery — entry points and directory scanning."""

    def test_scan_entry_points_returns_discovery_result(self):
        discovery = PluginDiscovery(entry_point_group="codomyrmex.plugins")
        result = discovery.scan_entry_points()
        assert isinstance(result, DiscoveryResult)
        assert isinstance(result.plugins, list)
        assert isinstance(result.errors, list)

    def test_scan_entry_points_has_correct_source(self):
        discovery = PluginDiscovery(entry_point_group="codomyrmex.plugins")
        result = discovery.scan_entry_points()
        assert any("entry_point:codomyrmex.plugins" in s for s in result.scan_sources)

    def test_scan_nonexistent_directory_reports_error(self):
        discovery = PluginDiscovery()
        result = discovery.scan_directory("/tmp/does_not_exist_xyz_12345")
        assert len(result.errors) > 0

    def test_scan_empty_directory_finds_no_plugins(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            discovery = PluginDiscovery()
            result = discovery.scan_directory(tmpdir)
            assert result.plugins == []
            assert result.errors == []

    def test_scan_directory_finds_plugin_info_dict(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_file = os.path.join(tmpdir, "my_plugin.py")
            with open(plugin_file, "w") as f:
                f.write(
                    'PLUGIN_INFO = {"name": "my_plugin", "version": "1.2.3", '
                    '"description": "A test plugin"}\n'
                )
            discovery = PluginDiscovery()
            result = discovery.scan_directory(tmpdir)
            assert len(result.plugins) == 1
            assert result.plugins[0].name == "my_plugin"
            assert result.plugins[0].version == "1.2.3"

    def test_scan_directory_finds_plugin_class(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_file = os.path.join(tmpdir, "cls_plugin.py")
            with open(plugin_file, "w") as f:
                f.write(
                    "class Plugin:\n"
                    '    name = "class_plugin"\n'
                    '    version = "0.5.0"\n'
                    '    description = "Class-based plugin"\n'
                )
            discovery = PluginDiscovery()
            result = discovery.scan_directory(tmpdir)
            assert any(p.name == "class_plugin" for p in result.plugins)

    def test_scan_directory_ignores_private_modules(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            private_file = os.path.join(tmpdir, "_private.py")
            with open(private_file, "w") as f:
                f.write('PLUGIN_INFO = {"name": "should_not_appear"}\n')
            discovery = PluginDiscovery()
            result = discovery.scan_directory(tmpdir)
            assert result.plugins == []

    def test_scan_directory_ignores_non_py_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            txt_file = os.path.join(tmpdir, "readme.txt")
            with open(txt_file, "w") as f:
                f.write("not a plugin")
            discovery = PluginDiscovery()
            result = discovery.scan_directory(tmpdir)
            assert result.plugins == []

    def test_scan_full_combines_entry_points_and_directories(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_file = os.path.join(tmpdir, "combo_plugin.py")
            with open(plugin_file, "w") as f:
                f.write('PLUGIN_INFO = {"name": "combo", "version": "1.0"}\n')
            discovery = PluginDiscovery(
                entry_point_group="codomyrmex.plugins",
                plugin_dirs=[tmpdir],
            )
            result = discovery.scan()
            plugin_names = [p.name for p in result.plugins]
            assert "combo" in plugin_names

    def test_plugin_info_state_on_discovery(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_file = os.path.join(tmpdir, "state_test.py")
            with open(plugin_file, "w") as f:
                f.write('PLUGIN_INFO = {"name": "state_test", "version": "0.1"}\n')
            discovery = PluginDiscovery()
            result = discovery.scan_directory(tmpdir)
            assert result.plugins[0].state == DiscoveryPluginState.DISCOVERED

    def test_plugin_info_with_dependencies_from_dict(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_file = os.path.join(tmpdir, "dep_plugin.py")
            with open(plugin_file, "w") as f:
                f.write(
                    'PLUGIN_INFO = {"name": "dep_plug", "version": "1.0", '
                    '"dependencies": ["base_lib"]}\n'
                )
            discovery = PluginDiscovery()
            result = discovery.scan_directory(tmpdir)
            assert result.plugins[0].dependencies == ["base_lib"]


# ---------------------------------------------------------------------------
# TestMCPToolsPluginSystem
# ---------------------------------------------------------------------------


class TestMCPToolsPluginSystem:
    """Tests for plugin_system MCP tools."""

    def test_plugin_scan_entry_points_returns_success(self):
        from codomyrmex.plugin_system.mcp_tools import plugin_scan_entry_points

        result = plugin_scan_entry_points()
        assert result["status"] == "success"
        assert "plugin_count" in result
        assert isinstance(result["plugins"], list)
        assert isinstance(result["errors"], list)

    def test_plugin_scan_custom_group(self):
        from codomyrmex.plugin_system.mcp_tools import plugin_scan_entry_points

        result = plugin_scan_entry_points(entry_point_group="nonexistent.group.xyz")
        assert result["status"] == "success"
        assert result["plugin_count"] == 0

    def test_plugin_resolve_dependencies_simple_chain(self):
        from codomyrmex.plugin_system.mcp_tools import plugin_resolve_dependencies

        plugins = [
            {"name": "base"},
            {"name": "middle", "dependencies": ["base"]},
            {"name": "top", "dependencies": ["middle"]},
        ]
        result = plugin_resolve_dependencies(plugins)
        assert result["status"] == "success"
        assert result["resolution_status"] == "resolved"
        order = result["load_order"]
        assert order.index("base") < order.index("middle")
        assert order.index("middle") < order.index("top")

    def test_plugin_resolve_dependencies_no_deps(self):
        from codomyrmex.plugin_system.mcp_tools import plugin_resolve_dependencies

        plugins = [{"name": "standalone"}]
        result = plugin_resolve_dependencies(plugins)
        assert result["status"] == "success"
        assert result["load_order"] == ["standalone"]

    def test_plugin_resolve_dependencies_missing_dep(self):
        from codomyrmex.plugin_system.mcp_tools import plugin_resolve_dependencies

        plugins = [{"name": "needs_missing", "dependencies": ["not_here"]}]
        result = plugin_resolve_dependencies(plugins)
        assert result["status"] == "success"
        assert result["resolution_status"] == "missing"
        assert "not_here" in result["missing"]

    def test_plugin_resolve_dependencies_circular(self):
        from codomyrmex.plugin_system.mcp_tools import plugin_resolve_dependencies

        plugins = [
            {"name": "a", "dependencies": ["b"]},
            {"name": "b", "dependencies": ["a"]},
        ]
        result = plugin_resolve_dependencies(plugins)
        assert result["status"] == "success"
        assert result["resolution_status"] == "circular"
