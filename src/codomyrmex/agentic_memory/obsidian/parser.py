"""Obsidian markdown parser — frontmatter, wikilinks, embeds, tags, callouts, headings.

All extraction is regex/YAML-based with no external Obsidian dependencies.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover – yaml is an optional dep
    yaml = None  # type: ignore[assignment]

from codomyrmex.agentic_memory.obsidian.models import (
    Callout,
    Embed,
    Note,
    Tag,
    Wikilink,
)

# ── regex patterns ───────────────────────────────────────────────────

_FM_RE = re.compile(r"^---\n(.*?)^---\n?", re.MULTILINE | re.DOTALL)
_WIKILINK_RE = re.compile(r"(?<!\!)\[\[([^\]]+?)\]\]")
_EMBED_RE = re.compile(r"!\[\[([^\]]+?)\]\]")
_TAG_RE = re.compile(r"(?:^|\s)#([\w][\w/\-]*)", re.MULTILINE)
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
_CALLOUT_RE = re.compile(
    r"^> \[!([\w]+)\]([+-]?)\s*(.*?)$\n((?:^> .*$\n?)*)",
    re.MULTILINE,
)


# ── frontmatter ──────────────────────────────────────────────────────

def parse_frontmatter(raw: str) -> tuple[dict[str, Any], str]:
    """Split raw markdown into ``(frontmatter_dict, body)``."""
    match = _FM_RE.match(raw)
    if not match:
        return {}, raw
    fm_text = match.group(1).strip()
    body = raw[match.end():]
    if not fm_text:
        return {}, body
    if yaml is not None:
        fm = yaml.safe_load(fm_text) or {}
    else:
        fm = {}
    return fm, body


# ── wikilinks ────────────────────────────────────────────────────────

def extract_wikilinks(content: str) -> list[Wikilink]:
    """Extract ``[[target]]``, ``[[target|alias]]``, ``[[target#heading]]``."""
    results: list[Wikilink] = []
    for m in _WIKILINK_RE.finditer(content):
        raw = m.group(1)
        alias: str | None = None
        heading: str | None = None

        # Handle heading + alias: [[Note#Section|Custom Text]]
        if "|" in raw:
            target_part, alias = raw.split("|", 1)
        else:
            target_part = raw

        if "#" in target_part:
            target, heading = target_part.split("#", 1)
        else:
            target = target_part

        results.append(Wikilink(target=target, alias=alias, heading=heading))
    return results


# ── embeds ───────────────────────────────────────────────────────────

def extract_embeds(content: str) -> list[Embed]:
    """Extract ``![[file]]`` and ``![[file|WxH]]`` embeds."""
    results: list[Embed] = []
    for m in _EMBED_RE.finditer(content):
        raw = m.group(1)
        width: int | None = None
        height: int | None = None

        if "|" in raw:
            target, dims = raw.split("|", 1)
            if "x" in dims:
                parts = dims.split("x", 1)
                width = int(parts[0])
                height = int(parts[1])
            else:
                width = int(dims)
        else:
            target = raw

        results.append(Embed(target=target, width=width, height=height))
    return results


# ── tags ─────────────────────────────────────────────────────────────

def extract_tags(
    content: str,
    frontmatter: dict[str, Any] | None = None,
) -> list[Tag]:
    """Extract inline ``#tags`` and frontmatter ``tags`` list."""
    tags: list[Tag] = []
    for m in _TAG_RE.finditer(content):
        tags.append(Tag(name=m.group(1), source="content"))

    if frontmatter and "tags" in frontmatter:
        for t in frontmatter["tags"]:
            tags.append(Tag(name=str(t), source="frontmatter"))
    return tags


# ── headings ─────────────────────────────────────────────────────────

def extract_headings(content: str) -> list[tuple[int, str]]:
    """Return ``(level, text)`` tuples for every heading."""
    return [(len(m.group(1)), m.group(2).strip()) for m in _HEADING_RE.finditer(content)]


# ── callouts ─────────────────────────────────────────────────────────

def extract_callouts(content: str) -> list[Callout]:
    """Extract Obsidian-style callout blocks."""
    results: list[Callout] = []
    for m in _CALLOUT_RE.finditer(content):
        ctype = m.group(1)
        fold_char = m.group(2)
        title = m.group(3).strip()
        body_raw = m.group(4)
        body = "\n".join(line.lstrip("> ").rstrip() for line in body_raw.strip().split("\n") if line.strip())

        foldable = fold_char in ("-", "+")
        default_open = fold_char == "+"
        results.append(Callout(
            type=ctype, title=title, content=body,
            foldable=foldable, default_open=default_open,
        ))
    return results


# ── full note parser ─────────────────────────────────────────────────

def parse_note(path: Path, *, raw: str | None = None) -> Note:
    """Parse a markdown file (or raw string) into a ``Note``."""
    if raw is None:
        if not path.exists():
            raise FileNotFoundError(path)
        raw = path.read_text()

    fm, body = parse_frontmatter(raw)
    return Note(
        title=path.stem,
        path=path,
        frontmatter=fm,
        content=body,
        links=extract_wikilinks(body),
        embeds=extract_embeds(body),
        tags=extract_tags(body, fm),
        headings=extract_headings(body),
        callouts=extract_callouts(body),
    )


# ── serialize ────────────────────────────────────────────────────────

def serialize_note(note: Note) -> str:
    """Reconstruct markdown text from a ``Note``."""
    parts: list[str] = []
    if note.frontmatter:
        if yaml is not None:
            fm_str = yaml.dump(note.frontmatter, default_flow_style=False).strip()
        else:
            fm_str = "\n".join(f"{k}: {v}" for k, v in note.frontmatter.items())
        parts.append(f"---\n{fm_str}\n---\n")
    parts.append(note.content)
    return "".join(parts)
