#!/usr/bin/env python3
"""Validate the generated manuscript variable and provenance contract.

This command is read-only. It checks the source tree against the generated
variable snapshot; it does not invent missing values or rewrite manuscript
outputs. Run the generator first when the snapshot is stale.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _project_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in (here, *here.parents):
        if (candidate / "pyproject.toml").is_file():
            return candidate
    return here.parent


def main() -> int:
    root = _project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--variables", type=Path, default=root / "output/data/manuscript_variables.json"
    )
    parser.add_argument("--manuscript-dir", type=Path, default=root / "docs/manuscript")
    parser.add_argument(
        "--figure-source",
        type=Path,
        default=root / "src/codomyrmex/manuscript/figures",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=root / "output/data/manuscript_variable_manifest.json",
    )
    args = parser.parse_args()

    if not args.variables.is_file():
        print(f"ERROR: variable snapshot not found: {args.variables}", file=sys.stderr)
        return 1
    try:
        variables = json.loads(args.variables.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read variable snapshot: {exc}", file=sys.stderr)
        return 1
    if not isinstance(variables, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in variables.items()
    ):
        print(
            "ERROR: variable snapshot must be a string-to-string JSON object",
            file=sys.stderr,
        )
        return 1

    from codomyrmex.manuscript.variables import validate_variable_contract

    report = validate_variable_contract(
        manuscript_dir=args.manuscript_dir,
        variables=variables,
        figure_source_dir=args.figure_source,
    )
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"manifest": str(args.manifest), "status": report["status"]}))
    for error in report["errors"]:
        print(f"- {error}", file=sys.stderr)
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
