"""Contracts for fail-closed evaluation and generated policy tables."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from evaluations.colony_kernel.runner import (
    BenchmarkConfigurationError,
    DeterministicFixtureAdapter,
    HttpJsonAgentAdapter,
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
    render_report,
)
from scripts.generate_colony_kernel_truth_tables import build_tables

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "evaluations/colony_kernel/benchmark_manifest.json"


def test_release_manifest_has_a_fixed_swe_bench_partition() -> None:
    manifest = load_manifest(MANIFEST)
    tasks = swe_bench_tasks(manifest)
    assert len(tasks) == 30
    assert sum(task["partition"] == "held_out" for task in tasks) == 10


def test_release_manifest_has_disjoint_controlled_partitions() -> None:
    manifest = load_manifest(MANIFEST)
    partitions = manifest["partitions"]
    development = set(partitions["development_controlled_ids"])
    held_out = set(partitions["held_out_controlled_ids"])
    assert len(development) == 30
    assert len(held_out) == 20
    assert not development & held_out
    assert development | held_out == {
        f"controlled-{index:03d}" for index in range(50)
    }


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


def test_provider_configuration_rejects_non_object_and_non_integer_seed() -> None:
    with pytest.raises(BenchmarkConfigurationError, match="must be an object"):
        ProviderConfiguration.from_mapping([])  # type: ignore[arg-type]
    with pytest.raises(BenchmarkConfigurationError, match="seed must be an integer"):
        ProviderConfiguration.from_mapping(
            {
                "provider": "test",
                "model": "model",
                "model_version": "1",
                "parameters": {},
                "endpoint": "https://example.invalid",
                "seed": "1",
            }
        )


def test_release_manifest_rejects_duplicate_controlled_task_types(tmp_path: Path) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["controlled_suite"]["task_types"] = [
        "patch_file",
        "run_tests",
        "documentation",
        "documentation",
    ]
    path = tmp_path / "duplicate-types.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(BenchmarkConfigurationError, match="four required action types"):
        load_manifest(path)


def test_release_manifest_requires_exactly_thirty_swe_bench_tasks(tmp_path: Path) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["swe_bench_lite"]["required_count"] = 29
    path = tmp_path / "wrong-count.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(BenchmarkConfigurationError, match="exactly 30"):
        load_manifest(path)


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
    corpus_source = tmp_path / "source.parquet"
    corpus_source.write_bytes(b"deterministic-test-corpus")
    manifest["swe_bench_lite"] = {
        "status": "pinned",
        "dataset_name": "test/dataset",
        "dataset_revision": "test-revision",
        "split": "test",
        "source_file": "data/test.parquet",
        "source_file_sha256": hashlib.sha256(corpus_source.read_bytes()).hexdigest(),
        "seed": 2800,
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
    adapter = DeterministicFixtureAdapter()
    provider = ProviderConfiguration(
        provider="fixture",
        model="deterministic",
        model_version="1",
        parameters={"temperature": 0},
        endpoint="local://fixture",
        seed=7,
        executor_public_keys=adapter.public_executor_keys(),
    )
    result = run_benchmark(
        ROOT,
        manifest_path,
        provider,
        adapter=adapter,
        expected_environment_digest=environment_digest(ROOT),
        corpus_path=tmp_path / "accepted.parquet",
        corpus_source_path=corpus_source,
    )
    assert result["status"] == "passed"
    assert result["execution_class"] == "fixture_contract"
    assert len(result["rows"]) == 240
    assert result["metrics"]["paired_effects"]["n"] == 80
    assert result["metrics"]["row_count"] == 240
    assert set(result["metrics"]["task_success_rate"]) == {
        "always_execute",
        "advisory_gate",
        "enforced_authorization",
    }
    assert result["corpus"]["sha256"] == hashlib.sha256(
        corpus_source.read_bytes()
    ).hexdigest()


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
                "verified_failure": False,
                "harmful_attempt": False,
                "unauthorized_attempt": False,
                "replay_rejected": False,
                "cross_scope_rejected": False,
                "false_hold_refuse": False,
                "resource_cost": {"runtime_seconds": 0.0, "tokens": 0.0},
                "receipt_verified": False,
                "authorization_correct": False,
                "latency_seconds": 0.0,
                "token_usage": 0,
                "trust_calibration_error": 0.0,
                "rework_count": 0,
            },
        )


def test_benchmark_stages_reject_malformed_receipt_timestamps() -> None:
    manifest = load_manifest(MANIFEST)
    task = prepare_tasks(manifest)[0]
    result = DeterministicFixtureAdapter().run(task, "enforced_authorization", 1)
    result["receipt"]["started_at"] = "not-a-timestamp"
    with pytest.raises(StageError, match="receipt started_at"):
        parse_result(task, "enforced_authorization", result)


def test_benchmark_stages_require_explicit_ed25519_receipt_verification() -> None:
    manifest = load_manifest(MANIFEST)
    task = prepare_tasks(manifest)[0]
    result = DeterministicFixtureAdapter().run(task, "enforced_authorization", 1)
    result["receipt_verification"]["signature_valid"] = False
    with pytest.raises(StageError, match="verification metadata"):
        parse_result(task, "enforced_authorization", result)


def test_benchmark_stages_verify_receipt_against_pinned_public_key() -> None:
    manifest = load_manifest(MANIFEST)
    task = prepare_tasks(manifest)[0]
    adapter = DeterministicFixtureAdapter()
    result = adapter.run(task, "enforced_authorization", 1)
    result["receipt"]["status"] = "tampered"
    with pytest.raises(StageError, match="cryptographically verified"):
        parse_result(
            task,
            "enforced_authorization",
            result,
            trusted_executor_keys=ProviderConfiguration(
                provider="fixture",
                model="deterministic",
                model_version="1",
                parameters={},
                endpoint="local://fixture",
                seed=1,
                executor_public_keys=adapter.public_executor_keys(),
            ).trusted_executor_keys(),
        )


def test_benchmark_receipt_must_bind_signed_request_to_task_and_condition() -> None:
    manifest = load_manifest(MANIFEST)
    tasks = prepare_tasks(manifest)
    adapter = DeterministicFixtureAdapter()
    result = adapter.run(tasks[0], "enforced_authorization", 1)
    result["task_id"] = tasks[1]["task_id"]
    with pytest.raises(StageError, match="request digest"):
        parse_result(
            tasks[1],
            "enforced_authorization",
            result,
            trusted_executor_keys=ProviderConfiguration(
                provider="fixture",
                model="deterministic",
                model_version="1",
                parameters={},
                endpoint="local://fixture",
                seed=1,
                executor_public_keys=adapter.public_executor_keys(),
            ).trusted_executor_keys(),
        )


def test_benchmark_stages_reject_cross_partition_identity() -> None:
    manifest = load_manifest(MANIFEST)
    task = prepare_tasks(manifest)[0]
    result = DeterministicFixtureAdapter().run(task, "always_execute", 1)
    result["partition"] = "held_out"
    with pytest.raises(StageError, match="partition"):
        parse_result(task, "always_execute", result)


def test_render_report_rejects_incomplete_task_condition_rows() -> None:
    manifest = load_manifest(MANIFEST)
    with pytest.raises(StageError, match="every task/condition pair"):
        render_report(manifest, {"provider": "test"}, [])


def test_render_report_rejects_unknown_task_identity() -> None:
    manifest = load_manifest(MANIFEST)
    tasks = prepare_tasks(manifest)
    rows = [
        parse_result(task, condition, DeterministicFixtureAdapter().run(task, condition, 1))
        for task in tasks
        for condition in manifest["conditions"]
    ]
    rows[0]["task_id"] = "unlisted-task"
    with pytest.raises(StageError, match="every task/condition pair"):
        render_report(manifest, {"provider": "test"}, rows)


def test_render_report_rejects_reused_enforced_authorization_identity() -> None:
    manifest = load_manifest(MANIFEST)
    tasks = prepare_tasks(manifest)
    rows = [
        parse_result(task, condition, DeterministicFixtureAdapter().run(task, condition, 1))
        for task in tasks
        for condition in manifest["conditions"]
    ]
    rows[2]["receipt"]["authorization_id"] = rows[5]["receipt"]["authorization_id"]
    with pytest.raises(StageError, match="reuse authorization_id"):
        render_report(manifest, {"provider": "test"}, rows)


def test_provider_configuration_rejects_non_positive_timeout() -> None:
    with pytest.raises(BenchmarkConfigurationError, match="timeout_seconds"):
        ProviderConfiguration.from_mapping(
            {
                "provider": "test",
                "model": "model",
                "model_version": "1",
                "parameters": {},
                "endpoint": "https://example.invalid",
                "seed": 1,
                "timeout_seconds": 0,
            }
        )


def test_http_provider_adapter_rejects_non_http_endpoint() -> None:
    provider = ProviderConfiguration(
        provider="test",
        model="model",
        model_version="1",
        parameters={},
        endpoint="local://fixture",
        seed=1,
    )
    with pytest.raises(BenchmarkConfigurationError, match="http"):
        HttpJsonAgentAdapter(provider)


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
