"""Plugin and theme management CLI commands.

Wraps ``obsidian plugins``, ``obsidian plugin:*``, ``obsidian themes``,
``obsidian theme:*``, ``obsidian snippets``, ``obsidian snippet:*`` commands.
Supports filter, format, and version listing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codomyrmex.agentic_memory.obsidian.cli import CLIResult, ObsidianCLI


@dataclass
class PluginInfo:
    """Metadata about an Obsidian plugin."""

    id: str
    name: str = ""
    enabled: bool = False
    version: str = ""
    raw: str = ""


@dataclass
class ThemeInfo:
    """Metadata about an Obsidian theme."""

    name: str
    version: str = ""
    active: bool = False
    raw: str = ""


@dataclass
class SnippetInfo:
    """Metadata about a CSS snippet."""

    name: str
    enabled: bool = False
    raw: str = ""


def _parse_plugins(lines: list[str], *, enabled: bool = False) -> list[PluginInfo]:
    """Parse plugin listing output into :class:`PluginInfo` objects."""
    plugins: list[PluginInfo] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split("\t")
        if len(parts) >= 2:
            plugins.append(PluginInfo(
                id=parts[0].strip(),
                name=parts[1].strip() if len(parts) > 1 else parts[0].strip(),
                version=parts[2].strip() if len(parts) > 2 else "",
                enabled=enabled,
                raw=line,
            ))
        else:
            plugins.append(PluginInfo(
                id=stripped, name=stripped, enabled=enabled, raw=line
            ))
    return plugins


# ── plugins ──────────────────────────────────────────────────────────


def list_plugins(
    cli: ObsidianCLI,
    *,
    filter: str | None = None,
    versions: bool = False,
    format: str | None = None,
    vault: str | None = None,
) -> list[PluginInfo]:
    """List installed plugins.

    Maps to ``obsidian plugins [filter=core|community] [versions] [format=...]``.
    """
    params: dict[str, str] = {}
    flags: list[str] = []
    if filter:
        params["filter"] = filter
    if format:
        params["format"] = format
    if versions:
        flags.append("versions")
    result = cli.run("plugins", vault=vault, params=params or None, flags=flags)
    return _parse_plugins(result.lines)


def list_enabled(
    cli: ObsidianCLI,
    *,
    filter: str | None = None,
    vault: str | None = None,
) -> list[PluginInfo]:
    """List enabled plugins.

    Maps to ``obsidian plugins:enabled [filter=core|community]``.
    """
    params: dict[str, str] = {}
    if filter:
        params["filter"] = filter
    result = cli.run("plugins:enabled", vault=vault, params=params or None)
    return _parse_plugins(result.lines, enabled=True)


def get_plugin_info(
    cli: ObsidianCLI,
    plugin_id: str,
    *,
    vault: str | None = None,
) -> CLIResult:
    """Get detailed info about a specific plugin.

    Maps to ``obsidian plugin id=<id>``.
    """
    return cli.run("plugin", vault=vault, params={"id": plugin_id})


def enable_plugin(
    cli: ObsidianCLI,
    plugin_id: str,
    *,
    filter: str | None = None,
    vault: str | None = None,
) -> CLIResult:
    """Enable a plugin by ID.

    Maps to ``obsidian plugin:enable id=<id> [filter=core|community]``.
    """
    params: dict[str, str] = {"id": plugin_id}
    if filter:
        params["filter"] = filter
    return cli.run("plugin:enable", vault=vault, params=params)


def disable_plugin(
    cli: ObsidianCLI,
    plugin_id: str,
    *,
    filter: str | None = None,
    vault: str | None = None,
) -> CLIResult:
    """Disable a plugin by ID.

    Maps to ``obsidian plugin:disable id=<id> [filter=core|community]``.
    """
    params: dict[str, str] = {"id": plugin_id}
    if filter:
        params["filter"] = filter
    return cli.run("plugin:disable", vault=vault, params=params)


def install_plugin(
    cli: ObsidianCLI,
    plugin_id: str,
    *,
    enable: bool = False,
    vault: str | None = None,
) -> CLIResult:
    """Install a community plugin by ID.

    Maps to ``obsidian plugin:install id=<id> [enable]``.
    """
    flags = ["enable"] if enable else []
    return cli.run(
        "plugin:install", vault=vault, params={"id": plugin_id}, flags=flags
    )


def uninstall_plugin(
    cli: ObsidianCLI,
    plugin_id: str,
    *,
    vault: str | None = None,
) -> CLIResult:
    """Uninstall a community plugin by ID.

    Maps to ``obsidian plugin:uninstall id=<id>``.
    """
    return cli.run("plugin:uninstall", vault=vault, params={"id": plugin_id})


def reload_plugin(
    cli: ObsidianCLI,
    plugin_id: str,
    *,
    vault: str | None = None,
) -> CLIResult:
    """Reload a plugin by ID (useful during development).

    Maps to ``obsidian plugin:reload id=<id>``.
    """
    return cli.run("plugin:reload", vault=vault, params={"id": plugin_id})


# ── themes ───────────────────────────────────────────────────────────


def list_themes(
    cli: ObsidianCLI,
    *,
    versions: bool = False,
    vault: str | None = None,
) -> list[str]:
    """List installed themes.

    Maps to ``obsidian themes [versions]``.
    """
    flags = ["versions"] if versions else []
    result = cli.run("themes", vault=vault, flags=flags)
    return result.lines


def get_theme_info(
    cli: ObsidianCLI,
    *,
    name: str | None = None,
    vault: str | None = None,
) -> CLIResult:
    """Get active theme info or info for a specific theme.

    Maps to ``obsidian theme [name=<name>]``.
    """
    params: dict[str, str] = {}
    if name:
        params["name"] = name
    return cli.run("theme", vault=vault, params=params or None)


def set_theme(
    cli: ObsidianCLI,
    name: str,
    *,
    vault: str | None = None,
) -> CLIResult:
    """Set the active theme.

    Maps to ``obsidian theme:set name=<name>``.
    """
    return cli.run("theme:set", vault=vault, params={"name": name})


def install_theme(
    cli: ObsidianCLI,
    name: str,
    *,
    enable: bool = False,
    vault: str | None = None,
) -> CLIResult:
    """Install a theme.

    Maps to ``obsidian theme:install name=<name> [enable]``.
    """
    flags = ["enable"] if enable else []
    return cli.run(
        "theme:install", vault=vault, params={"name": name}, flags=flags
    )


def uninstall_theme(
    cli: ObsidianCLI,
    name: str,
    *,
    vault: str | None = None,
) -> CLIResult:
    """Uninstall a theme.

    Maps to ``obsidian theme:uninstall name=<name>``.
    """
    return cli.run("theme:uninstall", vault=vault, params={"name": name})


# ── CSS snippets ─────────────────────────────────────────────────────


def list_snippets(
    cli: ObsidianCLI,
    *,
    vault: str | None = None,
) -> list[str]:
    """List CSS snippets.

    Maps to ``obsidian snippets``.
    """
    result = cli.run("snippets", vault=vault)
    return result.lines


def list_enabled_snippets(
    cli: ObsidianCLI,
    *,
    vault: str | None = None,
) -> list[str]:
    """List enabled CSS snippets.

    Maps to ``obsidian snippets:enabled``.
    """
    result = cli.run("snippets:enabled", vault=vault)
    return result.lines


def enable_snippet(
    cli: ObsidianCLI,
    name: str,
    *,
    vault: str | None = None,
) -> CLIResult:
    """Enable a CSS snippet.

    Maps to ``obsidian snippet:enable name=<name>``.
    """
    return cli.run("snippet:enable", vault=vault, params={"name": name})


def disable_snippet(
    cli: ObsidianCLI,
    name: str,
    *,
    vault: str | None = None,
) -> CLIResult:
    """Disable a CSS snippet.

    Maps to ``obsidian snippet:disable name=<name>``.
    """
    return cli.run("snippet:disable", vault=vault, params={"name": name})
