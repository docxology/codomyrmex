"""Verifier-first negative controls for release provenance."""

from __future__ import annotations

import base64
import hashlib
import json
import subprocess
from pathlib import Path

from evaluations.colony_kernel.runner import (
    DeterministicFixtureAdapter,
    ProviderConfiguration,
    load_manifest,
)
from evaluations.colony_kernel.stages import parse_result, prepare_tasks, render_report
from scripts.generate_release_manifest import (
    REQUIRED_ARTIFACTS,
    _aggregate_hash,
    _artifact_freshness,
    artifact_files_for_manifest,
    input_files_for_manifest,
    source_files_for_manifest,
)
from scripts.package_release_evidence import package
from scripts.verify_release_candidate import (
    _environment_digest,
    _provider_config_digest,
    verify,
)

from codomyrmex.colony_kernel.authorization import Ed25519Authority


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


def test_verifier_fails_closed_for_a_non_object_manifest(tmp_path: Path) -> None:
    root, manifest_path = _candidate(tmp_path)
    manifest_path.write_text("[]", encoding="utf-8")

    report = verify(root, manifest_path)

    assert report["status"] == "failed"
    assert "release manifest must be a JSON object" in report["failures"]


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
    registry = root / "evaluations/colony_kernel/executor_key_registry.json"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(
        json.dumps({"registry_version": "2", "keys": {}, "key_classes": {}}),
        encoding="utf-8",
    )
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


def test_verifier_rejects_structurally_valid_fixture_evidence(tmp_path: Path) -> None:
    """A signed fixture result must never satisfy the provider release gate."""

    root, manifest_path = _candidate(tmp_path)
    authority = Ed25519Authority.generate()
    encoded_key = base64.urlsafe_b64encode(authority.public_key).decode("ascii")
    registry = root / "evaluations/colony_kernel/executor_key_registry.json"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(
        json.dumps(
            {
                "registry_version": "2",
                "status": "test-fixture",
                "keys": {authority.key_id: encoded_key},
                "key_classes": {authority.key_id: "fixture_contract"},
            }
        ),
        encoding="utf-8",
    )
    result_path = root / "output/evaluations/colony_kernel/benchmark.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    provider = {
        "provider": "fixture",
        "model": "deterministic",
        "model_version": "1",
        "parameters": {},
        "endpoint": "https://fixture.invalid",
        "seed": 1,
        "executor_public_keys": {authority.key_id: encoded_key},
    }
    result_path.write_text(
        json.dumps(
            {
                "status": "passed",
                "execution_class": "fixture_contract",
                "manifest": {},
                "provider": provider,
                "rows": [],
                "metrics": {},
            }
        ),
        encoding="utf-8",
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["benchmark"].update(
        {
            "status": "passed",
            "ready": True,
            "result_hash": hashlib.sha256(result_path.read_bytes()).hexdigest(),
        }
    )
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    report = verify(root, manifest_path)

    assert (
        "benchmark result is not provider-backed; fixture_contract evidence cannot unlock release"
        in report["failures"]
    )
    assert "provider benchmark executor keys must be classified as provider_backed" in report[
        "failures"
    ]


def test_verifier_rejects_forged_metrics_even_with_complete_rows(tmp_path: Path) -> None:
    """A complete signed matrix cannot override recomputed release metrics."""

    root, manifest_path = _candidate(tmp_path)
    repository_root = Path(__file__).resolve().parents[3]
    benchmark_manifest = load_manifest(
        repository_root / "evaluations/colony_kernel/benchmark_manifest.json"
    )
    benchmark_manifest_path = root / "evaluations/colony_kernel/benchmark_manifest.json"
    benchmark_manifest_path.write_text(json.dumps(benchmark_manifest), encoding="utf-8")
    for relative in ("pyproject.toml", "uv.lock"):
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((repository_root / relative).read_bytes())

    adapter = DeterministicFixtureAdapter()
    registry_keys = adapter.public_executor_keys()
    registry = root / "evaluations/colony_kernel/executor_key_registry.json"
    registry.write_text(
        json.dumps(
            {
                "registry_version": "2",
                "keys": registry_keys,
                "key_classes": dict.fromkeys(registry_keys, "provider_backed"),
            }
        ),
        encoding="utf-8",
    )
    provider = {
        "provider": "fixture-replay",
        "model": "deterministic",
        "model_version": "1",
        "parameters": {},
        "endpoint": "https://provider.example.invalid/run",
        "seed": 1,
        "executor_public_keys": registry_keys,
    }
    trusted_keys = ProviderConfiguration.from_mapping(provider).trusted_executor_keys()
    rows = [
        parse_result(task, condition, adapter.run(task, condition, 1), trusted_executor_keys=trusted_keys)
        for task in prepare_tasks(benchmark_manifest)
        for condition in benchmark_manifest["conditions"]
    ]
    calculated = render_report(
        provider=provider, manifest=benchmark_manifest, rows=rows
    )["metrics"]
    forged_metrics = dict(calculated)
    forged_metrics["row_count"] = int(calculated["row_count"]) + 1

    corpus = root / "corpus.bin"
    corpus.write_bytes(b"pinned-test-corpus")
    result_path = root / "output/evaluations/colony_kernel/benchmark.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(
        json.dumps(
            {
                "status": "passed",
                "execution_class": "provider_backed",
                "manifest": benchmark_manifest,
                "provider": provider,
                "provider_config_digest": _provider_config_digest(provider),
                "rows": rows,
                "metrics": forged_metrics,
                "corpus": {
                    "sha256": hashlib.sha256(corpus.read_bytes()).hexdigest(),
                    "path": "corpus.bin",
                },
                "environment_digest": _environment_digest(root),
            }
        ),
        encoding="utf-8",
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["inputs"]["lockfile_config_source_hash"] = _aggregate_hash(
        input_files_for_manifest(root), root
    )
    manifest["benchmark"].update(
        {
            "manifest_hash": hashlib.sha256(benchmark_manifest_path.read_bytes()).hexdigest(),
            "status": "passed",
            "ready": True,
            "result_hash": hashlib.sha256(result_path.read_bytes()).hexdigest(),
        }
    )
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    report = verify(root, manifest_path)

    assert "benchmark metrics do not match the validated raw rows" in report["failures"]


def test_provider_digest_uses_runner_normalization() -> None:
    """Equivalent provider inputs must hash to the runner's canonical mapping."""

    raw = {
        "provider": "test",
        "model": "model",
        "model_version": "1",
        "parameters": {"temperature": 0},
        "endpoint": " https://example.invalid ",
        "seed": 7,
        "timeout_seconds": 300,
    }
    normalized = ProviderConfiguration.from_mapping(raw).public_mapping()

    assert _provider_config_digest(raw) == hashlib.sha256(
        json.dumps(normalized, sort_keys=True).encode("utf-8")
    ).hexdigest()
    assert _provider_config_digest(raw) != hashlib.sha256(
        json.dumps(raw, sort_keys=True).encode("utf-8")
    ).hexdigest()


def test_verifier_fails_closed_for_a_non_object_benchmark_result(tmp_path: Path) -> None:
    root, manifest_path = _candidate(tmp_path)
    result_path = root / "output/evaluations/colony_kernel/benchmark.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text("[]", encoding="utf-8")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["benchmark"]["result_hash"] = hashlib.sha256(
        result_path.read_bytes()
    ).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    report = verify(root, manifest_path)

    assert report["status"] == "failed"
    assert "benchmark result is not a passed JSON object" in report["failures"]


def test_verifier_rejects_a_self_asserted_executor_key_registry(tmp_path: Path) -> None:
    root, manifest_path = _candidate(tmp_path)
    authority = Ed25519Authority.generate()
    encoded_key = base64.urlsafe_b64encode(authority.public_key).decode("ascii")
    registry = root / "evaluations/colony_kernel/executor_key_registry.json"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(
        json.dumps(
            {
                "registry_version": "2",
                "keys": {authority.key_id: "not-a-key"},
                "key_classes": {authority.key_id: "provider_backed"},
            }
        ),
        encoding="utf-8",
    )
    result_path = root / "output/evaluations/colony_kernel/benchmark.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    provider = {
        "provider": "test",
        "model": "test",
        "model_version": "1",
        "parameters": {},
        "endpoint": "https://example.invalid",
        "seed": 1,
        "executor_public_keys": {authority.key_id: encoded_key},
    }
    result_path.write_text(
        json.dumps({"status": "passed", "provider": provider}), encoding="utf-8"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["benchmark"]["result_hash"] = hashlib.sha256(
        result_path.read_bytes()
    ).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    report = verify(root, manifest_path)

    assert report["status"] == "failed"
    assert any("trusted executor key registry is invalid" in failure for failure in report["failures"])


def test_verifier_rejects_tampered_release_package_hash(tmp_path: Path) -> None:
    root, manifest_path = _candidate(tmp_path)
    package_path = root / "output/release_package.tar.gz"
    package_path.write_bytes(b"candidate-package")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["release_package_hash"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    report = verify(root, manifest_path)

    assert "release package hash does not match the checkout" in report["failures"]


def test_release_package_hash_is_stable_across_repeated_builds(tmp_path: Path) -> None:
    """The evidence transport hash must not depend on wall-clock time."""

    required = (
        "output/paper.pdf",
        "output/paper.html",
        "output/release_manifest.json",
        "output/data/manuscript_variables.json",
        "output/data/colony_kernel_coverage.json",
        "output/data/colony_kernel_test_report.xml",
        "output/data/colony_kernel_test_status.json",
        "docs/manuscript/RELEASE_PROVENANCE.md",
        "evaluations/colony_kernel/benchmark_manifest.json",
        "evaluations/colony_kernel/executor_key_registry.json",
        "evaluations/colony_kernel/RESEARCH_PROTOCOL.md",
        "evaluations/colony_kernel/truth_tables.json",
        "evaluations/colony_kernel/truth_tables.md",
        "review_artifacts/Codomyrmex_Reproduction_Evidence_Follow_Up_2026-07-13.md",
        "review_artifacts/Codomyrmex_Action_Register_2026-07-13_Follow_Up.xlsx",
        "review_artifacts/Codomyrmex_RedTeam_FirstPrinciples_Science_Follow_Up_2026-07-14.md",
        "output/figures/example.txt",
        "output/manuscript/example.md",
    )
    for relative in required:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if relative == "output/release_manifest.json":
            path.write_text("{}", encoding="utf-8")
        else:
            path.write_bytes(path.as_posix().encode("utf-8"))

    first = package(tmp_path, tmp_path / "output" / "first.tar.gz")
    manifest_path = tmp_path / "output/release_manifest.json"
    manifest_path.write_text(
        json.dumps({"release_package_hash": hashlib.sha256(first.read_bytes()).hexdigest()}),
        encoding="utf-8",
    )
    second = package(tmp_path, tmp_path / "output" / "second.tar.gz")

    assert hashlib.sha256(first.read_bytes()).digest() == hashlib.sha256(
        second.read_bytes()
    ).digest()
