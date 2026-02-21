"""Data models for the Obsidian integration layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Wikilink:
    """An Obsidian ``[[target]]``, ``[[target|alias]]``, or ``[[target#heading]]`` link."""

    target: str
    alias: str | None = None
    heading: str | None = None


@dataclass
class Embed:
    """An Obsidian embed (``![[file]]``) with optional dimensions."""

    target: str
    width: int | None = None
    height: int | None = None


@dataclass
class Tag:
    """A tag extracted from content (``#inline``) or YAML frontmatter."""

    name: str
    source: str = "content"  # "content" | "frontmatter"


@dataclass
class Callout:
    """An Obsidian callout block (``> [!type] title``)."""

    type: str
    title: str = ""
    content: str = ""
    foldable: bool = False
    default_open: bool = False


@dataclass
class Note:
    """Parsed representation of an Obsidian markdown note."""

    title: str
    path: Path | None = None
    frontmatter: dict[str, Any] = field(default_factory=dict)
    content: str = ""
    links: list[Wikilink] = field(default_factory=list)
    embeds: list[Embed] = field(default_factory=list)
    tags: list[Tag] = field(default_factory=list)
    headings: list[tuple[int, str]] = field(default_factory=list)
    callouts: list[Callout] = field(default_factory=list)


@dataclass
class SearchResult:
    """A search hit with scoring and match context."""

    note: Note
    score: float = 0.0
    match_type: str = "content"  # "title" | "content" | "tag"
    context: str = ""


@dataclass
class VaultMetadata:
    """Summary statistics for a vault."""

    note_count: int = 0
    tag_count: int = 0
    link_count: int = 0


# ── Canvas models ────────────────────────────────────────────────────

@dataclass
class CanvasNode:
    """JSON Canvas node."""

    id: str
    type: str  # "text" | "file" | "link" | "group"
    x: int = 0
    y: int = 0
    width: int = 250
    height: int = 140
    text: str | None = None
    file: str | None = None
    url: str | None = None
    color: str | None = None


@dataclass
class CanvasEdge:
    """JSON Canvas edge."""

    id: str
    fromNode: str = ""
    toNode: str = ""
    fromSide: str | None = None
    toSide: str | None = None
    label: str | None = None


@dataclass
class Canvas:
    """An Obsidian JSON Canvas document."""

    nodes: list[CanvasNode] = field(default_factory=list)
    edges: list[CanvasEdge] = field(default_factory=list)
    path: Path | None = None
