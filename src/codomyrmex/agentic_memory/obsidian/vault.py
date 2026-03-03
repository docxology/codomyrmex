"""Obsidian vault loader and navigator.

``ObsidianVault`` scans a directory tree for ``.md`` files, parses them
via :func:`parser.parse_note`, and caches the results.  Excludes
``.obsidian`` and other dot-directories.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from codomyrmex.agentic_memory.obsidian.models import Note, VaultMetadata
from codomyrmex.agentic_memory.obsidian.parser import (
    parse_note,
)
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class ObsidianVault:
    """Load and navigate an Obsidian vault directory."""

    def __init__(self, path: str | Path) -> None:
        """Initialize the vault from a directory path."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Vault path does not exist: {path}")
        if not path.is_dir():
            raise ValueError(f"Vault path is not a directory: {path}")
        self.path = path.resolve()
        self._notes: dict[str, Note] | None = None

    # ── notes cache ──────────────────────────────────────────────

    @property
    def notes(self) -> dict[str, Note]:
        """Lazy-loaded mapping ``relative_path → Note``.  Call :meth:`refresh`
        to invalidate."""
        if self._notes is None:
            self._notes = self._scan()
        return self._notes

    def refresh(self) -> None:
        """Re-scan the vault directory."""
        self._notes = self._scan()

    def _scan(self) -> dict[str, Note]:
        """Scan the vault for .md files, parse each, and return as dict."""
        result: dict[str, Note] = {}
        for md in sorted(self.path.rglob("*.md")):
            rel = str(md.relative_to(self.path))
            # Skip dot-directories (.obsidian, .trash, etc.)
            if any(part.startswith(".") for part in md.relative_to(self.path).parts):
                continue
            try:
                note = parse_note(md)
                result[rel] = note
            except Exception as e:
                logger.warning("Skipping unparseable vault file %s: %s", md, e)
                continue
        return result

    # ── lookup ───────────────────────────────────────────────────

    def get_note(self, name: str) -> Note | None:
        """Lookup by relative path, filename, or title (no extension)."""
        notes = self.notes
        # Exact relative path
        if name in notes:
            return notes[name]
        # Filename with .md
        if not name.endswith(".md"):
            name_md = name + ".md"
        else:
            name_md = name
            name = name[:-3]

        for rel, note in notes.items():
            if rel == name_md or rel.endswith("/" + name_md):
                return note
        # Match by title
        for note in notes.values():
            if note.title == name:
                return note
        # Match by alias
        for note in notes.values():
            if name in note.aliases:
                return note
        return None

    def has_note(self, name: str) -> bool:
        """Return ``True`` if a note matching *name* exists."""
        return self.get_note(name) is not None

    def list_notes(self, *, folder: str | None = None) -> list[str]:
        """Return relative paths to all notes, optionally within *folder*."""
        paths = list(self.notes.keys())
        if folder:
            folder = folder.rstrip("/") + "/"
            paths = [p for p in paths if p.startswith(folder)]
        return sorted(paths)

    def list_folders(self) -> list[str]:
        """Return all unique folder paths in the vault."""
        folders: set[str] = set()
        for rel in self.notes:
            parts = rel.rsplit("/", 1)
            if len(parts) == 2:
                folders.add(parts[0])
        return sorted(folders)

    def get_notes_by_tag(self, tag: str) -> list[Note]:
        """Return all notes containing the given tag."""
        tag = tag.lstrip("#")
        results: list[Note] = []
        for note in self.notes.values():
            for t in note.tags:
                if t.name == tag or t.name.startswith(tag + "/"):
                    results.append(note)
                    break
        return results

    # ── metadata ─────────────────────────────────────────────────

    @property
    def metadata(self) -> VaultMetadata:
        """Compute summary statistics for the vault."""
        total_links = sum(len(n.links) for n in self.notes.values())
        all_tags = self.get_all_tags()
        total_words = sum(n.word_count for n in self.notes.values())
        folders = self.list_folders()
        return VaultMetadata(
            note_count=len(self.notes),
            tag_count=len(all_tags),
            link_count=total_links,
            total_words=total_words,
            folder_count=len(folders),
        )

    def get_all_tags(self) -> set[str]:
        """Return the set of unique tag names across the vault."""
        tags: set[str] = set()
        for note in self.notes.values():
            for t in note.tags:
                tags.add(t.name)
        return tags

    # ── config ───────────────────────────────────────────────────

    def get_config(self) -> dict[str, Any]:
        """Read ``.obsidian/`` config files into a nested dict."""
        config: dict[str, Any] = {}
        obsidian_dir = self.path / ".obsidian"
        if obsidian_dir.is_dir():
            for json_file in obsidian_dir.glob("*.json"):
                try:
                    data = json.loads(json_file.read_text())
                    config[json_file.stem] = data
                except Exception as e:
                    logger.warning("Obsidian vault config read failed for %s: %s", json_file, str(e))
                    raise
        return config

    def get_daily_notes_config(self) -> dict[str, Any]:
        """Return daily-notes plugin configuration, if available."""
        config = self.get_config()
        return config.get("daily-notes", {})

    # ── magic methods ────────────────────────────────────────────

    def __repr__(self) -> str:
        return f"ObsidianVault({self.path!r})"

    def __len__(self) -> int:
        return len(self.notes)

    def __contains__(self, name: str) -> bool:
        return self.has_note(name)

    def __iter__(self):
        return iter(self.notes.values())
