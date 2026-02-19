"""
Obsidian Markdown Parser.

Parses Obsidian-flavored markdown including frontmatter, wikilinks,
embeds, callouts, tags, and headings. Supports round-trip serialization.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .models import Callout, Embed, Note, Tag, WikiLink

# --- Regex patterns ---

# Wikilinks: [[target]], [[target|alias]], [[target#heading]], [[target#^block]]
_WIKILINK_RE = re.compile(
    r"(?<!!)\[\[([^\]|#]+?)(?:#([^\]|]*?))?(?:\|([^\]]*?))?\]\]"
)

# Embeds: ![[file]], ![[file|W]], ![[file|WxH]]
_EMBED_RE = re.compile(
    r"!\[\[([^\]|]+?)(?:\|(\d+)(?:x(\d+))?)?\]\]"
)

# Inline tags: #tag, #parent/child (not inside code blocks or URLs)
_TAG_RE = re.compile(r"(?<!\w)#([\w][\w/\-]*(?:/[\w\-]+)*)")

# Headings: # through ######
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)(?:\s+#*)?$", re.MULTILINE)

# Callout header: > [!type]+/- Title
_CALLOUT_HEADER_RE = re.compile(
    r"^>\s*\[!(\w+)\]([+-])?\s*(.*?)$", re.MULTILINE
)

# Frontmatter delimiters
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
_FRONTMATTER_EMPTY_RE = re.compile(r"^---\s*\n---\s*\n?", re.DOTALL)


def parse_frontmatter(raw: str) -> tuple[dict[str, Any], str]:
    """Split raw markdown into (frontmatter_dict, body_content).

    Uses PyYAML for parsing. Falls back to empty dict if no frontmatter found.
    """
    # Check for empty frontmatter first (---\n---\n)
    empty_match = _FRONTMATTER_EMPTY_RE.match(raw)
    if empty_match:
        # Check if this is truly empty (no content between delimiters)
        match = _FRONTMATTER_RE.match(raw)
        if not match:
            return {}, raw[empty_match.end():]

    match = _FRONTMATTER_RE.match(raw)
    if not match:
        return {}, raw

    yaml_str = match.group(1)
    body = raw[match.end():]

    try:
        fm = yaml.safe_load(yaml_str)
        if not isinstance(fm, dict):
            fm = {}
    except yaml.YAMLError:
        fm = {}

    return fm, body


def extract_wikilinks(content: str) -> list[WikiLink]:
    """Extract wikilinks from markdown content.

    Handles: [[target]], [[target|alias]], [[target#heading]], [[target#^block]].
    Skips embeds (handled by extract_embeds).
    """
    results = []
    for match in _WIKILINK_RE.finditer(content):
        target = match.group(1).strip()
        heading = match.group(2)
        alias = match.group(3)
        if heading is not None:
            heading = heading.strip() or None
        if alias is not None:
            alias = alias.strip() or None
        results.append(
            WikiLink(
                target=target,
                alias=alias,
                heading=heading,
                is_embed=False,
                raw=match.group(0),
            )
        )
    return results


def extract_embeds(content: str) -> list[Embed]:
    """Extract embeds from markdown content.

    Handles: ![[file]], ![[file|W]], ![[file|WxH]].
    """
    results = []
    for match in _EMBED_RE.finditer(content):
        target = match.group(1).strip()
        width_str = match.group(2)
        height_str = match.group(3)
        width = int(width_str) if width_str else None
        height = int(height_str) if height_str else None
        results.append(
            Embed(
                target=target,
                width=width,
                height=height,
                raw=match.group(0),
            )
        )
    return results


def extract_tags(content: str, frontmatter: dict[str, Any] | None = None) -> list[Tag]:
    """Extract tags from content and frontmatter.

    Content tags: #tag, #parent/child
    Frontmatter tags: from 'tags' key (list of strings).
    """
    tags: list[Tag] = []

    # Content tags
    for match in _TAG_RE.finditer(content):
        tag_name = match.group(1)
        tags.append(Tag(name=tag_name, source="content"))

    # Frontmatter tags
    if frontmatter:
        fm_tags = frontmatter.get("tags", [])
        if isinstance(fm_tags, list):
            for t in fm_tags:
                if isinstance(t, str):
                    tags.append(Tag(name=t, source="frontmatter"))
        elif isinstance(fm_tags, str):
            # Handle comma-separated or single tag
            for t in fm_tags.split(","):
                t = t.strip().lstrip("#")
                if t:
                    tags.append(Tag(name=t, source="frontmatter"))

    return tags


def extract_callouts(content: str) -> list[Callout]:
    """Extract callout blocks from markdown content.

    Handles: > [!type] Title, > [!type]+ Title (foldable open),
    > [!type]- Title (foldable closed).
    """
    callouts: list[Callout] = []
    lines = content.split("\n")
    i = 0

    while i < len(lines):
        header_match = _CALLOUT_HEADER_RE.match(lines[i])
        if header_match:
            callout_type = header_match.group(1).lower()
            fold_char = header_match.group(2)
            title = header_match.group(3).strip()

            foldable = fold_char is not None
            default_open = fold_char != "-"

            # Collect callout body lines
            body_lines: list[str] = []
            i += 1
            while i < len(lines) and lines[i].startswith(">"):
                # Strip the leading > and optional space
                line = lines[i]
                if line.startswith("> "):
                    body_lines.append(line[2:])
                elif line == ">":
                    body_lines.append("")
                else:
                    body_lines.append(line[1:])
                i += 1

            callouts.append(
                Callout(
                    type=callout_type,
                    title=title,
                    content="\n".join(body_lines),
                    foldable=foldable,
                    default_open=default_open,
                )
            )
        else:
            i += 1

    return callouts


def extract_headings(content: str) -> list[tuple[int, str]]:
    """Extract headings as (level, text) tuples."""
    return [
        (len(match.group(1)), match.group(2).strip())
        for match in _HEADING_RE.finditer(content)
    ]


def parse_note(path: Path, raw: str | None = None) -> Note:
    """Full parse pipeline: read file -> extract all elements -> Note object.

    Args:
        path: Path to the markdown file.
        raw: Optional raw content. If None, reads from path.
    """
    if raw is None:
        raw = path.read_text(encoding="utf-8")

    frontmatter, body = parse_frontmatter(raw)
    title = path.stem

    return Note(
        path=path,
        title=title,
        frontmatter=frontmatter,
        content=body,
        raw=raw,
        links=extract_wikilinks(body),
        embeds=extract_embeds(body),
        tags=extract_tags(body, frontmatter),
        callouts=extract_callouts(body),
        headings=extract_headings(body),
    )


def serialize_note(note: Note) -> str:
    """Serialize Note back to markdown string. Round-trip safe.

    Reconstructs: frontmatter (if any) + content body.
    """
    parts: list[str] = []

    if note.frontmatter:
        yaml_str = yaml.dump(
            note.frontmatter,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        ).rstrip("\n")
        parts.append(f"---\n{yaml_str}\n---\n")

    parts.append(note.content)
    return "".join(parts)
