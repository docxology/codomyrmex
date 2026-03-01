"""Tests for plugin, theme, and snippet management CLI commands."""


import pytest

from codomyrmex.agentic_memory.obsidian.cli import ObsidianCLI, ObsidianCLINotAvailable
from codomyrmex.agentic_memory.obsidian.plugins import (
    PluginInfo,
    SnippetInfo,
    ThemeInfo,
    _parse_plugins,
    disable_plugin,
    disable_snippet,
    enable_plugin,
    enable_snippet,
    get_plugin_info,
    get_theme_info,
    install_plugin,
    install_theme,
    list_enabled,
    list_enabled_snippets,
    list_plugins,
    list_snippets,
    list_themes,
    reload_plugin,
    set_theme,
    uninstall_plugin,
    uninstall_theme,
)


class TestPluginInfo:
    def test_create(self):
        p = PluginInfo(id="dataview", name="Dataview", enabled=True, version="0.5.67")
        assert p.id == "dataview"
        assert p.enabled is True

    def test_defaults(self):
        p = PluginInfo(id="test-plugin")
        assert p.name == ""
        assert p.enabled is False
        assert p.version == ""


class TestThemeInfo:
    def test_create(self):
        t = ThemeInfo(name="Minimal", version="7.4.0", active=True)
        assert t.name == "Minimal"
        assert t.active is True

    def test_defaults(self):
        t = ThemeInfo(name="Test")
        assert t.version == ""
        assert t.active is False


class TestSnippetInfo:
    def test_create(self):
        s = SnippetInfo(name="custom-css", enabled=True)
        assert s.name == "custom-css"
        assert s.enabled is True


class TestParsePlugins:
    def test_tab_separated(self):
        lines = ["dataview\tDataview\tv0.5.67", "templater\tTemplater\tv2.1.3"]
        plugins = _parse_plugins(lines)
        assert len(plugins) == 2
        assert plugins[0].id == "dataview"
        assert plugins[0].version == "v0.5.67"

    def test_single_column(self):
        plugins = _parse_plugins(["dataview", "templater"])
        assert len(plugins) == 2
        assert plugins[1].id == "templater"

    def test_empty_lines(self):
        plugins = _parse_plugins(["dataview", "", "   ", "templater"])
        assert len(plugins) == 2

    def test_with_enabled_flag(self):
        plugins = _parse_plugins(["dataview"], enabled=True)
        assert plugins[0].enabled is True


class TestPluginUnavailable:
    def _cli(self):
        return ObsidianCLI(binary="__nonexistent__")

    def test_list_plugins(self):
        with pytest.raises(ObsidianCLINotAvailable):
            list_plugins(self._cli())

    def test_list_plugins_with_filter(self):
        with pytest.raises(ObsidianCLINotAvailable):
            list_plugins(self._cli(), filter="community", versions=True, format="json")

    def test_list_enabled(self):
        with pytest.raises(ObsidianCLINotAvailable):
            list_enabled(self._cli())

    def test_get_plugin_info(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_plugin_info(self._cli(), "dataview")

    def test_enable_plugin(self):
        with pytest.raises(ObsidianCLINotAvailable):
            enable_plugin(self._cli(), "test")

    def test_disable_plugin(self):
        with pytest.raises(ObsidianCLINotAvailable):
            disable_plugin(self._cli(), "test")

    def test_install_plugin(self):
        with pytest.raises(ObsidianCLINotAvailable):
            install_plugin(self._cli(), "test", enable=True)

    def test_uninstall_plugin(self):
        with pytest.raises(ObsidianCLINotAvailable):
            uninstall_plugin(self._cli(), "test")

    def test_reload_plugin(self):
        with pytest.raises(ObsidianCLINotAvailable):
            reload_plugin(self._cli(), "test")


class TestThemeUnavailable:
    def _cli(self):
        return ObsidianCLI(binary="__nonexistent__")

    def test_list_themes(self):
        with pytest.raises(ObsidianCLINotAvailable):
            list_themes(self._cli())

    def test_get_theme_info(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_theme_info(self._cli(), name="Minimal")

    def test_set_theme(self):
        with pytest.raises(ObsidianCLINotAvailable):
            set_theme(self._cli(), "Minimal")

    def test_install_theme(self):
        with pytest.raises(ObsidianCLINotAvailable):
            install_theme(self._cli(), "Minimal", enable=True)

    def test_uninstall_theme(self):
        with pytest.raises(ObsidianCLINotAvailable):
            uninstall_theme(self._cli(), "Minimal")


class TestSnippetUnavailable:
    def _cli(self):
        return ObsidianCLI(binary="__nonexistent__")

    def test_list_snippets(self):
        with pytest.raises(ObsidianCLINotAvailable):
            list_snippets(self._cli())

    def test_list_enabled_snippets(self):
        with pytest.raises(ObsidianCLINotAvailable):
            list_enabled_snippets(self._cli())

    def test_enable_snippet(self):
        with pytest.raises(ObsidianCLINotAvailable):
            enable_snippet(self._cli(), "custom")

    def test_disable_snippet(self):
        with pytest.raises(ObsidianCLINotAvailable):
            disable_snippet(self._cli(), "custom")
