"""Obsidian note CRUD — create, read, update, delete, rename.

All operations use the filesystem directly via ``ObsidianVault``.
Path traversal is blocked.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from codomyrmex.agentic_memory.obsidian.models import Note
from codomyrmex.agentic_memory.obsidian.parser import (
    parse_frontmatter,
    parse_note,
    serialize_note,
)

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


def _resolve_path(vault_path: Path, name: str) -> Path:
    """Resolve *name* inside the vault, blocking traversal."""
    if ".." in name:
        raise ValueError(f"Path traversal blocked: {name}")
    if not name.endswith(".md"):
        name = name + ".md"
    return vault_path / name


# ── create ───────────────────────────────────────────────────────────


def create_note(
    vault: Any,
    name: str,
    *,
    content: str = "",
    frontmatter: dict[str, Any] | None = None,
) -> Note:
    """Create a new note file in the vault."""
    path = _resolve_path(vault.path, name)
    if path.exists():
        raise FileExistsError(f"Note already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)

    parts: list[str] = []
    if frontmatter:
        if yaml is not None:
            fm_str = yaml.dump(frontmatter, default_flow_style=False).strip()
        else:
            fm_str = "\n".join(f"{k}: {v}" for k, v in frontmatter.items())
        parts.append(f"---\n{fm_str}\n---\n")
    parts.append(content)
    path.write_text("".join(parts))

    note = parse_note(path)
    vault.refresh()
    return note


# ── read ─────────────────────────────────────────────────────────────


def read_note(vault: Any, name: str) -> Note:
    """Read and parse an existing note."""
    path = _resolve_path(vault.path, name)
    if not path.exists():
        raise FileNotFoundError(f"Note not found: {path}")
    return parse_note(path)


# ── update ───────────────────────────────────────────────────────────


def update_note(
    vault: Any,
    name: str,
    *,
    content: str | None = None,
    frontmatter: dict[str, Any] | None = None,
) -> Note:
    """Update an existing note's content and/or frontmatter."""
    path = _resolve_path(vault.path, name)
    if not path.exists():
        raise FileNotFoundError(f"Note not found: {path}")

    note = parse_note(path)
    if content is not None:
        note.content = content
    if frontmatter is not None:
        note.frontmatter.update(frontmatter)

    path.write_text(serialize_note(note))
    vault.refresh()
    return parse_note(path)


# ── delete ───────────────────────────────────────────────────────────


def delete_note(vault: Any, name: str) -> bool:
    """Delete a note. Returns ``True`` if it existed."""
    if ".." in name:
        raise ValueError(f"Path traversal blocked: {name}")
    path = _resolve_path(vault.path, name)
    if not path.exists():
        return False
    path.unlink()
    vault.refresh()
    return True


# ── frontmatter ──────────────────────────────────────────────────────


def get_frontmatter(vault: Any, name: str) -> dict[str, Any]:
    """Return frontmatter from a note."""
    note = read_note(vault, name)
    return note.frontmatter


def set_frontmatter(
    vault: Any,
    name: str,
    updates: dict[str, Any],
) -> Note:
    """Merge *updates* into the note's frontmatter (preserves existing keys)."""
    return update_note(vault, name, frontmatter=updates)


# ── rename ───────────────────────────────────────────────────────────


def rename_note(vault: Any, old_name: str, new_name: str) -> Note:
    """Rename a note and update wikilinks across the vault."""
    old_path = _resolve_path(vault.path, old_name)
    if not old_path.exists():
        raise FileNotFoundError(f"Note not found: {old_path}")
    new_path = _resolve_path(vault.path, new_name)
    if new_path.exists():
        raise FileExistsError(f"Target already exists: {new_path}")

    old_title = old_path.stem
    new_title = new_path.stem

    # Move the file
    new_path.parent.mkdir(parents=True, exist_ok=True)
    old_path.rename(new_path)

    # Update wikilinks in other notes
    for md in vault.path.rglob("*.md"):
        if md == new_path:
            continue
        if any(part.startswith(".") for part in md.relative_to(vault.path).parts):
            continue
        text = md.read_text()
        updated = text.replace(f"[[{old_title}]]", f"[[{new_title}]]")
        updated = updated.replace(f"[[{old_title}|", f"[[{new_title}|")
        updated = updated.replace(f"[[{old_title}#", f"[[{new_title}#")
        if updated != text:
            md.write_text(updated)

    vault.refresh()
    return parse_note(new_path)
