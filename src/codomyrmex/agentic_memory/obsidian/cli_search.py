"""Search CLI commands — search, search:context, search:open.

Extends the filesystem-based search in this module with CLI-backed
search that uses Obsidian's full search engine including index and
ranking.  Supports limit, format, case sensitivity, path scoping.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codomyrmex.agentic_memory.obsidian.cli import CLIResult, ObsidianCLI


def cli_search(
    cli: ObsidianCLI,
    query: str,
    *,
    path: str | None = None,
    limit: int | None = None,
    format: str | None = None,
    total: bool = False,
    case: bool = False,
    vault: str | None = None,
) -> list[str]:
    """Search the vault via CLI, returning matching file paths.

    Maps to ``obsidian search query=<text> [path=<folder>]
    [limit=<n>] [format=text|json] [total] [case]``.

    Parameters
    ----------
    query : str
        The search query string.
    path : str | None
        Restrict search to a folder.
    limit : int | None
        Maximum number of results.
    format : str | None
        Output format: ``"text"`` or ``"json"``.
    total : bool
        Show total count only.
    case : bool
        Case-sensitive search.
    vault : str | None
        Override the default vault.
    """
    params: dict[str, str] = {"query": query}
    flags: list[str] = []
    if path:
        params["path"] = path
    if limit is not None:
        params["limit"] = str(limit)
    if format:
        params["format"] = format
    if total:
        flags.append("total")
    if case:
        flags.append("case")

    result = cli.run("search", vault=vault, params=params, flags=flags)
    return result.lines


def cli_search_context(
    cli: ObsidianCLI,
    query: str,
    *,
    path: str | None = None,
    limit: int | None = None,
    case: bool = False,
    vault: str | None = None,
) -> list[str]:
    """Search with context (grep-style output).

    Maps to ``obsidian search:context query=<text> [path=] [limit=] [case]``.
    """
    params: dict[str, str] = {"query": query}
    flags: list[str] = []
    if path:
        params["path"] = path
    if limit is not None:
        params["limit"] = str(limit)
    if case:
        flags.append("case")

    result = cli.run("search:context", vault=vault, params=params, flags=flags)
    return result.lines


def cli_search_open(
    cli: ObsidianCLI,
    query: str | None = None,
    *,
    vault: str | None = None,
) -> CLIResult:
    """Open the search view in Obsidian, optionally with a query.

    Maps to ``obsidian search:open [query=<text>]``.
    """
    params: dict[str, str] = {}
    if query:
        params["query"] = query
    return cli.run("search:open", vault=vault, params=params or None)
