"""Resolve GitHub ``owner/repo`` for Jules CLI ``--repo``."""

from __future__ import annotations

import os
import re
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

DEFAULT_REPO_SLUG = "docxology/codomyrmex"


def _parse_github_origin_slug(url: str) -> str | None:
    """Return ``owner/repo`` from a GitHub remote URL, or None if not parsed."""
    u = url.strip().rstrip("/").removesuffix(".git")
    m = re.search(r"github\.com[/:]([^/]+)/([^/]+)$", u)
    if m:
        return f"{m.group(1)}/{m.group(2)}"
    return None


def resolve_repo_slug(explicit: str | None, repo_root: Path) -> tuple[str, str]:
    """Resolve GitHub slug for ``jules new --repo``.

    Precedence: non-empty ``explicit``, env ``JULES_REPO``, ``git remote get-url origin``,
    then :data:`DEFAULT_REPO_SLUG`.

    Returns:
        Tuple of (slug, source_label) for logging.
    """
    if explicit and explicit.strip():
        return explicit.strip(), "cli --repo"
    env_slug = (os.environ.get("JULES_REPO") or "").strip()
    if env_slug:
        return env_slug, "env JULES_REPO"
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
            timeout=8,
        )
        parsed = _parse_github_origin_slug(proc.stdout)
        if parsed:
            return parsed, "git origin"
    except (subprocess.CalledProcessError, FileNotFoundError, TimeoutError, OSError):
        pass
    return DEFAULT_REPO_SLUG, f"default ({DEFAULT_REPO_SLUG})"
