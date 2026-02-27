"""Miscellaneous Obsidian CLI commands.

Wraps vault-wide informational and utility commands: ``commands``,
``command``, ``hotkeys``, ``hotkey``, ``diff``, ``history``,
``backlinks``, ``links``, ``unresolved``, ``orphans``, ``deadends``,
``outline``, ``wordcount``, ``random``, ``unique``, ``web``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codomyrmex.agentic_memory.obsidian.cli import CLIResult, ObsidianCLI


# ── result models ────────────────────────────────────────────────────


@dataclass
class DiffResult:
    """A diff output for a file."""

    file: str
    diff_text: str = ""
    has_changes: bool = False


@dataclass
class HistoryEntry:
    """A version-history entry for a file."""

    version: str = ""
    timestamp: str = ""
    size: str = ""
    raw: str = ""


@dataclass
class OutlineItem:
    """A heading/outline entry for a file."""

    level: int = 0
    text: str = ""
    raw: str = ""


@dataclass
class WordCount:
    """Word-count statistics for a file."""

    words: int = 0
    characters: int = 0
    sentences: int = 0
    paragraphs: int = 0
    raw: str = ""


# ── command palette ──────────────────────────────────────────────────


def list_commands(
    cli: ObsidianCLI,
    *,
    filter: str | None = None,
    vault: str | None = None,
) -> list[str]:
    """List all registered command IDs.

    Maps to ``obsidian commands [filter=<text>]``.
    """
    params: dict[str, str] = {}
    if filter:
        params["filter"] = filter
    result = cli.run("commands", vault=vault, params=params or None)
    return result.lines


def run_command(
    cli: ObsidianCLI,
    command_id: str,
    *,
    vault: str | None = None,
) -> CLIResult:
    """Execute a registered command by ID.

    Maps to ``obsidian command id=<id>``.
    """
    return cli.run("command", vault=vault, params={"id": command_id})


def list_hotkeys(
    cli: ObsidianCLI,
    *,
    vault: str | None = None,
) -> list[str]:
    """List all configured hotkeys.

    Maps to ``obsidian hotkeys``.
    """
    return cli.run("hotkeys", vault=vault).lines


def get_hotkey(
    cli: ObsidianCLI,
    command_id: str,
    *,
    vault: str | None = None,
) -> CLIResult:
    """Get the hotkey for a specific command.

    Maps to ``obsidian hotkey id=<id>``.
    """
    return cli.run("hotkey", vault=vault, params={"id": command_id})


# ── diff & history ───────────────────────────────────────────────────


def get_diff(
    cli: ObsidianCLI,
    *,
    file: str | None = None,
    path: str | None = None,
    from_version: int | None = None,
    to_version: int | None = None,
    filter: str | None = None,
    vault: str | None = None,
) -> DiffResult:
    """Get diff of changes for a file.

    Maps to ``obsidian diff [file=|path=] [from=<n>] [to=<n>]
    [filter=local|sync]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    if from_version is not None:
        params["from"] = str(from_version)
    if to_version is not None:
        params["to"] = str(to_version)
    if filter:
        params["filter"] = filter

    result = cli.run("diff", vault=vault, params=params or None)
    target = file or path or ""
    return DiffResult(
        file=target,
        diff_text=result.stdout,
        has_changes=bool(result.stdout.strip()),
    )


def get_history(
    cli: ObsidianCLI,
    *,
    file: str | None = None,
    path: str | None = None,
    vault: str | None = None,
) -> CLIResult:
    """Get version history overview for a file.

    Maps to ``obsidian history [file=|path=]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    return cli.run("history", vault=vault, params=params or None)


def list_history(
    cli: ObsidianCLI,
    *,
    file: str | None = None,
    path: str | None = None,
    vault: str | None = None,
) -> list[HistoryEntry]:
    """List version history entries for a file.

    Maps to ``obsidian history:list [file=|path=]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    result = cli.run("history:list", vault=vault, params=params or None)
    entries: list[HistoryEntry] = []
    for line in result.lines:
        parts = line.split("\t")
        entries.append(HistoryEntry(
            version=parts[0].strip() if len(parts) > 0 else "",
            timestamp=parts[1].strip() if len(parts) > 1 else "",
            size=parts[2].strip() if len(parts) > 2 else "",
            raw=line,
        ))
    return entries


def read_history(
    cli: ObsidianCLI,
    *,
    file: str | None = None,
    path: str | None = None,
    version: str | None = None,
    vault: str | None = None,
) -> str:
    """Read a specific version of a file from history.

    Maps to ``obsidian history:read [file=|path=] [version=<n>]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    if version:
        params["version"] = version
    return cli.run("history:read", vault=vault, params=params or None).stdout


def restore_history(
    cli: ObsidianCLI,
    *,
    file: str | None = None,
    path: str | None = None,
    version: str | None = None,
    vault: str | None = None,
) -> CLIResult:
    """Restore a file to a specific version from history.

    Maps to ``obsidian history:restore [file=|path=] [version=<n>]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    if version:
        params["version"] = version
    return cli.run("history:restore", vault=vault, params=params or None)


def open_history(
    cli: ObsidianCLI,
    *,
    file: str | None = None,
    path: str | None = None,
    vault: str | None = None,
) -> CLIResult:
    """Open file history view in Obsidian.

    Maps to ``obsidian history:open [file=|path=]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    return cli.run("history:open", vault=vault, params=params or None)


# ── links ────────────────────────────────────────────────────────────


def get_backlinks_cli(
    cli: ObsidianCLI,
    *,
    file: str | None = None,
    path: str | None = None,
    vault: str | None = None,
) -> list[str]:
    """Get backlinks to a file via CLI.

    Maps to ``obsidian backlinks [file=|path=]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    return cli.run("backlinks", vault=vault, params=params or None).lines


def get_links(
    cli: ObsidianCLI,
    *,
    file: str | None = None,
    path: str | None = None,
    vault: str | None = None,
) -> list[str]:
    """Get outgoing links from a file.

    Maps to ``obsidian links [file=|path=]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    return cli.run("links", vault=vault, params=params or None).lines


def get_unresolved(
    cli: ObsidianCLI,
    *,
    vault: str | None = None,
) -> list[str]:
    """List unresolved (broken) links in the vault.

    Maps to ``obsidian unresolved``.
    """
    return cli.run("unresolved", vault=vault).lines


def get_orphans(
    cli: ObsidianCLI,
    *,
    vault: str | None = None,
) -> list[str]:
    """List orphan notes (no incoming links).

    Maps to ``obsidian orphans``.
    """
    return cli.run("orphans", vault=vault).lines


def get_deadends(
    cli: ObsidianCLI,
    *,
    vault: str | None = None,
) -> list[str]:
    """List dead-end notes (no outgoing links).

    Maps to ``obsidian deadends``.
    """
    return cli.run("deadends", vault=vault).lines


# ── outline & word count ─────────────────────────────────────────────


def get_outline(
    cli: ObsidianCLI,
    *,
    file: str | None = None,
    path: str | None = None,
    vault: str | None = None,
) -> list[OutlineItem]:
    """Get the heading outline of a file.

    Maps to ``obsidian outline [file=|path=]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    result = cli.run("outline", vault=vault, params=params or None)
    items: list[OutlineItem] = []
    for line in result.lines:
        stripped = line.strip()
        level = 0
        text = stripped
        if stripped.startswith("#"):
            hashes = stripped.split(" ", 1)[0]
            level = len(hashes)
            text = stripped[level:].strip()
        elif stripped.startswith("\t") or stripped.startswith("  "):
            level = len(stripped) - len(stripped.lstrip())
            text = stripped.strip()
        items.append(OutlineItem(level=level, text=text, raw=line))
    return items


def get_wordcount(
    cli: ObsidianCLI,
    *,
    file: str | None = None,
    path: str | None = None,
    vault: str | None = None,
) -> WordCount:
    """Get word count statistics for a file.

    Maps to ``obsidian wordcount [file=|path=]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    result = cli.run("wordcount", vault=vault, params=params or None)
    wc = WordCount(raw=result.stdout)
    for line in result.lines:
        parts = line.split(":")
        if len(parts) == 2:
            label = parts[0].strip().lower()
            try:
                val = int(parts[1].strip().replace(",", ""))
            except ValueError:
                continue
            if "word" in label:
                wc.words = val
            elif "character" in label or "char" in label:
                wc.characters = val
            elif "sentence" in label:
                wc.sentences = val
            elif "paragraph" in label:
                wc.paragraphs = val
    return wc


# ── random, unique, web ─────────────────────────────────────────────


def open_random(
    cli: ObsidianCLI,
    *,
    vault: str | None = None,
) -> CLIResult:
    """Open a random note in Obsidian.

    Maps to ``obsidian random``.
    """
    return cli.run("random", vault=vault)


def read_random(
    cli: ObsidianCLI,
    *,
    vault: str | None = None,
) -> str:
    """Read the content of a random note.

    Maps to ``obsidian random:read``.
    """
    return cli.run("random:read", vault=vault).stdout


def generate_unique_id(
    cli: ObsidianCLI,
    *,
    vault: str | None = None,
) -> str:
    """Generate a unique note ID.

    Maps to ``obsidian unique``.
    """
    return cli.run("unique", vault=vault).text


def open_web(
    cli: ObsidianCLI,
    url: str,
    *,
    vault: str | None = None,
) -> CLIResult:
    """Open a URL in Obsidian's web view.

    Maps to ``obsidian web url=<url>``.
    """
    return cli.run("web", vault=vault, params={"url": url})


# ── app control ──────────────────────────────────────────────────────


def get_version(cli: ObsidianCLI) -> str:
    """Return the Obsidian version string."""
    return cli.version()


def reload_vault(cli: ObsidianCLI, *, vault: str | None = None) -> CLIResult:
    """Reload the vault."""
    return cli.reload(vault=vault)


def restart_app(cli: ObsidianCLI) -> CLIResult:
    """Restart the Obsidian application."""
    return cli.restart()
