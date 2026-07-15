"""Unit tests for the versioned paired-binary analysis layer."""

from __future__ import annotations

import pytest
from evaluations.colony_kernel.analysis import (
    ANALYSIS_SCHEMA_VERSION,
    condition_summaries,
    paired_binary_effects,
)
from scripts.analyze_colony_kernel_benchmark import build_analysis, classify_result


def test_paired_analysis_reports_exact_interval_and_mcnemar_counts() -> None:
    rows = [
        {"task_id": "a", "condition": "always_execute", "task_success": True},
        {"task_id": "a", "condition": "enforced_authorization", "task_success": False},
        {"task_id": "b", "condition": "always_execute", "task_success": False},
        {"task_id": "b", "condition": "enforced_authorization", "task_success": True},
    ]

    result = paired_binary_effects(rows)

    assert result["statistics_version"] == ANALYSIS_SCHEMA_VERSION
    assert result["n"] == 2
    assert result["ci95_exact"] == pytest.approx(
        [-0.9748417658, 0.9748417658], abs=1e-9
    )
    assert result["mcnemar"]["discordant_pairs"] == 2
    assert result["mcnemar"]["exact_two_sided_pvalue"] == 1.0


def test_singleton_pair_keeps_a_degenerate_compatibility_interval() -> None:
    rows = [
        {"task_id": "a", "condition": "always_execute", "task_success": True},
        {"task_id": "a", "condition": "enforced_authorization", "task_success": False},
    ]

    result = paired_binary_effects(rows)

    assert result["n"] == 1
    assert result["standard_error"] == 0.0
    assert result["ci95"] == [-1.0, -1.0]


def test_condition_summaries_preserve_partition_denominators() -> None:
    rows = [
        {
            "task_id": "dev-1",
            "condition": "always_execute",
            "partition": "development",
            "task_success": True,
            "verified_failure": False,
            "harmful_attempt": False,
        },
        {
            "task_id": "hold-1",
            "condition": "always_execute",
            "partition": "held_out",
            "task_success": False,
            "verified_failure": True,
            "harmful_attempt": True,
        },
    ]

    result = condition_summaries(rows)

    assert result["row_denominator"] == 2
    assert result["partition_denominators"] == {"development": 1, "held_out": 1}
    assert result["by_partition"]["held_out"]["always_execute"]["harmful_attempt_count"] == 1


def test_paired_analysis_rejects_duplicate_identity() -> None:
    rows = [
        {"task_id": "a", "condition": "always_execute", "task_success": True},
        {"task_id": "a", "condition": "always_execute", "task_success": False},
    ]

    with pytest.raises(ValueError, match="duplicate paired observation"):
        paired_binary_effects(rows)


def test_visualization_input_labels_fixture_as_contractual(tmp_path) -> None:
    result_path = tmp_path / "fixture.json"
    result_path.write_text(
        '{"status": "passed", "execution_class": "fixture_contract", "rows": []}',
        encoding="utf-8",
    )

    payload = build_analysis(result_path)

    assert classify_result({"execution_class": "fixture_contract"})[0] == "fixture_contract"
    assert payload["evidence_status"] == "fixture_contract"
    assert payload["empirical_effect_claim_permitted"] is False
