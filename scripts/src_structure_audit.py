#!/usr/bin/env python3
"""Audit top-level ``src/codomyrmex`` module structure."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    """Run the source structure audit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=_repo_root())
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)

    from codomyrmex.system_discovery.structure_audit import audit_module_structure

    audit = audit_module_structure(args.repo_root)
    if args.json:
        print(json.dumps(audit.to_dict(), indent=2, sort_keys=True))
    else:
        print(audit.to_markdown())
    return 0 if audit.passed else 1


if __name__ == "__main__":
    sys.exit(main())
