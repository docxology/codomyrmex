#!/usr/bin/env python3
"""Shared prompt context utilities for Hermes eval and dispatch scripts.

This module builds rich, project-aware context blocks for injection into
Hermes assessment and improvement prompts. Richer context → better suggestions.

Functions exported:
    build_project_context(target_dir, repo_root, exemplar_paths) -> str
    load_agents_md(directory) -> str
    load_exemplary_scripts(paths, max_chars) -> str
"""

from __future__ import annotations

from pathlib import Path

# Truncation limits for loaded content to keep prompts manageable
_MAX_AGENTS_CHARS = 3_000
_MAX_EXEMPLAR_CHARS = 4_000


def load_agents_md(directory: Path) -> str:
    """Load AGENTS.md from *directory*, walking up to repo root if not found.

    Returns the content (truncated to _MAX_AGENTS_CHARS) or an empty string.

    Args:
        directory: Start directory to search.

    Returns:
        AGENTS.md content string, or empty string if not found.
    """
    candidate = directory
    while candidate != candidate.parent:
        agents_md = candidate / "AGENTS.md"
        if agents_md.exists():
            try:
                content = agents_md.read_text(encoding="utf-8")
                if len(content) > _MAX_AGENTS_CHARS:
                    content = content[:_MAX_AGENTS_CHARS] + "\n... [truncated]"
                return content
            except OSError:
                return ""
        candidate = candidate.parent
    return ""


def load_exemplary_scripts(paths: list[Path], max_chars: int = _MAX_EXEMPLAR_CHARS) -> str:
    """Load one or more exemplary (COMPLIANT) scripts as positive examples.

    Content is concatenated and truncated to *max_chars* total.

    Args:
        paths: List of paths to exemplary Python scripts.
        max_chars: Maximum total characters across all scripts.

    Returns:
        Formatted string of exemplary script content(s).
    """
    blocks: list[str] = []
    total = 0
    for p in paths:
        if not p.exists():
            continue
        try:
            content = p.read_text(encoding="utf-8")
        except OSError:
            continue
        remaining = max_chars - total
        if remaining <= 0:
            break
        if len(content) > remaining:
            content = content[:remaining] + "\n# ... [truncated]"
        blocks.append(f"### {p.name}\n```python\n{content}\n```")
        total += len(content)
    return "\n\n".join(blocks)


def build_project_context(
    target_dir: Path,
    repo_root: Path | None = None,
    exemplar_paths: list[Path] | None = None,
) -> str:
    """Build a rich project context block to inject into Hermes prompts.

    Includes:
    - AGENTS.md from the target directory (or nearest parent)
    - Exemplary COMPLIANT scripts as positive examples (if provided)

    Args:
        target_dir: The scripts directory being evaluated (e.g. scripts/api).
        repo_root: Repository root Path (for cross-dir exemplar loading).
        exemplar_paths: Paths to exemplary scripts to show as positive examples.

    Returns:
        A formatted multi-section string block for prompt injection.
    """
    sections: list[str] = ["=" * 60, "## PROJECT CONTEXT", "=" * 60]

    # AGENTS.md from target directory (walking up to repo root if needed)
    agents_content = load_agents_md(target_dir)
    if agents_content:
        sections.append("")
        sections.append("## LOCAL AGENTS.md (directory-specific rules)")
        sections.append("=" * 60)
        sections.append(agents_content)

    # Exemplary COMPLIANT scripts (positive examples)
    if exemplar_paths:
        exemplar_content = load_exemplary_scripts(exemplar_paths)
        if exemplar_content:
            sections.append("")
            sections.append("## EXEMPLARY SCRIPTS (these are COMPLIANT — model your output on these)")
            sections.append("=" * 60)
            sections.append(exemplar_content)

    sections.append("=" * 60)
    return "\n".join(sections)


# ── Default exemplary scripts exported for use by eval and dispatch ────────────
# These are well-rated hermes orchestrators that demonstrate the pattern correctly.
_REPO_ROOT_DEFAULT: Path = Path(__file__).resolve().parent.parent.parent.parent
_EXEMPLAR_SCRIPTS: list[Path] = [
    _REPO_ROOT_DEFAULT / "scripts" / "agents" / "hermes" / "observe_hermes.py",
    _REPO_ROOT_DEFAULT / "scripts" / "agents" / "hermes" / "setup_hermes.py",
]
