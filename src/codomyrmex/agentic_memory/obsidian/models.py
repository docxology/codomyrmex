"""
Obsidian Vault Data Models.

Dataclasses representing Obsidian vault structures: notes, wikilinks,
embeds, callouts, tags, canvas elements, and search results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class WikiLink:
    """An Obsidian wikilink: [[target]], [[target|alias]], [[target#heading]]."""

    target: str
    alias: str | None = None
    heading: str | None = None
    is_embed: bool = False
    raw: str = ""


@dataclass
class Embed:
    """An Obsidian embed: ![[file]], ![[file|WxH]]."""

    target: str
    width: int | None = None
    height: int | None = None
    raw: str = ""


@dataclass
class Callout:
    """An Obsidian callout block: > [!type]+/- Title."""

    type: str
    title: str = ""
    content: str = ""
    foldable: bool = False
    default_open: bool = True


@dataclass
class Tag:
    """A tag from content (#tag) or frontmatter."""

    name: str
    source: str = "content"  # "content" or "frontmatter"


@dataclass
class Note:
    """A parsed Obsidian note with all extracted metadata."""

    path: Path
    title: str = ""
    frontmatter: dict[str, Any] = field(default_factory=dict)
    content: str = ""
    raw: str = ""
    links: list[WikiLink] = field(default_factory=list)
    embeds: list[Embed] = field(default_factory=list)
    tags: list[Tag] = field(default_factory=list)
    callouts: list[Callout] = field(default_factory=list)
    headings: list[tuple[int, str]] = field(default_factory=list)


@dataclass
class VaultMetadata:
    """Aggregate statistics for an Obsidian vault."""

    path: Path
    note_count: int = 0
    tag_count: int = 0
    link_count: int = 0
    broken_link_count: int = 0
    orphan_count: int = 0


@dataclass
class CanvasNode:
    """A node in an Obsidian JSON Canvas."""

    id: str
    type: str  # "text", "file", "link", "group"
    x: int = 0
    y: int = 0
    width: int = 250
    height: int = 140
    text: str | None = None
    file: str | None = None
    url: str | None = None
    label: str | None = None
    color: str | None = None


@dataclass
class CanvasEdge:
    """An edge in an Obsidian JSON Canvas."""

    id: str
    fromNode: str
    toNode: str
    fromSide: str | None = None
    toSide: str | None = None
    label: str | None = None
    color: str | None = None


@dataclass
class Canvas:
    """An Obsidian JSON Canvas (.canvas file)."""

    nodes: list[CanvasNode] = field(default_factory=list)
    edges: list[CanvasEdge] = field(default_factory=list)
    path: Path | None = None


@dataclass
class SearchResult:
    """A search result with relevance scoring and context."""

    note: Note
    score: float = 0.0
    context: str = ""
    match_type: str = "content"  # "content", "title", "tag", "frontmatter"
