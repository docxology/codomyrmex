#!/usr/bin/env python3
# /// script
# requires-python = ">=3.15"
# dependencies = ["aiohttp>=3.13.3", "jsonschema>=4.23.0", "pydantic>=2.8.0", "python-dotenv>=1.0.0", "pyyaml>=6.0.2", "requests>=2.31.0", "rich>=13.0.0"]
# ///
"""Profile portable MLX configuration and write a new offline evidence bundle.

Usage: uv run --python 3.15 --script scripts/llm/mlx_profile.py
           --output-dir output/mlx-profile --iterations 2000 --repeats 7

Script dependencies exclude MLX; native generation is never attempted.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    """Keep CLI orchestration thin and all measurements in reusable APIs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--repeats", type=int, default=7)
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root / "src"))
    from codomyrmex.llm.mlx.profile_report import write_profile_bundle
    from codomyrmex.llm.mlx.profiling import profile_cache_configuration
    from codomyrmex.logging_monitoring import get_logger

    logger = get_logger(__name__)
    try:
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=root,
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            ).stdout
        )
        report = profile_cache_configuration(
            args.iterations, args.repeats, revision, dirty
        )
        paths = write_profile_bundle(report, args.output_dir)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        logger.error("MLX portable profiling failed: %s", exc)
        parser.exit(2, f"error: {exc}\n")
    print(json.dumps(paths, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
