#!/usr/bin/env python3
"""Audit manuscript citations and resolve bibliography source metadata.

Online ISBN checks prefer an exact Open Library edition lookup and use bounded,
identifier-checked Open Library search and Google Books feed fallbacks when a
provider is transiently unavailable.

Examples:
    uv run --locked python scripts/audit_bibliography.py
    uv run --locked python scripts/audit_bibliography.py --online
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from codomyrmex.manuscript.bibliography import (
    audit_bibliography,
    write_bibliography_audit,
)


def main() -> int:
    """Run the bibliography audit and write its machine-readable receipt."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--online", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        help="Receipt path (default: output/data/bibliography_audit.json).",
    )
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    root = args.root.resolve()
    manuscript_dir = root / "docs" / "manuscript"
    bibliography = manuscript_dir / "references.bib"
    output = (
        args.output.resolve()
        if args.output is not None
        else root / "output" / "data" / "bibliography_audit.json"
    )
    audit = audit_bibliography(
        bibliography,
        sorted(manuscript_dir.glob("[0-9]*.md")),
        verify_online=args.online,
        timeout=args.timeout,
        workers=args.workers,
    )
    write_bibliography_audit(output, audit)
    summary = {
        key: audit[key]
        for key in (
            "record_count",
            "cited_count",
            "missing_citations",
            "unused_bibliography_keys",
            "unresolved_locators",
            "online_failures",
            "title_mismatches",
        )
    }
    print(json.dumps(summary, indent=2))
    return (
        0
        if not any(summary[key] for key in summary if isinstance(summary[key], list))
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
