"""Fail-closed, provider-neutral Colony Kernel benchmark runner.

The manifest pins the SWE-bench Lite revision and issue IDs. A real provider adapter and
fully specified model configuration are required before any result can be reported as
release evidence; deterministic fixtures are reserved for contract tests.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import os
import statistics
import subprocess
import sys
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from codomyrmex.colony_kernel.authorization import (
    Ed25519Authority,
    _receipt_payload,
    canonical_json,
)
from codomyrmex.colony_kernel.models import ExecutionReceipt


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
    executor_public_keys: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> ProviderConfiguration:
        if not isinstance(raw, dict):
            raise BenchmarkConfigurationError("provider configuration must be an object")
        required = ("provider", "model", "model_version", "parameters", "endpoint", "seed")
        missing = [
            key
            for key in required
            if key not in {"parameters", "seed"}
            and (not isinstance(raw.get(key), str) or not raw[key].strip())
        ]
        if raw.get("parameters") is None:
            missing.append("parameters")
        if raw.get("seed") is None:
            missing.append("seed")
        if missing:
            raise BenchmarkConfigurationError(
                f"provider configuration is incomplete: {', '.join(missing)}"
            )
        if not isinstance(raw["parameters"], dict):
            raise BenchmarkConfigurationError("provider parameters must be an object")
        if isinstance(raw["seed"], bool) or not isinstance(raw["seed"], int):
            raise BenchmarkConfigurationError("provider seed must be an integer")
        timeout_seconds = raw.get("timeout_seconds", 300.0)
        if (
            isinstance(timeout_seconds, bool)
            or not isinstance(timeout_seconds, (int, float))
            or not math.isfinite(float(timeout_seconds))
            or timeout_seconds <= 0
        ):
            raise BenchmarkConfigurationError("timeout_seconds must be a positive finite number")
        auth_env = raw.get("auth_env")
        if auth_env is not None and (
            not isinstance(auth_env, str) or not auth_env.strip()
        ):
            raise BenchmarkConfigurationError("auth_env must be a non-empty string when provided")
        public_keys = raw.get("executor_public_keys", {})
        if public_keys is None:
            public_keys = {}
        if not isinstance(public_keys, dict) or any(
            not isinstance(key_id, str)
            or not key_id.strip()
            or not isinstance(encoded_key, str)
            or not encoded_key.strip()
            for key_id, encoded_key in public_keys.items()
        ):
            raise BenchmarkConfigurationError(
                "executor_public_keys must map non-empty key IDs to base64 strings"
            )
        for key_id, encoded_key in public_keys.items():
            try:
                public_key = base64.urlsafe_b64decode(encoded_key.encode("ascii"))
            except (ValueError, UnicodeEncodeError) as exc:
                raise BenchmarkConfigurationError(
                    f"executor public key is not valid base64: {key_id}"
                ) from exc
            if len(public_key) != 32 or hashlib.sha256(public_key).hexdigest()[:32] != key_id:
                raise BenchmarkConfigurationError(
                    f"executor public key does not match key ID: {key_id}"
                )
        return cls(
            provider=raw["provider"].strip(),
            model=raw["model"].strip(),
            model_version=raw["model_version"].strip(),
            parameters=dict(raw["parameters"]),
            endpoint=raw["endpoint"].strip(),
            seed=raw["seed"],
            auth_env=auth_env.strip() if auth_env else None,
            timeout_seconds=float(timeout_seconds),
            executor_public_keys={str(key): str(value) for key, value in public_keys.items()},
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
            "executor_public_keys": dict(sorted(self.executor_public_keys.items())),
        }

    def trusted_executor_keys(self) -> dict[str, bytes]:
        """Decode the pinned executor key registry for receipt verification."""

        return {
            key_id: base64.urlsafe_b64decode(encoded.encode("ascii"))
            for key_id, encoded in self.executor_public_keys.items()
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
    if not isinstance(data, dict):
        raise BenchmarkConfigurationError("benchmark manifest must be a JSON object")

    def integer(value: Any, label: str, *, minimum: int | None = None) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise BenchmarkConfigurationError(f"{label} must be an integer")
        if minimum is not None and value < minimum:
            raise BenchmarkConfigurationError(f"{label} must be at least {minimum}")
        return value

    def string_list(value: Any, label: str) -> list[str]:
        if not isinstance(value, list) or any(
            not isinstance(item, str) or not item.strip() for item in value
        ):
            raise BenchmarkConfigurationError(f"{label} must be a list of non-empty strings")
        return value

    def sha256_hex(value: Any, label: str) -> str:
        if not isinstance(value, str) or len(value) != 64:
            raise BenchmarkConfigurationError(f"{label} must be a SHA-256 hex digest")
        try:
            int(value, 16)
        except ValueError as exc:
            raise BenchmarkConfigurationError(f"{label} must be a SHA-256 hex digest") from exc
        return value

    suite = data.get("controlled_suite", {})
    if not isinstance(suite, dict):
        raise BenchmarkConfigurationError("controlled_suite must be an object")
    task_count = integer(suite.get("task_count"), "controlled task_count")
    if task_count != 50:
        raise BenchmarkConfigurationError("controlled suite must contain exactly 50 tasks")
    task_id_prefix = suite.get("task_id_prefix")
    task_types = suite.get("task_types")
    if (
        not isinstance(task_id_prefix, str)
        or not task_id_prefix
        or not isinstance(task_types, list)
        or len(task_types) != len(REQUIRED_CONTROLLED_TASK_TYPES)
        or any(not isinstance(task_type, str) for task_type in task_types)
        or set(task_types) != REQUIRED_CONTROLLED_TASK_TYPES
    ):
        raise BenchmarkConfigurationError(
            "controlled suite must declare the four required action types and a task prefix"
        )
    controlled_ids = {
        f"{task_id_prefix}{index:03d}" for index in range(task_count)
    }
    partitions = data.get("partitions", {})
    if not isinstance(partitions, dict):
        raise BenchmarkConfigurationError("partitions must be an object")
    development_controlled_values = string_list(
        partitions.get("development_controlled_ids"),
        "development_controlled_ids",
    )
    held_out_controlled_values = string_list(
        partitions.get("held_out_controlled_ids"),
        "held_out_controlled_ids",
    )
    development_controlled = set(development_controlled_values)
    held_out_controlled = set(held_out_controlled_values)
    if (
        len(development_controlled_values) != 30
        or len(held_out_controlled_values) != 20
        or len(development_controlled) != len(development_controlled_values)
        or len(held_out_controlled) != len(held_out_controlled_values)
        or development_controlled & held_out_controlled
        or development_controlled | held_out_controlled != controlled_ids
    ):
        raise BenchmarkConfigurationError(
            "controlled development and held-out IDs must partition all 50 tasks"
        )
    swe = data.get("swe_bench_lite", {})
    if not isinstance(swe, dict):
        raise BenchmarkConfigurationError("swe_bench_lite must be an object")
    issue_ids = string_list(swe.get("issue_ids"), "SWE-bench issue_ids")
    required_count = integer(swe.get("required_count"), "SWE-bench required_count")
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
        or any(
            not isinstance(swe.get(field), str) or not swe[field].strip()
            for field in required_swe_fields
            if field != "seed"
        )
        or not isinstance(swe.get("seed"), int)
        or isinstance(swe.get("seed"), bool)
        or not sha256_hex(swe.get("source_file_sha256"), "SWE-bench source_file_sha256")
        or required_count != 30
        or len(issue_ids) != required_count
        or len(set(issue_ids)) != len(issue_ids)
    ):
        raise BenchmarkConfigurationError(
            "SWE-bench Lite revision and exactly 30 predeclared issue IDs are required"
        )
    development_swe_values = string_list(
        partitions.get("development_swe_bench_ids"),
        "development_swe_bench_ids",
    )
    held_out_swe = string_list(
        partitions.get("held_out_swe_bench_ids"),
        "held_out_swe_bench_ids",
    )
    development_swe = set(development_swe_values)
    if (
        len(development_swe_values) != 20
        or len(held_out_swe) != 10
        or len(development_swe) != len(development_swe_values)
        or len(set(held_out_swe)) != len(held_out_swe)
        or not set(held_out_swe).issubset(set(issue_ids))
        or not development_swe.issubset(set(issue_ids))
        or development_swe & set(held_out_swe)
        or development_swe | set(held_out_swe) != set(issue_ids)
    ):
        raise BenchmarkConfigurationError(
            "development and held-out SWE-bench Lite IDs must partition the manifest"
        )
    if data.get("conditions") != list(REQUIRED_CONDITIONS):
        raise BenchmarkConfigurationError("all three required benchmark conditions must be present")
    requirements = data.get("requirements", {})
    if not isinstance(requirements, dict):
        raise BenchmarkConfigurationError("requirements must be an object")
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

    def __init__(self) -> None:
        self._authority = Ed25519Authority.generate()

    def public_executor_keys(self) -> dict[str, str]:
        return {
            self._authority.key_id: base64.urlsafe_b64encode(
                self._authority.public_key
            ).decode("ascii")
        }

    def run(self, task: dict[str, Any], condition: str, seed: int) -> dict[str, Any]:
        del seed
        success = condition != "always_execute" or task["action_type"] != "archive_module"
        enforced = condition == "enforced_authorization"
        receipt = None
        receipt_verification = None
        if enforced:
            receipt = {
                "authorization_id": f"fixture-auth:{task['task_id']}",
                "proposal_id": f"fixture-proposal:{task['task_id']}",
                "executor_id": "fixture-executor",
                "action_digest": "fixture-action-digest",
                "result_digest": "fixture-result-digest",
                "started_at": 0.0,
                "completed_at": 0.0,
                "exit_code": 0 if success else 1,
                "status": "completed" if success else "failed",
                "executor_key_id": self._authority.key_id,
                "signature": "",
                "request_digest": f"fixture-request-digest:{task['task_id']}",
            }
            unsigned = ExecutionReceipt(**receipt)
            receipt["signature"] = self._authority.sign(
                canonical_json(_receipt_payload(unsigned))
            )
            receipt_verification = {
                "algorithm": "Ed25519",
                "public_key_id": self._authority.key_id,
                "signature_valid": True,
            }
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
            "receipt": receipt,
            "receipt_verification": receipt_verification,
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
    trusted_executor_keys = provider_config.trusted_executor_keys()
    if not trusted_executor_keys:
        raise BenchmarkConfigurationError(
            "trusted executor public keys are required for signed benchmark receipts"
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
                    trusted_executor_keys=trusted_executor_keys,
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
