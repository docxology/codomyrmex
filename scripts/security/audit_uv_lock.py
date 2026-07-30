#!/usr/bin/env python3
"""Audit the complete uv lock graph rather than the audit tool's environment.

The exported requirements file includes every dependency group and optional
extra, but excludes the editable Codomyrmex project itself. The sole advisory
exception is applied only when the lock contains ``wasmtime==42.0.0``:
PYSEC-2026-151 describes an upstream Rust-crate defect confined to 43.0.0,
and the authoritative RustSec record explicitly marks versions below 43.0.0
as unaffected.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WASMTIME_UNAFFECTED_VERSION = "42.0.0"
WASMTIME_ADVISORY = "PYSEC-2026-151"
WASMTIME_REQUIREMENT = re.compile(r"^wasmtime==([^ \\\\]+)", re.MULTILINE)


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit every locked Codomyrmex dependency with pip-audit."
    )
    parser.add_argument(
        "--format",
        choices=("columns", "json", "markdown"),
        default="columns",
        help="pip-audit output format (default: columns)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional report path. By default, write the report to stdout.",
    )
    return parser.parse_args(argv)


def _run(
    command: list[str],
    *,
    env: dict[str, str] | None = None,
    suppress_stdout: bool = False,
) -> int:
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        env=env,
        check=False,
        stdout=subprocess.DEVNULL if suppress_stdout else None,
    ).returncode


def main(argv: Sequence[str] | None = None) -> int:
    """Export and audit the complete lock graph, returning pip-audit's status."""
    args = _parse_args(argv)
    uv_env = os.environ.copy()
    uv_env.pop("VIRTUAL_ENV", None)

    with tempfile.TemporaryDirectory(prefix="codomyrmex-lock-audit-") as tmp:
        requirements = Path(tmp) / "requirements.txt"
        export_command = [
            "uv",
            "export",
            "--locked",
            "--all-groups",
            "--all-extras",
            "--no-emit-project",
            "--no-annotate",
            "--no-header",
            "--format",
            "requirements-txt",
            "--output-file",
            str(requirements),
        ]
        export_status = _run(export_command, env=uv_env, suppress_stdout=True)
        if export_status:
            return export_status

        requirement_text = requirements.read_text(encoding="utf-8")
        wasmtime_match = WASMTIME_REQUIREMENT.search(requirement_text)
        wasmtime_version = wasmtime_match.group(1) if wasmtime_match else None

        audit_command = [
            sys.executable,
            "-m",
            "pip_audit",
            "--requirement",
            str(requirements),
            "--no-deps",
            "--disable-pip",
            "--strict",
            "--format",
            args.format,
        ]
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            audit_command.extend(("--output", str(args.output)))

        if wasmtime_version == WASMTIME_UNAFFECTED_VERSION:
            audit_command.extend(("--ignore-vuln", WASMTIME_ADVISORY))
            print(
                "Lock audit note: ignoring PYSEC-2026-151 only for "
                "wasmtime==42.0.0; RustSec marks versions below 43.0.0 "
                "unaffected.",
                file=sys.stderr,
            )

        return _run(audit_command)


if __name__ == "__main__":
    raise SystemExit(main())
