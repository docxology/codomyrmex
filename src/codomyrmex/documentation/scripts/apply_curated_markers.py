#!/usr/bin/env python3
"""
Prepend curated HTML comments to AGENTS.md and README.md under bootstrap surfaces.

After a bootstrap run, this locks leaf docs so a later bootstrap skips overwrites
(see AGENTS_CURATED_MARKER / README_CURATED_MARKER in bootstrap_agents_readmes).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from codomyrmex.documentation.scripts.bootstrap_agents_readmes import (
    AGENTS_CURATED_MARKER,
    DocumentationBootstrapper,
    README_CURATED_MARKER,
)
from codomyrmex.logging_monitoring import get_logger, setup_logging

try:
    setup_logging()
except Exception:
    import logging

    logging.basicConfig(level=logging.INFO)

logger = get_logger(__name__)

_HEAD_BYTES = 800


def _prepend_marker(path: Path, marker: str, *, dry_run: bool) -> bool:
    """Return True if a write would happen / happened."""
    if not path.is_file():
        return False
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        logger.warning("Skip %s: %s", path, exc)
        return False
    head = raw[:_HEAD_BYTES]
    if marker in head:
        return False
    new_body = f"{marker}\n\n{raw}"
    if dry_run:
        logger.info("DRY RUN would prepend %s to %s", marker, path)
        return True
    path.write_text(new_body, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepend curated markers to AGENTS.md and README.md under bootstrap surfaces."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root (default: cwd)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log actions without writing files",
    )
    args = parser.parse_args()
    repo_root = (args.repo_root or Path.cwd()).resolve()

    bootstrapper = DocumentationBootstrapper(repo_root)
    dirs = bootstrapper.iter_processable_directories()

    agents_n = 0
    readme_n = 0
    for dir_path in dirs:
        if _prepend_marker(
            dir_path / "AGENTS.md", AGENTS_CURATED_MARKER, dry_run=args.dry_run
        ):
            agents_n += 1
        if _prepend_marker(
            dir_path / "README.md", README_CURATED_MARKER, dry_run=args.dry_run
        ):
            readme_n += 1

    mode = "DRY RUN" if args.dry_run else "Wrote"
    print(f"{mode}: curated markers prepended to {agents_n} AGENTS.md, {readme_n} README.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
