"""
Obsidian Vault Management.

Discovers, loads, and indexes Obsidian vaults from the filesystem.
Provides lazy note loading and vault metadata aggregation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Note, VaultMetadata
from .parser import parse_note


class ObsidianVault:
    """Represents a loaded Obsidian vault.

    Lazily loads and caches notes on first access. Provides
    note lookup by path or title, and aggregate metadata.
    """

    def __init__(self, path: str | Path) -> None:
        """Initialize vault from filesystem path.

        Args:
            path: Path to the Obsidian vault root directory.

        Raises:
            FileNotFoundError: If path doesn't exist.
            ValueError: If path is not a directory or contains no .md files.
        """
        self._path = Path(path).resolve()
        if not self._path.exists():
            raise FileNotFoundError(f"Vault path does not exist: {self._path}")
        if not self._path.is_dir():
            raise ValueError(f"Vault path is not a directory: {self._path}")

        self._notes: dict[str, Note] | None = None
        self._md_files: list[Path] | None = None

    @property
    def path(self) -> Path:
        """Vault root directory path."""
        return self._path

    def _discover_files(self) -> list[Path]:
        """Find all .md files in the vault, excluding .obsidian/ and .trash/."""
        if self._md_files is None:
            self._md_files = [
                f
                for f in self._path.rglob("*.md")
                if not any(
                    part.startswith(".")
                    for part in f.relative_to(self._path).parts[:-1]
                )
            ]
        return self._md_files

    def _load_notes(self) -> dict[str, Note]:
        """Parse all discovered .md files into Note objects."""
        if self._notes is None:
            self._notes = {}
            for md_file in self._discover_files():
                rel_path = str(md_file.relative_to(self._path))
                try:
                    note = parse_note(md_file)
                    # Store with relative path as key
                    note.path = Path(rel_path)
                    self._notes[rel_path] = note
                except Exception:
                    # Skip unparseable files
                    continue
        return self._notes

    @property
    def notes(self) -> dict[str, Note]:
        """All notes indexed by relative path within the vault."""
        return self._load_notes()

    def get_note(self, path: str) -> Note | None:
        """Get a single note by relative path or title.

        Args:
            path: Relative path (e.g., "folder/note.md") or note title.

        Returns:
            Note if found, None otherwise.
        """
        notes = self.notes

        # Direct path lookup
        if path in notes:
            return notes[path]

        # Try with .md extension
        if not path.endswith(".md"):
            path_md = path + ".md"
            if path_md in notes:
                return notes[path_md]

        # Title search
        for note in notes.values():
            if note.title == path:
                return note

        return None

    @property
    def metadata(self) -> VaultMetadata:
        """Aggregate vault statistics."""
        notes = self.notes
        all_tags: set[str] = set()
        total_links = 0
        broken_links = 0
        linked_notes: set[str] = set()
        linking_notes: set[str] = set()

        note_names = {n.title for n in notes.values()}

        for note in notes.values():
            for tag in note.tags:
                all_tags.add(tag.name)
            total_links += len(note.links)
            if note.links:
                linking_notes.add(str(note.path))
            for link in note.links:
                if link.target in note_names:
                    linked_notes.add(link.target)
                else:
                    # Check if target matches a relative path
                    target_md = link.target + ".md" if not link.target.endswith(".md") else link.target
                    if target_md not in notes and link.target not in notes:
                        broken_links += 1

        # Orphans: notes with no inbound AND no outbound links
        all_paths = set(notes.keys())
        connected = linking_notes | {
            str(n.path) for n in notes.values() if n.title in linked_notes
        }
        orphan_count = len(all_paths - connected)

        return VaultMetadata(
            path=self._path,
            note_count=len(notes),
            tag_count=len(all_tags),
            link_count=total_links,
            broken_link_count=broken_links,
            orphan_count=orphan_count,
        )

    def refresh(self) -> None:
        """Clear caches and re-scan vault for changes."""
        self._notes = None
        self._md_files = None

    def get_config(self) -> dict[str, Any]:
        """Read .obsidian/ config files (read-only).

        Returns:
            Dict with app and appearance config, or empty dicts if not found.
        """
        config: dict[str, Any] = {}
        obsidian_dir = self._path / ".obsidian"

        for config_name in ("app.json", "appearance.json"):
            config_file = obsidian_dir / config_name
            if config_file.exists():
                try:
                    config[config_name.replace(".json", "")] = json.loads(
                        config_file.read_text(encoding="utf-8")
                    )
                except (json.JSONDecodeError, OSError):
                    config[config_name.replace(".json", "")] = {}

        return config

    def get_all_tags(self) -> dict[str, int]:
        """Get all tags with their occurrence counts.

        Returns:
            Dict mapping tag name to count across all notes.
        """
        tag_counts: dict[str, int] = {}
        for note in self.notes.values():
            for tag in note.tags:
                tag_counts[tag.name] = tag_counts.get(tag.name, 0) + 1
        return tag_counts

    def get_canvas_files(self) -> list[Path]:
        """Find all .canvas files in the vault."""
        return [
            f
            for f in self._path.rglob("*.canvas")
            if not any(
                part.startswith(".")
                for part in f.relative_to(self._path).parts[:-1]
            )
        ]
