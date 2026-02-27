"""Property CLI commands — aliases, property read/set/remove, tags.

Wraps ``obsidian aliases``, ``obsidian properties``, ``obsidian property:*``,
and ``obsidian tags`` CLI commands for reading and writing YAML frontmatter
properties.  Supports output formats (yaml, json, tsv) and sorting.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from codomyrmex.agentic_memory.obsidian.cli import CLIResult, ObsidianCLI


@dataclass
class PropertyValue:
    """A single property key-value pair from a note."""

    key: str
    value: str
    type: str = ""  # text, list, number, checkbox, date, datetime
    raw: str = ""


# ── aliases ──────────────────────────────────────────────────────────


def get_aliases(
    cli: ObsidianCLI,
    *,
    file: str | None = None,
    path: str | None = None,
    total: bool = False,
    verbose: bool = False,
    active: bool = False,
    vault: str | None = None,
) -> list[str]:
    """Return aliases for a note.

    Maps to ``obsidian aliases [file=|path=] [total] [verbose] [active]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    flags: list[str] = []
    if total:
        flags.append("total")
    if verbose:
        flags.append("verbose")
    if active:
        flags.append("active")
    result = cli.run("aliases", vault=vault, params=params or None, flags=flags)
    return result.lines


# ── properties ───────────────────────────────────────────────────────


def get_properties(
    cli: ObsidianCLI,
    *,
    file: str | None = None,
    path: str | None = None,
    name: str | None = None,
    sort: str | None = None,
    format: str | None = None,
    total: bool = False,
    counts: bool = False,
    active: bool = False,
    vault: str | None = None,
) -> list[PropertyValue]:
    """Return all properties (frontmatter keys) for a note or vault.

    Maps to ``obsidian properties [file=|path=] [name=<name>]
    [sort=count] [format=yaml|json|tsv] [total] [counts] [active]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    flags: list[str] = []
    if name:
        params["name"] = name
    if sort:
        params["sort"] = sort
    if format:
        params["format"] = format
    if total:
        flags.append("total")
    if counts:
        flags.append("counts")
    if active:
        flags.append("active")

    result = cli.run("properties", vault=vault, params=params or None, flags=flags)
    props: list[PropertyValue] = []
    for line in result.lines:
        if ":" in line:
            key, _, value = line.partition(":")
            props.append(PropertyValue(
                key=key.strip(), value=value.strip(), raw=line
            ))
        else:
            props.append(PropertyValue(key=line.strip(), value="", raw=line))
    return props


def read_property(
    cli: ObsidianCLI,
    name: str,
    *,
    file: str | None = None,
    path: str | None = None,
    vault: str | None = None,
) -> str:
    """Read a single property's value from a note.

    Maps to ``obsidian property:read name=<name> [file=|path=]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    params["name"] = name
    return cli.run("property:read", vault=vault, params=params).text


def set_property(
    cli: ObsidianCLI,
    name: str,
    value: str,
    *,
    type: str | None = None,
    file: str | None = None,
    path: str | None = None,
    vault: str | None = None,
) -> CLIResult:
    """Set a property on a note.

    Maps to ``obsidian property:set name=<name> value=<value>
    [type=text|list|number|checkbox|date|datetime] [file=|path=]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    params["name"] = name
    params["value"] = value
    if type:
        params["type"] = type
    return cli.run("property:set", vault=vault, params=params)


def remove_property(
    cli: ObsidianCLI,
    name: str,
    *,
    file: str | None = None,
    path: str | None = None,
    vault: str | None = None,
) -> CLIResult:
    """Remove a property from a note.

    Maps to ``obsidian property:remove name=<name> [file=|path=]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    params["name"] = name
    return cli.run("property:remove", vault=vault, params=params)


# ── tags ─────────────────────────────────────────────────────────────


def get_tags(
    cli: ObsidianCLI,
    *,
    counts: bool = False,
    vault: str | None = None,
) -> list[str]:
    """List all tags in the vault.

    Maps to ``obsidian tags [counts]``.
    """
    flags = ["counts"] if counts else []
    result = cli.run("tags", vault=vault, flags=flags)
    return result.lines
