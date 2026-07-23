#!/usr/bin/env python3
"""Replay the checked-in Colony Kernel paired-locality contract.

Examples
--------
``uv run python scripts/replay_colony_kernel.py``
``uv run python scripts/replay_colony_kernel.py --seed 0 --output /tmp/replay.json``

The command runs two identical semantic replays and writes a JSON record with
the inputs, decisions, pressure observations, assertion results, and digests.
It does not contact an external service and does not claim outcome attestation.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent-trust", type=float, default=0.50)
    parser.add_argument("--recovery-ticks", type=int, default=20)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/data/colony_kernel_replay.json"),
    )
    args = parser.parse_args()

    root = _project_root()
    if not args.output.is_absolute():
        args.output = root / args.output
    sys.path.insert(0, str(root / "src"))

    from codomyrmex.colony_kernel.replay import (
        run_paired_locality_replay,
        write_replay_artifact,
    )

    record = run_paired_locality_replay(
        agent_trust=args.agent_trust,
        recovery_ticks=args.recovery_ticks,
        seed=args.seed,
    )
    file_sha256 = write_replay_artifact(args.output, record)
    print(json.dumps({"path": str(args.output), "sha256": file_sha256}, indent=2))
    return 0 if all(record["assertions"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
