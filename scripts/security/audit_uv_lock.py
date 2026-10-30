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
import json
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
        advisory="CVE-2026-112940",
        package="filelock",
        version="3.32.7",
        justification="filelock is required by safety to be < 4.0; waiting on upstream for compatibility",
    ),
    ScopedIgnore(
        advisory="CVE-2026-112913",
        package="filelock",
        version="3.32.7",
        justification="filelock is required by safety to be < 4.0; waiting on upstream for compatibility",
    ),
    ScopedIgnore(
        advisory="CVE-2026-112907",
        package="filelock",
        version="3.32.7",
        justification="filelock is required by safety to be < 4.0; waiting on upstream for compatibility",
    ),
    ScopedIgnore(
        advisory="CVE-2026-112938",
        package="filelock",
        version="3.32.7",
        justification="filelock is required by safety to be < 4.0; waiting on upstream for compatibility",
    ),
    ScopedIgnore(
        advisory="CVE-2026-112936",
        package="filelock",
        version="3.32.7",
        justification="filelock is required by safety to be < 4.0; waiting on upstream for compatibility",
    ),
    ScopedIgnore(
        advisory="CVE-2026-112910",
        package="filelock",
        version="3.32.7",
        justification="filelock is required by safety to be < 4.0; waiting on upstream for compatibility",
    ),
    ScopedIgnore(
        advisory="CVE-2026-112909",
        package="filelock",
        version="3.32.7",
        justification="filelock is required by safety to be < 4.0; waiting on upstream for compatibility",
    ),
    ScopedIgnore(
        advisory="CVE-2026-112911",
        package="filelock",
        version="3.32.7",
        justification="filelock is required by safety to be < 4.0; waiting on upstream for compatibility",
    ),
    ScopedIgnore(
        advisory="CVE-2026-112939",
        package="filelock",
        version="3.32.7",
        justification="filelock is required by safety to be < 4.0; waiting on upstream for compatibility",
    ),
    ScopedIgnore(
        advisory="CVE-2026-112915",
        package="filelock",
        version="3.32.7",
        justification="filelock is required by safety to be < 4.0; waiting on upstream for compatibility",
    ),
    ScopedIgnore(
        advisory="CVE-2026-112935",
        package="filelock",
        version="3.32.7",
        justification="filelock is required by safety to be < 4.0; waiting on upstream for compatibility",
    ),
    ScopedIgnore(
        advisory="CVE-2026-112912",
        package="filelock",
        version="3.32.7",
        justification="filelock is required by safety to be < 4.0; waiting on upstream for compatibility",
    ),
    ScopedIgnore(
        advisory="CVE-2026-112908",
        package="filelock",
        version="3.32.7",
        justification="filelock is required by safety to be < 4.0; waiting on upstream for compatibility",
    ),
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


def locked_pairs(requirement_text: str) -> list[tuple[str, str]]:
    """Retain every exact export pin, independent of environment markers."""
    pairs: set[tuple[str, str]] = set()
    for line in requirement_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "--hash=")):
            continue
        match = re.match(r"^([A-Za-z0-9_.-]+)==([^\s;\\]+)", stripped)
        if not match:
            raise ValueError(
                "Lock export contains a dependency without an auditable exact pin"
            )
        name = re.sub(r"[-_.]+", "-", match[1]).lower()
        pairs.add((name, match[2]))
    if not pairs:
        raise ValueError("Lock export contains no auditable packages")
    return sorted(pairs)


def locked_version(requirement_text: str, package: str) -> str | None:
    """Return a pin only when every matching export entry has that version."""
    name = re.sub(r"[-_.]+", "-", package).lower()
    versions = {
        version
        for candidate, version in locked_pairs(requirement_text)
        if candidate == name
    }
    return next(iter(versions)) if len(versions) == 1 else None


def applicable_ignores(requirement_text: str) -> list[ScopedIgnore]:
    """Require an unambiguous reviewed version; conflicting pins fail closed."""
    return [
        ignore
        for ignore in SCOPED_IGNORES
        if locked_version(requirement_text, ignore.package) == ignore.version
    ]


def audit_batches(pairs: list[tuple[str, str]]) -> list[list[tuple[str, str]]]:
    """pip-audit rejects multiple versions of one package in a requirements file."""
    batches: list[list[tuple[str, str]]] = []
    occurrences: dict[str, int] = {}
    for name, version in pairs:
        index = occurrences.get(name, 0)
        if index == len(batches):
            batches.append([])
        batches[index].append((name, version))
        occurrences[name] = index + 1
    return batches


def apply_scoped_ignores(dependency: dict) -> None:
    """Filter advisories only for this dependency's exact reviewed pin."""
    for ignore in SCOPED_IGNORES:
        if (dependency.get("name"), dependency.get("version")) != (
            ignore.package,
            ignore.version,
        ):
            continue
        retained = []
        for vulnerability in dependency.get("vulns", []):
            ids = {vulnerability.get("id"), *vulnerability.get("aliases", [])}
            if ignore.advisory in ids:
                ignored = dict(vulnerability, justification=ignore.justification)
                dependency.setdefault("ignored_vulns", []).append(ignored)
            else:
                retained.append(vulnerability)
        dependency["vulns"] = retained


def validate_batch_report(
    result: dict, batch: list[tuple[str, str]], status: int
) -> list[dict]:
    """Reject incomplete, malformed or exit-status-inconsistent evidence."""
    observed = result["dependencies"]
    if not isinstance(observed, list) or any(
        not isinstance(dep, dict) for dep in observed
    ):
        raise ValueError("advisory report dependencies must be objects")
    observed_pairs = {(dep["name"], dep["version"]) for dep in observed}
    if observed_pairs != set(batch) or len(observed) != len(batch):
        raise ValueError("advisory report does not cover every requested pin")
    for dependency in observed:
        if "skip_reason" in dependency or not isinstance(dependency.get("vulns"), list):
            raise ValueError("dependency advisory collection was incomplete")
        for vulnerability in dependency["vulns"]:
            if (
                not isinstance(vulnerability, dict)
                or not isinstance(vulnerability.get("id"), str)
                or not vulnerability["id"]
            ):
                raise ValueError("advisory identity was missing or malformed")
            for key in ("aliases", "fix_versions"):
                values = vulnerability.get(key, [])
                if not isinstance(values, list) or any(
                    not isinstance(value, str) for value in values
                ):
                    raise ValueError("advisory metadata was malformed")
    has_findings = any(dep["vulns"] for dep in observed)
    if status != int(has_findings):
        raise ValueError("advisory exit status contradicts the retained report")
    return observed


def render_report(report: dict, format_name: str) -> str:
    """Emit one complete report, retaining version-bound exception evidence."""
    if format_name == "json":
        return json.dumps(report, indent=2) + "\n"
    rows = []
    for dependency in report["dependencies"]:
        for vulnerability in dependency.get("vulns", []):
            rows.append(
                (
                    dependency["name"],
                    dependency["version"],
                    vulnerability["id"],
                    ", ".join(vulnerability.get("fix_versions", [])),
                )
            )
    if format_name == "markdown":
        lines = [
            "| Package | Version | Advisory | Fix versions |",
            "| --- | --- | --- | --- |",
        ]
        lines.extend("| " + " | ".join(row) + " |" for row in rows)
    else:
        lines = ["Package Version Advisory Fix versions"]
        lines.extend(" ".join(row) for row in rows)
    ignored = sum(len(dep.get("ignored_vulns", [])) for dep in report["dependencies"])
    lines.append(
        f"Audited {len(report['dependencies'])} distinct locked pins; {len(rows)} vulnerabilities; {ignored} version-scoped exceptions."
    )
    return "\n".join(lines) + "\n"


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

        try:
            pairs = locked_pairs(requirements.read_text(encoding="utf-8"))
        except ValueError as exc:
            print(f"Lock audit failed: {exc}", file=sys.stderr)
            return 2
        dependencies: list[dict] = []
        for index, batch in enumerate(audit_batches(pairs)):
            # Strip markers only after retaining every exported version. Never
            # resolve or install dependencies during advisory collection.
            batch_input = Path(tmp) / f"batch-{index}.txt"
            batch_report = Path(tmp) / f"batch-{index}.json"
            batch_input.write_text(
                "".join(f"{name}=={version}\n" for name, version in batch),
                encoding="utf-8",
            )
            audit_command = [
                sys.executable,
                "-m",
                "pip_audit",
                "--requirement",
                str(batch_input),
                "--no-deps",
                "--disable-pip",
                "--strict",
                "--format",
                "json",
                "--output",
                str(batch_report),
            ]
            status = _run(audit_command)
            if status not in (0, 1) or not batch_report.exists():
                print(
                    "Lock audit failed to collect a complete advisory report",
                    file=sys.stderr,
                )
                return status or 2
            try:
                result = json.loads(batch_report.read_text(encoding="utf-8"))
                observed = validate_batch_report(result, batch, status)
                for dependency in observed:
                    apply_scoped_ignores(dependency)
                dependencies.extend(observed)
            except (ValueError, KeyError, TypeError) as exc:
                print(f"Lock audit failed: {exc}", file=sys.stderr)
                return 2
        dependencies.sort(key=lambda dep: (dep["name"], dep["version"]))
        report = {"dependencies": dependencies, "fixes": []}
        rendered = render_report(report, args.format)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        for dependency in dependencies:
            for ignored in dependency.get("ignored_vulns", []):
                print(
                    f"Lock audit note: ignoring {ignored['id']} only for {dependency['name']}=={dependency['version']}: {ignored['justification']}",
                    file=sys.stderr,
                )
        return int(any(dep["vulns"] for dep in dependencies))


if __name__ == "__main__":
    raise SystemExit(main())
