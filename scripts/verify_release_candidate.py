#!/usr/bin/env python3
"""Verify release-manifest gates without mutating the checkout."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

REQUIRED_TEST_KEYS = ("collected", "passed", "skipped", "failed", "errors")
REQUIRED_ARTIFACTS = (
    "output/paper.pdf",
    "output/data/manuscript_variables.json",
    "output/data/colony_kernel_coverage.json",
    "output/data/colony_kernel_test_report.xml",
    "output/data/colony_kernel_test_status.json",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(root: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures: list[str] = []
    git_status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    if manifest.get("git", {}).get("dirty") or git_status:
        failures.append("checkout is dirty")
    status = manifest.get("test_status", {})
    for key in REQUIRED_TEST_KEYS:
        if key not in status:
            failures.append(f"test status is missing {key}")
    if any(int(status.get(key, 1)) != 0 for key in ("skipped", "failed", "errors")):
        failures.append("required tests have skips, failures, or errors")
    if int(status.get("passed", 0)) != int(status.get("collected", 0)):
        failures.append("passed count does not equal collected count")
    for relative in REQUIRED_ARTIFACTS:
        path = root / relative
        expected = manifest.get("artifact_hashes", {}).get(relative)
        if not path.is_file():
            failures.append(f"required artifact is missing: {relative}")
        elif expected != sha256(path):
            failures.append(f"artifact hash mismatch: {relative}")
        if not manifest.get("artifact_freshness", {}).get(relative, False):
            failures.append(f"artifact is stale: {relative}")
    benchmark = manifest.get("benchmark", {})
    if not benchmark.get("ready") or benchmark.get("status") != "passed":
        failures.append("benchmark manifest/results are not passed and pinned")
    if manifest.get("publication_ready") is not True:
        failures.append("manifest publication_ready is false")
    return {
        "status": "passed" if not failures else "failed",
        "failures": failures,
        "commit_sha": manifest.get("git", {}).get("commit_sha"),
        "tag": manifest.get("git", {}).get("tag"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("output/release_manifest.json"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest_path = args.manifest if args.manifest.is_absolute() else root / args.manifest
    try:
        report = verify(root, manifest_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "failed", "failures": [str(exc)]}))
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
