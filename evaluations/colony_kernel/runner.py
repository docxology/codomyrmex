"""Fail-closed, provider-neutral Colony Kernel benchmark runner.

The manifest pins the SWE-bench Lite revision and issue IDs. A real provider adapter and
fully specified model configuration are required before any result can be reported as
release evidence; deterministic fixtures are reserved for contract tests.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import statistics
import subprocess
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


class BenchmarkConfigurationError(RuntimeError):
    """Raised when a release benchmark input is missing or inconsistent."""


REQUIRED_CONDITIONS = (
    "always_execute",
    "advisory_gate",
    "enforced_authorization",
)
REQUIRED_CONTROLLED_TASK_TYPES = frozenset(
    {"patch_file", "run_tests", "documentation", "archive_module"}
)


@dataclass(frozen=True)
class ProviderConfiguration:
    provider: str
    model: str
    model_version: str
    parameters: dict[str, Any]
    endpoint: str
    seed: int
    auth_env: str | None = None
    timeout_seconds: float = 300.0

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
        timeout_seconds = raw.get("timeout_seconds", 300.0)
        if (
            isinstance(timeout_seconds, bool)
            or not isinstance(timeout_seconds, (int, float))
            or not math.isfinite(float(timeout_seconds))
            or timeout_seconds <= 0
        ):
            raise BenchmarkConfigurationError("timeout_seconds must be a positive finite number")
        return cls(
            provider=str(raw["provider"]),
            model=str(raw["model"]),
            model_version=str(raw["model_version"]),
            parameters=dict(raw["parameters"]),
            endpoint=str(raw["endpoint"]),
            seed=int(raw["seed"]),
            auth_env=str(raw["auth_env"]) if raw.get("auth_env") else None,
            timeout_seconds=float(timeout_seconds),
        )

    def public_mapping(self) -> dict[str, Any]:
        """Return reproducibility metadata without materializing secret values."""

        return {
            "provider": self.provider,
            "model": self.model,
            "model_version": self.model_version,
            "parameters": self.parameters,
            "endpoint": self.endpoint,
            "seed": self.seed,
            "auth_env": self.auth_env,
            "timeout_seconds": self.timeout_seconds,
        }


class AgentAdapter(Protocol):
    """Provider-neutral interface for an evaluated agent."""

    def run(self, task: dict[str, Any], condition: str, seed: int) -> dict[str, Any]:
        """Return a structured proposal/result record."""


class HttpJsonAgentAdapter:
    """Provider-neutral JSON-over-HTTP adapter for the release harness.

    The endpoint must return the structured result schema validated by
    ``evaluations.colony_kernel.stages.parse_result``. Authentication is read
    from the named environment variable and is never written to reports.
    """

    def __init__(self, configuration: ProviderConfiguration) -> None:
        if not configuration.endpoint.startswith(("http://", "https://")):
            raise BenchmarkConfigurationError(
                "provider endpoint must use http:// or https:// for release runs"
            )
        self.configuration = configuration

    def run(self, task: dict[str, Any], condition: str, seed: int) -> dict[str, Any]:
        payload = {
            "provider": self.configuration.provider,
            "model": self.configuration.model,
            "model_version": self.configuration.model_version,
            "parameters": self.configuration.parameters,
            "task": task,
            "condition": condition,
            "seed": seed,
        }
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.configuration.auth_env:
            token = os.environ.get(self.configuration.auth_env)
            if not token:
                raise BenchmarkConfigurationError(
                    f"authentication environment variable is unset: {self.configuration.auth_env}"
                )
            headers["Authorization"] = f"Bearer {token}"
        request = urllib.request.Request(
            self.configuration.endpoint,
            data=json.dumps(payload, sort_keys=True).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(
                request, timeout=self.configuration.timeout_seconds
            ) as response:
                result = json.loads(response.read().decode("utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise BenchmarkConfigurationError(f"provider adapter request failed: {exc}") from exc
        if not isinstance(result, dict):
            raise BenchmarkConfigurationError("provider adapter response must be a JSON object")
        return result


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
    task_id_prefix = suite.get("task_id_prefix")
    task_types = suite.get("task_types")
    if (
        not isinstance(task_id_prefix, str)
        or not task_id_prefix
        or not isinstance(task_types, list)
        or set(task_types) != REQUIRED_CONTROLLED_TASK_TYPES
    ):
        raise BenchmarkConfigurationError(
            "controlled suite must declare the four required action types and a task prefix"
        )
    controlled_ids = {
        f"{task_id_prefix}{index:03d}" for index in range(int(suite["task_count"]))
    }
    partitions = data.get("partitions", {})
    development_controlled = set(partitions.get("development_controlled_ids", []))
    held_out_controlled = set(partitions.get("held_out_controlled_ids", []))
    if (
        len(development_controlled) != 30
        or len(held_out_controlled) != 20
        or development_controlled & held_out_controlled
        or development_controlled | held_out_controlled != controlled_ids
    ):
        raise BenchmarkConfigurationError(
            "controlled development and held-out IDs must partition all 50 tasks"
        )
    swe = data.get("swe_bench_lite", {})
    issue_ids = swe.get("issue_ids", [])
    required_swe_fields = (
        "dataset_name",
        "dataset_revision",
        "split",
        "source_file",
        "source_file_sha256",
        "seed",
    )
    if (
        swe.get("status") != "pinned"
        or any(swe.get(field) in (None, "") for field in required_swe_fields)
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
    if tuple(data.get("conditions", [])) != REQUIRED_CONDITIONS:
        raise BenchmarkConfigurationError("all three required benchmark conditions must be present")
    requirements = data.get("requirements", {})
    if any(requirements.get(key) is not True for key in (
        "environment_digest", "signed_receipts", "verified_results", "zero_required_protocol_errors"
    )):
        raise BenchmarkConfigurationError("all release benchmark evidence requirements must be true")
    return data


def expected_benchmark_keys(manifest: dict[str, Any]) -> set[tuple[str, str]]:
    """Return the complete task/condition key set required in a release report."""

    tasks = [*controlled_tasks(manifest), *swe_bench_tasks(manifest)]
    return {
        (str(task["task_id"]), condition)
        for task in tasks
        for condition in REQUIRED_CONDITIONS
    }


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
    """Compute paired differences and a deterministic normal-approximation interval."""

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
        return {
            "n": 0,
            "mean_difference": None,
            "standard_error": None,
            "ci95": [None, None],
            "ci95_method": "normal_approximation",
        }
    mean = statistics.fmean(pairs)
    if len(pairs) == 1:
        lower = upper = mean
        standard_error = 0.0
    else:
        standard_error = statistics.stdev(pairs) / math.sqrt(len(pairs))
        margin = statistics.NormalDist().inv_cdf(0.975) * standard_error
        lower = max(-1.0, mean - margin)
        upper = min(1.0, mean + margin)
    return {
        "n": len(pairs),
        "mean_difference": mean,
        "standard_error": standard_error,
        "ci95": [lower, upper],
        "ci95_method": "normal_approximation",
    }


class DeterministicFixtureAdapter:
    """A non-provider baseline adapter for contract tests only."""

    def run(self, task: dict[str, Any], condition: str, seed: int) -> dict[str, Any]:
        del seed
        success = condition != "always_execute" or task["action_type"] != "archive_module"
        enforced = condition == "enforced_authorization"
        return {
            "task_id": task["task_id"],
            "condition": condition,
            "task_success": bool(success),
            "verified_failure": not success,
            "harmful_attempt": condition == "always_execute" and not success,
            "unauthorized_attempt": condition == "always_execute",
            "replay_rejected": False,
            "cross_scope_rejected": False,
            "false_hold_refuse": False,
            "receipt_verified": enforced,
            "authorization_correct": enforced,
            "latency_seconds": 0.0,
            "token_usage": 0,
            "trust_calibration_error": 0.0,
            "rework_count": 0,
            "receipt": (
                {
                    "authorization_id": f"fixture-auth:{task['task_id']}",
                    "proposal_id": f"fixture-proposal:{task['task_id']}",
                    "executor_id": "fixture-executor",
                    "action_digest": "fixture-action-digest",
                    "result_digest": "fixture-result-digest",
                    "started_at": 0.0,
                    "completed_at": 0.0,
                    "exit_code": 0 if success else 1,
                    "status": "completed" if success else "failed",
                    "executor_key_id": "fixture-key",
                    "signature": "fixture-signature",
                    "request_digest": "fixture-request-digest",
                }
                if enforced
                else None
            ),
            "receipt_verification": (
                {
                    "algorithm": "Ed25519",
                    "public_key_id": "fixture-key",
                    "signature_valid": True,
                }
                if enforced
                else None
            ),
            "resource_cost": {"runtime_seconds": 0.0, "tokens": 0.0},
        }


def run_benchmark(
    root: Path,
    manifest_path: Path,
    provider_config: ProviderConfiguration,
    *,
    adapter: AgentAdapter | None = None,
    expected_environment_digest: str | None = None,
    corpus_path: Path | None = None,
    corpus_source_path: Path | None = None,
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
        acquire_pinned_task_corpus,
        parse_result,
        prepare_tasks,
        render_report,
    )

    default_corpus_path = (
        root
        / "output/evaluations/colony_kernel/corpus"
        / Path(manifest["swe_bench_lite"]["source_file"]).name
    )
    try:
        acquired_corpus = acquire_pinned_task_corpus(
            manifest,
            corpus_path or default_corpus_path,
            source_path=corpus_source_path,
        )
    except StageError as exc:
        raise BenchmarkConfigurationError(str(exc)) from exc

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
    report = render_report(manifest, provider_config.public_mapping(), rows)
    report["environment_digest"] = actual_environment_digest
    try:
        corpus_report_path = str(acquired_corpus.relative_to(root))
    except ValueError:
        corpus_report_path = str(acquired_corpus)
    report["corpus"] = {
        "path": corpus_report_path,
        "sha256": _sha256(acquired_corpus),
    }
    report["provider_config_digest"] = hashlib.sha256(
        json.dumps(provider_config.public_mapping(), sort_keys=True).encode("utf-8")
    ).hexdigest()
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
    parser.add_argument("--corpus", type=Path)
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
            adapter=HttpJsonAgentAdapter(provider),
            expected_environment_digest=args.environment_digest,
            corpus_path=args.corpus,
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError, BenchmarkConfigurationError) as exc:
        print(f"benchmark refused: {exc}", file=sys.stderr)
        return 2
    output = args.output if args.output.is_absolute() else root / args.output
    _write_json_atomic(output, result)
    print(json.dumps({"status": result["status"], "output": str(output)}))
    return 0


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
