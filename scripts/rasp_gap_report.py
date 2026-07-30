#!/usr/bin/env python3
"""Scan repo roots for directories missing AGENTS.md and/or README.md.

Writes docs/plans/agents-readme-gap-report.md (Markdown) and prints summary.

Excludes: __pycache__, .git, node_modules, .venv, venv, dist, build, htmlcov,
.pytest_cache, .ruff_cache, .docusaurus, .tox, *.egg-info, .eggs,
vendor/generated/embedded trees, and paths matching SUBSTRING_EXCLUDES. The
first-party inclusion boundary is aligned with
``scripts/documentation/validate_agents_structure.py``; embedded application,
upstream skill, and generated documentation trees are not RASP targets.
Filesystem-empty directory remnants are ignored because Git does not version
directories and therefore they are not package or documentation surfaces.

Run from repo root: uv run python scripts/rasp_gap_report.py
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

EXCLUDE_DIR_NAMES = frozenset(
    {
        "__pycache__",
        ".git",
        "node_modules",
        ".venv",
        "venv",
        "dist",
        "build",
        "htmlcov",
        ".pytest_cache",
        ".ruff_cache",
        ".docusaurus",
        ".tox",
        ".eggs",
        ".cursor",
        ".claude",
        ".benchmarks",
    }
)

# Skip subtrees (path fragment after normalizing to forward slashes).
SUBSTRING_EXCLUDES = (
    "/.git/",
    "/node_modules/",
    "/__pycache__/",
    "/.venv/",
    "/venv/",
    "/htmlcov/",
    "/.pytest_cache/",
    "/.ruff_cache/",
    "/.docusaurus/",
    "/.tox/",
    "/.eggs/",
    "/vendor/openfang/",
    # Embedded or generated trees excluded by the authoritative AGENTS validator.
    "/src/codomyrmex/agents/open_gauss/",
    "/src/codomyrmex/agents/mission_control/app/",
    "/src/codomyrmex/skills/skills/upstream/",
    "/src/codomyrmex/skills/skills/custom/",
    "/src/codomyrmex/documentation/docs/",
    "/src/codomyrmex/agents/hermes/evolution/",
    "/src/codomyrmex/llm/outputs/config/",
    "/src/codomyrmex/llm/outputs/logs/",
    "/src/codomyrmex/llm/outputs/models/",
    "/src/codomyrmex/skills/skills/.cache/",
    "/docs/assets/demo_stills/",
    "/.cursor/",
    "/.claude/plugins/cache/",
    # Ephemeral / generated — not RASP documentation targets
    "/.benchmarks/",
    "/scripts/output/",
    "/scripts/agents/hermes/output/",
    "/scripts/sair/output/",
)

ROOTS = ("src/codomyrmex", "docs", "projects", "scripts", "config", ".github")


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def norm_rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root).as_posix()


def should_skip_dir(path: Path, root: Path) -> bool:
    name = path.name
    if name in EXCLUDE_DIR_NAMES:
        return True
    if name.endswith(".egg-info"):
        return True
    rel = "/" + norm_rel(path, root) + "/"
    return any(frag in rel for frag in SUBSTRING_EXCLUDES)


def iter_dirs_under(root: Path, base: Path):
    """Yield directories whose included subtree contains at least one file."""

    if not base.is_dir():
        return

    discovered: list[Path] = []
    live: set[Path] = set()
    for dirpath, dirnames, filenames in os.walk(base, topdown=True):
        dp = Path(dirpath)
        dirnames[:] = [d for d in sorted(dirnames) if not should_skip_dir(dp / d, root)]
        discovered.append(dp)
        if filenames:
            live.add(dp)

    for directory in reversed(discovered):
        if directory in live and directory != base:
            live.add(directory.parent)

    yield from (directory for directory in discovered if directory in live)


def scan_root(root: Path, rel_root: str) -> list[tuple[str, bool, bool]]:
    """Return list of (relative_path, has_agents, has_readme)."""
    base = root / rel_root
    if not base.is_dir():
        return []
    rows: list[tuple[str, bool, bool]] = []
    for d in iter_dirs_under(root, base):
        rel = norm_rel(d, root)
        has_agents = (d / "AGENTS.md").is_file()
        has_readme = (d / "README.md").is_file()
        if not has_agents or not has_readme:
            rows.append((rel, has_agents, has_readme))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit the scoped first-party README.md / AGENTS.md pairs."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=repo_root(),
        help="Repository root. Defaults to the root containing this script.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/plans/agents-readme-gap-report.md"),
        help="Report path, relative to --repo-root unless absolute.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for gaps without writing a report; exit nonzero when gaps exist.",
    )
    args = parser.parse_args()
    root = args.repo_root.resolve()
    out_path = args.output
    if not out_path.is_absolute():
        out_path = root / out_path

    by_root: dict[str, list[tuple[str, bool, bool]]] = {}
    for rr in ROOTS:
        by_root[rr] = scan_root(root, rr)

    lines: list[str] = [
        "# AGENTS.md / README.md gap report",
        "",
        "Auto-generated by `uv run --locked python scripts/rasp_gap_report.py --repo-root .`. Refresh after reviewed documentation changes.",
        "",
        "## Inclusion rules",
        "",
        "- Roots: `src/codomyrmex/`, `docs/`, `projects/`, `scripts/`, `config/`, `.github/`.",
        "- Excluded directory names and path fragments: see `EXCLUDE_DIR_NAMES` and `SUBSTRING_EXCLUDES` in `scripts/rasp_gap_report.py`.",
        "",
        "## Summary",
        "",
    ]

    total_dirs = 0
    missing_agents = 0
    missing_readme = 0
    missing_both = 0
    for rr, rows in by_root.items():
        ta = sum(1 for _r, a, _re in rows if not a)
        tr = sum(1 for _r, _a, re in rows if not re)
        tb = sum(1 for _r, a, re in rows if not a and not re)
        total_dirs += len(rows)
        missing_agents += ta
        missing_readme += tr
        missing_both += tb
        lines.append(
            f"- **{rr}/**: dirs with any gap: {len(rows)}; missing AGENTS.md: {ta}; missing README.md: {tr}; missing both: {tb}"
        )

    lines.extend(
        [
            "",
            f"- **Totals (rows = dirs missing at least one file)**: {total_dirs}; missing AGENTS.md: {missing_agents}; missing README.md: {missing_readme}; missing both: {missing_both}",
            "",
            "## Detail by root",
            "",
        ]
    )

    for rr, rows in by_root.items():
        if not rows:
            lines.append(f"### `{rr}/`")
            lines.append("")
            lines.append("(root missing or no gaps)")
            lines.append("")
            continue
        lines.append(f"### `{rr}/`")
        lines.append("")
        lines.append("| Directory | AGENTS.md | README.md |")
        lines.append("| --- | --- | --- |")
        for rel, a, r in sorted(rows, key=lambda x: x[0]):
            lines.append(
                f"| `{rel}` | {'yes' if a else '**no**'} | {'yes' if r else '**no**'} |"
            )
        lines.append("")

    if args.check:
        print(
            f"Checked {sum(len(rows) for rows in by_root.values())} gap rows "
            f"across {len(ROOTS)} roots; both missing: {missing_both}"
        )
        return 1 if total_dirs else 0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        display_path = out_path.relative_to(root)
    except ValueError:
        display_path = out_path
    print(f"Wrote {display_path}")
    print(f"Summary: {total_dirs} dir-rows with gaps; both missing: {missing_both}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
