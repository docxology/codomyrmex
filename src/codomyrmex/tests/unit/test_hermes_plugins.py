"""Unit tests for the Hermes plugin system (plugins_cmd.py).

Zero-Mock Policy: tests use real filesystem operations (tmp_path),
real subprocess calls (git), and real YAML parsing. No MagicMock patches.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helpers to locate the upstream plugins_cmd module
# ---------------------------------------------------------------------------

def _hermes_agent_root() -> Path | None:
    """Find the installed hermes-agent source under ~/.hermes/hermes-agent."""
    candidate = Path.home() / ".hermes" / "hermes-agent"
    return candidate if candidate.exists() else None


def _import_plugins_cmd():
    """Import hermes_cli.plugins_cmd from ~/.hermes/hermes-agent, or skip."""
    root = _hermes_agent_root()
    if root is None:
        pytest.skip("~/.hermes/hermes-agent not found — Hermes not installed")

    import sys
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    try:
        import hermes_cli.plugins_cmd as pc
        return pc
    except ImportError as e:
        pytest.skip(f"hermes_cli.plugins_cmd not importable: {e}")


# ---------------------------------------------------------------------------
# _plugins_dir()
# ---------------------------------------------------------------------------


class TestPluginsDir:
    """_plugins_dir() respects HERMES_HOME and creates if missing."""

    def test_default_under_home(self, monkeypatch, tmp_path):
        pc = _import_plugins_cmd()
        monkeypatch.setenv("HERMES_HOME", str(tmp_path / ".hermes"))
        plugins_dir = pc._plugins_dir()
        assert plugins_dir == tmp_path / ".hermes" / "plugins"
        assert plugins_dir.exists()

    def test_creates_missing_directory(self, monkeypatch, tmp_path):
        pc = _import_plugins_cmd()
        hermes_home = tmp_path / "custom_hermes"
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        plugins_dir = pc._plugins_dir()
        assert plugins_dir.exists()
        assert plugins_dir.is_dir()

    def test_custom_hermes_home(self, monkeypatch, tmp_path):
        pc = _import_plugins_cmd()
        custom = tmp_path / "myhermes"
        monkeypatch.setenv("HERMES_HOME", str(custom))
        plugins_dir = pc._plugins_dir()
        assert str(custom) in str(plugins_dir)


# ---------------------------------------------------------------------------
# _resolve_git_url()
# ---------------------------------------------------------------------------


class TestResolveGitUrl:
    """_resolve_git_url converts identifiers to cloneable Git URLs."""

    def test_shorthand_owner_repo(self):
        pc = _import_plugins_cmd()
        url = pc._resolve_git_url("owner/repo")
        assert url == "https://github.com/owner/repo.git"

    def test_full_https_url_passthrough(self):
        pc = _import_plugins_cmd()
        url = pc._resolve_git_url("https://github.com/owner/repo.git")
        assert url == "https://github.com/owner/repo.git"

    def test_ssh_url_passthrough(self):
        pc = _import_plugins_cmd()
        url = pc._resolve_git_url("git@github.com:owner/repo.git")
        assert url == "git@github.com:owner/repo.git"

    def test_ssh_url_scheme_passthrough(self):
        pc = _import_plugins_cmd()
        url = pc._resolve_git_url("ssh://git@github.com/owner/repo.git")
        assert url.startswith("ssh://")

    def test_file_scheme_passthrough(self):
        pc = _import_plugins_cmd()
        url = pc._resolve_git_url("file:///tmp/myplugin")
        assert url == "file:///tmp/myplugin"

    def test_invalid_identifier_raises(self):
        pc = _import_plugins_cmd()
        with pytest.raises(ValueError, match="Invalid plugin identifier"):
            pc._resolve_git_url("not-a-valid-ident")

    def test_three_part_path_raises(self):
        pc = _import_plugins_cmd()
        with pytest.raises(ValueError):
            pc._resolve_git_url("owner/repo/extra")


# ---------------------------------------------------------------------------
# _sanitize_plugin_name()
# ---------------------------------------------------------------------------


class TestSanitizePluginName:
    """_sanitize_plugin_name() blocks path traversal attacks."""

    def test_valid_name_returns_path(self, tmp_path):
        pc = _import_plugins_cmd()
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()
        result = pc._sanitize_plugin_name("my-plugin", plugins_dir)
        assert result == plugins_dir / "my-plugin"

    def test_dotdot_raises(self, tmp_path):
        pc = _import_plugins_cmd()
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()
        with pytest.raises(ValueError, match=".."):
            pc._sanitize_plugin_name("../evil", plugins_dir)

    def test_backslash_raises(self, tmp_path):
        pc = _import_plugins_cmd()
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()
        with pytest.raises(ValueError):
            pc._sanitize_plugin_name("evil\\plugin", plugins_dir)

    def test_slash_in_name_raises(self, tmp_path):
        pc = _import_plugins_cmd()
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()
        with pytest.raises(ValueError):
            pc._sanitize_plugin_name("sub/plugin", plugins_dir)

    def test_empty_name_raises(self, tmp_path):
        pc = _import_plugins_cmd()
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()
        with pytest.raises(ValueError, match="must not be empty"):
            pc._sanitize_plugin_name("", plugins_dir)


# ---------------------------------------------------------------------------
# _repo_name_from_url()
# ---------------------------------------------------------------------------


class TestRepoNameFromUrl:
    """_repo_name_from_url() extracts the repo name from various URL formats."""

    def test_https_with_git_suffix(self):
        pc = _import_plugins_cmd()
        assert pc._repo_name_from_url("https://github.com/owner/my-plugin.git") == "my-plugin"

    def test_https_without_git_suffix(self):
        pc = _import_plugins_cmd()
        assert pc._repo_name_from_url("https://github.com/owner/my-plugin") == "my-plugin"

    def test_trailing_slash_stripped(self):
        pc = _import_plugins_cmd()
        assert pc._repo_name_from_url("https://github.com/owner/my-plugin/") == "my-plugin"


# ---------------------------------------------------------------------------
# _read_manifest()
# ---------------------------------------------------------------------------


class TestReadManifest:
    """_read_manifest() parses plugin.yaml or returns empty dict."""

    def test_valid_manifest(self, tmp_path):
        pc = _import_plugins_cmd()
        plugin_dir = tmp_path / "my-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.yaml").write_text(
            "name: my-plugin\nversion: 1.0.0\ndescription: A test plugin\n"
        )
        manifest = pc._read_manifest(plugin_dir)
        assert manifest["name"] == "my-plugin"
        assert manifest["version"] == "1.0.0"
        assert manifest["description"] == "A test plugin"

    def test_missing_manifest_returns_empty(self, tmp_path):
        pc = _import_plugins_cmd()
        plugin_dir = tmp_path / "no-manifest"
        plugin_dir.mkdir()
        manifest = pc._read_manifest(plugin_dir)
        assert manifest == {}

    def test_empty_yaml_returns_empty(self, tmp_path):
        pc = _import_plugins_cmd()
        plugin_dir = tmp_path / "empty-yaml"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.yaml").write_text("")
        manifest = pc._read_manifest(plugin_dir)
        assert manifest == {}

    def test_manifest_with_manifest_version(self, tmp_path):
        pc = _import_plugins_cmd()
        plugin_dir = tmp_path / "versioned-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.yaml").write_text(
            "name: test\nmanifest_version: 1\n"
        )
        manifest = pc._read_manifest(plugin_dir)
        assert manifest["manifest_version"] == 1


# ---------------------------------------------------------------------------
# _copy_example_files()
# ---------------------------------------------------------------------------


class TestCopyExampleFiles:
    """_copy_example_files() creates real files from .example templates."""

    def test_copies_example_to_real(self, tmp_path):
        pc = _import_plugins_cmd()
        plugin_dir = tmp_path / "plugin"
        plugin_dir.mkdir()
        (plugin_dir / "config.yaml.example").write_text("key: value\n")

        from rich.console import Console
        console = Console(quiet=True)
        pc._copy_example_files(plugin_dir, console)

        assert (plugin_dir / "config.yaml").exists()
        assert (plugin_dir / "config.yaml").read_text() == "key: value\n"

    def test_does_not_overwrite_existing(self, tmp_path):
        pc = _import_plugins_cmd()
        plugin_dir = tmp_path / "plugin"
        plugin_dir.mkdir()
        (plugin_dir / "config.yaml.example").write_text("new: value\n")
        (plugin_dir / "config.yaml").write_text("existing: value\n")

        from rich.console import Console
        console = Console(quiet=True)
        pc._copy_example_files(plugin_dir, console)

        # Existing file should be preserved
        assert (plugin_dir / "config.yaml").read_text() == "existing: value\n"
