"""Obsidian markdown parser — frontmatter, wikilinks, embeds, tags, callouts,
code blocks, math blocks, Dataview fields, headings.

All extraction is regex/YAML-based with no external Obsidian dependencies.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

try:
    import yaml
except ImportError:  # pragma: no cover – yaml is an optional dep
    yaml = None  # type: ignore[assignment]

from codomyrmex.agentic_memory.obsidian.models import (
    Callout,
    CodeBlock,
    DataviewField,
    Embed,
    MathBlock,
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
_CODE_BLOCK_RE = re.compile(
    r"^```(\w*)\n(.*?)^```",
    re.MULTILINE | re.DOTALL,
)
_MATH_BLOCK_RE = re.compile(r"\$\$(.*?)\$\$", re.DOTALL)
_MATH_INLINE_RE = re.compile(r"(?<!\$)\$([^\$\n]+?)\$(?!\$)")
_DATAVIEW_FIELD_RE = re.compile(r"^([A-Za-z][\w\-]*)\s*::\s*(.+)$", re.MULTILINE)


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
    """Extract ``[[target]]``, ``[[target|alias]]``, ``[[target#heading]]``,
    ``[[target#^block-id]]``."""
    results: list[Wikilink] = []
    for m in _WIKILINK_RE.finditer(content):
        raw = m.group(1)
        alias: str | None = None
        heading: str | None = None
        block: str | None = None

        # Handle alias: [[Note|Alias]]
        if "|" in raw:
            target_part, alias = raw.split("|", 1)
        else:
            target_part = raw

        # Handle block ref: [[Note#^block-id]]
        if "#^" in target_part:
            target, block = target_part.split("#^", 1)
        elif "#" in target_part:
            target, heading = target_part.split("#", 1)
        else:
            target = target_part

        results.append(Wikilink(
            target=target, alias=alias, heading=heading, block=block
        ))
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
                try:
                    width = int(parts[0])
                    height = int(parts[1])
                except ValueError as e:
                    logger.debug("Non-integer embed dimensions %r: %s", dims, e)
                    pass
            else:
                try:
                    width = int(dims)
                except ValueError as e:
                    logger.debug("Non-integer embed width %r: %s", dims, e)
                    pass
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
        fm_tags = frontmatter["tags"]
        if isinstance(fm_tags, list):
            for t in fm_tags:
                tags.append(Tag(name=str(t), source="frontmatter"))
        elif isinstance(fm_tags, str):
            for t in fm_tags.split(","):
                tags.append(Tag(name=t.strip(), source="frontmatter"))
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
        body = "\n".join(
            line.lstrip("> ").rstrip()
            for line in body_raw.strip().split("\n") if line.strip()
        )

        foldable = fold_char in ("-", "+")
        default_open = fold_char == "+"
        results.append(Callout(
            type=ctype, title=title, content=body,
            foldable=foldable, default_open=default_open,
        ))
    return results


# ── code blocks ──────────────────────────────────────────────────────

def extract_code_blocks(content: str) -> list[CodeBlock]:
    """Extract fenced code blocks (```language ... ```)."""
    blocks: list[CodeBlock] = []
    for m in _CODE_BLOCK_RE.finditer(content):
        line_start = content[:m.start()].count("\n") + 1
        blocks.append(CodeBlock(
            language=m.group(1).strip(),
            content=m.group(2).strip(),
            line_start=line_start,
        ))
    return blocks


# ── math blocks ──────────────────────────────────────────────────────

def extract_math(content: str) -> list[MathBlock]:
    """Extract display math (``$$...$$``) and inline math (``$...$``)."""
    blocks: list[MathBlock] = []
    for m in _MATH_BLOCK_RE.finditer(content):
        blocks.append(MathBlock(content=m.group(1).strip(), inline=False))
    for m in _MATH_INLINE_RE.finditer(content):
        blocks.append(MathBlock(content=m.group(1).strip(), inline=True))
    return blocks


# ── Dataview inline fields ───────────────────────────────────────────

def extract_dataview_fields(content: str) -> list[DataviewField]:
    """Extract Dataview inline fields (``key:: value``)."""
    fields: list[DataviewField] = []
    for i, line in enumerate(content.split("\n"), 1):
        m = _DATAVIEW_FIELD_RE.match(line)
        if m:
            fields.append(DataviewField(
                key=m.group(1).strip(),
                value=m.group(2).strip(),
                line=i,
            ))
    return fields


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
        code_blocks=extract_code_blocks(body),
        math_blocks=extract_math(body),
        dataview_fields=extract_dataview_fields(body),
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
