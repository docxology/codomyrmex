#!/usr/bin/env python3
"""Generate machine-readable provenance for a publication candidate.

The manifest is intentionally derived from the evaluated checkout and the
fresh generator artifacts.  It records a dirty tree instead of silently
turning a worktree snapshot into a release claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REQUIRED_ARTIFACTS = (
    "output/paper.pdf",
    "output/data/manuscript_variables.json",
    "output/data/colony_kernel_coverage.json",
    "output/data/colony_kernel_test_report.xml",
    "output/data/colony_kernel_test_status.json",
)

RELEASE_INPUT_PATHS = (
    "pyproject.toml",
    "uv.lock",
    "docs/manuscript/config.yaml",
    "docs/manuscript/manuscript.css",
    "config/colony_kernel/kernel.yaml",
    "evaluations/colony_kernel/benchmark_manifest.json",
)

RELEASE_EVIDENCE_PATHS = (
    "evaluations/colony_kernel/README.md",
    "evaluations/colony_kernel/RESEARCH_PROTOCOL.md",
    "review_artifacts/Codomyrmex_Reproduction_Evidence_Follow_Up_2026-07-13.md",
    "review_artifacts/Codomyrmex_Action_Register_2026-07-13_Follow_Up.xlsx",
    "review_artifacts/Codomyrmex_RedTeam_FirstPrinciples_Science_Follow_Up_2026-07-14.md",
)


def _run(root: Path, argv: list[str]) -> tuple[int, str]:
    result = subprocess.run(
        argv,
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    output = (result.stdout or result.stderr).strip().splitlines()
    return result.returncode, output[0] if output else ""


def _run_lines(root: Path, argv: list[str]) -> tuple[int, list[str]]:
    """Run a command while preserving every output line for provenance."""
    result = subprocess.run(
        argv,
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    output = (result.stdout or result.stderr).strip()
    return result.returncode, output.splitlines() if output else []


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _aggregate_hash(paths: list[Path], root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(str(path.relative_to(root)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _existing_files(root: Path, paths: list[str]) -> list[Path]:
    return [root / path for path in paths if (root / path).is_file()]


def source_files_for_manifest(root: Path) -> list[Path]:
    """Return the source surfaces that determine the release artifacts."""

    paths = [
        *sorted((root / "src" / "codomyrmex" / "colony_kernel").rglob("*.py")),
        *sorted((root / "tests" / "unit" / "colony_kernel").rglob("*.py")),
        root / "src" / "codomyrmex" / "manuscript" / "variables.py",
        *sorted((root / "src" / "codomyrmex" / "manuscript" / "figures").rglob("*.py")),
        *sorted(
            path
            for path in (root / "docs" / "manuscript").glob("*.md")
            if path.name != "RELEASE_PROVENANCE.md"
        ),
        *sorted((root / "config" / "colony_kernel").glob("*")),
        root / "scripts" / "z_generate_manuscript_variables.py",
        root / "scripts" / "generate_manuscript_figures.py",
        root / "scripts" / "compile_manuscript.py",
        root / "scripts" / "generate_release_manifest.py",
        root / "scripts" / "package_release_evidence.py",
        root / "scripts" / "verify_release_candidate.py",
        *sorted((root / "evaluations" / "colony_kernel").glob("*.py")),
        *sorted((root / "evaluations" / "colony_kernel").glob("*.json")),
        *_existing_files(root, list(RELEASE_EVIDENCE_PATHS)),
    ]
    return [path for path in paths if path.is_file()]


def input_files_for_manifest(root: Path) -> list[Path]:
    """Return lockfile and configuration inputs used by the release build."""

    return _existing_files(root, list(RELEASE_INPUT_PATHS))


def artifact_files_for_manifest(root: Path) -> list[Path]:
    """Return generated artifacts present in the evaluated checkout."""

    return _existing_files(
        root,
        [
            *REQUIRED_ARTIFACTS,
            "output/paper.html",
            "output/evaluations/colony_kernel/benchmark.json",
        ],
    )


def _artifact_freshness(
    artifacts: list[Path], source_files: list[Path], root: Path
) -> dict[str, bool]:
    """Return whether each generated artifact postdates the evaluated inputs."""
    if not source_files:
        return {str(path.relative_to(root)): False for path in artifacts}
    newest_source = max(path.stat().st_mtime_ns for path in source_files)
    return {
        str(path.relative_to(root)): path.stat().st_mtime_ns > newest_source
        for path in artifacts
    }


def _tool_versions(root: Path) -> dict[str, str]:
    commands = {
        "python": [sys.executable, "--version"],
        "uv": ["uv", "--version"],
        "pytest": [sys.executable, "-m", "pytest", "--version"],
        "ruff": ["ruff", "--version"],
        "ty": ["ty", "--version"],
        "pandoc": ["pandoc", "--version"],
        "qpdf": ["qpdf", "--version"],
    }
    versions: dict[str, str] = {}
    for name, argv in commands.items():
        try:
            code, output = _run(root, argv)
        except OSError as exc:
            versions[name] = f"unavailable: {exc}"
            continue
        versions[name] = output if code == 0 else f"unavailable: {output}"
    versions["platform"] = platform.platform()
    return versions


def _build_timestamp() -> str:
    """Return a pinned manifest timestamp when SOURCE_DATE_EPOCH is supplied."""
    raw_epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if raw_epoch is None:
        return datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        epoch = int(raw_epoch)
    except ValueError as exc:
        raise RuntimeError("SOURCE_DATE_EPOCH must be an integer Unix timestamp") from exc
    return datetime.fromtimestamp(epoch, tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"required {label} is missing: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"required {label} is not a JSON object: {path}")
    return data


def build_manifest(root: Path, *, extra_commands: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    status_path = root / "output" / "data" / "colony_kernel_test_status.json"
    variables_path = root / "output" / "data" / "manuscript_variables.json"
    coverage_path = root / "output" / "data" / "colony_kernel_coverage.json"
    status = _load_json(status_path, "test status")
    variables = _load_json(variables_path, "manuscript variables")
    coverage = _load_json(coverage_path, "coverage report")

    test_status = {
        key: int(status.get(key, 0))
        for key in ("collected", "passed", "skipped", "failed", "errors")
    }
    totals = coverage.get("totals", {})
    if not isinstance(totals, dict):
        raise RuntimeError("coverage totals are not a JSON object")

    commit_code, commit = _run(root, ["git", "rev-parse", "HEAD"])
    if commit_code != 0:
        raise RuntimeError(f"cannot identify git revision: {commit}")
    status_code, dirty_lines = _run_lines(
        root, ["git", "status", "--porcelain", "--untracked-files=all"]
    )
    if status_code != 0:
        raise RuntimeError(f"cannot identify git status: {dirty_lines}")
    tag_code, tag = _run(root, ["git", "describe", "--tags", "--exact-match", "HEAD"])

    source_files = source_files_for_manifest(root)
    input_paths = input_files_for_manifest(root)
    artifacts = artifact_files_for_manifest(root)
    required_artifacts = set(REQUIRED_ARTIFACTS)
    artifact_paths = {str(path.relative_to(root)) for path in artifacts}
    freshness_inputs = [*source_files, *input_paths]
    artifact_freshness = _artifact_freshness(artifacts, freshness_inputs, root)

    benchmark_manifest_path = root / "evaluations" / "colony_kernel" / "benchmark_manifest.json"
    benchmark_manifest = _load_json(benchmark_manifest_path, "benchmark manifest")
    benchmark_result_path = root / "output" / "evaluations" / "colony_kernel" / "benchmark.json"
    benchmark_result = (
        _load_json(benchmark_result_path, "benchmark result")
        if benchmark_result_path.is_file()
        else {}
    )
    benchmark_ready = (
        benchmark_result.get("status") == "passed"
        and benchmark_manifest.get("swe_bench_lite", {}).get("status") == "pinned"
    )
    key_metadata = {
        name: value
        for name in (
            "COLONY_AUTHORIZATION_KEY_ID",
            "COLONY_EXECUTOR_KEY_ID",
            "COLONY_EVALUATOR_KEY_ID",
        )
        if (value := os.environ.get(name))
    }
    release_package = root / "output" / "release_package.tar.gz"

    commands = [
        {
            "argv": ["uv", "run", "python", "scripts/z_generate_manuscript_variables.py"],
            "exit_code": 0,
        },
        *status.get("commands", []),
        *(extra_commands or []),
    ]
    publication_ready = (
        not dirty_lines
        and required_artifacts.issubset(artifact_paths)
        and all(artifact_freshness.get(path, False) for path in required_artifacts)
        and test_status["skipped"] == 0
        and test_status["failed"] == 0
        and test_status["errors"] == 0
        and benchmark_ready
        and all(int(command.get("exit_code", 1)) == 0 for command in commands)
    )

    return {
        "manifest_version": "1.1",
        "generated_at": _build_timestamp(),
        "reproducible_build": {
            "source_date_epoch": os.environ.get("SOURCE_DATE_EPOCH"),
            "font_and_pdf_id_normalization": "qpdf-qdf-stable-subset-prefixes-and-fixed-id",
        },
        "publication_ready": publication_ready,
        "git": {
            "commit_sha": commit,
            "dirty": bool(dirty_lines),
            "status_porcelain": dirty_lines,
            "tag": tag if tag_code == 0 else None,
        },
        "inputs": {
            "lockfile_config_hashes": {
                str(path.relative_to(root)): _sha256(path) for path in input_paths
            },
            "lockfile_config_source_hash": _aggregate_hash(input_paths, root),
            "source_hash": _aggregate_hash(source_files, root),
        },
        "commands": commands,
        "benchmark": {
            "manifest_hash": _sha256(benchmark_manifest_path),
            "result_hash": _sha256(benchmark_result_path) if benchmark_result_path.is_file() else None,
            "status": benchmark_result.get("status", "missing"),
            "ready": benchmark_ready,
        },
        "signature_metadata": {
            "key_ids": key_metadata,
            "private_keys_recorded": False,
            "public_key_material": "external-key-registry",
        },
        "test_status": test_status,
        "coverage": {
            "line_percent": totals.get("percent_covered"),
            "branch_percent": totals.get("percent_branches_covered"),
            "statements": totals.get("num_statements"),
            "covered_lines": totals.get("covered_lines"),
            "branches": totals.get("num_branches"),
            "covered_branches": totals.get("covered_branches"),
            "floor": variables.get("CONFIG_COVERAGE_FLOOR"),
        },
        "tool_versions": _tool_versions(root),
        "artifact_hashes": {
            str(path.relative_to(root)): _sha256(path) for path in artifacts
        },
        "release_package_hash": _sha256(release_package) if release_package.is_file() else None,
        "artifact_freshness": artifact_freshness,
    }


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("output/release_manifest.json"))
    parser.add_argument(
        "--extra-command",
        action="append",
        default=[],
        help="Command string already executed for this candidate; records exit 0.",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    extras = [
        {"argv": command.split(), "exit_code": 0} for command in args.extra_command
    ]
    manifest = build_manifest(root, extra_commands=extras)
    output = args.output if args.output.is_absolute() else root / args.output
    write_manifest(output, manifest)
    print(json.dumps({"output": str(output), "publication_ready": manifest["publication_ready"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
