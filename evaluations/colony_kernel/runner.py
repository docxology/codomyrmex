"""Fail-closed, provider-neutral Colony Kernel benchmark runner.

The manifest pins the SWE-bench Lite revision and issue IDs, but execution remains
pending until a concrete provider adapter and model configuration are supplied. This
prevents a partial local fixture run from being reported as a release benchmark.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


class BenchmarkConfigurationError(RuntimeError):
    """Raised when a release benchmark input is missing or inconsistent."""


@dataclass(frozen=True)
class ProviderConfiguration:
    provider: str
    model: str
    model_version: str
    parameters: dict[str, Any]
    endpoint: str
    seed: int

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> ProviderConfiguration:
        required = ("provider", "model", "model_version", "parameters", "endpoint", "seed")
        missing = [key for key in required if raw.get(key) in (None, "")]
        if missing:
            raise BenchmarkConfigurationError(
                f"provider configuration is incomplete: {', '.join(missing)}"
            )
        if not isinstance(raw["parameters"], dict):
            raise BenchmarkConfigurationError("provider parameters must be an object")
        return cls(
            provider=str(raw["provider"]),
            model=str(raw["model"]),
            model_version=str(raw["model_version"]),
            parameters=dict(raw["parameters"]),
            endpoint=str(raw["endpoint"]),
            seed=int(raw["seed"]),
        )


class AgentAdapter(Protocol):
    """Provider-neutral interface for an evaluated agent."""

    def run(self, task: dict[str, Any], condition: str, seed: int) -> dict[str, Any]:
        """Return a structured proposal/result record."""


def controlled_tasks(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    suite = manifest["controlled_suite"]
    count = int(suite["task_count"])
    task_types = list(suite["task_types"])
    return [
        {
            "task_id": f"{suite['task_id_prefix']}{index:03d}",
            "action_type": task_types[index % len(task_types)],
            "target": (
                f"src/fixture_{index:03d}.py"
                if index % len(task_types) != 2
                else f"docs/fixture_{index:03d}.md"
            ),
            "seed": int(suite["seed"]) + index,
            "expected": {"task_success": True},
        }
        for index in range(count)
    ]


def swe_bench_tasks(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the fixed SWE-bench task specifications in manifest order."""

    swe = manifest["swe_bench_lite"]
    held_out = set(manifest["partitions"]["held_out_swe_bench_ids"])
    return [
        {
            "task_id": f"swe-{index:03d}",
            "instance_id": instance_id,
            "dataset_revision": swe["dataset_revision"],
            "partition": "held_out" if instance_id in held_out else "development",
            "seed": int(swe.get("seed", 2800)) + index,
            "action_type": "patch_file",
            "target": f"swe_bench/{instance_id}",
            "expected": {"task_success": True},
        }
        for index, instance_id in enumerate(swe["issue_ids"])
    ]


def load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    suite = data.get("controlled_suite", {})
    if int(suite.get("task_count", 0)) != 50:
        raise BenchmarkConfigurationError("controlled suite must contain exactly 50 tasks")
    swe = data.get("swe_bench_lite", {})
    issue_ids = swe.get("issue_ids", [])
    if (
        swe.get("status") != "pinned"
        or swe.get("dataset_revision") in (None, "")
        or len(issue_ids) != int(swe.get("required_count", 30))
        or len(set(issue_ids)) != len(issue_ids)
    ):
        raise BenchmarkConfigurationError(
            "SWE-bench Lite revision and exactly 30 predeclared issue IDs are required"
        )
    development_swe = set(data.get("partitions", {}).get("development_swe_bench_ids", []))
    held_out_swe = data.get("partitions", {}).get("held_out_swe_bench_ids", [])
    if (
        not held_out_swe
        or not development_swe
        or not set(held_out_swe).issubset(set(issue_ids))
        or not development_swe.issubset(set(issue_ids))
        or development_swe & set(held_out_swe)
        or development_swe | set(held_out_swe) != set(issue_ids)
    ):
        raise BenchmarkConfigurationError(
            "development and held-out SWE-bench Lite IDs must partition the manifest"
        )
    if set(data.get("conditions", [])) != {
        "always_execute",
        "advisory_gate",
        "enforced_authorization",
    }:
        raise BenchmarkConfigurationError("all three required benchmark conditions must be present")
    return data


def environment_digest(root: Path) -> str:
    """Digest locked environment metadata used by the benchmark."""

    parts = []
    for relative in ("pyproject.toml", "uv.lock", "evaluations/colony_kernel/benchmark_manifest.json"):
        path = root / relative
        if not path.is_file():
            raise BenchmarkConfigurationError(f"environment input is missing: {relative}")
        parts.append(relative.encode() + b"\0" + path.read_bytes())
    return hashlib.sha256(b"".join(parts)).hexdigest()


def paired_effects(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute deterministic paired differences and a percentile interval."""

    grouped: dict[str, dict[str, float]] = {}
    for row in rows:
        grouped.setdefault(str(row["task_id"]), {})[str(row["condition"])] = float(
            row.get("task_success", 0)
        )
    pairs = [
        values["enforced_authorization"] - values["always_execute"]
        for values in grouped.values()
        if {"enforced_authorization", "always_execute"} <= values.keys()
    ]
    if not pairs:
        return {"n": 0, "mean_difference": None, "ci95": [None, None]}
    ordered = sorted(pairs)
    if len(ordered) < 20:
        lower, upper = ordered[0], ordered[-1]
    else:
        lower = ordered[max(0, int(0.025 * (len(ordered) - 1)))]
        upper = ordered[min(len(ordered) - 1, int(0.975 * (len(ordered) - 1)))]
    return {
        "n": len(pairs),
        "mean_difference": statistics.fmean(pairs),
        "ci95": [lower, upper],
    }


class DeterministicFixtureAdapter:
    """A non-provider baseline adapter for contract tests only."""

    def run(self, task: dict[str, Any], condition: str, seed: int) -> dict[str, Any]:
        del seed
        success = condition != "always_execute" or task["action_type"] != "archive_module"
        return {
            "task_id": task["task_id"],
            "condition": condition,
            "task_success": bool(success),
            "unauthorized_attempt": condition == "always_execute",
            "receipt_verified": condition == "enforced_authorization",
            "receipt": (
                {"fixture": True, "task_id": task["task_id"]}
                if condition == "enforced_authorization"
                else None
            ),
            "resource_cost": {"runtime_seconds": 0.0, "tokens": 0},
        }


def run_benchmark(
    root: Path,
    manifest_path: Path,
    provider_config: ProviderConfiguration,
    *,
    adapter: AgentAdapter | None = None,
    expected_environment_digest: str | None = None,
) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    actual_environment_digest = environment_digest(root)
    if expected_environment_digest not in (None, actual_environment_digest):
        raise BenchmarkConfigurationError("environment digest does not match the manifest input")
    if adapter is None:
        raise BenchmarkConfigurationError(
            "a concrete provider adapter is required; fixture results are test-only"
        )
    from evaluations.colony_kernel.stages import (
        StageError,
        parse_result,
        prepare_tasks,
        render_report,
    )

    tasks = prepare_tasks(manifest)
    rows: list[dict[str, Any]] = []
    for task in tasks:
        for condition in manifest["conditions"]:
            try:
                row = parse_result(
                    task,
                    condition,
                    adapter.run(task, condition, int(task["seed"])),
                )
            except StageError as exc:
                raise BenchmarkConfigurationError(str(exc)) from exc
            rows.append(row)
    report = render_report(manifest, provider_config.__dict__, rows)
    report["environment_digest"] = actual_environment_digest
    return report


def _write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    temporary.replace(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path(__file__).with_name("benchmark_manifest.json"))
    parser.add_argument("--provider-config", type=Path, required=True)
    parser.add_argument("--environment-digest", required=True)
    parser.add_argument("--output", type=Path, default=Path("output/evaluations/colony_kernel/benchmark.json"))
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    try:
        provider = ProviderConfiguration.from_mapping(
            json.loads(args.provider_config.read_text(encoding="utf-8"))
        )
        result = run_benchmark(
            root,
            args.manifest,
            provider,
            expected_environment_digest=args.environment_digest,
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError, BenchmarkConfigurationError) as exc:
        print(f"benchmark refused: {exc}", file=sys.stderr)
        return 2
    output = args.output if args.output.is_absolute() else root / args.output
    _write_json_atomic(output, result)
    print(json.dumps({"status": result["status"], "output": str(output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
