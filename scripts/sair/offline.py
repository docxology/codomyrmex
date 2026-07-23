"""Deterministic, provider-free SAIR evaluation fixtures."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from scripts.sair.evaluate import parse_llm_response
from scripts.sair.utils import (
    compute_file_hash,
    load_jsonl,
    save_json,
    summarize_results,
)


def _rule_verdict(problem: dict[str, Any]) -> tuple[str, float, str]:
    """Apply a deliberately narrow non-LLM rule without reading the label."""

    equation1 = " ".join(str(problem.get("equation1", "")).split())
    equation2 = " ".join(str(problem.get("equation2", "")).split())
    if equation1 and equation1 == equation2:
        return "TRUE", 0.99, "syntactic identity rule"
    return "FALSE", 0.01, "non-identity conservative rule"


def run_offline_evaluation(
    dataset_path: str | Path,
    *,
    condition: str = "offline_rule",
    cheatsheet_path: str | Path | None = None,
    limit: int | None = None,
    seed: int = 0,
    output_file: str | Path | None = None,
) -> dict[str, Any]:
    """Run a deterministic local policy and save a provenance-rich result."""

    if seed < 0:
        raise ValueError("seed must be non-negative")
    dataset = Path(dataset_path)
    if not dataset.is_file():
        raise FileNotFoundError(dataset)
    problems = load_jsonl(str(dataset))
    if limit is not None:
        if limit < 0:
            raise ValueError("limit must be non-negative")
        problems = problems[:limit]
    results: list[dict[str, Any]] = []
    for problem in problems:
        verdict, confidence, rationale = _rule_verdict(problem)
        ground_truth_raw = str(
            problem.get("answer", problem.get("expected_verdict", ""))
        ).upper()
        ground_truth = (
            ground_truth_raw if ground_truth_raw in {"TRUE", "FALSE"} else None
        )
        result = {
            "problem_id": problem.get("id"),
            "equation1": problem.get("equation1"),
            "equation2": problem.get("equation2"),
            "ground_truth": ground_truth,
            "verdict": verdict,
            "confidence": confidence,
            "confidence_status": "reported_offline_rule",
            "confidence_source": "declared_heuristic_not_calibrated",
            "is_correct": verdict == ground_truth if ground_truth else None,
            "log_loss": None,
            "parsed": parse_llm_response(
                f"VERDICT: {verdict}\nCONFIDENCE: {confidence}\nREASONING: {rationale}"
            ),
            "raw_response": rationale,
            "latency": 0.0,
            "memory_delta_mb": 0.0,
            "usage": {"total_tokens": 0},
            "model": "offline-rule-v1",
            "condition": condition,
            "cheatsheet_hash": compute_file_hash(cheatsheet_path)
            if cheatsheet_path
            else None,
            "attempts": 1,
        }
        results.append(result)
    summary = summarize_results(results)
    summary.update(
        {
            "model": "offline-rule-v1",
            "condition": condition,
            "seed": seed,
            "live": False,
            "dataset_sha256": compute_file_hash(dataset),
            "dataset_path": str(dataset),
            "dataset_count": len(problems),
        }
    )
    data = {"schema_version": "1.0", "summary": summary, "results": results}
    data["artifact_sha256"] = hashlib.sha256(
        json.dumps(data, sort_keys=True, default=str).encode()
    ).hexdigest()
    if output_file:
        save_json(data, str(output_file))
    return data


def run_offline_pair(
    dataset_path: str | Path,
    *,
    limit: int | None = None,
    seed: int = 0,
    output_file: str | Path | None = None,
) -> dict[str, Any]:
    """Run paired baseline/refinement policies over identical inputs."""

    baseline = run_offline_evaluation(
        dataset_path, condition="baseline", limit=limit, seed=seed
    )
    refinement = run_offline_evaluation(
        dataset_path, condition="refinement", limit=limit, seed=seed
    )
    pair = {
        "schema_version": "1.0",
        "seed": seed,
        "dataset_sha256": baseline["summary"]["dataset_sha256"],
        "baseline": baseline,
        "refinement": refinement,
        "paired_inputs": baseline["summary"]["dataset_sha256"]
        == refinement["summary"]["dataset_sha256"],
    }
    pair["artifact_sha256"] = hashlib.sha256(
        json.dumps(pair, sort_keys=True, default=str).encode()
    ).hexdigest()
    if output_file:
        save_json(pair, str(output_file))
    return pair


__all__ = ["run_offline_evaluation", "run_offline_pair"]
