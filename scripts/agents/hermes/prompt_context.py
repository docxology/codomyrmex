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
from typing import Optional

# ── Hard-coded project standards ──────────────────────────────────────────────
# These are derived from pyproject.toml (requires-python >=3.11, ruff line-length=88)
# and the Codomyrmex AGENTS.md Zero-Mock and Zero-Bare-Except policies.
_PROJECT_STANDARDS = """
## Codomyrmex Project Coding Standards

**Python version**: 3.11+ — use modern syntax exclusively:
  - Type hints: `dict[str, int]` not `Dict[str, int]`; `list[str]` not `List[str]`
  - Unions: `str | None` not `Optional[str]`; `dict | None` not `Optional[Dict]`
  - Do NOT import from `typing` for basic containers (Dict, List, Tuple, Optional are legacy)
  - f-strings always (not % or .format())

**Ruff / linting**: line-length=88, target=py311
  - No bare `except:` — always name the exception(s): `except (ValueError, KeyError):`
  - No shadow of builtins (`list`, `dict`, `type`, `id`, `input`, etc.)
  - No wildcard imports (`from module import *`)
  - No unused imports

**Architecture — Thin Orchestrator pattern**:
  - Scripts MUST be thin shells: accept config, call a library method, log output, exit
  - NO business logic or data transformation inside the script file itself
  - NO hardcoded paths — use `Path(__file__).resolve().parent` or env vars
  - MUST exit with `sys.exit(int)` — 0 for success, non-zero for failure
  - Configuration loaded from `config/<area>/config.yaml` or environment variables

**Zero-Mock policy**: test with real methods, not mocks or stubs.

**Logging**: use `print_info`, `print_success`, `print_error` from
`codomyrmex.utils.cli_helpers` — not bare `print()` for status messages.
""".strip()

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
    for _ in range(5):  # walk up at most 5 levels
        agents_md = candidate / "AGENTS.md"
        if agents_md.exists():
            try:
                content = agents_md.read_text(encoding="utf-8")
                if len(content) > _MAX_AGENTS_CHARS:
                    content = content[:_MAX_AGENTS_CHARS] + "\n... [truncated]"
                return content
            except OSError:
                return ""
        parent = candidate.parent
        if parent == candidate:
            break
        candidate = parent
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
    repo_root: Optional[Path] = None,
    exemplar_paths: Optional[list[Path]] = None,
) -> str:
    """Build a rich project context block to inject into Hermes prompts.

    Includes:
    - Codomyrmex project coding standards (Python 3.11+, ruff, Thin Orchestrator)
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

    # 1. Project coding standards
    sections.append(_PROJECT_STANDARDS)

    # 2. AGENTS.md from target directory
    agents_content = load_agents_md(target_dir)
    if agents_content:
        sections.append("")
        sections.append("## LOCAL AGENTS.md (directory-specific rules)")
        sections.append("=" * 60)
        sections.append(agents_content)

    # 3. Exemplary COMPLIANT scripts (positive examples)
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
