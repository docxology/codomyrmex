#!/usr/bin/env python3
"""Verify release-manifest gates without mutating the checkout."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

try:  # Direct script execution puts ``scripts`` on sys.path.
    from generate_release_manifest import (
        REQUIRED_ARTIFACTS,
        _aggregate_hash,
        _artifact_freshness,
        artifact_files_for_manifest,
        input_files_for_manifest,
        source_files_for_manifest,
    )
except ModuleNotFoundError:  # Package/test execution resolves from the repo root.
    from scripts.generate_release_manifest import (
        REQUIRED_ARTIFACTS,
        _aggregate_hash,
        _artifact_freshness,
        artifact_files_for_manifest,
        input_files_for_manifest,
        source_files_for_manifest,
    )

REQUIRED_TEST_KEYS = ("collected", "passed", "skipped", "failed", "errors")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_value(root: Path, argv: list[str]) -> tuple[int, str]:
    result = subprocess.run(
        ["git", *argv],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout.strip()


def _parse_junit_status(path: Path) -> dict[str, int]:
    """Parse test outcomes independently of the generated status JSON."""

    if not path.is_file():
        raise RuntimeError(f"JUnit test report is missing: {path}")
    testcases = list(ET.parse(path).getroot().iter("testcase"))
    skipped = sum(case.find("skipped") is not None for case in testcases)
    failed = sum(case.find("failure") is not None for case in testcases)
    errors = sum(case.find("error") is not None for case in testcases)
    collected = len(testcases)
    return {
        "collected": collected,
        "passed": max(0, collected - skipped - failed - errors),
        "skipped": skipped,
        "failed": failed,
        "errors": errors,
    }


def _compare_test_status(
    status: dict[str, Any], junit_status: dict[str, int], failures: list[str]
) -> None:
    try:
        normalized = {key: int(status[key]) for key in REQUIRED_TEST_KEYS}
    except (KeyError, TypeError, ValueError) as exc:
        failures.append(f"test status contains a non-numeric value: {exc}")
        return
    if normalized != junit_status:
        failures.append(
            "test status does not match independently parsed JUnit evidence"
        )
    if normalized["collected"] <= 0:
        failures.append("required test report collected zero tests")
    if normalized["collected"] != sum(normalized[key] for key in REQUIRED_TEST_KEYS[1:]):
        failures.append("test status counts do not sum to collected")


def _read_status_artifact(root: Path, failures: list[str]) -> dict[str, Any] | None:
    path = root / "output/data/colony_kernel_test_status.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"test status artifact cannot be parsed: {exc}")
        return None
    if not isinstance(data, dict):
        failures.append("test status artifact is not a JSON object")
        return None
    return data


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
    manifest_git = manifest.get("git", {})
    commit_code, current_commit = _git_value(root, ["rev-parse", "HEAD"])
    if commit_code != 0:
        failures.append("cannot identify current checkout commit")
    elif manifest_git.get("commit_sha") != current_commit:
        failures.append("manifest commit does not match the current checkout")
    tag_code, current_tag = _git_value(root, ["describe", "--tags", "--exact-match", "HEAD"])
    expected_tag = manifest_git.get("tag")
    if expected_tag and (tag_code != 0 or expected_tag != current_tag):
        failures.append("manifest tag does not match the exact tag on HEAD")
    if manifest.get("publication_ready") is True and not expected_tag:
        failures.append("publication-ready manifest is not pinned to a tag")
    declared_status = manifest_git.get("status_porcelain", "")
    if isinstance(declared_status, list):
        declared_status = "\n".join(str(line) for line in declared_status)
    if declared_status != git_status:
        failures.append("manifest git status does not match the checkout")
    if bool(manifest_git.get("dirty")) != bool(git_status):
        failures.append("manifest dirty flag does not match the checkout")
    if manifest_git.get("dirty") or git_status:
        failures.append("checkout is dirty")
    status = manifest.get("test_status", {})
    for key in REQUIRED_TEST_KEYS:
        if key not in status:
            failures.append(f"test status is missing {key}")
    status_artifact = _read_status_artifact(root, failures)
    if status_artifact is not None:
        for key in REQUIRED_TEST_KEYS:
            if status_artifact.get(key) != status.get(key):
                failures.append("manifest test status does not match the status artifact")
                break
    junit_path = root / "output/data/colony_kernel_test_report.xml"
    try:
        _compare_test_status(status, _parse_junit_status(junit_path), failures)
    except (OSError, ET.ParseError, RuntimeError) as exc:
        failures.append(str(exc))
    try:
        status_values = {key: int(status.get(key, 1)) for key in REQUIRED_TEST_KEYS}
    except (TypeError, ValueError) as exc:
        status_values = dict.fromkeys(REQUIRED_TEST_KEYS, 1)
        failures.append(f"test status contains a non-numeric value: {exc}")
    if any(status_values[key] != 0 for key in ("skipped", "failed", "errors")):
        failures.append("required tests have skips, failures, or errors")
    if status_values["passed"] != status_values["collected"]:
        failures.append("passed count does not equal collected count")
    declared_hashes = manifest.get("artifact_hashes", {})
    if not isinstance(declared_hashes, dict):
        failures.append("manifest artifact_hashes is not an object")
        declared_hashes = {}
    declared_artifacts = set(declared_hashes)
    for relative in sorted(declared_artifacts | set(REQUIRED_ARTIFACTS)):
        path = root / relative
        expected = declared_hashes.get(relative)
        if not path.is_file():
            failures.append(
                f"required artifact is missing: {relative}"
                if relative in REQUIRED_ARTIFACTS
                else f"declared artifact is missing: {relative}"
            )
        elif not isinstance(expected, str) or expected != sha256(path):
            failures.append(f"artifact hash mismatch: {relative}")

    source_files = source_files_for_manifest(root)
    input_files = input_files_for_manifest(root)
    freshness_inputs = [*source_files, *input_files]
    inputs = manifest.get("inputs", {})
    if inputs.get("source_hash") != _aggregate_hash(source_files, root):
        failures.append("manifest source hash does not match the checkout")
    if inputs.get("lockfile_config_source_hash") != _aggregate_hash(input_files, root):
        failures.append("manifest lockfile/config hash does not match the checkout")
    expected_freshness = _artifact_freshness(
        artifact_files_for_manifest(root), freshness_inputs, root
    )
    declared_freshness = manifest.get("artifact_freshness", {})
    for relative, fresh in expected_freshness.items():
        if declared_freshness.get(relative) is not fresh:
            failures.append(f"artifact freshness claim is incorrect: {relative}")

    benchmark_manifest_path = root / "evaluations/colony_kernel/benchmark_manifest.json"
    benchmark = manifest.get("benchmark", {})
    if not benchmark_manifest_path.is_file() or benchmark.get("manifest_hash") != sha256(
        benchmark_manifest_path
    ):
        failures.append("benchmark manifest hash does not match the checkout")
    benchmark_result_path = root / "output/evaluations/colony_kernel/benchmark.json"
    result_hash = benchmark.get("result_hash")
    if result_hash is not None and (
        not benchmark_result_path.is_file() or result_hash != sha256(benchmark_result_path)
    ):
        failures.append("benchmark result hash does not match the checkout")
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
