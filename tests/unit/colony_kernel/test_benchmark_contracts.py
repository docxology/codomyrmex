"""Contracts for fail-closed evaluation and generated policy tables."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from evaluations.colony_kernel.runner import (
    BenchmarkConfigurationError,
    DeterministicFixtureAdapter,
    ProviderConfiguration,
    controlled_tasks,
    environment_digest,
    load_manifest,
    paired_effects,
    run_benchmark,
    swe_bench_tasks,
)
from evaluations.colony_kernel.stages import (
    StageError,
    acquire_pinned_task_corpus,
    parse_result,
    prepare_tasks,
)
from scripts.generate_colony_kernel_truth_tables import build_tables

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "evaluations/colony_kernel/benchmark_manifest.json"


def test_release_manifest_has_a_fixed_swe_bench_partition() -> None:
    manifest = load_manifest(MANIFEST)
    tasks = swe_bench_tasks(manifest)
    assert len(tasks) == 30
    assert sum(task["partition"] == "held_out" for task in tasks) == 10


def test_incomplete_swe_bench_manifest_fails_closed(tmp_path: Path) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["swe_bench_lite"]["status"] = "pending-acquisition"
    manifest["swe_bench_lite"]["issue_ids"] = []
    path = tmp_path / "incomplete.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(BenchmarkConfigurationError, match="SWE-bench Lite"):
        load_manifest(path)


def test_controlled_suite_is_exactly_fifty_and_deterministic() -> None:
    raw = json.loads(MANIFEST.read_text(encoding="utf-8"))
    first = controlled_tasks(raw)
    second = controlled_tasks(raw)
    assert len(first) == 50
    assert first == second
    assert first[0]["task_id"] == "controlled-000"
    assert first[-1]["task_id"] == "controlled-049"


def test_provider_configuration_requires_every_release_pin() -> None:
    with pytest.raises(BenchmarkConfigurationError, match="provider configuration"):
        ProviderConfiguration.from_mapping({})


def test_paired_effect_is_reproducible() -> None:
    rows = [
        {"task_id": "a", "condition": "always_execute", "task_success": True},
        {"task_id": "a", "condition": "enforced_authorization", "task_success": False},
        {"task_id": "b", "condition": "always_execute", "task_success": False},
        {"task_id": "b", "condition": "enforced_authorization", "task_success": True},
    ]
    result = paired_effects(rows)
    assert result["n"] == 2
    assert result["mean_difference"] == 0.0
    assert result["ci95"] == [-1.0, 1.0]


def test_controlled_runner_only_runs_after_manifest_is_fully_pinned(tmp_path: Path) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["swe_bench_lite"] = {
        "status": "pinned",
        "dataset_revision": "test-revision",
        "issue_ids": [f"issue-{index:02d}" for index in range(30)],
        "required_count": 30,
    }
    manifest["partitions"]["held_out_swe_bench_ids"] = [
        f"issue-{index:02d}" for index in range(20, 30)
    ]
    manifest["partitions"]["development_swe_bench_ids"] = [
        f"issue-{index:02d}" for index in range(20)
    ]
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    provider = ProviderConfiguration(
        provider="fixture",
        model="deterministic",
        model_version="1",
        parameters={"temperature": 0},
        endpoint="local://fixture",
        seed=7,
    )
    result = run_benchmark(
        ROOT,
        manifest_path,
        provider,
        adapter=DeterministicFixtureAdapter(),
        expected_environment_digest=environment_digest(ROOT),
    )
    assert result["status"] == "passed"
    assert len(result["rows"]) == 240
    assert result["metrics"]["paired_effects"]["n"] == 80


def test_provider_run_without_concrete_adapter_fails_closed(tmp_path: Path) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    provider = ProviderConfiguration(
        provider="unconfigured",
        model="unconfigured",
        model_version="unconfigured",
        parameters={},
        endpoint="local://unconfigured",
        seed=7,
    )
    with pytest.raises(BenchmarkConfigurationError, match="concrete provider adapter"):
        run_benchmark(
            ROOT,
            manifest_path,
            provider,
            expected_environment_digest=environment_digest(ROOT),
        )


def test_benchmark_stages_prepare_and_reject_unverified_receipts() -> None:
    manifest = load_manifest(MANIFEST)
    tasks = prepare_tasks(manifest)
    assert len(tasks) == 80
    assert tasks[0]["action_spec"]["action_type"] == "patch_file"
    with pytest.raises(StageError, match="verified receipt"):
        parse_result(
            tasks[0],
            "enforced_authorization",
            {
                "task_id": tasks[0]["task_id"],
                "condition": "enforced_authorization",
                "task_success": True,
                "unauthorized_attempt": False,
                "resource_cost": {},
                "receipt_verified": False,
            },
        )


def test_acquisition_stage_accepts_only_the_pinned_corpus(tmp_path: Path) -> None:
    manifest = load_manifest(MANIFEST)
    source = tmp_path / "source.parquet"
    source.write_bytes(b"not-the-real-corpus")
    with pytest.raises(StageError, match="digest"):
        acquire_pinned_task_corpus(
            manifest, tmp_path / "accepted.parquet", source_path=source
        )


def test_generated_truth_table_tracks_all_resource_dimensions() -> None:
    tables = build_tables()
    assert tables["budget_dimensions"]["count"] == 7
    assert tables["budget_dimensions"]["resource_cost_fields"] == [
        "llm_calls",
        "runtime_seconds",
        "risk_level",
        "human_attention_minutes",
        "merge_risk",
        "doc_debt",
        "security_exposure",
    ]
    assert tables["severity_policy"][-1]["recommendation"] == "refuse"
