"""Obsidian vault search and filtering.

Full-text search with title-boosted scoring, plus tag, frontmatter,
and date-based filters.
"""

from __future__ import annotations

from datetime import datetime, date
from typing import Any

from codomyrmex.agentic_memory.obsidian.models import Note, SearchResult
from codomyrmex.agentic_memory.obsidian.parser import extract_tags


# ── full-text search ─────────────────────────────────────────────────


def search_vault(
    vault: Any,
    query: str,
    *,
    limit: int = 50,
) -> list[SearchResult]:
    """Case-insensitive search across title and content with scoring."""
    if not query.strip():
        return []

    q = query.lower()
    results: list[SearchResult] = []

    for _rel, note in vault.notes.items():
        score = 0.0
        match_type = "content"
        context = ""

        # Title match (boosted — highest priority)
        if q in note.title.lower():
            score += 2.0
            match_type = "title"
            context = note.title

        # Content match
        body_lower = note.content.lower()
        if q in body_lower:
            score += 1.0
            idx = body_lower.find(q)
            start = max(0, idx - 40)
            end = min(len(note.content), idx + len(q) + 40)
            if match_type != "title":
                match_type = "content"
                context = note.content[start:end].strip()

        # Tag match
        for tag in note.tags:
            if q in tag.name.lower():
                score += 0.5
                if match_type not in ("title",):
                    match_type = "tag"

        if score > 0:
            results.append(SearchResult(
                note=note,
                score=score,
                match_type=match_type,
                context=context,
            ))

    results.sort(key=lambda r: r.score, reverse=True)
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
