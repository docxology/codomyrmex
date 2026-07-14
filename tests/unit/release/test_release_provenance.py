"""Verifier-first negative controls for release provenance."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from scripts.generate_release_manifest import (
    REQUIRED_ARTIFACTS,
    _aggregate_hash,
    _artifact_freshness,
    artifact_files_for_manifest,
    input_files_for_manifest,
    source_files_for_manifest,
)
from scripts.verify_release_candidate import verify


def _candidate(tmp_path: Path) -> tuple[Path, Path]:
    """Create a minimal real git checkout and internally consistent evidence."""

    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.invalid"],
        cwd=tmp_path,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Release Test"], cwd=tmp_path, check=True
    )
    (tmp_path / "README.md").write_text("candidate\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "candidate"], cwd=tmp_path, check=True)

    data_dir = tmp_path / "output" / "data"
    data_dir.mkdir(parents=True)
    for relative in REQUIRED_ARTIFACTS:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if relative.endswith(".xml"):
            path.write_text(
                '<testsuites><testsuite><testcase name="pass"/></testsuite></testsuites>',
                encoding="utf-8",
            )
        elif relative.endswith("test_status.json"):
            path.write_text(
                json.dumps(
                    {
                        "collected": 1,
                        "passed": 1,
                        "skipped": 0,
                        "failed": 0,
                        "errors": 0,
                    }
                ),
                encoding="utf-8",
            )
        else:
            path.write_text("{}", encoding="utf-8")
    benchmark_manifest = tmp_path / "evaluations/colony_kernel/benchmark_manifest.json"
    benchmark_manifest.parent.mkdir(parents=True)
    benchmark_manifest.write_text("{}", encoding="utf-8")

    source_files = source_files_for_manifest(tmp_path)
    input_files = input_files_for_manifest(tmp_path)
    artifacts = artifact_files_for_manifest(tmp_path)
    freshness = _artifact_freshness([*artifacts], [*source_files, *input_files], tmp_path)
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True, text=True
    ).stdout.strip()
    artifact_hashes = {}
    import hashlib

    for path in artifacts:
        artifact_hashes[str(path.relative_to(tmp_path))] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
    manifest = {
        "publication_ready": False,
        "git": {
            "commit_sha": commit,
            "dirty": False,
            "status_porcelain": "",
            "tag": None,
        },
        "test_status": {"collected": 1, "passed": 1, "skipped": 0, "failed": 0, "errors": 0},
        "artifact_hashes": artifact_hashes,
        "artifact_freshness": freshness,
        "inputs": {
            "source_hash": _aggregate_hash(source_files, tmp_path),
            "lockfile_config_source_hash": _aggregate_hash(input_files, tmp_path),
        },
        "benchmark": {
            "manifest_hash": hashlib.sha256(benchmark_manifest.read_bytes()).hexdigest(),
            "status": "missing",
            "ready": False,
        },
    }
    manifest_path = tmp_path / "output/release_manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return tmp_path, manifest_path


def test_verifier_rejects_manifest_bound_to_another_commit(tmp_path: Path) -> None:
    root, manifest_path = _candidate(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["git"]["commit_sha"] = "0" * 40
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    report = verify(root, manifest_path)

    assert report["status"] == "failed"
    assert "manifest commit does not match the current checkout" in report["failures"]


def test_verifier_rejects_hand_edited_test_status(tmp_path: Path) -> None:
    root, manifest_path = _candidate(tmp_path)
    status_path = root / "output/data/colony_kernel_test_status.json"
    status_path.write_text(
        json.dumps({"collected": 1, "passed": 0, "skipped": 0, "failed": 1, "errors": 0}),
        encoding="utf-8",
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    import hashlib

    manifest["artifact_hashes"]["output/data/colony_kernel_test_status.json"] = hashlib.sha256(status_path.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    report = verify(root, manifest_path)

    assert "manifest test status does not match the status artifact" in report["failures"]


def test_verifier_rejects_manifest_status_that_disagrees_with_junit(
    tmp_path: Path,
) -> None:
    root, manifest_path = _candidate(tmp_path)
    status_path = root / "output/data/colony_kernel_test_status.json"
    status_path.write_text(
        json.dumps({"collected": 1, "passed": 0, "skipped": 0, "failed": 1, "errors": 0}),
        encoding="utf-8",
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["test_status"] = {
        "collected": 1,
        "passed": 0,
        "skipped": 0,
        "failed": 1,
        "errors": 0,
    }
    import hashlib

    manifest["artifact_hashes"]["output/data/colony_kernel_test_status.json"] = hashlib.sha256(
        status_path.read_bytes()
    ).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    report = verify(root, manifest_path)

    assert "test status does not match independently parsed JUnit evidence" in report[
        "failures"
    ]


def test_verifier_rejects_changed_source_inputs(tmp_path: Path) -> None:
    root, manifest_path = _candidate(tmp_path)
    source = root / "src/codomyrmex/colony_kernel/models.py"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("changed\n", encoding="utf-8")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    report = verify(root, manifest_path)

    assert "manifest source hash does not match the checkout" in report["failures"]


def test_verifier_rejects_incomplete_passed_benchmark_result(tmp_path: Path) -> None:
    root, manifest_path = _candidate(tmp_path)
    result_path = root / "output/evaluations/colony_kernel/benchmark.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(
        json.dumps({"status": "passed", "manifest": {}, "rows": [], "metrics": {}}),
        encoding="utf-8",
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    import hashlib

    manifest["benchmark"].update(
        {
            "status": "passed",
            "ready": True,
            "result_hash": hashlib.sha256(result_path.read_bytes()).hexdigest(),
        }
    )
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    report = verify(root, manifest_path)

    assert "benchmark result is missing pinned provider/model metadata" in report[
        "failures"
    ]
    assert "benchmark result is missing required release metrics" in report["failures"]


def test_verifier_rejects_tampered_release_package_hash(tmp_path: Path) -> None:
    root, manifest_path = _candidate(tmp_path)
    package_path = root / "output/release_package.tar.gz"
    package_path.write_bytes(b"candidate-package")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["release_package_hash"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    report = verify(root, manifest_path)

    assert "release package hash does not match the checkout" in report["failures"]
