"""Template CLI commands.

Wraps ``obsidian templates``, ``obsidian template:read``,
and ``obsidian template:insert`` commands.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codomyrmex.agentic_memory.obsidian.cli import CLIResult, ObsidianCLI


@dataclass
class TemplateInfo:
    """Metadata about a template file."""

    name: str
    path: str = ""
    raw: str = ""


def _parse_templates(lines: list[str]) -> list[TemplateInfo]:
    """Parse template listing output."""
    templates: list[TemplateInfo] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        name = stripped.rsplit("/", 1)[-1]
        if name.endswith(".md"):
            name = name[:-3]
        templates.append(TemplateInfo(name=name, path=stripped, raw=line))
    return templates


def list_templates(
    cli: ObsidianCLI,
    *,
    vault: str | None = None,
) -> list[TemplateInfo]:
    """List available templates.

    Maps to ``obsidian templates``.
    """
    result = cli.run("templates", vault=vault)
    return _parse_templates(result.lines)


def read_template(
    cli: ObsidianCLI,
    *,
    file: str | None = None,
    path: str | None = None,
    resolve: bool = False,
    vault: str | None = None,
) -> str:
    """Read a template's content, optionally with variables resolved.

    Maps to ``obsidian template:read [file=|path=] [resolve]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    flags = ["resolve"] if resolve else []
    return cli.run(
        "template:read", vault=vault, params=params or None, flags=flags
    ).stdout


def insert_template(
    cli: ObsidianCLI,
    template: str,
    *,
    file: str | None = None,
    path: str | None = None,
    vault: str | None = None,
) -> CLIResult:
    """Insert a template into a file.

    Maps to ``obsidian template:insert [template=<name>] [file=|path=]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    params["template"] = template
    return cli.run("template:insert", vault=vault, params=params)
