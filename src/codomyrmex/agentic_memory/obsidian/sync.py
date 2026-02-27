"""Sync & Publish CLI commands.

Wraps ``obsidian sync:*`` and ``obsidian publish:*`` CLI commands
for managing Obsidian Sync and Publish services.
Supports on/off toggling, status, history, restore, deleted files,
and publish site/list/add/remove operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codomyrmex.agentic_memory.obsidian.cli import CLIResult, ObsidianCLI


@dataclass
class SyncStatus:
    """Overall sync status for a vault."""

    connected: bool = False
    vault_name: str = ""
    last_sync: str = ""
    pending_changes: int = 0
    raw: str = ""


@dataclass
class SyncHistoryEntry:
    """A single entry from the sync history."""

    file: str = ""
    action: str = ""
    timestamp: str = ""
    raw: str = ""


@dataclass
class PublishStatus:
    """Overall publish status for a vault."""

    site_url: str = ""
    published_count: int = 0
    pending_count: int = 0
    raw: str = ""


# ── Sync ─────────────────────────────────────────────────────────────


def sync_toggle(
    cli: ObsidianCLI,
    state: str | None = None,
    *,
    vault: str | None = None,
) -> CLIResult:
    """Toggle sync on/off or show current state.

    Maps to ``obsidian sync [on|off]``.
    """
    flags = [state] if state in ("on", "off") else []
    return cli.run("sync", vault=vault, flags=flags)


def sync_status(
    cli: ObsidianCLI,
    *,
    vault: str | None = None,
) -> SyncStatus:
    """Get the current sync status.

    Maps to ``obsidian sync:status``.
    """
    result = cli.run("sync:status", vault=vault)
    status = SyncStatus(raw=result.stdout)
    for line in result.lines:
        lower = line.lower()
        if "connected" in lower:
            status.connected = "true" in lower or "yes" in lower
        elif "vault" in lower and ":" in line:
            status.vault_name = line.split(":", 1)[1].strip()
        elif "last" in lower and "sync" in lower and ":" in line:
            status.last_sync = line.split(":", 1)[1].strip()
    return status


def sync_history(
    cli: ObsidianCLI,
    *,
    vault: str | None = None,
) -> list[SyncHistoryEntry]:
    """Get sync history.

    Maps to ``obsidian sync:history``.
    """
    result = cli.run("sync:history", vault=vault)
    entries: list[SyncHistoryEntry] = []
    for line in result.lines:
        parts = line.split("\t")
        entries.append(SyncHistoryEntry(
            file=parts[0].strip() if len(parts) > 0 else "",
            action=parts[1].strip() if len(parts) > 1 else "",
            timestamp=parts[2].strip() if len(parts) > 2 else "",
            raw=line,
        ))
    return entries


def sync_read(
    cli: ObsidianCLI,
    *,
    file: str | None = None,
    path: str | None = None,
    vault: str | None = None,
) -> str:
    """Read a file's synced version.

    Maps to ``obsidian sync:read [file=|path=]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    return cli.run("sync:read", vault=vault, params=params or None).stdout


def sync_restore(
    cli: ObsidianCLI,
    *,
    file: str | None = None,
    path: str | None = None,
    version: str | None = None,
    vault: str | None = None,
) -> CLIResult:
    """Restore a file to a previous sync version.

    Maps to ``obsidian sync:restore [file=|path=] [version=<id>]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    if version:
        params["version"] = version
    return cli.run("sync:restore", vault=vault, params=params or None)


def sync_open(
    cli: ObsidianCLI,
    *,
    file: str | None = None,
    path: str | None = None,
    vault: str | None = None,
) -> CLIResult:
    """Open sync history for a file in Obsidian.

    Maps to ``obsidian sync:open [file=|path=]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    return cli.run("sync:open", vault=vault, params=params or None)


def sync_deleted(
    cli: ObsidianCLI,
    *,
    vault: str | None = None,
) -> list[str]:
    """List deleted files tracked by sync.

    Maps to ``obsidian sync:deleted``.
    """
    result = cli.run("sync:deleted", vault=vault)
    return result.lines


# ── Publish ──────────────────────────────────────────────────────────


def publish_site(
    cli: ObsidianCLI,
    *,
    vault: str | None = None,
) -> CLIResult:
    """Get publish site information.

    Maps to ``obsidian publish:site``.
    """
    return cli.run("publish:site", vault=vault)


def publish_list(
    cli: ObsidianCLI,
    *,
    vault: str | None = None,
) -> list[str]:
    """List published files.

    Maps to ``obsidian publish:list``.
    """
    result = cli.run("publish:list", vault=vault)
    return result.lines


def publish_status(
    cli: ObsidianCLI,
    *,
    vault: str | None = None,
) -> PublishStatus:
    """Get publish status.

    Maps to ``obsidian publish:status``.
    """
    result = cli.run("publish:status", vault=vault)
    status = PublishStatus(raw=result.stdout)
    for line in result.lines:
        lower = line.lower()
        if "url" in lower and ":" in line:
            status.site_url = line.split(":", 1)[1].strip()
    return status


def publish_add(
    cli: ObsidianCLI,
    *,
    file: str | None = None,
    path: str | None = None,
    vault: str | None = None,
) -> CLIResult:
    """Add a file to publishing.

    Maps to ``obsidian publish:add [file=|path=]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    return cli.run("publish:add", vault=vault, params=params or None)


def publish_remove(
    cli: ObsidianCLI,
    *,
    file: str | None = None,
    path: str | None = None,
    vault: str | None = None,
) -> CLIResult:
    """Remove a file from publishing.

    Maps to ``obsidian publish:remove [file=|path=]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    return cli.run("publish:remove", vault=vault, params=params or None)


def publish_open(
    cli: ObsidianCLI,
    *,
    file: str | None = None,
    path: str | None = None,
    vault: str | None = None,
) -> CLIResult:
    """Open publish view for a file.

    Maps to ``obsidian publish:open [file=|path=]``.
    """
    from codomyrmex.agentic_memory.obsidian.cli import _file_or_path
    params = _file_or_path(file, path)
    return cli.run("publish:open", vault=vault, params=params or None)
