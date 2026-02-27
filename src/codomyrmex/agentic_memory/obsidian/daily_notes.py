"""Daily notes CLI commands — open, read, append, prepend.

Wraps ``obsidian daily*`` CLI commands.  Supports the ``paneType``,
``inline``, and ``open`` parameters from the official CLI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codomyrmex.agentic_memory.obsidian.cli import CLIResult, ObsidianCLI


def open_daily(
    cli: ObsidianCLI,
    *,
    pane_type: str | None = None,
    vault: str | None = None,
) -> CLIResult:
    """Open today's daily note in Obsidian.

    Maps to ``obsidian daily [paneType=tab|split|window]``.
    """
    params: dict[str, str] = {}
    if pane_type:
        params["paneType"] = pane_type
    return cli.run("daily", vault=vault, params=params or None)


def get_daily_path(cli: ObsidianCLI, *, vault: str | None = None) -> str:
    """Return the file path of today's daily note (even if not yet created).

    Maps to ``obsidian daily:path``.
    """
    return cli.run("daily:path", vault=vault).text


def read_daily(cli: ObsidianCLI, *, vault: str | None = None) -> str:
    """Read the content of today's daily note.

    Maps to ``obsidian daily:read``.
    """
    return cli.run("daily:read", vault=vault).stdout


def append_daily(
    cli: ObsidianCLI,
    content: str,
    *,
    pane_type: str | None = None,
    inline: bool = False,
    open: bool = False,
    vault: str | None = None,
) -> CLIResult:
    """Append content to today's daily note.

    Maps to ``obsidian daily:append content=<text>
    [paneType=...] [inline] [open]``.
    """
    params: dict[str, str] = {"content": content}
    flags: list[str] = []
    if pane_type:
        params["paneType"] = pane_type
    if inline:
        flags.append("inline")
    if open:
        flags.append("open")
    return cli.run("daily:append", vault=vault, params=params, flags=flags)


def prepend_daily(
    cli: ObsidianCLI,
    content: str,
    *,
    pane_type: str | None = None,
    inline: bool = False,
    open: bool = False,
    vault: str | None = None,
) -> CLIResult:
    """Prepend content to today's daily note (after frontmatter).

    Maps to ``obsidian daily:prepend content=<text>
    [paneType=...] [inline] [open]``.
    """
    params: dict[str, str] = {"content": content}
    flags: list[str] = []
    if pane_type:
        params["paneType"] = pane_type
    if inline:
        flags.append("inline")
    if open:
        flags.append("open")
    return cli.run("daily:prepend", vault=vault, params=params, flags=flags)
