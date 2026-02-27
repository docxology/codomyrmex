"""Bookmark CLI commands.

Wraps ``obsidian bookmarks`` and ``obsidian bookmark`` commands for listing
and creating bookmarks of various types (file, folder, search, URL).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codomyrmex.agentic_memory.obsidian.cli import CLIResult, ObsidianCLI


@dataclass
class BookmarkItem:
    """A single bookmark entry."""

    title: str
    path: str = ""
    type: str = "file"  # file, folder, search, graph, url
    raw: str = ""


def _parse_bookmarks(lines: list[str]) -> list[BookmarkItem]:
    """Parse bookmark listing output."""
    bookmarks: list[BookmarkItem] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split("\t")
        if len(parts) >= 2:
            bookmarks.append(BookmarkItem(
                title=parts[0].strip(),
                path=parts[1].strip(),
                raw=line,
            ))
        else:
            bookmarks.append(BookmarkItem(
                title=stripped, path=stripped, raw=line
            ))
    return bookmarks


def list_bookmarks(
    cli: ObsidianCLI,
    *,
    total: bool = False,
    verbose: bool = False,
    format: str | None = None,
    vault: str | None = None,
) -> list[BookmarkItem]:
    """List all bookmarks in the vault.

    Maps to ``obsidian bookmarks [total] [verbose] [format=...]``.
    """
    params: dict[str, str] = {}
    flags: list[str] = []
    if format:
        params["format"] = format
    if total:
        flags.append("total")
    if verbose:
        flags.append("verbose")
    result = cli.run("bookmarks", vault=vault, params=params or None, flags=flags)
    return _parse_bookmarks(result.lines)


def bookmark_file(
    cli: ObsidianCLI,
    *,
    file: str | None = None,
    path: str | None = None,
    vault: str | None = None,
) -> CLIResult:
    """Bookmark a file.

    Maps to ``obsidian bookmark [file=|path=]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    return cli.run("bookmark", vault=vault, params=params or None)


def bookmark_folder(
    cli: ObsidianCLI,
    folder: str,
    *,
    vault: str | None = None,
) -> CLIResult:
    """Bookmark a folder.

    Maps to ``obsidian bookmark folder=<path>``.
    """
    return cli.run("bookmark", vault=vault, params={"folder": folder})


def bookmark_search(
    cli: ObsidianCLI,
    query: str,
    *,
    vault: str | None = None,
) -> CLIResult:
    """Bookmark a search query.

    Maps to ``obsidian bookmark search=<query>``.
    """
    return cli.run("bookmark", vault=vault, params={"search": query})


def bookmark_url(
    cli: ObsidianCLI,
    url: str,
    *,
    title: str | None = None,
    vault: str | None = None,
) -> CLIResult:
    """Bookmark a URL.

    Maps to ``obsidian bookmark url=<url> [title=<title>]``.
    """
    params: dict[str, str] = {"url": url}
    if title:
        params["title"] = title
    return cli.run("bookmark", vault=vault, params=params)
