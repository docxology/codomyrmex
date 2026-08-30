
"""Regression test: no unfilled placeholders in module documentation.

P2-4: Verifies that [Module Name] and [YourToolName] placeholders have been
filled in for real module documentation files. Template directories and
.template.-suffixed files are excluded, since they are meant to retain
placeholders for reuse.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def _find_files_with_placeholder(
    repo: Path,
    placeholder: str,
    exclude_patterns: list[str] | None = None,
) -> list[Path]:
    """Return paths under ``repo`` containing literal ``placeholder``,
    excluding directories matching any pattern in ``exclude_patterns``."""
    exclude = exclude_patterns or [
        "module_template",
        ".template.",
        ".git",
        "__pycache__",
        "node_modules",
        ".venv",
    ]

    # Use -F (fixed string) so square brackets are not treated as regex
    cmd = [
        "grep", "-Frl",
        placeholder,
        "--include=*.md",
        str(repo),
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []

    paths: list[Path] = []
    for raw in result.stdout.strip().split("\n"):
        if not raw:
            continue
        p = Path(raw)
        if not any(pat in p.as_posix() for pat in exclude):
            paths.append(p)
    return paths


def test_no_unfilled_module_name_placeholders() -> None:
    """No [Module Name] placeholder remains in non-template module docs."""
    found = _find_files_with_placeholder(
        REPO_ROOT,
        "[Module Name]",
        exclude_patterns=[
            "module_template",
            ".template.",
            ".git",
            "__pycache__",
            "node_modules",
            ".venv",
        ],
    )
    assert len(found) == 0, (
        f"Found {len(found)} file(s) with unfilled [Module Name] placeholder:\n"
        + "\n".join(str(p.relative_to(REPO_ROOT)) for p in found)
    )


def test_no_unfilled_yourtoolname_placeholders() -> None:
    """No [YourToolName] placeholder remains in non-template MCP docs."""
    found = _find_files_with_placeholder(
        REPO_ROOT,
        "[YourToolName]",
        exclude_patterns=[
            "module_template",
            ".template.",
            ".git",
            "__pycache__",
            "node_modules",
            ".venp",
        ],
    )
    assert len(found) == 0, (
        f"Found {len(found)} file(s) with unfilled [YourToolName] placeholder:\n"
        + "\n".join(str(p.relative_to(REPO_ROOT)) for p in found)
    )
