"""Workspace and tab management CLI commands.

Wraps ``obsidian workspace*``, ``obsidian workspaces``, ``obsidian tabs``,
``obsidian tab:open``, and ``obsidian recents`` commands.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codomyrmex.agentic_memory.obsidian.cli import CLIResult, ObsidianCLI


# ── workspaces ───────────────────────────────────────────────────────


def get_active_workspace(
    cli: ObsidianCLI,
    *,
    vault: str | None = None,
) -> CLIResult:
    """Get the active workspace.

    Maps to ``obsidian workspace``.
    """
    return cli.run("workspace", vault=vault)


def list_workspaces(
    cli: ObsidianCLI,
    *,
    vault: str | None = None,
) -> list[str]:
    """List all saved workspaces.

    Maps to ``obsidian workspaces``.
    """
    result = cli.run("workspaces", vault=vault)
    return result.lines


def save_workspace(
    cli: ObsidianCLI,
    name: str,
    *,
    vault: str | None = None,
) -> CLIResult:
    """Save the current layout as a workspace.

    Maps to ``obsidian workspace:save name=<name>``.
    """
    return cli.run("workspace:save", vault=vault, params={"name": name})


def load_workspace(
    cli: ObsidianCLI,
    name: str,
    *,
    vault: str | None = None,
) -> CLIResult:
    """Load a saved workspace by name.

    Maps to ``obsidian workspace:load name=<name>``.
    """
    return cli.run("workspace:load", vault=vault, params={"name": name})


def delete_workspace(
    cli: ObsidianCLI,
    name: str,
    *,
    vault: str | None = None,
) -> CLIResult:
    """Delete a saved workspace.

    Maps to ``obsidian workspace:delete name=<name>``.
    """
    return cli.run("workspace:delete", vault=vault, params={"name": name})


# ── tabs ─────────────────────────────────────────────────────────────


def list_tabs(
    cli: ObsidianCLI,
    *,
    vault: str | None = None,
) -> list[str]:
    """List open tabs.

    Maps to ``obsidian tabs``.
    """
    result = cli.run("tabs", vault=vault)
    return result.lines


def open_tab(
    cli: ObsidianCLI,
    *,
    file: str | None = None,
    path: str | None = None,
    vault: str | None = None,
) -> CLIResult:
    """Open a file in a new tab.

    Maps to ``obsidian tab:open [file=|path=]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    return cli.run("tab:open", vault=vault, params=params or None)


# ── recents ──────────────────────────────────────────────────────────


def list_recents(
    cli: ObsidianCLI,
    *,
    vault: str | None = None,
) -> list[str]:
    """List recently opened files.

    Maps to ``obsidian recents``.
    """
    result = cli.run("recents", vault=vault)
    return result.lines
