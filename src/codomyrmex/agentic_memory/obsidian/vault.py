"""Obsidian vault loader and navigator.

``ObsidianVault`` scans a directory tree for ``.md`` files, parses them
via :func:`parser.parse_note`, and caches the results.  Excludes
``.obsidian`` and other dot-directories.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

from codomyrmex.agentic_memory.obsidian.models import Note, VaultMetadata
from codomyrmex.agentic_memory.obsidian.parser import (
    parse_note,
)


class ObsidianVault:
    """Load and navigate an Obsidian vault directory."""

    def __init__(self, path: str | Path) -> None:
        """Execute   Init   operations natively."""
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
        """Execute  Scan operations natively."""
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
                logging.getLogger(__name__).warning("Skipping unparseable vault file %s: %s", md, e)
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
        return None

    # ── metadata ─────────────────────────────────────────────────

    @property
    def metadata(self) -> VaultMetadata:
        """Execute Metadata operations natively."""
        total_links = sum(len(n.links) for n in self.notes.values())
        all_tags = self.get_all_tags()
        return VaultMetadata(
            note_count=len(self.notes),
            tag_count=len(all_tags),
            link_count=total_links,
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
