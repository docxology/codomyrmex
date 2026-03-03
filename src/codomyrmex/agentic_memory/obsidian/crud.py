"""Obsidian note CRUD — create, read, update, delete, rename, append, prepend, move.

All operations use the filesystem directly via ``ObsidianVault``.
Path traversal is blocked.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from codomyrmex.agentic_memory.obsidian.models import Note
from codomyrmex.agentic_memory.obsidian.parser import (
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
    overwrite: bool = False,
    template: str | None = None,
) -> Note:
    """Create a new note file in the vault.

    Parameters
    ----------
    vault : ObsidianVault
        The vault instance.
    name : str
        Note name or path (relative to vault root).
    content : str
        Body text for the note.
    frontmatter : dict | None
        YAML frontmatter key-value pairs.
    overwrite : bool
        If ``True``, replace an existing note.
    template : str | None
        If given, read the template file and use its content as a base.
    """
    path = _resolve_path(vault.path, name)
    if path.exists() and not overwrite:
        raise FileExistsError(f"Note already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)

    # Template support
    if template:
        template_path = _resolve_path(vault.path, template)
        if template_path.exists():
            template_content = template_path.read_text()
            if not content:
                content = template_content

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


def read_note_raw(vault: Any, name: str) -> str:
    """Read the raw text of an existing note (no parsing)."""
    path = _resolve_path(vault.path, name)
    if not path.exists():
        raise FileNotFoundError(f"Note not found: {path}")
    return path.read_text()


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


# ── append / prepend ─────────────────────────────────────────────────


def append_note(
    vault: Any,
    name: str,
    content: str,
    *,
    newline: bool = True,
) -> Note:
    """Append text to the end of an existing note.

    Parameters
    ----------
    newline : bool
        If ``True``, prepend a newline before the appended content if
        the file doesn't already end with one.
    """
    path = _resolve_path(vault.path, name)
    if not path.exists():
        raise FileNotFoundError(f"Note not found: {path}")

    existing = path.read_text()
    separator = "\n" if newline and existing and not existing.endswith("\n") else ""
    path.write_text(existing + separator + content)
    vault.refresh()
    return parse_note(path)


def prepend_note(
    vault: Any,
    name: str,
    content: str,
    *,
    after_frontmatter: bool = True,
) -> Note:
    """Prepend text to a note.

    Parameters
    ----------
    after_frontmatter : bool
        If ``True`` (default), insert after any YAML frontmatter block.
        If ``False``, insert at the very start of the file.
    """
    path = _resolve_path(vault.path, name)
    if not path.exists():
        raise FileNotFoundError(f"Note not found: {path}")

    existing = path.read_text()
    if after_frontmatter and existing.startswith("---\n"):
        # Find the end of frontmatter
        end_idx = existing.find("\n---\n", 4)
        if end_idx >= 0:
            fm_end = end_idx + 5  # After the closing ---\n
            path.write_text(existing[:fm_end] + content + "\n" + existing[fm_end:])
        else:
            path.write_text(content + "\n" + existing)
    else:
        path.write_text(content + "\n" + existing)

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


def remove_frontmatter_key(vault: Any, name: str, key: str) -> Note:
    """Remove a single key from the note's frontmatter."""
    path = _resolve_path(vault.path, name)
    if not path.exists():
        raise FileNotFoundError(f"Note not found: {path}")

    note = parse_note(path)
    note.frontmatter.pop(key, None)
    path.write_text(serialize_note(note))
    vault.refresh()
    return parse_note(path)


# ── rename / move ────────────────────────────────────────────────────


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
    _update_links_across_vault(vault, old_title, new_title, exclude=new_path)

    vault.refresh()
    return parse_note(new_path)


def move_note(vault: Any, name: str, *, to: str) -> Note:
    """Move a note to a new folder path, updating all wikilinks.

    Parameters
    ----------
    to : str
        Target path (folder/name.md or just folder/).
    """
    old_path = _resolve_path(vault.path, name)
    if not old_path.exists():
        raise FileNotFoundError(f"Note not found: {old_path}")

    # If 'to' is a folder path (ends with /), preserve the filename
    if to.endswith("/"):
        to = to + old_path.name
    elif not to.endswith(".md"):
        to = to + ".md"

    new_path = _resolve_path(vault.path, to)
    if new_path.exists():
        raise FileExistsError(f"Target already exists: {new_path}")

    old_title = old_path.stem
    new_title = new_path.stem

    new_path.parent.mkdir(parents=True, exist_ok=True)
    old_path.rename(new_path)

    if old_title != new_title:
        _update_links_across_vault(vault, old_title, new_title, exclude=new_path)

    vault.refresh()
    return parse_note(new_path)


# ── helpers ──────────────────────────────────────────────────────────


def _update_links_across_vault(
    vault: Any,
    old_title: str,
    new_title: str,
    *,
    exclude: Path | None = None,
) -> int:
    """Replace wikilinks pointing to old_title with new_title.

    Returns the number of files modified.
    """
    modified = 0
    for md in vault.path.rglob("*.md"):
        if exclude and md == exclude:
            continue
        if any(part.startswith(".") for part in md.relative_to(vault.path).parts):
            continue
        text = md.read_text()
        updated = text.replace(f"[[{old_title}]]", f"[[{new_title}]]")
        updated = updated.replace(f"[[{old_title}|", f"[[{new_title}|")
        updated = updated.replace(f"[[{old_title}#", f"[[{new_title}#")
        if updated != text:
            md.write_text(updated)
            modified += 1
    return modified
