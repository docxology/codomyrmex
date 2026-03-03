"""Obsidian vault search and filtering.

Full-text search with title-boosted scoring, regex search, plus tag,
frontmatter, date-based, and multi-criteria filters.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

from codomyrmex.agentic_memory.obsidian.models import Note, SearchResult

# ── full-text search ─────────────────────────────────────────────────


def search_vault(
    vault: Any,
    query: str,
    *,
    limit: int = 50,
    case_sensitive: bool = False,
    folder: str | None = None,
) -> list[SearchResult]:
    """Case-insensitive search across title, content, and tags with scoring.

    Parameters
    ----------
    limit : int
        Maximum number of results (default 50).
    case_sensitive : bool
        If ``True``, perform case-sensitive matching.
    folder : str | None
        Restrict search to notes within a specific folder.
    """
    if not query.strip():
        return []

    q = query if case_sensitive else query.lower()
    results: list[SearchResult] = []

    for rel, note in vault.notes.items():
        # Folder filter
        if folder and not rel.startswith(folder.rstrip("/") + "/"):
            continue

        score = 0.0
        match_type = "content"
        context = ""

        title = note.title if case_sensitive else note.title.lower()
        body = note.content if case_sensitive else note.content.lower()

        # Title match (boosted — highest priority)
        if q in title:
            score += 2.0
            match_type = "title"
            context = note.title

        # Content match
        if q in body:
            score += 1.0
            idx = body.find(q)
            start = max(0, idx - 40)
            end = min(len(note.content), idx + len(q) + 40)
            if match_type != "title":
                match_type = "content"
                context = note.content[start:end].strip()

        # Tag match
        for tag in note.tags:
            tag_name = tag.name if case_sensitive else tag.name.lower()
            if q in tag_name:
                score += 0.5
                if match_type not in ("title",):
                    match_type = "tag"

        # Frontmatter value match
        for _key, val in note.frontmatter.items():
            val_str = str(val) if case_sensitive else str(val).lower()
            if q in val_str:
                score += 0.3
                break

        if score > 0:
            results.append(SearchResult(
                note=note,
                score=score,
                match_type=match_type,
                context=context,
            ))

    results.sort(key=lambda r: r.score, reverse=True)
    return results[:limit]


# ── regex search ─────────────────────────────────────────────────────


def search_regex(
    vault: Any,
    pattern: str,
    *,
    limit: int = 50,
    flags: int = re.IGNORECASE,
) -> list[SearchResult]:
    """Search note content using a regular expression pattern.

    Parameters
    ----------
    pattern : str
        Regular expression pattern.
    limit : int
        Maximum number of results.
    flags : int
        Regex flags (default ``re.IGNORECASE``).
    """
    compiled = re.compile(pattern, flags)
    results: list[SearchResult] = []

    for _rel, note in vault.notes.items():
        match = compiled.search(note.content)
        if match:
            idx = match.start()
            start = max(0, idx - 40)
            end = min(len(note.content), match.end() + 40)
            results.append(SearchResult(
                note=note,
                score=1.0,
                match_type="content",
                context=note.content[start:end].strip(),
            ))
    return results[:limit]


# ── tag filter ───────────────────────────────────────────────────────


def filter_by_tag(
    vault: Any,
    tag: str,
    *,
    include_nested: bool = True,
) -> list[Note]:
    """Return notes containing the given tag.

    If *include_nested* is ``True``, ``#parent`` matches ``#parent/child``.
    A leading ``#`` on *tag* is stripped automatically.
    """
    tag = tag.lstrip("#")
    results: list[Note] = []
    for _rel, note in vault.notes.items():
        for t in note.tags:
            if include_nested:
                if t.name == tag or t.name.startswith(tag + "/"):
                    results.append(note)
                    break
            else:
                if t.name == tag:
                    results.append(note)
                    break
    return results


def filter_by_tags(
    vault: Any,
    tags: list[str],
    *,
    match_all: bool = True,
) -> list[Note]:
    """Return notes matching multiple tags.

    Parameters
    ----------
    tags : list[str]
        Tags to filter by (leading ``#`` stripped).
    match_all : bool
        If ``True`` (default), notes must contain ALL tags.
        If ``False``, notes matching ANY tag are included.
    """
    cleaned_tags = [t.lstrip("#") for t in tags]
    results: list[Note] = []

    for _rel, note in vault.notes.items():
        note_tag_names = {t.name for t in note.tags}
        if match_all:
            if all(t in note_tag_names for t in cleaned_tags):
                results.append(note)
        else:
            if any(t in note_tag_names for t in cleaned_tags):
                results.append(note)
    return results


# ── frontmatter filter ───────────────────────────────────────────────


def filter_by_frontmatter(
    vault: Any,
    key: str,
    value: Any = None,
) -> list[Note]:
    """Return notes whose frontmatter contains *key* (optionally with a matching *value*)."""
    results: list[Note] = []
    for _rel, note in vault.notes.items():
        if key in note.frontmatter:
            if value is None or note.frontmatter[key] == value:
                results.append(note)
    return results


def filter_by_frontmatter_exists(
    vault: Any,
    *keys: str,
) -> list[Note]:
    """Return notes that have ALL specified frontmatter keys."""
    results: list[Note] = []
    for _rel, note in vault.notes.items():
        if all(k in note.frontmatter for k in keys):
            results.append(note)
    return results


# ── date filter ──────────────────────────────────────────────────────


def filter_by_date(
    vault: Any,
    *,
    after: str | None = None,
    before: str | None = None,
    date_field: str = "created",
) -> list[Note]:
    """Return notes whose frontmatter *date_field* falls within the
    ``after``/``before`` range (ISO 8601 date strings)."""
    after_dt = datetime.fromisoformat(after).date() if after else None
    before_dt = datetime.fromisoformat(before).date() if before else None

    results: list[Note] = []
    for _rel, note in vault.notes.items():
        raw = note.frontmatter.get(date_field)
        if raw is None:
            continue
        if isinstance(raw, date):
            note_date = raw
        elif isinstance(raw, datetime):
            note_date = raw.date()
        elif isinstance(raw, str):
            try:
                note_date = datetime.fromisoformat(raw).date()
            except ValueError:
                continue
        else:
            continue

        if after_dt and note_date < after_dt:
            continue
        if before_dt and note_date > before_dt:
            continue
        results.append(note)

    return results


# ── link-based search ────────────────────────────────────────────────


def find_notes_linking_to(vault: Any, target: str) -> list[Note]:
    """Return notes that contain a wikilink to *target*."""
    results: list[Note] = []
    for _rel, note in vault.notes.items():
        for link in note.links:
            if link.target == target:
                results.append(note)
                break
    return results


def find_notes_with_embeds(vault: Any, target: str | None = None) -> list[Note]:
    """Return notes that embed files.

    If *target* is given, only return notes embedding that specific file.
    """
    results: list[Note] = []
    for _rel, note in vault.notes.items():
        if target:
            if any(e.target == target for e in note.embeds):
                results.append(note)
        else:
            if note.embeds:
                results.append(note)
    return results
