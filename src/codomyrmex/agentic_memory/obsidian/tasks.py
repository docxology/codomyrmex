"""Task CLI commands — list, filter, toggle, set status.

Wraps ``obsidian tasks`` and ``obsidian task`` CLI commands for managing
Obsidian checkbox tasks across a vault.  Supports output formats
(json, tsv, csv), status filtering, and the ref= shorthand.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codomyrmex.agentic_memory.obsidian.cli import CLIResult, ObsidianCLI


@dataclass
class TaskItem:
    """A single task extracted from CLI output."""

    text: str
    status: str  # " " (todo), "x" (done), or custom status char
    file: str = ""
    line: int = 0
    raw: str = ""

    @property
    def is_done(self) -> bool:
        """Return ``True`` if the task is completed."""
        return self.status.lower() == "x"

    @property
    def is_todo(self) -> bool:
        """Return ``True`` if the task is unchecked."""
        return self.status.strip() == ""


# ── parsing helpers ──────────────────────────────────────────────────

_TASK_LINE_RE = re.compile(
    r"^(?P<file>[^:]*):?(?P<line>\d+)?:?\s*"
    r"- \[(?P<status>.)\]\s+(?P<text>.*)$"
)


def _parse_tasks(lines: list[str]) -> list[TaskItem]:
    """Parse CLI task output lines into :class:`TaskItem` objects."""
    tasks: list[TaskItem] = []
    for line in lines:
        m = _TASK_LINE_RE.match(line)
        if m:
            tasks.append(TaskItem(
                text=m.group("text").strip(),
                status=m.group("status"),
                file=m.group("file") or "",
                line=int(m.group("line")) if m.group("line") else 0,
                raw=line,
            ))
        elif line.strip().startswith("- ["):
            # Simpler fallback format: just the checkbox
            status_match = re.match(r"- \[(.)\]\s+(.*)", line.strip())
            if status_match:
                tasks.append(TaskItem(
                    text=status_match.group(2).strip(),
                    status=status_match.group(1),
                    raw=line,
                ))
    return tasks


# ── public API ───────────────────────────────────────────────────────


def list_tasks(
    cli: ObsidianCLI,
    *,
    file: str | None = None,
    path: str | None = None,
    status: str | None = None,
    format: str | None = None,
    done: bool = False,
    todo: bool = False,
    daily: bool = False,
    active: bool = False,
    verbose: bool = False,
    total: bool = False,
    vault: str | None = None,
) -> list[TaskItem]:
    """List tasks across the vault with optional filters.

    Maps to ``obsidian tasks [file=|path=] [status="<char>"]
    [format=json|tsv|csv] [done] [todo] [daily] [active] [verbose] [total]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    flags: list[str] = []
    if status is not None:
        params["status"] = status
    if format:
        params["format"] = format
    if done:
        flags.append("done")
    if todo:
        flags.append("todo")
    if daily:
        flags.append("daily")
    if active:
        flags.append("active")
    if verbose:
        flags.append("verbose")
    if total:
        flags.append("total")

    result = cli.run("tasks", vault=vault, params=params or None, flags=flags)
    return _parse_tasks(result.lines)


def get_task(
    cli: ObsidianCLI,
    *,
    ref: str | None = None,
    file: str | None = None,
    path: str | None = None,
    line: int | None = None,
    daily: bool = False,
    vault: str | None = None,
) -> CLIResult:
    """Show a single task's details.

    Maps to ``obsidian task [ref=<path:line>] [file=|path=] [line=<n>] [daily]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    flags: list[str] = []
    if ref:
        params["ref"] = ref
    if line is not None:
        params["line"] = str(line)
    if daily:
        flags.append("daily")
    return cli.run("task", vault=vault, params=params or None, flags=flags)


def toggle_task(
    cli: ObsidianCLI,
    *,
    ref: str | None = None,
    file: str | None = None,
    path: str | None = None,
    line: int | None = None,
    daily: bool = False,
    vault: str | None = None,
) -> CLIResult:
    """Toggle a task's completion state.

    Maps to ``obsidian task [ref=|file=|path=] [line=<n>] toggle [daily]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    flags: list[str] = ["toggle"]
    if ref:
        params["ref"] = ref
    if line is not None:
        params["line"] = str(line)
    if daily:
        flags.append("daily")
    return cli.run("task", vault=vault, params=params or None, flags=flags)


def set_task_status(
    cli: ObsidianCLI,
    status: str,
    *,
    ref: str | None = None,
    file: str | None = None,
    path: str | None = None,
    line: int | None = None,
    daily: bool = False,
    vault: str | None = None,
) -> CLIResult:
    """Set a task to a specific status character.

    Maps to ``obsidian task [ref=|file=|path=] [line=<n>]
    status="<char>" [daily]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    params["status"] = status
    flags: list[str] = []
    if ref:
        params["ref"] = ref
    if line is not None:
        params["line"] = str(line)
    if daily:
        flags.append("daily")
    return cli.run("task", vault=vault, params=params or None, flags=flags)
