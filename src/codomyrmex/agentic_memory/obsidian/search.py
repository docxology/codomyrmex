"""
Obsidian Vault Search and Filtering.

Full-text search, tag filtering, frontmatter queries, and date filtering
across vault notes.
"""

from __future__ import annotations

import re
from typing import Any

from .models import Note, SearchResult
from .vault import ObsidianVault


def search_vault(
    vault: ObsidianVault, query: str, limit: int = 20
) -> list[SearchResult]:
    """Case-insensitive full-text search across note content and titles.

    Scores results by match frequency and location (title matches score higher).

    Args:
        vault: The Obsidian vault.
        query: Search query string.
        limit: Maximum number of results to return.

    Returns:
        List of SearchResult sorted by relevance score (descending).
    """
    if not query.strip():
        return []

    pattern = re.compile(re.escape(query), re.IGNORECASE)
    results: list[SearchResult] = []

    for note in vault.notes.values():
        score = 0.0
        match_type = "content"
        context = ""

        # Title match (high weight)
        title_matches = len(pattern.findall(note.title))
        if title_matches > 0:
            score += title_matches * 10.0
            match_type = "title"
            context = note.title

        # Content match
        content_matches = list(pattern.finditer(note.content))
        if content_matches:
            score += len(content_matches) * 1.0
            if match_type != "title":
                match_type = "content"
            # Extract context snippet around first match
            first = content_matches[0]
            start = max(0, first.start() - 40)
            end = min(len(note.content), first.end() + 40)
            snippet = note.content[start:end].replace("\n", " ").strip()
            if not context:
                context = f"...{snippet}..."

        # Tag match
        for tag in note.tags:
            if pattern.search(tag.name):
                score += 5.0
                if match_type == "content" and score <= 5.0:
                    match_type = "tag"

        # Frontmatter match
        fm_str = str(note.frontmatter)
        fm_matches = len(pattern.findall(fm_str))
        if fm_matches > 0:
            score += fm_matches * 2.0
            if match_type == "content" and score <= 2.0:
                match_type = "frontmatter"

        if score > 0:
            results.append(
                SearchResult(
                    note=note,
                    score=score,
                    context=context,
                    match_type=match_type,
                )
            )

    # Sort by score descending
    results.sort(key=lambda r: r.score, reverse=True)
    return results[:limit]


def filter_by_tag(
    vault: ObsidianVault, tag: str, include_nested: bool = True
) -> list[Note]:
    """Filter notes by tag.

    Args:
        vault: The Obsidian vault.
        tag: Tag to filter by (without #).
        include_nested: If True, #parent matches #parent/child.

    Returns:
        List of matching notes.
    """
    tag = tag.lstrip("#")
    matching: list[Note] = []

    for note in vault.notes.values():
        for note_tag in note.tags:
            if include_nested:
                if note_tag.name == tag or note_tag.name.startswith(tag + "/"):
                    matching.append(note)
                    break
            else:
                if note_tag.name == tag:
                    matching.append(note)
                    break

    return matching


def filter_by_frontmatter(
    vault: ObsidianVault, key: str, value: Any = None
) -> list[Note]:
    """Filter notes by frontmatter key/value.

    Args:
        vault: The Obsidian vault.
        key: Frontmatter key to check.
        value: If None, checks for key existence. Otherwise checks equality.

    Returns:
        List of matching notes.
    """
    matching: list[Note] = []

    for note in vault.notes.values():
        if key in note.frontmatter:
            if value is None or note.frontmatter[key] == value:
                matching.append(note)

    return matching


def filter_by_date(
    vault: ObsidianVault,
    *,
    after: str | None = None,
    before: str | None = None,
    date_field: str = "created",
) -> list[Note]:
    """Filter notes by frontmatter date field.

    Args:
        vault: The Obsidian vault.
        after: Include notes after this date (YYYY-MM-DD format).
        before: Include notes before this date (YYYY-MM-DD format).
        date_field: Frontmatter key containing the date.

    Returns:
        List of matching notes.
    """
    matching: list[Note] = []

    for note in vault.notes.values():
        date_val = note.frontmatter.get(date_field)
        if date_val is None:
            continue

        date_str = str(date_val)[:10]  # Take first 10 chars (YYYY-MM-DD)

        if after and date_str < after:
            continue
        if before and date_str > before:
            continue

        matching.append(note)

    return matching
