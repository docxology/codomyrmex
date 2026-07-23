#!/usr/bin/env python3
"""Run offline Colony Kernel research fixtures and emit a hashed artifact.

Usage:
    uv run python scripts/run_colony_research.py --output output/research/r2.json

No network or provider calls are made by this command.  External adapters must
be invoked separately with their dedicated ``RUN_LIVE_*`` controls.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from codomyrmex.colony_kernel.research import run_paired_benchmark


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    if args.seed < 0:
        parser.error("--seed must be non-negative")

    run = run_paired_benchmark(seed=args.seed, repo_root=Path.cwd())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(run.to_dict(), indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {"output": str(args.output), "artifact_hash": run.artifact_hash},
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
