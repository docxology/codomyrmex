#!/usr/bin/env python3
"""Audit the complete uv lock graph rather than the audit tool's environment.

The exported requirements file includes every dependency group and optional
extra, but excludes the editable Codomyrmex project itself.

Advisory exceptions live in ``SCOPED_IGNORES``. Each one is pinned to an exact
``package==version`` and is applied only while the lock still contains that
exact version, so any upgrade or downgrade re-enables the advisory and forces
a fresh review. Every entry must carry a written justification.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ScopedIgnore:
    """An advisory exception valid only for one exact locked version."""

    advisory: str
    package: str
    version: str
    justification: str


SCOPED_IGNORES: tuple[ScopedIgnore, ...] = (
    ScopedIgnore(
        advisory="PYSEC-2026-151",
        package="wasmtime",
        version="42.0.0",
        justification=(
            "upstream Rust-crate defect confined to 43.0.0; the authoritative "
            "RustSec record marks versions below 43.0.0 unaffected"
        ),
    ),
    ScopedIgnore(
        advisory="PYSEC-2026-3740",
        package="nltk",
        version="3.10.3",
        justification=(
            "no patched release exists; nltk is only a transitive dependency of "
            "the `safety` audit tool, Codomyrmex never imports nltk, and the "
            "advisory needs pathsec-enforced model save/load on attacker-chosen "
            "paths (GHSA-8mgp-746c-j5xp)"
        ),
    ),
)


def locked_version(requirement_text: str, package: str) -> str | None:
    """Return the exact version pinned for ``package`` in exported requirements."""
    pattern = re.compile(
        rf"^{re.escape(package)}==([^\s;\\]+)", re.MULTILINE | re.IGNORECASE
    )
    match = pattern.search(requirement_text)
    return match.group(1) if match else None


def applicable_ignores(requirement_text: str) -> list[ScopedIgnore]:
    """Scoped ignores whose exact package version is present in the lock export."""
    return [
        ignore
        for ignore in SCOPED_IGNORES
        if locked_version(requirement_text, ignore.package) == ignore.version
    ]


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

        for ignore in applicable_ignores(requirement_text):
            audit_command.extend(("--ignore-vuln", ignore.advisory))
            print(
                f"Lock audit note: ignoring {ignore.advisory} only for "
                f"{ignore.package}=={ignore.version}: {ignore.justification}.",
                file=sys.stderr,
            )

        return _run(audit_command)


if __name__ == "__main__":
    raise SystemExit(main())
