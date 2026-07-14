#!/usr/bin/env python3
"""Manuscript variable computation library for Codomyrmex.

All non-trivial logic lives here; the orchestrator
(scripts/z_generate_manuscript_variables.py) is a thin driver.

Public surface
--------------
compute_variables(config_path, project_root) -> dict[str, str]
    Returns every manuscript token as a flat string-keyed, string-valued dict.

Token injection is performed by the project-local orchestrator after this module
returns the complete, validated map.
"""

# SIZE_OK: Token provenance stays centralized for publication auditability.

from __future__ import annotations

import hashlib
import inspect
import json
import math
import os
import platform
import re
import subprocess
import sys
import tomllib
import xml.etree.ElementTree as ET
from dataclasses import fields
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import yaml  # stdlib-compatible: PyYAML

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def inject_manuscript_variables(
    manuscript_dir: Path,
    output_dir: Path,
    variables: dict[str, str],
) -> list[Path]:
    """Resolve every source token before atomically writing hydrated sections.

    The computation module owns substitution so the script remains a thin
    orchestrator. Undefined and unresolved tokens fail before any section is
    written; this prevents partially hydrated manuscript trees.
    """
    sources = sorted(manuscript_dir.glob("[0-9]*.md"))
    preamble = manuscript_dir / "preamble.md"
    if preamble.exists():
        sources.append(preamble)

    hydrated: dict[Path, str] = {}
    for source in sources:
        content = source.read_text(encoding="utf-8")
        required = set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", content))
        missing = required - variables.keys()
        if missing:
            raise RuntimeError(
                f"Undefined manuscript variables in {source.name}: "
                + ", ".join(sorted(missing))
            )
        for key in required:
            content = content.replace("{{" + key + "}}", variables[key])
        unresolved = re.findall(r"\{\{[A-Z0-9_]+\}\}", content)
        if unresolved:
            raise RuntimeError(
                f"Unresolved manuscript variables in {source.name}: "
                + ", ".join(sorted(set(unresolved)))
            )
        hydrated[source] = content

    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for source, content in hydrated.items():
        destination = output_dir / source.name
        temporary = destination.with_name(f".{destination.name}.{os.getpid()}.tmp")
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(destination)
        written.append(destination)
    return written


def inject_via_infrastructure(
    manuscript_dir: Path,
    output_dir: Path,
    variables: dict[str, str],
) -> list[Path]:
    """Compatibility alias for the deterministic local injection contract."""
    return inject_manuscript_variables(manuscript_dir, output_dir, variables)


def _count_python_files(directory: Path) -> int:
    """Count *.py files directly inside *directory* (non-recursive)."""
    if not directory.is_dir():
        return 0
    return sum(1 for f in directory.iterdir() if f.suffix == ".py" and f.is_file())


def _count_loc(directory: Path) -> int:
    """Count non-blank, non-comment lines across all *.py files under *directory*."""
    total = 0
    if not directory.is_dir():
        return total
    for py_file in directory.rglob("*.py"):
        try:
            for line in py_file.read_text(
                encoding="utf-8", errors="replace"
            ).splitlines():
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    total += 1
        except OSError:
            pass
    return total


def _count_files_matching(directory: Path, pattern: str) -> int:
    if not directory.is_dir():
        return 0
    return sum(1 for path in directory.glob(pattern) if path.is_file())


def _count_colony_kernel_docs(project_root: Path) -> int:
    return _count_files_matching(
        project_root / "docs" / "modules" / "colony_kernel", "*.md"
    )


def _colony_kernel_test_dir(project_root: Path) -> Path:
    """Return colony-kernel unit test directory (top-level ``tests/`` layout)."""
    top_level = project_root / "tests" / "unit" / "colony_kernel"
    if top_level.is_dir():
        return top_level
    return project_root / "src" / "codomyrmex" / "tests" / "unit" / "colony_kernel"


def _count_colony_kernel_test_suites(project_root: Path) -> int:
    return _count_files_matching(_colony_kernel_test_dir(project_root), "test_*.py")


def _count_colony_kernel_config_files(project_root: Path) -> int:
    config_dir = project_root / "config" / "colony_kernel"
    return _count_files_matching(config_dir, "*.yaml") + _count_files_matching(
        config_dir, "*.yml"
    )


def _count_colony_kernel_mcp_tools(colony_kernel_dir: Path) -> int:
    mcp_tools_py = colony_kernel_dir / "mcp_tools.py"
    if not mcp_tools_py.exists():
        raise RuntimeError(f"MCP tool source is missing: {mcp_tools_py}")
    text = mcp_tools_py.read_text(encoding="utf-8", errors="replace")
    count = text.count("@mcp_tool(")
    if count <= 0:
        raise RuntimeError(f"No @mcp_tool definitions found in {mcp_tools_py}")
    return count


def _count_top_level_modules(src_package_dir: Path) -> int:
    """Count immediate sub-directories of a package dir that contain __init__.py.

    The `tests` directory is a support surface, not a runtime module.
    """
    if not src_package_dir.is_dir():
        return 0
    skip_names = {"tests", "__pycache__"}
    return sum(
        1
        for d in src_package_dir.iterdir()
        if d.is_dir() and (d / "__init__.py").exists() and d.name not in skip_names
    )


def _required_mapping(parent: dict[str, Any], key: str, source: Path) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise RuntimeError(f"Required mapping {key!r} is missing from {source}")
    return value


def _required_list(parent: dict[str, Any], key: str, source: Path) -> list[Any]:
    value = parent.get(key)
    if not isinstance(value, list) or not value:
        raise RuntimeError(f"Required non-empty list {key!r} is missing from {source}")
    return value


def _required_value(parent: dict[str, Any], key: str, source: Path) -> Any:
    if key not in parent or parent[key] is None or parent[key] == "":
        raise RuntimeError(f"Required value {key!r} is missing from {source}")
    return parent[key]


def _extract_float(source: str, pattern: str, label: str) -> float:
    match = re.search(pattern, source, flags=re.DOTALL)
    if match is None:
        raise RuntimeError(f"Could not derive {label} from live runtime source")
    return float(match.group(1))


def _extract_int(source: str, pattern: str, label: str) -> int:
    match = re.search(pattern, source, flags=re.DOTALL)
    if match is None:
        raise RuntimeError(f"Could not derive {label} from live runtime source")
    return int(match.group(1))


def _gate_weights(actuation_gate_source: str) -> dict[str, float]:
    """Read the four live score coefficients from ActuationGate.evaluate."""
    weights: dict[str, float] = {}
    for component in ("budget_ok", "risk_ok", "trust_ok", "completeness"):
        weights[component] = _extract_float(
            actuation_gate_source,
            rf"\b{component}\s*\*\s*([0-9]+(?:\.[0-9]+)?)",
            f"{component} gate weight",
        )
    if not math.isclose(sum(weights.values()), 1.0):
        raise RuntimeError(f"Live ActuationGate weights do not sum to one: {weights}")
    return weights


def _count_falsification_checks(project_root: Path) -> int:
    worker_path = (
        project_root
        / "src"
        / "codomyrmex"
        / "colony_kernel"
        / "falsification"
        / "worker.py"
    )
    source = worker_path.read_text(encoding="utf-8")
    match = re.search(r"\bchecks\s*=\s*\[(.*?)\n\s*\]", source, flags=re.DOTALL)
    if match is None:
        raise RuntimeError(f"Could not locate falsification check registry in {worker_path}")
    count = len(re.findall(r"\bcheck_[a-z_]+\(", match.group(1)))
    if count <= 0:
        raise RuntimeError(f"Falsification check registry is empty in {worker_path}")
    return count


def _count_figure_generators(project_root: Path) -> int:
    orchestrator = (
        project_root
        / "src"
        / "codomyrmex"
        / "manuscript"
        / "figures"
        / "orchestrator.py"
    )
    source = orchestrator.read_text(encoding="utf-8")
    count = len(re.findall(r'^\s*\("[^"]+\.png",\s*fig_', source, flags=re.MULTILINE))
    if count <= 0:
        raise RuntimeError(f"Figure generator registry is empty in {orchestrator}")
    return count


def _coverage_floor(project_root: Path) -> float:
    pyproject = project_root / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    try:
        return float(data["tool"]["coverage"]["report"]["fail_under"])
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError(f"Coverage floor is missing from {pyproject}") from exc


def _format_acknowledgements(entries: list[Any], source: Path) -> str:
    rendered: list[str] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise RuntimeError(f"Acknowledgement {index} is not a mapping in {source}")
        name = str(_required_value(entry, "name", source)).strip()
        contribution = str(_required_value(entry, "contribution", source)).strip()
        rendered.append(f"We thank {name} for {contribution}.")
    return " ".join(rendered)


def _publication_date(raw_value: object) -> str:
    configured = str(raw_value or "").strip()
    if configured and configured.lower() not in {"auto", "today"}:
        return configured
    return date.today().isoformat()


def _display_date(iso_date: str) -> str:
    try:
        parsed = datetime.strptime(iso_date, "%Y-%m-%d").date()
    except ValueError:
        return iso_date
    return f"{parsed:%B} {parsed.day}, {parsed.year}"


def _extract_pytest_count(output: str) -> int:
    patterns = [
        r"collected\s+(\d+)\s+items?",
        r"(\d+)\s+tests?\s+collected",
        r"(\d+)\s+passed\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, output)
        if match:
            return int(match.group(1))
    return 0


def _parse_junit_status(path: Path) -> dict[str, int]:
    """Return collected/passed/skipped/failed/errored counts from JUnit XML."""
    if not path.exists():
        raise RuntimeError(f"JUnit test report is missing: {path}")
    root = ET.parse(path).getroot()
    testcases = list(root.iter("testcase"))
    collected = len(testcases)
    skipped = sum(1 for case in testcases if case.find("skipped") is not None)
    failed = sum(1 for case in testcases if case.find("failure") is not None)
    errored = sum(1 for case in testcases if case.find("error") is not None)
    passed = max(0, collected - skipped - failed - errored)
    return {
        "collected": collected,
        "passed": passed,
        "skipped": skipped,
        "failed": failed,
        "errors": errored,
    }


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write a JSON artifact by replacement, never by partial final writes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    temporary.replace(path)


def _paired_locality_snapshot(
    *, agent_trust: float, recovery_ticks: int
) -> dict[str, Any]:
    """Execute the manuscript's paired locality fixture with real subsystems."""
    from codomyrmex.colony_kernel.kernel import ColonyKernel
    from codomyrmex.colony_kernel.models import (
        ActionProposal,
        AgentTrustProfile,
        SignalType,
    )
    from codomyrmex.colony_kernel.role_adapter import RoleAdapter

    kernel = ColonyKernel()
    try:
        profile = AgentTrustProfile(
            agent_id="manuscript-independent-reviewer",
            trust_score=agent_trust,
            total_proposals=3,
        )
        profile.role = RoleAdapter.infer_role(profile)
        target = "codomyrmex.manuscript.paired_target"
        unrelated_target = "codomyrmex.manuscript.unrelated_target"

        def proposal(target_name: str) -> ActionProposal:
            return ActionProposal(
                agent_id=profile.agent_id,
                agent_type=profile.role.value,
                action_type="patch_file",
                target=target_name,
                rationale="Apply a bounded correction with a verified rollback path.",
                expected_outcome="targeted tests pass",
                rollback_plan="revert the bounded correction",
                evidence={"test": "tests/unit/manuscript/paired_contract"},
            )

        same_target = proposal(target)
        unrelated = proposal(unrelated_target)
        before = kernel.actuation_gate.evaluate(same_target, profile, [], True)

        reported = ActionProposal(
            agent_id="manuscript-outcome-reporter",
            agent_type="reporter",
            action_type="patch_file",
            target=target,
            rationale="Record the paired fixture's failed outcome.",
            expected_outcome="targeted tests fail",
            rollback_plan="revert the paired fixture",
            evidence={"fixture": "paired-locality"},
        )
        kernel.record_outcome(
            reported,
            outcome={"summary": "targeted tests failed"},
            tests_passed=False,
        )

        after = kernel.actuation_gate.evaluate(same_target, profile, [], True)
        unaffected = kernel.actuation_gate.evaluate(unrelated, profile, [], True)
        risk_after = kernel.pheromone_store.sense(target, SignalType.RISK)
        failure_after = kernel.pheromone_store.sense(target, SignalType.FAILURE)

        for _ in range(recovery_ticks):
            kernel.tick()
        recovered = kernel.actuation_gate.evaluate(same_target, profile, [], True)
        risk_recovered = kernel.pheromone_store.sense(target, SignalType.RISK)
        failure_recovered = kernel.pheromone_store.sense(target, SignalType.FAILURE)

        rows = "\n".join(
            [
                "| Same target, before failure | "
                f"0.000 | 0.000 | 0.000 | {before.gate_score:.3f} | {before.decision.value} |",
                "| Same target, after failed outcome | "
                f"{risk_after:.3f} | {failure_after:.3f} | "
                f"{max(risk_after, failure_after):.3f} | {after.gate_score:.3f} | {after.decision.value} |",
                "| Unrelated target, after failed outcome | "
                f"0.000 | 0.000 | 0.000 | {unaffected.gate_score:.3f} | {unaffected.decision.value} |",
                f"| Same target, after {recovery_ticks} passive ticks | "
                f"{risk_recovered:.3f} | {failure_recovered:.3f} | "
                f"{max(risk_recovered, failure_recovered):.3f} | "
                f"{recovered.gate_score:.3f} | {recovered.decision.value} |",
            ]
        )
        return {
            "agent_trust": agent_trust,
            "clear_score": before.gate_score,
            "failure_score": after.gate_score,
            "unrelated_score": unaffected.gate_score,
            "recovered_score": recovered.gate_score,
            "failure_pressure": failure_after,
            "score_change": after.gate_score - before.gate_score,
            "recovery_ticks": recovery_ticks,
            "rows": rows,
        }
    finally:
        kernel.consequence_memory.close()


def _trust_trajectory_rows(
    *,
    checkpoints: list[int],
    initial_trust: float,
    pass_delta: float,
    hard_floor: float,
) -> str:
    from codomyrmex.colony_kernel.models import AgentTrustProfile
    from codomyrmex.colony_kernel.role_adapter import RoleAdapter

    rows: list[str] = []
    for outcome_count in checkpoints:
        trust = min(1.0, initial_trust + outcome_count * pass_delta)
        profile = AgentTrustProfile(
            agent_id="manuscript-trust-trajectory",
            trust_score=trust,
            total_proposals=outcome_count,
        )
        role = RoleAdapter.infer_role(profile)
        if role.value == "sandbox":
            implication = "Role override refuses"
        elif trust < hard_floor:
            implication = "Role changes, but trust remains below the gate floor"
        else:
            implication = "Ordinary scoring reachable"
        rows.append(
            f"| {outcome_count} | {trust:.3f} | {role.value.upper()} | {implication} |"
        )
    return "\n".join(rows)


def _decay_rows(
    *, checkpoints: list[int], evaporation: dict[str, float]
) -> str:
    rows: list[str] = []
    for tick in checkpoints:
        values = [max(0.0, 1.0 - tick * evaporation[name]) for name in evaporation]
        rows.append(
            f"| {tick} | " + " | ".join(f"{value:.2f}" for value in values) + " |"
        )
    return "\n".join(rows)


def _representative_gate_rows(
    *,
    weights: dict[str, float],
    hard_floor: float,
    execute_threshold: float,
    hold_threshold: float,
    missing_field_penalty: float,
) -> str:
    def score(budget: float, hazard: float, trust: float, completeness: float) -> float:
        return (
            budget * weights["budget_ok"]
            + hazard * weights["risk_ok"]
            + trust * weights["trust_ok"]
            + completeness * weights["completeness"]
        )

    def decision(value: float) -> str:
        if value >= execute_threshold:
            return "EXECUTE"
        if value >= hold_threshold:
            return "HOLD"
        return "REFUSE"

    completeness_none = max(0.0, 1.0 - 3 * missing_field_penalty)
    completeness_one = max(0.0, 1.0 - 2 * missing_field_penalty)
    cases = [
        ("SANDBOX, otherwise clear", None, None, None, None, 0.0, "REFUSE override"),
        (
            f"Trust {hard_floor - 0.01:.2f}, otherwise clear",
            None,
            None,
            None,
            None,
            0.0,
            "REFUSE override",
        ),
        (
            "Lower trust, clear, no completeness fields",
            1.0,
            1.0,
            0.5,
            completeness_none,
            score(1.0, 1.0, 0.5, completeness_none),
            "",
        ),
        (
            "Lower trust, clear, one of three fields present",
            1.0,
            1.0,
            0.5,
            completeness_one,
            score(1.0, 1.0, 0.5, completeness_one),
            "",
        ),
        (
            "Lower trust, medium hazard, complete",
            1.0,
            0.5,
            0.5,
            1.0,
            score(1.0, 0.5, 0.5, 1.0),
            "",
        ),
        (
            "Full trust, high hazard, complete",
            1.0,
            0.0,
            1.0,
            1.0,
            score(1.0, 0.0, 1.0, 1.0),
            "",
        ),
        (
            "Full trust, clear, complete",
            1.0,
            1.0,
            1.0,
            1.0,
            score(1.0, 1.0, 1.0, 1.0),
            "",
        ),
    ]
    rows: list[str] = []
    for label, budget, hazard, trust, completeness, value, forced in cases:
        cells = [budget, hazard, trust, completeness]
        rendered = ["—" if cell is None else f"{cell:.2f}" for cell in cells]
        verdict = forced or decision(value)
        rows.append(
            f"| {label} | {' | '.join(rendered)} | {value:.3f} | {verdict} |"
        )
    return "\n".join(rows)


def _run_pytest_json(
    project_root: Path, test_path: Path | None = None
) -> dict[str, Any]:
    cmd = [sys.executable, "-m", "pytest", "--tb=no", "-q", "--no-header", "--co", "-q"]
    if test_path is not None and test_path.is_dir():
        cmd.append(str(test_path))
    result = subprocess.run(
        cmd,
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=60,
    )
    output = f"{result.stdout}\n{result.stderr}".strip()
    if result.returncode != 0:
        raise RuntimeError(
            "pytest collection failed while computing manuscript metrics "
            f"(exit {result.returncode}):\n{output}"
        )

    for line in output.splitlines():
        line = line.strip()
        if ("test" in line and "collected" in line) or "selected" in line:
            parts = line.split()
            for part in parts:
                if part.isdigit():
                    return {"collected": int(part)}
    raise RuntimeError(f"pytest collection did not report a test count:\n{output}")


def _run_colony_kernel_coverage(
    project_root: Path, test_path: Path, coverage_floor: float
) -> dict[str, Any]:
    coverage_path = project_root / "output" / "data" / "colony_kernel_coverage.json"
    junit_path = project_root / "output" / "data" / "colony_kernel_test_report.xml"
    coverage_path.parent.mkdir(parents=True, exist_ok=True)
    # Release evidence is regenerated for the current tree. Final artifacts are
    # removed before the gate and only replaced after every quality gate passes.
    coverage_path.unlink(missing_ok=True)
    junit_path.unlink(missing_ok=True)
    coverage_tmp = coverage_path.with_name(f".{coverage_path.name}.{os.getpid()}.tmp")
    junit_tmp = junit_path.with_name(f".{junit_path.name}.{os.getpid()}.tmp")
    coverage_tmp.unlink(missing_ok=True)
    junit_tmp.unlink(missing_ok=True)
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(test_path),
        "--cov=src/codomyrmex/colony_kernel",
        "--cov-branch",
        f"--cov-report=json:{coverage_tmp}",
        "--cov-report=term",
        f"--cov-fail-under={coverage_floor}",
        f"--junitxml={junit_tmp}",
        "-m",
        "not optional_artifact",
        "--tb=short",
        "-q",
    ]
    result = subprocess.run(
        cmd,
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=600,
    )
    output = f"{result.stdout}\n{result.stderr}".strip()
    try:
        if result.returncode != 0:
            raise RuntimeError(
                "scoped pytest coverage gate failed while computing manuscript metrics "
                f"(exit {result.returncode}):\n{output}"
            )
        if not coverage_tmp.exists():
            raise RuntimeError(f"pytest coverage gate did not create {coverage_tmp}")
        data = json.loads(coverage_tmp.read_text(encoding="utf-8"))
        totals = data.get("totals", {})
        pct = totals.get("percent_branches_covered")
        if pct is None:
            raise RuntimeError(
                f"coverage JSON lacks a branch coverage percent: {coverage_tmp}"
            )
        branch_pct = round(float(pct), 1)
        if branch_pct < coverage_floor:
            raise RuntimeError(
                f"scoped branch coverage {branch_pct:.1f}% is below the configured "
                f"floor {coverage_floor:.1f}%"
            )
        status = _parse_junit_status(junit_tmp)
        if status["skipped"] or status["failed"] or status["errors"]:
            raise RuntimeError(
                "publication test gate requires zero skipped, failed, and errored "
                f"tests; status={status}"
            )
        return {
            **status,
            "coverage_pct": branch_pct,
            "command": cmd,
            "exit_code": result.returncode,
            "coverage_tmp": str(coverage_tmp),
            "junit_tmp": str(junit_tmp),
        }
    except Exception:
        coverage_tmp.unlink(missing_ok=True)
        junit_tmp.unlink(missing_ok=True)
        raise


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------


def compute_variables(
    config_path: Path,
    project_root: Path,
) -> dict[str, str]:
    """Compute all manuscript variables and return them as a flat string dict."""

    # ------------------------------------------------------------------
    # 1. Load config.yaml
    # ------------------------------------------------------------------
    raw_config_bytes = config_path.read_bytes()
    loaded = yaml.safe_load(raw_config_bytes)
    if not isinstance(loaded, dict):
        raise RuntimeError(f"Manuscript configuration is not a mapping: {config_path}")
    config: dict[str, Any] = loaded

    paper = _required_mapping(config, "paper", config_path)
    authors_list = _required_list(config, "authors", config_path)
    keywords_list = _required_list(config, "keywords", config_path)
    acknowledgements = _required_list(config, "acknowledgements", config_path)
    experiment = _required_mapping(config, "experiment", config_path)

    # ------------------------------------------------------------------
    # 2. Derive CONFIG_* from config.yaml
    # ------------------------------------------------------------------

    paper_title = str(_required_value(paper, "title", config_path))
    paper_subtitle = str(_required_value(paper, "subtitle", config_path))
    project_short_name = paper_title.split(":", 1)[0].strip()
    publication_date = _publication_date(_required_value(paper, "date", config_path))
    publication_date_display: str = _display_date(publication_date)
    publication = _required_mapping(config, "publication", config_path)
    doi_value: str = str(
        publication.get("doi")
        or _required_value(publication, "doi_status", config_path)
    )
    github_repository = str(
        _required_value(publication, "github_repository", config_path)
    )
    config_version = str(_required_value(paper, "version", config_path))
    acknowledgement_text = _format_acknowledgements(acknowledgements, config_path)

    first_author_entry = authors_list[0]
    if not isinstance(first_author_entry, dict):
        raise RuntimeError(f"First author entry is not a mapping in {config_path}")
    first_author = str(_required_value(first_author_entry, "name", config_path))
    first_author_orcid = str(_required_value(first_author_entry, "orcid", config_path))
    keywords_str = ", ".join(str(keyword) for keyword in keywords_list)

    # Top-level submodule count from src/codomyrmex/
    codomyrmex_pkg = project_root / "src" / "codomyrmex"
    module_count: int = _count_top_level_modules(codomyrmex_pkg)
    if module_count == 0:
        raise RuntimeError(f"No top-level Codomyrmex modules found under {codomyrmex_pkg}")

    colony_kernel_dir = codomyrmex_pkg / "colony_kernel"
    if not colony_kernel_dir.is_dir():
        raise RuntimeError(f"Colony Kernel source is missing: {colony_kernel_dir}")

    # Runtime policy is authoritative. The manuscript config retains mirrors for
    # figure-generation compatibility, but every mirror is checked below.
    from codomyrmex.agentic_memory.stigmergy.models import StigmergyConfig
    from codomyrmex.colony_kernel.actuation_gate import (
        _FAILURE_PENALTY,
        _GATE_SCORE_EXECUTE,
        _GATE_SCORE_HOLD,
        _HIGH_RISK_THRESHOLD,
        _MED_RISK_THRESHOLD,
        _MISSING_FIELD_PENALTY,
        _TRUST_HARD_FLOOR,
    )
    from codomyrmex.colony_kernel.consequence_memory import (
        _CONSEQUENCE_HISTORY_MAX,
        ConsequenceMemory,
    )
    from codomyrmex.colony_kernel.falsification.models import _SEVERITY_RANK
    from codomyrmex.colony_kernel.falsification_worker import AttackVector
    from codomyrmex.colony_kernel.kernel import ColonyKernel
    from codomyrmex.colony_kernel.models import (
        _TRUST_DELTA_FAIL,
        _TRUST_DELTA_HUMAN_WEIGHT,
        _TRUST_DELTA_PASS,
        _TRUST_DELTA_REPAIR,
        AgentRole,
        DecayRate,
        FalsificationSeverity,
        GateDecision,
        ResourceCost,
        SignalType,
    )
    from codomyrmex.colony_kernel.pheromone_store import (
        _BASE_EVAPORATION,
        _SOURCE_MULTIPLIER,
    )
    from codomyrmex.colony_kernel.pruning_daemon import _PRUNING_MIN_CONFIDENCE
    from codomyrmex.colony_kernel.role_adapter import (
        _DEFAULT_TRUST_SCORE,
        _ROLE_DISPATCHER_MIN_TRUST,
        _ROLE_GUARD_MIN_TRUST,
        _ROLE_MEMORY_MIN_TRUST,
        _ROLE_MIN_PROPOSALS_FOR_PROMOTION,
        _ROLE_REPAIR_MIN_TRUST,
    )

    actuation_gate_path = colony_kernel_dir / "actuation_gate.py"
    actuation_gate_source = actuation_gate_path.read_text(encoding="utf-8")
    kernel_source = (colony_kernel_dir / "kernel.py").read_text(encoding="utf-8")
    pruning_source = (colony_kernel_dir / "pruning_daemon.py").read_text(
        encoding="utf-8"
    )
    gate_weights = _gate_weights(actuation_gate_source)
    gate_weight_budget = gate_weights["budget_ok"]
    gate_weight_risk = gate_weights["risk_ok"]
    gate_weight_trust = gate_weights["trust_ok"]
    gate_weight_completeness = gate_weights["completeness"]

    gate_execute_threshold = float(_GATE_SCORE_EXECUTE)
    gate_hold_threshold = float(_GATE_SCORE_HOLD)
    hazard_high_threshold = float(_HIGH_RISK_THRESHOLD)
    hazard_medium_threshold = float(_MED_RISK_THRESHOLD)
    trust_hard_floor = float(_TRUST_HARD_FLOOR)
    missing_field_penalty = float(_MISSING_FIELD_PENALTY)
    failure_penalty = float(_FAILURE_PENALTY)
    trust_full_credit_threshold = _extract_float(
        actuation_gate_source,
        r"profile\.trust_score\s*>=\s*([0-9]+(?:\.[0-9]+)?)",
        "full trust-credit threshold",
    )
    risk_credit_medium = _extract_float(
        actuation_gate_source,
        r"risk_ok\s*=\s*([0-9]+(?:\.[0-9]+)?)\s*\n\s*else:",
        "medium-hazard credit",
    )
    trust_credit_lower = _extract_float(
        actuation_gate_source,
        r"else:\s*\n\s*trust_ok\s*=\s*([0-9]+(?:\.[0-9]+)?)",
        "lower trust-tier credit",
    )
    recent_failure_threshold = _extract_int(
        actuation_gate_source,
        r"recent_fail_count\s*>=\s*([0-9]+)",
        "recent-failure penalty threshold",
    )
    completeness_field_count = len(
        set(re.findall(r'completeness_flags\["(has_[a-z_]+)"\]', actuation_gate_source))
    )
    if completeness_field_count <= 0:
        raise RuntimeError(f"No completeness fields found in {actuation_gate_path}")

    canonical_failure_strength = _extract_float(
        kernel_source.split("def record_outcome", 1)[1],
        r"signal_type=SignalType\.FAILURE,\s*strength=([0-9]+(?:\.[0-9]+)?)",
        "canonical record_outcome FAILURE strength",
    )

    base_evaporation_rate = float(_BASE_EVAPORATION)
    decay_rate_fast = float(DecayRate.FAST.value)
    decay_rate_normal = float(DecayRate.NORMAL.value)
    decay_rate_slow = float(DecayRate.SLOW.value)
    signal_types_count = len(SignalType)
    decay_rates_count = len(DecayRate)
    role_count = len(AgentRole)
    gate_decision_count = len(GateDecision)
    falsification_vectors = len(AttackVector)
    falsification_check_count = _count_falsification_checks(project_root)
    figure_count = _count_figure_generators(project_root)
    mcp_tool_count = _count_colony_kernel_mcp_tools(colony_kernel_dir)
    budget_dimensions_count = len(fields(ResourceCost))
    field_max_strength = float(StigmergyConfig().max_strength)

    kernel_for_inventory = ColonyKernel()
    try:
        operational_subsystem_count = sum(
            1
            for value in vars(kernel_for_inventory).values()
            if type(value).__module__.startswith("codomyrmex.colony_kernel")
            and type(value).__name__ != "ColonyKernelConfig"
        )
    finally:
        kernel_for_inventory.consequence_memory.close()
    colony_kernel_subsystems = operational_subsystem_count + 1

    recent_failure_window = int(
        inspect.signature(ConsequenceMemory.recent_failures)
        .parameters["window"]
        .default
    )
    consequence_history_max = int(_CONSEQUENCE_HISTORY_MAX)

    trust_sandbox_score = float(_DEFAULT_TRUST_SCORE)
    trust_promote_threshold = float(_ROLE_REPAIR_MIN_TRUST)
    trust_delta_pass = float(_TRUST_DELTA_PASS)
    trust_delta_fail = float(_TRUST_DELTA_FAIL)
    trust_delta_repair = float(_TRUST_DELTA_REPAIR)
    trust_delta_human = float(_TRUST_DELTA_HUMAN_WEIGHT)
    role_min_proposals = int(_ROLE_MIN_PROPOSALS_FOR_PROMOTION)
    role_repair_threshold = float(_ROLE_REPAIR_MIN_TRUST)
    role_memory_threshold = float(_ROLE_MEMORY_MIN_TRUST)
    role_dispatcher_threshold = float(_ROLE_DISPATCHER_MIN_TRUST)
    role_guard_threshold = float(_ROLE_GUARD_MIN_TRUST)

    source_multiplier_test = float(_SOURCE_MULTIPLIER["test"])
    source_multiplier_human = float(_SOURCE_MULTIPLIER["human"])
    source_multiplier_security = float(_SOURCE_MULTIPLIER["security"])
    source_multiplier_agent = float(_SOURCE_MULTIPLIER["agent"])
    source_multiplier_runtime = float(_SOURCE_MULTIPLIER["runtime"])

    pruning_staleness_days = _extract_int(
        pruning_source,
        r"_STALENESS\s*=\s*([0-9]+)\s*\*\s*86400",
        "pruning staleness days",
    )
    pruning_low_call_count = _extract_int(
        pruning_source,
        r"call_count\s*<\s*([0-9]+)",
        "pruning low-call threshold",
    )
    pruning_dependency_veto = _extract_float(
        pruning_source,
        r"SignalType\.DEPENDENCY\)\s*>=\s*([0-9]+(?:\.[0-9]+)?)",
        "pruning dependency veto",
    )
    pruning_duplicate_confidence = _extract_float(
        pruning_source,
        r"reason=f\"duplicate of \{duplicate_of\}\",\s*confidence=([0-9.]+)",
        "duplicate pruning confidence",
    )
    pruning_never_used_confidence = _extract_float(
        pruning_source,
        r'reason="never used since registration",\s*confidence=([0-9.]+)',
        "never-used pruning confidence",
    )
    pruning_stale_confidence = _extract_float(
        pruning_source,
        r'reason=f"no calls; last used .*?confidence=([0-9.]+)',
        "stale pruning confidence",
    )
    pruning_low_usage_confidence = _extract_float(
        pruning_source,
        r'f"low usage .*?confidence=([0-9.]+)',
        "low-usage pruning confidence",
    )
    pruning_min_confidence = float(_PRUNING_MIN_CONFIDENCE)

    dependency_check_source = (
        colony_kernel_dir / "falsification" / "checks" / "dependency_risk.py"
    ).read_text(encoding="utf-8")
    broad_check_source = (
        colony_kernel_dir / "falsification" / "checks" / "over_broad_module.py"
    ).read_text(encoding="utf-8")
    falsification_dependency_threshold = _extract_int(
        dependency_check_source,
        r"len\(risky\)\s*>=\s*([0-9]+)",
        "dependency-risk package threshold",
    )
    falsification_responsibility_threshold = _extract_int(
        broad_check_source,
        r"len\(responsibility_indicators\)\s*>=\s*([0-9]+)",
        "over-broad responsibility threshold",
    )

    severity_rank_low = int(_SEVERITY_RANK[FalsificationSeverity.LOW])
    severity_rank_medium = int(_SEVERITY_RANK[FalsificationSeverity.MEDIUM])
    severity_rank_high = int(_SEVERITY_RANK[FalsificationSeverity.HIGH])
    severity_rank_critical = int(_SEVERITY_RANK[FalsificationSeverity.CRITICAL])

    kernel_config_path = project_root / "config" / "colony_kernel" / "kernel.yaml"
    kernel_config = yaml.safe_load(kernel_config_path.read_text(encoding="utf-8")) or {}
    kernel_budget = kernel_config.get("budget", {})
    if not isinstance(kernel_budget, dict):
        raise RuntimeError(f"budget mapping missing from {kernel_config_path}")
    budget_max_llm_calls = int(kernel_budget["max_llm_calls"])
    budget_max_runtime = int(float(kernel_budget["max_runtime_seconds"]))
    budget_max_risk = float(kernel_budget["max_risk_level"])
    budget_max_security = float(kernel_budget["max_security_exposure"])

    # Proposed-study inputs remain configuration authority.
    agent_count = int(_required_value(experiment, "agent_count", config_path))
    workload_task_count = int(
        _required_value(experiment, "workload_task_count", config_path)
    )
    swe_bench_task_count = int(
        _required_value(experiment, "swe_bench_task_count", config_path)
    )
    warmup_ticks = int(_required_value(experiment, "warmup_ticks", config_path))
    trial_count = int(_required_value(experiment, "trial_count", config_path))
    benchmark_conditions = _required_list(
        experiment, "benchmark_conditions", config_path
    )
    benchmark_condition_count = len(benchmark_conditions)
    trust_checkpoints = [
        int(value)
        for value in _required_list(
            experiment, "trust_trajectory_checkpoints", config_path
        )
    ]
    decay_checkpoints = [
        int(value)
        for value in _required_list(experiment, "decay_table_ticks", config_path)
    ]
    paired_fixture = _required_mapping(experiment, "paired_fixture", config_path)
    paired_agent_trust = float(
        _required_value(paired_fixture, "agent_trust", config_path)
    )
    paired_recovery_ticks = int(
        _required_value(paired_fixture, "recovery_ticks", config_path)
    )

    # Manuscript mirrors must equal live code. They are compatibility inputs for
    # figure modules, never independent authorities.
    float_mirrors = {
        "gate_execute_threshold": gate_execute_threshold,
        "gate_hold_threshold": gate_hold_threshold,
        "trust_sandbox_score": trust_sandbox_score,
        "trust_hard_floor": trust_hard_floor,
        "trust_promote_threshold": trust_promote_threshold,
        "base_evaporation_rate": base_evaporation_rate,
        "trust_delta_pass": trust_delta_pass,
        "trust_delta_fail": trust_delta_fail,
    }
    for key, live_value in float_mirrors.items():
        configured = float(_required_value(experiment, key, config_path))
        if not math.isclose(configured, live_value):
            raise RuntimeError(
                f"Manuscript mirror experiment.{key}={configured} differs from "
                f"live runtime value {live_value}"
            )
    configured_weights = _required_mapping(
        experiment, "gate_score_weights", config_path
    )
    for configured_key, runtime_key in {
        "budget": "budget_ok",
        "risk": "risk_ok",
        "trust": "trust_ok",
        "completeness": "completeness",
    }.items():
        configured = float(
            _required_value(configured_weights, configured_key, config_path)
        )
        if not math.isclose(configured, gate_weights[runtime_key]):
            raise RuntimeError(
                f"Manuscript gate weight {configured_key}={configured} differs from "
                f"live ActuationGate value {gate_weights[runtime_key]}"
            )
    exact_mirrors = {
        "colony_signal_types": [member.name for member in SignalType],
        "decay_rates": [member.name for member in DecayRate],
        "agent_roles": [member.name for member in AgentRole],
        "budget_dimensions": [field.name for field in fields(ResourceCost)],
        "falsification_vectors": falsification_vectors,
        "colony_kernel_subsystems": colony_kernel_subsystems,
        "mcp_tool_count": mcp_tool_count,
        "config_yaml_files": _count_colony_kernel_config_files(project_root),
    }
    for key, live_value in exact_mirrors.items():
        configured = _required_value(experiment, key, config_path)
        if configured != live_value:
            raise RuntimeError(
                f"Manuscript mirror experiment.{key}={configured!r} differs from "
                f"live value {live_value!r}"
            )

    # Derived policy and deterministic-fixture values.
    trust_convergence_steps: int = math.ceil(
        (trust_promote_threshold - trust_sandbox_score) / max(trust_delta_pass, 1e-9)
    )

    # The implementation subtracts a fixed amount per tick, then floors at zero.
    # These unit-strength one-tick retentions are therefore 1 - evaporation.
    # Rounded to avoid leaking binary floating-point noise (e.g. 0.30000000000000004)
    # into rendered manuscript prose; matches the precision already used for the
    # derived pheromone_retention_* values below.
    evaporation_slow = round(base_evaporation_rate * decay_rate_slow, 3)
    evaporation_normal = round(base_evaporation_rate * decay_rate_normal, 3)
    evaporation_fast = round(base_evaporation_rate * decay_rate_fast, 3)
    evaporation = {
        "FAST": evaporation_fast,
        "NORMAL": evaporation_normal,
        "SLOW": evaporation_slow,
    }
    pheromone_retention_slow = round(max(0.0, 1.0 - evaporation_slow), 3)
    pheromone_retention_normal = round(max(0.0, 1.0 - evaporation_normal), 3)
    pheromone_retention_fast = round(max(0.0, 1.0 - evaporation_fast), 3)
    pheromone_retention_slow_pct: int = round(pheromone_retention_slow * 100)
    pheromone_retention_normal_pct: int = round(pheromone_retention_normal * 100)
    pheromone_retention_fast_pct: int = round(pheromone_retention_fast * 100)

    decay_report_tick = max(decay_checkpoints)
    pheromone_fast_loss_report_tick_pct = round(
        (1.0 - max(0.0, 1.0 - decay_report_tick * evaporation_fast)) * 100
    )
    pheromone_slow_retention_report_tick_pct = round(
        max(0.0, 1.0 - decay_report_tick * evaporation_slow) * 100
    )
    unit_extinction_fast = math.ceil(1.0 / evaporation_fast)
    unit_extinction_normal = math.ceil(1.0 / evaporation_normal)
    unit_extinction_slow = math.ceil(1.0 / evaporation_slow)
    trust_break_even = -trust_delta_fail / (trust_delta_pass - trust_delta_fail)
    trust_max_delta = trust_delta_pass + trust_delta_human
    trust_min_delta = trust_delta_fail + trust_delta_repair - trust_delta_human
    trust_replacement_sensitivity = trust_max_delta - trust_min_delta

    paired = _paired_locality_snapshot(
        agent_trust=paired_agent_trust,
        recovery_ticks=paired_recovery_ticks,
    )
    trust_trajectory_rows = _trust_trajectory_rows(
        checkpoints=trust_checkpoints,
        initial_trust=trust_sandbox_score,
        pass_delta=trust_delta_pass,
        hard_floor=trust_hard_floor,
    )
    decay_rows = _decay_rows(
        checkpoints=decay_checkpoints,
        evaporation=evaporation,
    )
    representative_gate_rows = _representative_gate_rows(
        weights=gate_weights,
        hard_floor=trust_hard_floor,
        execute_threshold=gate_execute_threshold,
        hold_threshold=gate_hold_threshold,
        missing_field_penalty=missing_field_penalty,
    )

    config_hash: str = hashlib.sha256(raw_config_bytes).hexdigest()

    # ------------------------------------------------------------------
    # 3. Derive RESULT_* from actual project files
    # ------------------------------------------------------------------

    colony_kernel_tests_dir = _colony_kernel_test_dir(project_root)
    coverage_floor = _coverage_floor(project_root)
    pytest_info = _run_colony_kernel_coverage(
        project_root, colony_kernel_tests_dir, coverage_floor
    )
    test_collected: int = int(pytest_info["collected"])
    test_passed: int = int(pytest_info["passed"])
    test_skipped: int = int(pytest_info["skipped"])
    test_failed: int = int(pytest_info["failed"])
    test_errors: int = int(pytest_info["errors"])
    test_count: int = test_passed
    if test_collected <= 0 or test_passed <= 0:
        raise RuntimeError("pytest collection returned zero colony-kernel tests")

    coverage_pct: float = float(pytest_info["coverage_pct"])

    # Ruff and ty errors — scoped to colony_kernel only (the manuscript's subject)
    colony_kernel_src_str = (
        str(colony_kernel_dir)
        if colony_kernel_dir.is_dir()
        else str(project_root / "src")
    )
    ruff_result = subprocess.run(
        ["ruff", "check", "--output-format=json", colony_kernel_src_str],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if ruff_result.returncode != 0:
        raise RuntimeError(
            "ruff gate failed while computing manuscript metrics "
            f"(exit {ruff_result.returncode}):\n{ruff_result.stderr or ruff_result.stdout}"
        )
    findings = json.loads(ruff_result.stdout or "[]")
    ruff_errors: int = len(findings)

    ty_result = subprocess.run(
        ["ty", "check", "--output-format", "concise", colony_kernel_src_str],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if ty_result.returncode != 0:
        raise RuntimeError(
            "ty gate failed while computing manuscript metrics "
            f"(exit {ty_result.returncode}):\n{ty_result.stderr or ty_result.stdout}"
        )
    ty_errors: int = sum(
        1
        for line in ty_result.stdout.splitlines()
        if "error[" in line or ": error:" in line
    )

    # Publish the fresh test and quality-gate evidence only after pytest,
    # coverage, Ruff, and ty have all passed.  The temporary coverage/JUnit
    # paths are intentionally not part of the final release surface.
    coverage_final = project_root / "output" / "data" / "colony_kernel_coverage.json"
    junit_final = project_root / "output" / "data" / "colony_kernel_test_report.xml"
    Path(str(pytest_info["coverage_tmp"])).replace(coverage_final)
    Path(str(pytest_info["junit_tmp"])).replace(junit_final)
    _atomic_write_json(
        project_root / "output" / "data" / "colony_kernel_test_status.json",
        {
            "collected": test_collected,
            "passed": test_passed,
            "skipped": test_skipped,
            "failed": test_failed,
            "errors": test_errors,
            "coverage_pct": coverage_pct,
            "coverage_floor": coverage_floor,
            "commands": [
                {"argv": pytest_info["command"], "exit_code": pytest_info["exit_code"]},
                {
                    "argv": [
                        "ruff",
                        "check",
                        "--output-format=json",
                        colony_kernel_src_str,
                    ],
                    "exit_code": ruff_result.returncode,
                },
                {
                    "argv": ["ty", "check", "--output-format", "concise", colony_kernel_src_str],
                    "exit_code": ty_result.returncode,
                },
            ],
        },
    )

    # Trust score traces derived from live runtime constants.
    trust_initial: float = trust_sandbox_score
    trust_after_promotion: float = trust_promote_threshold

    gate_score_sandbox: float = 0.0
    proposals_to_promotion: int = max(
        role_min_proposals,
        math.ceil(
            (trust_promote_threshold - trust_sandbox_score)
            / max(trust_delta_pass, 1e-9)
        ),
    )

    # Colony kernel metrics
    ck_loc = _count_loc(colony_kernel_dir)
    if ck_loc == 0:
        raise RuntimeError(f"No Colony Kernel source lines found under {colony_kernel_dir}")
    ck_files = _count_python_files(colony_kernel_dir)
    if ck_files == 0:
        raise RuntimeError(f"No top-level Colony Kernel files found under {colony_kernel_dir}")

    module_docs_count: int = _count_colony_kernel_docs(project_root)

    # ------------------------------------------------------------------
    # 4. ARTIFACT_* summary tokens
    # ------------------------------------------------------------------
    test_suite_count: int = _count_colony_kernel_test_suites(project_root)
    config_files_found: int = _count_colony_kernel_config_files(project_root)
    mcp_tools_artifact = _count_colony_kernel_mcp_tools(colony_kernel_dir)

    # ------------------------------------------------------------------
    # 5. Platform tokens
    # ------------------------------------------------------------------
    python_version: str = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    platform_name: str = platform.system()
    generation_timestamp: str = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    # ------------------------------------------------------------------
    # 6. Assemble flat string dict (all values coerced to str)
    # ------------------------------------------------------------------
    variables: dict[str, str] = {
        # CONFIG tokens
        "CONFIG_TITLE": paper_title,
        "CONFIG_PROJECT_SHORT_NAME": project_short_name,
        "CONFIG_SUBTITLE": paper_subtitle,
        "CONFIG_VERSION": config_version,
        "CONFIG_PUBLICATION_DATE": publication_date,
        "CONFIG_PUBLICATION_DATE_DISPLAY": publication_date_display,
        "CONFIG_DOI": doi_value,
        "CONFIG_GITHUB_REPOSITORY": github_repository,
        "CONFIG_ACKNOWLEDGEMENTS": acknowledgement_text,
        "CONFIG_COVERAGE_FLOOR": str(coverage_floor),
        "CONFIG_MODULE_COUNT": str(module_count),
        "CONFIG_COLONY_KERNEL_SUBSYSTEMS": str(colony_kernel_subsystems),
        "CONFIG_OPERATIONAL_SUBSYSTEM_COUNT": str(operational_subsystem_count),
        "CONFIG_MCP_TOOL_COUNT": str(mcp_tool_count),
        "CONFIG_GATE_COMPONENT_COUNT": str(len(gate_weights)),
        "CONFIG_GATE_DECISION_COUNT": str(gate_decision_count),
        "CONFIG_GATE_EXECUTE_THRESHOLD": str(gate_execute_threshold),
        "CONFIG_GATE_HOLD_THRESHOLD": str(gate_hold_threshold),
        "CONFIG_HAZARD_HIGH_THRESHOLD": str(hazard_high_threshold),
        "CONFIG_HAZARD_MEDIUM_THRESHOLD": str(hazard_medium_threshold),
        "CONFIG_RISK_CREDIT_MEDIUM": str(risk_credit_medium),
        "CONFIG_TRUST_SANDBOX_SCORE": str(trust_sandbox_score),
        "CONFIG_TRUST_HARD_FLOOR": str(trust_hard_floor),
        "CONFIG_TRUST_PROMOTE_THRESHOLD": str(trust_promote_threshold),
        "CONFIG_TRUST_FULL_CREDIT_THRESHOLD": str(trust_full_credit_threshold),
        "CONFIG_TRUST_CREDIT_LOWER": str(trust_credit_lower),
        "CONFIG_RECENT_FAILURE_COUNT_THRESHOLD": str(recent_failure_threshold),
        "CONFIG_RECENT_FAILURE_WINDOW": str(recent_failure_window),
        "CONFIG_FAILURE_PENALTY": str(failure_penalty),
        "CONFIG_MISSING_FIELD_PENALTY": str(missing_field_penalty),
        "CONFIG_COMPLETENESS_FIELD_COUNT": str(completeness_field_count),
        "CONFIG_CONSEQUENCE_HISTORY_MAX": str(consequence_history_max),
        "CONFIG_SIGNAL_TYPES_COUNT": str(signal_types_count),
        "CONFIG_DECAY_RATES_COUNT": str(decay_rates_count),
        "CONFIG_BASE_EVAPORATION_RATE": str(base_evaporation_rate),
        "CONFIG_DECAY_RATE_FAST": str(decay_rate_fast),
        "CONFIG_DECAY_RATE_NORMAL": str(decay_rate_normal),
        "CONFIG_DECAY_RATE_SLOW": str(decay_rate_slow),
        "CONFIG_EVAPORATION_FAST": str(evaporation_fast),
        "CONFIG_EVAPORATION_NORMAL": str(evaporation_normal),
        "CONFIG_EVAPORATION_SLOW": str(evaporation_slow),
        "CONFIG_FIELD_MAX_STRENGTH": str(field_max_strength),
        "CONFIG_SOURCE_MULTIPLIER_TEST": str(source_multiplier_test),
        "CONFIG_SOURCE_MULTIPLIER_HUMAN": str(source_multiplier_human),
        "CONFIG_SOURCE_MULTIPLIER_SECURITY": str(source_multiplier_security),
        "CONFIG_SOURCE_MULTIPLIER_AGENT": str(source_multiplier_agent),
        "CONFIG_SOURCE_MULTIPLIER_RUNTIME": str(source_multiplier_runtime),
        "CONFIG_CANONICAL_FAILURE_STRENGTH": str(canonical_failure_strength),
        "CONFIG_GATE_WEIGHT_BUDGET": str(gate_weight_budget),
        "CONFIG_GATE_WEIGHT_RISK": str(gate_weight_risk),
        "CONFIG_GATE_WEIGHT_TRUST": str(gate_weight_trust),
        "CONFIG_GATE_WEIGHT_COMPLETENESS": str(gate_weight_completeness),
        "CONFIG_BUDGET_DIMENSIONS_COUNT": str(budget_dimensions_count),
        "CONFIG_BUDGET_MAX_LLM_CALLS": str(budget_max_llm_calls),
        "CONFIG_BUDGET_MAX_RUNTIME": str(budget_max_runtime),
        "CONFIG_BUDGET_MAX_RISK": str(budget_max_risk),
        "CONFIG_BUDGET_MAX_SECURITY": str(budget_max_security),
        "CONFIG_YAML_CONFIG_FILES": str(config_files_found),
        "CONFIG_FALSIFICATION_VECTORS": str(falsification_vectors),
        "CONFIG_FALSIFICATION_CHECK_COUNT": str(falsification_check_count),
        "CONFIG_FALSIFICATION_DEPENDENCY_THRESHOLD": str(
            falsification_dependency_threshold
        ),
        "CONFIG_FALSIFICATION_RESPONSIBILITY_THRESHOLD": str(
            falsification_responsibility_threshold
        ),
        "CONFIG_SEVERITY_RANK_LOW": str(severity_rank_low),
        "CONFIG_SEVERITY_RANK_MEDIUM": str(severity_rank_medium),
        "CONFIG_SEVERITY_RANK_HIGH": str(severity_rank_high),
        "CONFIG_SEVERITY_RANK_CRITICAL": str(severity_rank_critical),
        "CONFIG_PRUNING_STALENESS_DAYS": str(pruning_staleness_days),
        "CONFIG_PRUNING_LOW_CALL_COUNT": str(pruning_low_call_count),
        "CONFIG_PRUNING_DEPENDENCY_VETO": str(pruning_dependency_veto),
        "CONFIG_PRUNING_DUPLICATE_CONFIDENCE": str(
            pruning_duplicate_confidence
        ),
        "CONFIG_PRUNING_NEVER_USED_CONFIDENCE": str(
            pruning_never_used_confidence
        ),
        "CONFIG_PRUNING_STALE_CONFIDENCE": str(pruning_stale_confidence),
        "CONFIG_PRUNING_LOW_USAGE_CONFIDENCE": str(
            pruning_low_usage_confidence
        ),
        "CONFIG_PRUNING_MIN_CONFIDENCE": str(pruning_min_confidence),
        "CONFIG_AGENT_COUNT": str(agent_count),
        "CONFIG_WORKLOAD_TASK_COUNT": str(workload_task_count),
        "CONFIG_SWE_BENCH_TASK_COUNT": str(swe_bench_task_count),
        "CONFIG_WARMUP_TICKS": str(warmup_ticks),
        "CONFIG_BENCHMARK_CONDITION_COUNT": str(benchmark_condition_count),
        "CONFIG_ROLE_COUNT": str(role_count),
        "CONFIG_ROLE_MIN_PROPOSALS": str(role_min_proposals),
        "CONFIG_ROLE_REPAIR_THRESHOLD": str(role_repair_threshold),
        "CONFIG_ROLE_MEMORY_THRESHOLD": str(role_memory_threshold),
        "CONFIG_ROLE_DISPATCHER_THRESHOLD": str(role_dispatcher_threshold),
        "CONFIG_ROLE_GUARD_THRESHOLD": str(role_guard_threshold),
        "CONFIG_TRUST_DELTA_PASS": str(trust_delta_pass),
        "CONFIG_TRUST_DELTA_FAIL": str(trust_delta_fail),
        "CONFIG_TRUST_DELTA_REPAIR": str(trust_delta_repair),
        "CONFIG_TRUST_DELTA_HUMAN_WEIGHT": str(trust_delta_human),
        "CONFIG_PHEROMONE_RETENTION_SLOW": str(pheromone_retention_slow),
        "CONFIG_PHEROMONE_RETENTION_NORMAL": str(pheromone_retention_normal),
        "CONFIG_PHEROMONE_RETENTION_FAST": str(pheromone_retention_fast),
        "CONFIG_PHEROMONE_RETENTION_SLOW_PCT": str(pheromone_retention_slow_pct),
        "CONFIG_PHEROMONE_RETENTION_NORMAL_PCT": str(pheromone_retention_normal_pct),
        "CONFIG_PHEROMONE_RETENTION_FAST_PCT": str(pheromone_retention_fast_pct),
        "CONFIG_DECAY_REPORT_TICK": str(decay_report_tick),
        "RESULT_PHEROMONE_FAST_LOSS_REPORT_TICK_PCT": str(
            pheromone_fast_loss_report_tick_pct
        ),
        "RESULT_PHEROMONE_SLOW_RETENTION_REPORT_TICK_PCT": str(
            pheromone_slow_retention_report_tick_pct
        ),
        "RESULT_UNIT_EXTINCTION_FAST_TICKS": str(unit_extinction_fast),
        "RESULT_UNIT_EXTINCTION_NORMAL_TICKS": str(unit_extinction_normal),
        "RESULT_UNIT_EXTINCTION_SLOW_TICKS": str(unit_extinction_slow),
        "RESULT_TRUST_BREAK_EVEN_PASS_RATE": f"{trust_break_even:.3f}",
        "RESULT_TRUST_MAX_DELTA": f"{trust_max_delta:+.2f}",
        "RESULT_TRUST_MIN_DELTA": f"{trust_min_delta:+.2f}",
        "RESULT_TRUST_REPLACEMENT_SENSITIVITY": f"{trust_replacement_sensitivity:.2f}",
        "RESULT_PAIRED_AGENT_TRUST": str(paired["agent_trust"]),
        "RESULT_PAIRED_CLEAR_SCORE": f"{paired['clear_score']:.3f}",
        "RESULT_PAIRED_FAILURE_SCORE": f"{paired['failure_score']:.3f}",
        "RESULT_PAIRED_UNRELATED_SCORE": f"{paired['unrelated_score']:.3f}",
        "RESULT_PAIRED_RECOVERED_SCORE": f"{paired['recovered_score']:.3f}",
        "RESULT_PAIRED_FAILURE_PRESSURE": f"{paired['failure_pressure']:.3f}",
        "RESULT_PAIRED_SCORE_CHANGE": f"{paired['score_change']:.3f}",
        "RESULT_PAIRED_RECOVERY_TICKS": str(paired["recovery_ticks"]),
        "RESULT_PAIRED_LOCALITY_ROWS": str(paired["rows"]),
        "RESULT_TRUST_TRAJECTORY_ROWS": trust_trajectory_rows,
        "RESULT_DECAY_ROWS": decay_rows,
        "RESULT_REPRESENTATIVE_GATE_ROWS": representative_gate_rows,
        "CONFIG_TRIAL_COUNT": str(trial_count),
        "CONFIG_TRIAL_COUNT_MINUS_1": str(trial_count - 1),
        "RESULT_TRUST_CONVERGENCE_STEPS": str(trust_convergence_steps),
        "CONFIG_FIRST_AUTHOR": first_author,
        "CONFIG_KEYWORDS": keywords_str,
        "CONFIG_HASH": config_hash,
        # RESULT tokens
        "RESULT_TEST_COUNT": str(test_count),
        # Compatibility aliases retain the historical passing-test token.
        "CONFIG_TEST_COUNT": str(test_count),
        "RESULT_TEST_COLLECTED": str(test_collected),
        "RESULT_TEST_PASSED": str(test_passed),
        "RESULT_TEST_SKIPPED": str(test_skipped),
        "RESULT_TEST_FAILED": str(test_failed),
        "RESULT_TEST_ERRORS": str(test_errors),
        "RESULT_COVERAGE_PCT": str(coverage_pct),
        "RESULT_RUFF_ERRORS": str(ruff_errors),
        "RESULT_TY_ERRORS": str(ty_errors),
        "RESULT_TRUST_INITIAL": str(trust_initial),
        "RESULT_TRUST_AFTER_PROMOTION": str(trust_after_promotion),
        "RESULT_GATE_SCORE_SANDBOX": str(gate_score_sandbox),
        "RESULT_PROPOSALS_TO_PROMOTION": str(proposals_to_promotion),
        "RESULT_COLONY_KERNEL_LOC": str(ck_loc),
        "RESULT_COLONY_KERNEL_FILES": str(ck_files),
        "RESULT_MODULE_DOCS_COUNT": str(module_docs_count),
        "CONFIG_AUTHOR_ORCID": str(first_author_orcid),
        # ARTIFACT tokens
        "ARTIFACT_TEST_SUITES": str(test_suite_count),
        "ARTIFACT_CONFIG_FILES": str(config_files_found),
        "ARTIFACT_MCP_TOOLS": str(mcp_tools_artifact),
        "ARTIFACT_FIGURE_COUNT": str(figure_count),
        "ARTIFACT_COMBINED_PDF_PATH": (
            f"output/pdf/{project_root.name}_combined.pdf"
        ),
        # Platform tokens
        "PYTHON_VERSION": python_version,
        "PLATFORM": platform_name,
        "GENERATION_TIMESTAMP": generation_timestamp,
    }

    return variables
