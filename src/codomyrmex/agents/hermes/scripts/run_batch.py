#!/usr/bin/env python3
"""Hermes batch execution script.

Reads prompts from a text file (one per line) and submits them all to the
Hermes agent, writing JSON results to stdout.

Usage::

    # Sequential (default)
    uv run python -m codomyrmex.agents.hermes.scripts.run_batch \\
        --file prompts.txt --backend ollama

    # Parallel
    uv run python -m codomyrmex.agents.hermes.scripts.run_batch \\
        --file prompts.txt --parallel --output results.json

    # From stdin
    echo "What is 2+2?" | uv run python -m codomyrmex.agents.hermes.scripts.run_batch
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="run_batch",
        description="Submit a batch of prompts to the Hermes agent.",
    )
    parser.add_argument(
        "--file",
        "-f",
        type=Path,
        default=None,
        help="Text file with one prompt per line (reads stdin if omitted).",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Write JSON results to this file (prints to stdout if omitted).",
    )
    parser.add_argument(
        "--backend",
        default="auto",
        choices=["auto", "cli", "ollama"],
        help="Hermes backend to use (default: auto).",
    )
    parser.add_argument(
        "--model",
        default="hermes3",
        help="Ollama model name (default: hermes3, used when backend=ollama).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Per-prompt timeout in seconds (default: 120).",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        default=False,
        help="Run all prompts concurrently (ThreadPoolExecutor).",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress progress messages.",
    )
    return parser.parse_args()


def main() -> int:
    """Entry point.

    Returns:
        Exit code (0 = all success, 1 = partial errors, 2 = fatal error).
    """
    args = _parse_args()

    # Load prompts
    if args.file:
        if not args.file.exists():
            print(f"Error: file not found: {args.file}", file=sys.stderr)
            return 2
        raw = args.file.read_text(encoding="utf-8")
    else:
        if not args.quiet:
            print("Reading prompts from stdin (one per line)…", file=sys.stderr)
        raw = sys.stdin.read()

    prompts = [line.strip() for line in raw.splitlines() if line.strip()]
    if not prompts:
        print("Error: no prompts found.", file=sys.stderr)
        return 2

    if not args.quiet:
        print(
            f"Submitting {len(prompts)} prompt(s) via backend={args.backend!r} "
            f"({'parallel' if args.parallel else 'sequential'})…",
            file=sys.stderr,
        )

    # Execute
    try:
        from codomyrmex.agents.hermes.hermes_client import HermesClient

        client = HermesClient(
            config={
                "hermes_backend": args.backend,
                "hermes_model": args.model,
                "hermes_timeout": args.timeout,
            }
        )
        results = client.batch_execute(prompts, parallel=args.parallel)
    except Exception as exc:
        print(f"Fatal error: {exc}", file=sys.stderr)
        return 2

    # Report
    errors = sum(1 for r in results if r["status"] == "error")
    summary = {
        "total": len(results),
        "success": len(results) - errors,
        "errors": errors,
        "results": results,
    }

    json_out = json.dumps(summary, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(json_out, encoding="utf-8")
        if not args.quiet:
            print(f"Results written to {args.output}", file=sys.stderr)
    else:
        print(json_out)

    if not args.quiet:
        print(
            f"Done. {len(results) - errors}/{len(results)} succeeded.",
            file=sys.stderr,
        )

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
