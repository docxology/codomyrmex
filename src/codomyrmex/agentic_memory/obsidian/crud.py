"""
Obsidian Note CRUD Operations.

Create, read, update, and delete notes within an Obsidian vault.
All operations validate paths to prevent directory traversal.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import Note
from .parser import parse_frontmatter, parse_note, serialize_note
from .vault import ObsidianVault


def _validate_path(vault: ObsidianVault, note_path: str) -> Path:
    """Validate that note_path resolves within the vault root.

    Raises:
        ValueError: If path would escape vault root (directory traversal).
    """
    # Normalize and resolve
    full_path = (vault.path / note_path).resolve()

    # Ensure it's within vault
    try:
        full_path.relative_to(vault.path)
    except ValueError:
        raise ValueError(
            f"Path '{note_path}' resolves outside vault root. "
            f"Possible directory traversal attempt."
        )

    return full_path


def create_note(
    vault: ObsidianVault,
    path: str,
    content: str = "",
    frontmatter: dict[str, Any] | None = None,
) -> Note:
    """Create a new note in the vault.

    Args:
        vault: The Obsidian vault.
        path: Relative path for the new note (e.g., "folder/note.md").
        content: Note body content.
        frontmatter: Optional YAML frontmatter dict.

    Returns:
        The created Note object.

    Raises:
        ValueError: If path is invalid or outside vault.
        FileExistsError: If note already exists.
    """
    if not path.endswith(".md"):
        path = path + ".md"

    full_path = _validate_path(vault, path)

    if full_path.exists():
        raise FileExistsError(f"Note already exists: {path}")

    # Build note content
    note = Note(
        path=Path(path),
        title=Path(path).stem,
        frontmatter=frontmatter or {},
        content=content,
    )

    raw = serialize_note(note)
    note.raw = raw

    # Create parent directories if needed
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(raw, encoding="utf-8")

    # Refresh vault cache
    vault.refresh()

    return note


def read_note(vault: ObsidianVault, path: str) -> Note:
    """Read and parse a note from the vault.

    Args:
        vault: The Obsidian vault.
        path: Relative path to the note.

    Returns:
        Parsed Note object.

    Raises:
        ValueError: If path is invalid.
        FileNotFoundError: If note doesn't exist.
    """
    if not path.endswith(".md"):
        path = path + ".md"

    full_path = _validate_path(vault, path)

    if not full_path.exists():
        raise FileNotFoundError(f"Note not found: {path}")

    return parse_note(full_path)


def update_note(
    vault: ObsidianVault,
    path: str,
    *,
    content: str | None = None,
    frontmatter: dict[str, Any] | None = None,
) -> Note:
    """Update a note's content and/or frontmatter.

    Args:
        vault: The Obsidian vault.
        path: Relative path to the note.
        content: New body content (None = keep existing).
        frontmatter: Dict to merge into existing frontmatter (None = keep existing).

    Returns:
        Updated Note object.

    Raises:
        ValueError: If path is invalid.
        FileNotFoundError: If note doesn't exist.
    """
    if not path.endswith(".md"):
        path = path + ".md"

    full_path = _validate_path(vault, path)

    if not full_path.exists():
        raise FileNotFoundError(f"Note not found: {path}")

    # Read existing
    existing = parse_note(full_path)

    # Update content
    if content is not None:
        existing.content = content

    # Merge frontmatter
    if frontmatter is not None:
        existing.frontmatter.update(frontmatter)

    # Serialize and write
    raw = serialize_note(existing)
    existing.raw = raw
    full_path.write_text(raw, encoding="utf-8")

    # Refresh vault cache
    vault.refresh()

    # Re-parse to get updated extractions
    return parse_note(full_path)


def delete_note(vault: ObsidianVault, path: str) -> bool:
    """Delete a note from the vault.

    Args:
        vault: The Obsidian vault.
        path: Relative path to the note.

    Returns:
        True if deleted, False if not found.

    Raises:
        ValueError: If path is invalid.
    """
    if not path.endswith(".md"):
        path = path + ".md"

    full_path = _validate_path(vault, path)

    if not full_path.exists():
        return False

    full_path.unlink()
    vault.refresh()
    return True


def get_frontmatter(vault: ObsidianVault, path: str) -> dict[str, Any]:
    """Get frontmatter dict for a note.

    Args:
        vault: The Obsidian vault.
        path: Relative path to the note.

    Returns:
        Frontmatter dictionary.
    """
    note = read_note(vault, path)
    return note.frontmatter


def set_frontmatter(
    vault: ObsidianVault, path: str, updates: dict[str, Any]
) -> Note:
    """Merge updates into existing frontmatter.

    Does not delete unmentioned keys — only adds or overwrites specified keys.

    Args:
        vault: The Obsidian vault.
        path: Relative path to the note.
        updates: Key-value pairs to merge into frontmatter.

    Returns:
        Updated Note object.
    """
    return update_note(vault, path, frontmatter=updates)


def rename_note(
    vault: ObsidianVault,
    old_path: str,
    new_path: str,
    update_links: bool = True,
) -> Note:
    """Rename a note and optionally update wikilinks across the vault.

    Args:
        vault: The Obsidian vault.
        old_path: Current relative path.
        new_path: New relative path.
        update_links: If True, update wikilinks in other notes.

    Returns:
        The renamed Note object at its new location.

    Raises:
        ValueError: If paths are invalid.
        FileNotFoundError: If source note doesn't exist.
        FileExistsError: If target already exists.
    """
    if not old_path.endswith(".md"):
        old_path = old_path + ".md"
    if not new_path.endswith(".md"):
        new_path = new_path + ".md"

    old_full = _validate_path(vault, old_path)
    new_full = _validate_path(vault, new_path)

    if not old_full.exists():
        raise FileNotFoundError(f"Source note not found: {old_path}")
    if new_full.exists():
        raise FileExistsError(f"Target already exists: {new_path}")

    # Create target directory if needed
    new_full.parent.mkdir(parents=True, exist_ok=True)

    # Read content before moving
    raw_content = old_full.read_text(encoding="utf-8")

    # Move file
    old_full.rename(new_full)

    # Update wikilinks in other notes
    if update_links:
        old_title = Path(old_path).stem
        new_title = Path(new_path).stem
        if old_title != new_title:
            for md_file in vault.path.rglob("*.md"):
                if md_file == new_full:
                    continue
                try:
                    text = md_file.read_text(encoding="utf-8")
                    # Replace [[old_title]] with [[new_title]] variants
                    updated = text.replace(
                        f"[[{old_title}]]", f"[[{new_title}]]"
                    )
                    updated = updated.replace(
                        f"[[{old_title}|", f"[[{new_title}|"
                    )
                    updated = updated.replace(
                        f"[[{old_title}#", f"[[{new_title}#"
                    )
                    if updated != text:
                        md_file.write_text(updated, encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue

    vault.refresh()
    return parse_note(new_full)
