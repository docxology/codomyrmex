#!/usr/bin/env python3
"""Merge multiple SARIF 2.1.0 files into one log (dedupe by fingerprint / location)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sarif_utils import merge_sarif_files


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge SARIF files")
    parser.add_argument("inputs", type=Path, nargs="+", help="Input .sarif files")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output path")
    args = parser.parse_args()
    for p in args.inputs:
        if not p.is_file():
            print(f"Missing file: {p}", file=sys.stderr)
            return 1
    merged = merge_sarif_files([p.resolve() for p in args.inputs])
    args.output.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    print(f"Wrote {args.output} ({len(merged.get('runs', []))} runs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
