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
import sqlite3
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import fields
from datetime import UTC, date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

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
        hydrated[source] = _render_template(
            content,
            variables,
            source_label=str(source),
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for source, content in hydrated.items():
        destination = output_dir / source.name
        destination.write_text(content, encoding="utf-8")
        written.append(destination)
    return written


def _render_template(
    content: str,
    variables: dict[str, str],
    *,
    source_label: str,
) -> str:
    """Resolve a complete token template or fail before writing an artifact.

    This shared renderer is used both for manuscript sections and configured figure
    captions. Keeping the missing/unresolved checks in one place prevents a caption
    from silently becoming a stale hardcoded claim when a new variable is introduced.
    """
    token_pattern = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
    required = set(token_pattern.findall(content))
    missing = required - variables.keys()
    if missing:
        raise RuntimeError(
            f"Undefined manuscript variables in {source_label}: "
            + ", ".join(sorted(missing))
        )
    rendered = token_pattern.sub(lambda match: variables[match.group(1)], content)
    unresolved = token_pattern.findall(rendered)
    if unresolved:
        raise RuntimeError(
            f"Unresolved manuscript variables in {source_label}: "
            + ", ".join(sorted(set(unresolved)))
        )
    return rendered


# These values are intentionally retained in the machine-readable snapshot for
# figure registries, compatibility with the authoring syntax table, and
# provenance inspection. They are not silently treated as manuscript evidence.
_SNAPSHOT_ONLY_VARIABLES = {
    "CONFIG_DECAY_PLOT_HORIZON_TICKS",
    "CONFIG_DECAY_PLOT_POINTS",
    "CONFIG_GATE_SURFACE_GRID_POINTS",
    "CONFIG_GATE_SURFACE_TRUST_SLICES",
    "CONFIG_HEATMAP_GRID_POINTS",
    "CONFIG_HEATMAP_PRESSURE_MAX",
    "CONFIG_MODULE_COUNT",
    "CONFIG_PHEROMONE_RETENTION_FAST",
    "CONFIG_PHEROMONE_RETENTION_NORMAL",
    "CONFIG_PHEROMONE_RETENTION_SLOW",
    "CONFIG_PRUNING_MIN_CONFIDENCE",
    "CONFIG_PUBLICATION_DATE",
    "CONFIG_SCORE_MID",
    "CONFIG_TEST_COUNT",
    "CONFIG_TRIAL_COUNT_MINUS_1",
    "CONFIG_TRUST_PLOT_PROJECTION_MARGIN",
    "CONFIG_TRUST_TRAJECTORY_CHECKPOINTS",
    "PLATFORM",
    "RESULT_GATE_SCORE_SANDBOX",
    "RESULT_PAIRED_RECOVERY_TICKS",
    "RESULT_TRUST_AFTER_PROMOTION",
    "RESULT_TRUST_CONVERGENCE_STEPS",
    "TOKEN",
}


def _active_manuscript_sources(manuscript_dir: Path) -> list[Path]:
    sources = sorted(manuscript_dir.glob("[0-9]*.md"))
    preamble = manuscript_dir / "preamble.md"
    if preamble.exists():
        sources.append(preamble)
    return sources


def validate_variable_contract(
    manuscript_dir: Path,
    variables: dict[str, str],
    *,
    figure_source_dir: Path | None = None,
) -> dict[str, Any]:
    """Audit manuscript tokens, figure dependencies, and provenance freshness.

    The report is deliberately machine-readable so CI and manuscript generation
    can enforce the same contract. Figure-registry metadata and snapshot-only
    compatibility values are listed explicitly rather than counted as active
    evidence. Any other unused generated key is actionable drift.
    """
    token_pattern = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
    references: dict[str, list[str]] = {}
    used: set[str] = set()

    def collect(path: Path, content: str) -> None:
        for token in token_pattern.findall(content):
            used.add(token)
            references.setdefault(token, []).append(str(path))

    for source in _active_manuscript_sources(manuscript_dir):
        collect(source, source.read_text(encoding="utf-8"))

    config_path = manuscript_dir / "config.yaml"
    if config_path.is_file():
        config_text = config_path.read_text(encoding="utf-8")
        collect(config_path, config_text)

    if figure_source_dir and figure_source_dir.is_dir():
        for source in sorted(figure_source_dir.glob("*.py")):
            content = source.read_text(encoding="utf-8")
            for token in re.findall(
                r"(?:_var_(?:str|float)|_require_variable)\(\s*[\"']([A-Z][A-Z0-9_]*)",
                content,
            ):
                used.add(token)
                references.setdefault(token, []).append(str(source))

    reserved = {
        name: "figure-registry metadata"
        for name in variables
        if name.startswith("FIGURE_")
    }
    reserved.update(
        dict.fromkeys(
            _SNAPSHOT_ONLY_VARIABLES,
            "snapshot-only or compatibility metadata",
        )
    )
    reserved["CONFIG_HASH"] = "provenance guard"
    undefined = sorted(used - variables.keys() - reserved.keys())
    unused = sorted(set(variables) - used - set(reserved))
    unresolved_set: set[str] = set()
    if not undefined:
        for source in _active_manuscript_sources(manuscript_dir):
            rendered = _render_template(
                source.read_text(encoding="utf-8"),
                variables,
                source_label=str(source),
            )
            unresolved_set.update(token_pattern.findall(rendered))
    unresolved = sorted(unresolved_set)
    stale: list[str] = []
    if config_path.is_file() and variables.get("CONFIG_HASH"):
        expected_hash = hashlib.sha256(config_path.read_bytes()).hexdigest()
        if variables["CONFIG_HASH"].replace(" ", "") != expected_hash:
            stale.append("CONFIG_HASH does not match docs/manuscript/config.yaml")
    errors = [
        *(f"undefined token: {token}" for token in undefined),
        *(f"unresolved token: {token}" for token in unresolved),
        *(f"unused generated variable: {token}" for token in unused),
        *stale,
    ]
    variable_digest = hashlib.sha256(
        json.dumps(variables, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "schema_version": "1.0",
        "status": "valid" if not errors else "invalid",
        "source_files": [
            str(path) for path in _active_manuscript_sources(manuscript_dir)
        ],
        "used_tokens": sorted(used),
        "references": {
            key: sorted(set(value)) for key, value in sorted(references.items())
        },
        "reserved_variables": dict(sorted(reserved.items())),
        "unused_variables": unused,
        "undefined_tokens": undefined,
        "unresolved_tokens": unresolved,
        "stale_reasons": stale,
        "errors": errors,
        "variable_sha256": variable_digest,
        "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest()
        if config_path.is_file()
        else "unavailable",
    }


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
    """Return the authoritative top-level colony-kernel unit-test directory."""
    return project_root / "tests" / "unit" / "colony_kernel"


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


_ROADMAP_FIELDS = (
    "id",
    "name",
    "status",
    "hypothesis",
    "artifact",
    "metric",
    "falsifier",
    "exit_criteria",
)
_ROADMAP_STATUSES = {"implemented", "next", "planned", "research"}


def _research_roadmap_entries(
    raw_entries: list[Any], source: Path
) -> list[dict[str, Any]]:
    """Validate and normalize the config-backed research roadmap.

    The roadmap is a planning artifact, but it is still part of the manuscript's
    provenance surface. Requiring every milestone to name an artifact, decisive
    metric, falsifier, and exit criterion prevents aspirational prose from being
    rendered as an untestable promise.
    """
    entries: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, raw_entry in enumerate(raw_entries):
        if not isinstance(raw_entry, dict):
            raise RuntimeError(
                f"Research roadmap entry {index} is not a mapping in {source}"
            )
        missing = [field for field in _ROADMAP_FIELDS if not raw_entry.get(field)]
        if missing:
            raise RuntimeError(
                f"Research roadmap entry {index} is missing {', '.join(missing)} in {source}"
            )
        entry: dict[str, Any] = {
            field: str(raw_entry[field]).strip() for field in _ROADMAP_FIELDS
        }
        artifact_paths = raw_entry.get("artifact_paths", [])
        if entry["status"] == "implemented":
            if not isinstance(artifact_paths, list) or not artifact_paths:
                raise RuntimeError(
                    f"Implemented research milestone {entry['id']!r} must list "
                    f"resolvable artifact_paths in {source}"
                )
        if not isinstance(artifact_paths, list):
            raise RuntimeError(
                f"Research milestone {entry['id']!r} artifact_paths must be a list"
            )
        normalized_artifact_paths = [str(path).strip() for path in artifact_paths]
        for relative_path in normalized_artifact_paths:
            if not (source.parent.parent.parent / relative_path).is_file():
                raise RuntimeError(
                    f"Research milestone {entry['id']!r} references missing "
                    f"artifact path {relative_path!r}"
                )
        entry["artifact_paths"] = normalized_artifact_paths
        if entry["id"] in seen_ids:
            raise RuntimeError(
                f"Duplicate research roadmap id {entry['id']!r} in {source}"
            )
        if entry["status"] not in _ROADMAP_STATUSES:
            allowed = ", ".join(sorted(_ROADMAP_STATUSES))
            raise RuntimeError(
                f"Research roadmap entry {entry['id']!r} has invalid status "
                f"{entry['status']!r}; expected one of {allowed}"
            )
        seen_ids.add(entry["id"])
        entries.append(entry)
    if not entries:
        raise RuntimeError(f"Research roadmap is empty in {source}")
    if not any(entry["status"] == "implemented" for entry in entries):
        raise RuntimeError(
            "Research roadmap must identify at least one implemented milestone"
        )
    return entries


def _research_roadmap_evidence_rows(entries: list[dict[str, str]]) -> str:
    """Render the roadmap's evidence-plan table body."""
    return "\n".join(
        "| {id} | **{name}** | {status} | {hypothesis} | {artifact} |".format(
            id=entry["id"],
            name=entry["name"],
            status=entry["status"].capitalize(),
            hypothesis=entry["hypothesis"],
            artifact=entry["artifact"],
        )
        for entry in entries
    )


def _research_roadmap_decision_rows(entries: list[dict[str, str]]) -> str:
    """Render the roadmap's falsifier and exit-contract table body."""
    return "\n".join(
        "| {id} | {metric} | {falsifier} | {exit_criteria} |".format(
            id=entry["id"],
            metric=entry["metric"],
            falsifier=entry["falsifier"],
            exit_criteria=entry["exit_criteria"],
        )
        for entry in entries
    )


_CROSSWALK_FIELDS = (
    "id",
    "name",
    "status",
    "formalism",
    "formal_object",
    "code_symbols",
    "bridge",
    "evidence",
    "claim_boundary",
)
_CROSSWALK_STATUSES = {"implemented", "partial", "next", "planned", "research"}


def _formalism_code_crosswalk_entries(
    raw_entries: list[Any], source: Path, project_root: Path
) -> list[dict[str, Any]]:
    """Validate formalism mappings against the repository's actual files.

    A crosswalk is useful only when its code and evidence anchors remain resolvable.
    This validation keeps the manuscript from turning a conceptual analogy into a
    source-backed claim after a file or test has moved.
    """
    entries: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, raw_entry in enumerate(raw_entries):
        if not isinstance(raw_entry, dict):
            raise RuntimeError(
                f"Formalism crosswalk entry {index} is not a mapping in {source}"
            )
        missing = [field for field in _CROSSWALK_FIELDS if not raw_entry.get(field)]
        for path_field in ("code_paths", "evidence_paths"):
            paths = raw_entry.get(path_field)
            if not isinstance(paths, list) or not paths:
                missing.append(path_field)
        if missing:
            raise RuntimeError(
                f"Formalism crosswalk entry {index} is missing "
                f"{', '.join(missing)} in {source}"
            )
        entry: dict[str, Any] = {
            field: str(raw_entry[field]).strip() for field in _CROSSWALK_FIELDS
        }
        entry["code_paths"] = [str(path).strip() for path in raw_entry["code_paths"]]
        entry["evidence_paths"] = [
            str(path).strip() for path in raw_entry["evidence_paths"]
        ]
        if entry["id"] in seen_ids:
            raise RuntimeError(
                f"Duplicate formalism crosswalk id {entry['id']!r} in {source}"
            )
        if entry["status"] not in _CROSSWALK_STATUSES:
            allowed = ", ".join(sorted(_CROSSWALK_STATUSES))
            raise RuntimeError(
                f"Formalism crosswalk entry {entry['id']!r} has invalid status "
                f"{entry['status']!r}; expected one of {allowed}"
            )
        for path_field in ("code_paths", "evidence_paths"):
            for relative_path in entry[path_field]:
                path = project_root / relative_path
                if not path.is_file():
                    raise RuntimeError(
                        f"Formalism crosswalk {entry['id']} references missing "
                        f"{path_field} path {relative_path!r}"
                    )
        code_text = "\n".join(
            (project_root / relative_path).read_text(encoding="utf-8", errors="replace")
            for relative_path in entry["code_paths"]
        )
        for symbol in entry["code_symbols"].split(";"):
            leaf = symbol.strip().split(".")[-1]
            if not leaf or re.search(rf"\b{re.escape(leaf)}\b", code_text) is None:
                raise RuntimeError(
                    f"Formalism crosswalk {entry['id']} cannot resolve code symbol "
                    f"{symbol.strip()!r}"
                )
        seen_ids.add(entry["id"])
        entries.append(entry)
    if not entries:
        raise RuntimeError(f"Formalism-to-code crosswalk is empty in {source}")
    if not any(entry["status"] == "implemented" for entry in entries):
        raise RuntimeError(
            "Formalism-to-code crosswalk must identify at least one implemented mapping"
        )
    return entries


def _formalism_crosswalk_rows(entries: list[dict[str, Any]]) -> str:
    """Render the compact formalism-to-code correspondence table."""
    return "\n".join(
        "| {id} | **{name}** | {formalism} | {formal_object} | {status} |".format(
            id=entry["id"],
            name=entry["name"],
            formalism=entry["formalism"],
            formal_object=entry["formal_object"],
            status=entry["status"].capitalize(),
        )
        for entry in entries
    )


def _formalism_crosswalk_evidence_rows(entries: list[dict[str, Any]]) -> str:
    """Render the bridge, code-anchor, evidence, and claim-boundary table."""
    return "\n".join(
        "| {id} | {symbols} | {bridge} | {evidence} | {claim} |".format(
            id=entry["id"],
            symbols="; ".join(
                " / ".join(part.strip().split("."))
                for part in entry["code_symbols"].split(";")
            ),
            bridge=entry["bridge"],
            evidence=entry["evidence"],
            claim=entry["claim_boundary"],
        )
        for entry in entries
    )


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
    """Read the four coefficients from the live gate mapping.

    The source argument is retained for the caller's existing source-loading flow,
    but coefficients are imported from the runtime mapping so the manuscript's
    equations cannot silently drift when the gate implementation is refactored.
    """
    del actuation_gate_source
    from codomyrmex.colony_kernel.actuation_gate import GATE_SCORE_WEIGHTS

    weights = {
        "budget_ok": float(GATE_SCORE_WEIGHTS["budget"]),
        "risk_ok": float(GATE_SCORE_WEIGHTS["risk"]),
        "trust_ok": float(GATE_SCORE_WEIGHTS["trust"]),
        "completeness": float(GATE_SCORE_WEIGHTS["completeness"]),
    }
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
        raise RuntimeError(
            f"Could not locate falsification check registry in {worker_path}"
        )
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


def _figure_generator_filenames(project_root: Path) -> list[str]:
    """Return figure filenames declared by the executable generator registry."""
    orchestrator = (
        project_root
        / "src"
        / "codomyrmex"
        / "manuscript"
        / "figures"
        / "orchestrator.py"
    )
    source = orchestrator.read_text(encoding="utf-8")
    filenames = re.findall(
        r'\(\s*"([^\"]+\.png)",\s*fig_[a-z0-9_]+,\s*"[^\"]+"\s*,?\s*\),',
        source,
        flags=re.MULTILINE,
    )
    if not filenames:
        raise RuntimeError(f"Figure generator registry is empty in {orchestrator}")
    return filenames


def _falsification_vector_severities(
    project_root: Path,
    attack_vectors: Any,
    severity_rank: dict[Any, int],
) -> dict[str, str]:
    """Derive each vector's highest live check severity from first-party checks."""
    checks_dir = (
        project_root
        / "src"
        / "codomyrmex"
        / "colony_kernel"
        / "falsification"
        / "checks"
    )
    severities: dict[str, int] = {}
    for check_path in sorted(checks_dir.glob("*.py")):
        source = check_path.read_text(encoding="utf-8", errors="replace")
        for vector in attack_vectors:
            matches = re.findall(
                rf"AttackVector\.{vector.name}\.value.{{0,220}}?"
                r"FalsificationSeverity\.([A-Z]+)",
                source,
                flags=re.DOTALL,
            )
            for severity_name in matches:
                severity = next(
                    (
                        member
                        for member in severity_rank
                        if getattr(member, "name", "") == severity_name
                    ),
                    None,
                )
                if severity is not None:
                    severities[vector.name] = max(
                        severities.get(vector.name, 0), severity_rank[severity]
                    )

    if set(severities) != {vector.name for vector in attack_vectors}:
        missing = {vector.name for vector in attack_vectors} - set(severities)
        raise RuntimeError(
            "Could not derive live severity for falsification vectors: "
            + ", ".join(sorted(missing))
        )
    rank_to_name = {rank: member.name for member, rank in severity_rank.items()}
    return {name: rank_to_name[rank] for name, rank in sorted(severities.items())}


def _coverage_floor(project_root: Path) -> float:
    pyproject = project_root / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    try:
        return float(data["tool"]["coverage"]["report"]["fail_under"])
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError(f"Coverage floor is missing from {pyproject}") from exc


def _sha256_file(path: Path) -> str:
    """Return the SHA-256 digest for a reproducibility input artifact."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_sqlite_sha256(path: Path) -> str:
    """Hash logical SQLite contents while normalizing ephemeral trace time."""
    connection = sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True)
    try:
        canonical_dump = "\n".join(connection.iterdump())
    finally:
        connection.close()
    # PersistentPheromoneStore records ``last_reinforced`` for decay semantics.
    # It is intentionally runtime-dependent and must not make an otherwise
    # identical manuscript fixture change its provenance digest on regeneration.
    canonical_dump = re.sub(
        r'"last_reinforced":\s*-?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?,?',
        "",
        canonical_dump,
    )
    return hashlib.sha256(canonical_dump.encode("utf-8")).hexdigest()


def _kernel_source_hash(project_root: Path) -> str:
    """Hash first-party sources whose values feed manuscript figures and claims."""
    digest = hashlib.sha256()
    source_root = project_root / "src" / "codomyrmex" / "colony_kernel"
    paths = sorted(source_root.rglob("*.py"))
    paths.append(project_root / "src" / "codomyrmex" / "manuscript" / "variables.py")
    for path in paths:
        digest.update(str(path.relative_to(project_root)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _display_identifier(value: str) -> str:
    """Add presentation-only line-break opportunities to long hex identifiers."""
    if len(value) >= 32 and re.fullmatch(r"[0-9a-fA-F]+", value):
        # Spaces are removed when comparing a rendered value with its artifact.
        return " ".join(value[index : index + 8] for index in range(0, len(value), 8))
    return value


def _git_snapshot(project_root: Path) -> tuple[str, bool]:
    """Capture commit identity and tracked/untracked worktree state."""
    commit_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    status_result = subprocess.run(
        ["git", "status", "--porcelain=v1"],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    commit = (
        commit_result.stdout.strip() if commit_result.returncode == 0 else "unknown"
    )
    return commit or "unknown", bool(status_result.stdout.strip())


def _authoritative_inventory(project_root: Path) -> dict[str, int]:
    """Read measured counts from the repository's inventory script."""
    inventory_script = project_root / "scripts" / "doc_inventory.py"
    result = subprocess.run(
        [sys.executable, str(inventory_script)],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "Authoritative inventory generation failed:\n"
            f"{result.stdout}\n{result.stderr}"
        )
    # The inventory labels contain punctuation, so map them from stable output
    # prefixes rather than making the parser depend on label spelling.
    prefixes = {
        "top_level_modules": "top_level_modules",
        "mcp_tools_py": "mcp_tools.py (non-test)",
        "mcp_decorators": "@mcp_tool (production)",
        "workflow_count": ".github/workflows *.yml",
    }
    parsed: dict[str, int] = {}
    for key, label in prefixes.items():
        match = re.search(
            rf"^\s*{re.escape(label)}:\s+(\d+)$", result.stdout, re.MULTILINE
        )
        if match is None:
            raise RuntimeError(f"Inventory output lacks {label!r}")
        parsed[key] = int(match.group(1))
    return parsed


def _environment_fingerprint() -> str:
    """Hash non-secret runtime facts used to compute manuscript values."""
    facts = {
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "pythonhashseed": os.environ.get("PYTHONHASHSEED", "random"),
    }
    return hashlib.sha256(
        json.dumps(facts, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


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


def _paired_locality_snapshot(record: dict[str, Any]) -> dict[str, Any]:
    """Project the standalone replay artifact into manuscript table values."""
    first_run = record["runs"]["first"]
    results = first_run["results"]
    pressure = first_run["pressure"]
    before = results["before_failure"]
    after = results["after_failure_same_target"]
    unaffected = results["after_failure_unrelated_target"]
    recovered = results["after_recovery"]
    before_pressure = pressure["before_failure"]
    after_pressure = pressure["after_failure_same_target"]
    unrelated_pressure = pressure["after_failure_unrelated_target"]
    recovered_pressure = pressure["after_recovery"]
    recovery_ticks = int(first_run["recovery_ticks"])
    rows = "\n".join(
        [
            "| Same target, before failure | "
            f"{before_pressure['risk']:.3f} | {before_pressure['failure']:.3f} | "
            f"{max(before_pressure.values()):.3f} | {before['gate_score']:.3f} | "
            f"{before['decision'].upper()} |",
            "| Same target, after failed outcome | "
            f"{after_pressure['risk']:.3f} | {after_pressure['failure']:.3f} | "
            f"{max(after_pressure.values()):.3f} | {after['gate_score']:.3f} | {after['decision'].upper()} |",
            "| Unrelated target, after failed outcome | "
            f"{unrelated_pressure['risk']:.3f} | {unrelated_pressure['failure']:.3f} | "
            f"{max(unrelated_pressure.values()):.3f} | {unaffected['gate_score']:.3f} | "
            f"{unaffected['decision'].upper()} |",
            f"| Same target, after {recovery_ticks} passive ticks | "
            f"{recovered_pressure['risk']:.3f} | {recovered_pressure['failure']:.3f} | "
            f"{max(recovered_pressure.values()):.3f} | "
            f"{recovered['gate_score']:.3f} | {recovered['decision'].upper()} |",
        ]
    )
    return {
        "agent_trust": first_run["profile"]["trust_score"],
        "clear_score": before["gate_score"],
        "clear_pressure": max(before_pressure.values()),
        "failure_score": after["gate_score"],
        "unrelated_score": unaffected["gate_score"],
        "unrelated_pressure": max(unrelated_pressure.values()),
        "recovered_score": recovered["gate_score"],
        "failure_pressure": after_pressure["failure"],
        "score_change": after["gate_score"] - before["gate_score"],
        "recovery_ticks": recovery_ticks,
        "rows": rows,
    }


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


def _decay_rows(*, checkpoints: list[int], evaporation: dict[str, float]) -> str:
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
        rows.append(f"| {label} | {' | '.join(rendered)} | {value:.3f} | {verdict} |")
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
    coverage_path.parent.mkdir(parents=True, exist_ok=True)
    # Release evidence is regenerated for the current tree. Removing the prior
    # report prevents a failed pytest process from being mistaken for fresh proof.
    coverage_path.unlink(missing_ok=True)
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(test_path),
        "--cov=src/codomyrmex/colony_kernel",
        "--cov-branch",
        f"--cov-report=json:{coverage_path}",
        "--cov-report=term",
        f"--cov-fail-under={coverage_floor}",
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
    if result.returncode != 0:
        raise RuntimeError(
            "scoped pytest coverage gate failed while computing manuscript metrics "
            f"(exit {result.returncode}):\n{output}"
        )
    if not coverage_path.exists():
        raise RuntimeError(f"pytest coverage gate did not create {coverage_path}")
    data = json.loads(coverage_path.read_text(encoding="utf-8"))
    totals = data.get("totals", {})
    pct = totals.get("percent_branches_covered")
    if pct is None:
        raise RuntimeError(
            f"coverage JSON lacks a branch coverage percent: {coverage_path}"
        )
    branch_pct = round(float(pct), 1)
    if branch_pct < coverage_floor:
        raise RuntimeError(
            f"scoped branch coverage {branch_pct:.1f}% is below the configured "
            f"floor {coverage_floor:.1f}%"
        )
    count = _extract_pytest_count(output)
    if count <= 0:
        count = _run_pytest_json(project_root, test_path=test_path)["collected"]
    return {"collected": count, "coverage_pct": branch_pct}


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
    figure_config = _required_mapping(config, "figures", config_path)
    figure_parameters = _required_mapping(experiment, "figure_parameters", config_path)
    research_roadmap = _research_roadmap_entries(
        _required_list(config, "research_roadmap", config_path),
        config_path,
    )
    research_roadmap_evidence_rows = _research_roadmap_evidence_rows(research_roadmap)
    research_roadmap_decision_rows = _research_roadmap_decision_rows(research_roadmap)
    formalism_crosswalk = _formalism_code_crosswalk_entries(
        _required_list(config, "formalism_code_crosswalk", config_path),
        config_path,
        project_root,
    )
    formalism_crosswalk_rows = _formalism_crosswalk_rows(formalism_crosswalk)
    formalism_crosswalk_evidence_rows = _formalism_crosswalk_evidence_rows(
        formalism_crosswalk
    )

    # ------------------------------------------------------------------
    # 2. Derive CONFIG_* from config.yaml
    # ------------------------------------------------------------------

    paper_title = str(_required_value(paper, "title", config_path))
    paper_subtitle = str(_required_value(paper, "subtitle", config_path))
    pdf_margin = str(_required_value(paper, "pdf_margin", config_path)).strip()
    margin_match = re.fullmatch(
        r"(?P<value>0|[0-9]+(?:\.[0-9]+)?)(?P<unit>in|cm|mm|pt)",
        pdf_margin,
    )
    if margin_match is None or float(margin_match.group("value")) <= 0:
        raise RuntimeError(
            "paper.pdf_margin must be a positive TeX length using in, cm, mm, or pt: "
            f"{pdf_margin!r} in {config_path}"
        )
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

    inventory = _authoritative_inventory(project_root)
    # Cross-check the authoritative inventory against the local filesystem so
    # a broken inventory parser cannot silently publish a plausible count.
    codomyrmex_pkg = project_root / "src" / "codomyrmex"
    module_count: int = inventory["top_level_modules"]
    if module_count != _count_top_level_modules(codomyrmex_pkg):
        raise RuntimeError("Inventory module count disagrees with the source tree")
    if module_count == 0:
        raise RuntimeError(
            f"No top-level Codomyrmex modules found under {codomyrmex_pkg}"
        )

    colony_kernel_dir = codomyrmex_pkg / "colony_kernel"
    if not colony_kernel_dir.is_dir():
        raise RuntimeError(f"Colony Kernel source is missing: {colony_kernel_dir}")

    # Runtime policy is authoritative. The manuscript config retains explicit
    # projections for figure generation, but every projection is checked below.
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
    from codomyrmex.colony_kernel.replay import (
        run_paired_locality_replay,
        write_replay_artifact,
    )
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
    models_source = (colony_kernel_dir / "models.py").read_text(encoding="utf-8")
    pruning_source = (colony_kernel_dir / "pruning_daemon.py").read_text(
        encoding="utf-8"
    )
    gate_weights = _gate_weights(actuation_gate_source)
    gate_weight_budget = gate_weights["budget_ok"]
    gate_weight_risk = gate_weights["risk_ok"]
    gate_weight_trust = gate_weights["trust_ok"]
    gate_weight_completeness = gate_weights["completeness"]
    gate_weight_sum = sum(gate_weights.values())

    gate_execute_threshold = float(_GATE_SCORE_EXECUTE)
    gate_hold_threshold = float(_GATE_SCORE_HOLD)
    hazard_high_threshold = float(_HIGH_RISK_THRESHOLD)
    hazard_medium_threshold = float(_MED_RISK_THRESHOLD)
    trust_hard_floor = float(_TRUST_HARD_FLOOR)
    human_feedback_min = _extract_float(
        models_source,
        r"if not (-[0-9]+(?:\.[0-9]+)?) <= self\.human_feedback",
        "human-feedback lower bound",
    )
    human_feedback_max = _extract_float(
        models_source,
        r"self\.human_feedback <= ([0-9]+(?:\.[0-9]+)?)",
        "human-feedback upper bound",
    )
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
    falsification_vector_severities = _falsification_vector_severities(
        project_root,
        AttackVector,
        _SEVERITY_RANK,
    )

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
    parameter_status_note = str(
        _required_value(experiment, "parameter_status_note", config_path)
    )
    parameter_status_short = str(
        _required_value(experiment, "parameter_status_short", config_path)
    )
    agent_count = int(_required_value(experiment, "agent_count", config_path))
    workload_task_count = int(
        _required_value(experiment, "workload_task_count", config_path)
    )
    warmup_ticks = int(_required_value(experiment, "warmup_ticks", config_path))
    trial_count = int(_required_value(experiment, "trial_count", config_path))
    experiment_seed = int(_required_value(experiment, "seed", config_path))
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
    trust_trajectory_horizon = max(trust_checkpoints)
    if trust_trajectory_horizon <= 0:
        raise RuntimeError(
            "Trust trajectory checkpoints must include a positive horizon"
        )
    paired_fixture = _required_mapping(experiment, "paired_fixture", config_path)
    paired_agent_trust = float(
        _required_value(paired_fixture, "agent_trust", config_path)
    )
    paired_recovery_ticks = int(
        _required_value(paired_fixture, "recovery_ticks", config_path)
    )

    # Figure inputs are configuration, while policy values below remain derived from
    # live runtime constants. This keeps presentation sampling reproducible without
    # allowing the plot modules to grow independent scientific authorities.
    figure_score_min = float(
        _required_value(figure_parameters, "score_min", config_path)
    )
    figure_score_max = float(
        _required_value(figure_parameters, "score_max", config_path)
    )
    heatmap_grid_points = int(
        _required_value(figure_parameters, "heatmap_grid_points", config_path)
    )
    heatmap_pressure_max = float(
        _required_value(figure_parameters, "heatmap_pressure_max", config_path)
    )
    decay_plot_horizon_ticks = int(
        _required_value(figure_parameters, "decay_plot_horizon_ticks", config_path)
    )
    decay_plot_points = int(
        _required_value(figure_parameters, "decay_plot_points", config_path)
    )
    gate_surface_grid_points = int(
        _required_value(figure_parameters, "gate_surface_grid_points", config_path)
    )
    gate_surface_trust_slices = [
        float(value)
        for value in _required_list(
            figure_parameters, "gate_surface_trust_slices", config_path
        )
    ]
    trust_plot_projection_margin = int(
        _required_value(figure_parameters, "trust_plot_projection_margin", config_path)
    )
    if not figure_score_min < figure_score_max:
        raise RuntimeError("Figure score range must be strictly increasing")
    if heatmap_grid_points < 2 or gate_surface_grid_points < 2:
        raise RuntimeError("Figure grids require at least two points")
    if decay_plot_horizon_ticks <= 0 or decay_plot_points < 2:
        raise RuntimeError("Decay figure horizon and resolution must be positive")
    if trust_plot_projection_margin < 0:
        raise RuntimeError("Trust figure projection margin cannot be negative")
    if not all(
        figure_score_min <= value <= figure_score_max
        for value in gate_surface_trust_slices
    ):
        raise RuntimeError("Gate surface trust slices must lie within the score range")

    generator_filenames = _figure_generator_filenames(project_root)
    configured_filenames: list[str] = []
    for key, spec in figure_config.items():
        if not isinstance(spec, dict):
            raise RuntimeError(f"Figure metadata {key!r} is not a mapping")
        filename = str(_required_value(spec, "filename", config_path))
        _required_value(spec, "label", config_path)
        _required_value(spec, "width", config_path)
        _required_value(spec, "evidence_class", config_path)
        _required_value(spec, "caption", config_path)
        configured_filenames.append(filename)
    if configured_filenames != generator_filenames:
        raise RuntimeError(
            "Configured figure registry differs from executable generators: "
            f"config={configured_filenames!r}, generators={generator_filenames!r}"
        )

    # Manuscript projections must equal live code. They feed figure modules, but
    # are never independent authorities.
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

    replay_record = run_paired_locality_replay(
        agent_trust=paired_agent_trust,
        recovery_ticks=paired_recovery_ticks,
        seed=experiment_seed,
    )
    if not all(replay_record["assertions"].values()):
        failed_assertions = [
            name for name, passed in replay_record["assertions"].items() if not passed
        ]
        raise RuntimeError(
            "Colony Kernel replay contract failed: " + ", ".join(failed_assertions)
        )
    paired = _paired_locality_snapshot(replay_record)
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
    git_commit, worktree_dirty = _git_snapshot(project_root)
    inventory_payload = {
        **inventory,
        "inventory_script_sha256": _sha256_file(
            project_root / "scripts" / "doc_inventory.py"
        ),
    }
    inventory_hash = hashlib.sha256(
        json.dumps(inventory_payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    pyproject_hash = _sha256_file(project_root / "pyproject.toml")
    lock_hash = _sha256_file(project_root / "uv.lock")
    environment_hash = _environment_fingerprint()
    kernel_source_hash = _kernel_source_hash(project_root)
    replay_record["provenance"] = {
        "git_commit": git_commit,
        "worktree_dirty": worktree_dirty,
        "config_sha256": config_hash,
        "environment_sha256": environment_hash,
        "pyproject_sha256": pyproject_hash,
        "lock_sha256": lock_hash,
        "inventory_sha256": inventory_hash,
    }
    replay_artifact_path = (
        project_root / "output" / "data" / "colony_kernel_replay.json"
    )
    replay_file_sha256 = write_replay_artifact(replay_artifact_path, replay_record)

    # Research-surface evidence is generated from the same runtime adapters used
    # by the focused tests. These are local fixtures, not provider or benchmark
    # claims; their status is carried into captions and the variable manifest.
    from codomyrmex.colony_kernel.attestation import AttestationLedger
    from codomyrmex.colony_kernel.models import ColonySignal, SignalSource
    from codomyrmex.colony_kernel.research.benchmark import run_paired_benchmark
    from codomyrmex.colony_kernel.research.persistent_store import (
        PersistentPheromoneStore,
    )

    attestation_ledger = AttestationLedger()
    attestation_run_id = "manuscript-attestation-fixture"
    proposal_event = attestation_ledger.record_proposal(
        attestation_run_id,
        "manuscript-fixture",
        {"proposal_id": "proposal-1", "target": "fixture.py"},
    )
    verdict_event = attestation_ledger.record_gate_verdict(
        attestation_run_id,
        "manuscript-fixture",
        proposal_event,
        "execute",
        {"decision": "execute", "score": 1.0},
    )
    authorization_event = attestation_ledger.authorize_execution(
        attestation_run_id, "manuscript-fixture", verdict_event
    )
    execution_event = attestation_ledger.record_execution(
        attestation_run_id,
        "manuscript-fixture",
        authorization_event,
        {"execution_id": "execution-1", "returncode": 0},
    )
    attestation_ledger.record_outcome(
        attestation_run_id,
        "manuscript-fixture",
        execution_event,
        {"tests_passed": True},
    )
    attestation_validation = attestation_ledger.validate(attestation_run_id)
    attestation_event_count = len(attestation_ledger.events(attestation_run_id))
    attestation_ledger.close()

    benchmark_run = run_paired_benchmark(
        seed=experiment_seed,
        repo_root=project_root,
        config={"source": "manuscript-local-synthetic-cases"},
    )
    benchmark_metrics = benchmark_run.metrics

    with tempfile.TemporaryDirectory(
        prefix="codomyrmex-manuscript-store-"
    ) as store_dir:
        store_path = Path(store_dir) / "signals.sqlite"
        persistent_store = PersistentPheromoneStore(store_path)
        persistent_store.deposit_signal(
            ColonySignal(
                location="manuscript-fixture.py",
                signal_type=SignalType.FAILURE,
                strength=1.0,
                decay_rate=DecayRate.NORMAL,
                source=SignalSource.TEST,
            )
        )
        persistent_store.close()
        restarted_store = PersistentPheromoneStore(store_path)
        persistence_restart_strength = restarted_store.sense(
            "manuscript-fixture.py", SignalType.FAILURE
        )
        restarted_store.close()
        # SQLite page layouts can differ across temporary paths and runs even
        # when their logical records are identical. Hash the canonical SQL
        # representation so manuscript regeneration remains reproducible.
        persistence_artifact_hash = _canonical_sqlite_sha256(store_path)

    formal_status_counts = {
        status: sum(1 for entry in formalism_crosswalk if entry["status"] == status)
        for status in {entry["status"] for entry in formalism_crosswalk}
    }
    calibration_status = "not_estimated"

    # ------------------------------------------------------------------
    # 3. Derive RESULT_* from actual project files
    # ------------------------------------------------------------------

    colony_kernel_tests_dir = _colony_kernel_test_dir(project_root)
    coverage_floor = _coverage_floor(project_root)
    pytest_info = _run_colony_kernel_coverage(
        project_root, colony_kernel_tests_dir, coverage_floor
    )
    test_count: int = pytest_info.get("collected", 0)
    if test_count <= 0:
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
        raise RuntimeError(
            f"No Colony Kernel source lines found under {colony_kernel_dir}"
        )
    ck_files = _count_python_files(colony_kernel_dir)
    if ck_files == 0:
        raise RuntimeError(
            f"No top-level Colony Kernel files found under {colony_kernel_dir}"
        )

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
        "CONFIG_PDF_MARGIN": pdf_margin,
        "CONFIG_VERSION": config_version,
        "CONFIG_PUBLICATION_DATE": publication_date,
        "CONFIG_PUBLICATION_DATE_DISPLAY": publication_date_display,
        "CONFIG_DOI": doi_value,
        "CONFIG_GITHUB_REPOSITORY": github_repository,
        "CONFIG_ACKNOWLEDGEMENTS": acknowledgement_text,
        "CONFIG_PARAMETER_STATUS_NOTE": parameter_status_note,
        "CONFIG_PARAMETER_STATUS_SHORT": parameter_status_short,
        "CONFIG_RESEARCH_ROADMAP_STAGE_COUNT": str(len(research_roadmap)),
        "CONFIG_RESEARCH_ROADMAP_STAGES": json.dumps(
            research_roadmap, ensure_ascii=False, separators=(",", ":")
        ),
        "CONFIG_FORMALISM_CROSSWALK_COUNT": str(len(formalism_crosswalk)),
        "CONFIG_FORMALISM_CODE_CROSSWALK": json.dumps(
            formalism_crosswalk, ensure_ascii=False, separators=(",", ":")
        ),
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
        "CONFIG_GATE_WEIGHT_SUM": str(gate_weight_sum),
        "CONFIG_SCORE_MIN": str(figure_score_min),
        "CONFIG_SCORE_MAX": str(figure_score_max),
        "CONFIG_UNIT_SCORE": str(figure_score_max),
        "CONFIG_ZERO_COUNT": "0",
        "CONFIG_SCORE_MID": str(
            figure_score_min + (figure_score_max - figure_score_min) / 2
        ),
        "CONFIG_HUMAN_FEEDBACK_MIN": str(human_feedback_min),
        "CONFIG_HUMAN_FEEDBACK_MAX": str(human_feedback_max),
        "CONFIG_HEATMAP_GRID_POINTS": str(heatmap_grid_points),
        "CONFIG_HEATMAP_PRESSURE_MAX": str(heatmap_pressure_max),
        "CONFIG_DECAY_PLOT_HORIZON_TICKS": str(decay_plot_horizon_ticks),
        "CONFIG_DECAY_PLOT_POINTS": str(decay_plot_points),
        "CONFIG_GATE_SURFACE_GRID_POINTS": str(gate_surface_grid_points),
        "CONFIG_GATE_SURFACE_TRUST_SLICES": json.dumps(
            gate_surface_trust_slices, separators=(",", ":")
        ),
        "CONFIG_TRUST_PLOT_PROJECTION_MARGIN": str(trust_plot_projection_margin),
        "CONFIG_TRUST_TRAJECTORY_HORIZON": str(trust_trajectory_horizon),
        "CONFIG_TRUST_TRAJECTORY_CHECKPOINTS": json.dumps(
            trust_checkpoints, separators=(",", ":")
        ),
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
        "CONFIG_FALSIFICATION_VECTOR_SEVERITIES": ";".join(
            f"{name}={severity}"
            for name, severity in falsification_vector_severities.items()
        ),
        "CONFIG_PRUNING_STALENESS_DAYS": str(pruning_staleness_days),
        "CONFIG_PRUNING_LOW_CALL_COUNT": str(pruning_low_call_count),
        "CONFIG_PRUNING_DEPENDENCY_VETO": str(pruning_dependency_veto),
        "CONFIG_PRUNING_DUPLICATE_CONFIDENCE": str(pruning_duplicate_confidence),
        "CONFIG_PRUNING_NEVER_USED_CONFIDENCE": str(pruning_never_used_confidence),
        "CONFIG_PRUNING_STALE_CONFIDENCE": str(pruning_stale_confidence),
        "CONFIG_PRUNING_LOW_USAGE_CONFIDENCE": str(pruning_low_usage_confidence),
        "CONFIG_PRUNING_MIN_CONFIDENCE": str(pruning_min_confidence),
        "CONFIG_AGENT_COUNT": str(agent_count),
        "CONFIG_WORKLOAD_TASK_COUNT": str(workload_task_count),
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
        "RESULT_PAIRED_CLEAR_PRESSURE": f"{paired['clear_pressure']:.3f}",
        "RESULT_PAIRED_CLEAR_SCORE": f"{paired['clear_score']:.3f}",
        "RESULT_PAIRED_FAILURE_SCORE": f"{paired['failure_score']:.3f}",
        "RESULT_PAIRED_UNRELATED_SCORE": f"{paired['unrelated_score']:.3f}",
        "RESULT_PAIRED_UNRELATED_PRESSURE": f"{paired['unrelated_pressure']:.3f}",
        "RESULT_PAIRED_RECOVERED_SCORE": f"{paired['recovered_score']:.3f}",
        "RESULT_PAIRED_FAILURE_PRESSURE": f"{paired['failure_pressure']:.3f}",
        "RESULT_PAIRED_SCORE_CHANGE": f"{paired['score_change']:.3f}",
        "RESULT_PAIRED_RECOVERY_TICKS": str(paired["recovery_ticks"]),
        "RESULT_PAIRED_LOCALITY_ROWS": str(paired["rows"]),
        "RESULT_REPLAY_SEMANTIC_DIGEST": _display_identifier(
            str(replay_record["semantic_digest"])
        ),
        "RESULT_REPLAY_RECORD_SHA256": _display_identifier(
            str(replay_record["record_sha256"])
        ),
        "RESULT_REPLAY_FILE_SHA256": _display_identifier(replay_file_sha256),
        "RESULT_REPLAY_REPEATABLE": str(
            replay_record["assertions"]["repeatable_semantics"]
        ).lower(),
        "RESULT_REPLAY_SAME_TARGET_DECISION": str(
            replay_record["runs"]["first"]["results"]["after_failure_same_target"][
                "decision"
            ]
        ).upper(),
        "RESULT_REPLAY_UNRELATED_DECISION": str(
            replay_record["runs"]["first"]["results"]["after_failure_unrelated_target"][
                "decision"
            ]
        ).upper(),
        "RESULT_REPLAY_RECOVERY_DECISION": str(
            replay_record["runs"]["first"]["results"]["after_recovery"]["decision"]
        ).upper(),
        "ARTIFACT_REPLAY_PATH": "output/data/colony_kernel_replay.json",
        "RESULT_TRUST_TRAJECTORY_ROWS": trust_trajectory_rows,
        "RESULT_DECAY_ROWS": decay_rows,
        "RESULT_REPRESENTATIVE_GATE_ROWS": representative_gate_rows,
        "RESULT_RESEARCH_ROADMAP_EVIDENCE_ROWS": research_roadmap_evidence_rows,
        "RESULT_RESEARCH_ROADMAP_DECISION_ROWS": research_roadmap_decision_rows,
        "RESULT_FORMALISM_CROSSWALK_ROWS": formalism_crosswalk_rows,
        "RESULT_FORMALISM_CROSSWALK_EVIDENCE_ROWS": formalism_crosswalk_evidence_rows,
        "CONFIG_TRIAL_COUNT": str(trial_count),
        "CONFIG_TRIAL_COUNT_MINUS_1": str(trial_count - 1),
        "RESULT_TRUST_CONVERGENCE_STEPS": str(trust_convergence_steps),
        "CONFIG_FIRST_AUTHOR": first_author,
        "CONFIG_KEYWORDS": keywords_str,
        "CONFIG_HASH": _display_identifier(config_hash),
        "CONFIG_EXPERIMENT_SEED": str(experiment_seed),
        "REPRO_GIT_COMMIT": _display_identifier(git_commit),
        "REPRO_WORKTREE_DIRTY": str(worktree_dirty).lower(),
        "REPRO_ENVIRONMENT_HASH": _display_identifier(environment_hash),
        "REPRO_KERNEL_SOURCE_HASH": _display_identifier(kernel_source_hash),
        "REPRO_PYPROJECT_HASH": _display_identifier(pyproject_hash),
        "REPRO_LOCK_HASH": _display_identifier(lock_hash),
        "REPRO_INVENTORY_HASH": _display_identifier(inventory_hash),
        "REPRO_INVENTORY_MODULE_COUNT": str(inventory["top_level_modules"]),
        "REPRO_INVENTORY_MCP_FILE_COUNT": str(inventory["mcp_tools_py"]),
        "REPRO_INVENTORY_MCP_DECORATOR_COUNT": str(inventory["mcp_decorators"]),
        "REPRO_INVENTORY_WORKFLOW_COUNT": str(inventory["workflow_count"]),
        # RESULT tokens
        "RESULT_TEST_COUNT": str(test_count),
        # CONFIG_TEST_COUNT: alias for RESULT_TEST_COUNT — 05_experimental_setup.md line 11
        # uses the CONFIG_ prefix to reference the same live pytest-collected count.
        "CONFIG_TEST_COUNT": str(test_count),
        "RESULT_COVERAGE_PCT": str(coverage_pct),
        "RESULT_RUFF_ERRORS": str(ruff_errors),
        "RESULT_TY_ERRORS": str(ty_errors),
        "RESULT_ATTESTATION_EVENT_COUNT": str(attestation_event_count),
        "RESULT_ATTESTATION_CHAIN_VALID": str(attestation_validation.valid).lower(),
        "RESULT_BENCHMARK_TASK_COUNT": str(benchmark_metrics["task_count"]),
        "RESULT_BENCHMARK_BASELINE_HARM_RATE": f"{benchmark_metrics['baseline_harmful_action_rate']:.3f}",
        "RESULT_BENCHMARK_MEDIATED_HARM_RATE": f"{benchmark_metrics['mediated_harmful_action_rate']:.3f}",
        "RESULT_BENCHMARK_BASELINE_UTILITY": f"{benchmark_metrics['baseline_utility']:.3f}",
        "RESULT_BENCHMARK_MEDIATED_UTILITY": f"{benchmark_metrics['mediated_utility']:.3f}",
        "RESULT_BENCHMARK_HARM_DELTA": f"{benchmark_metrics['harm_delta_ci']['estimate']:.3f}",
        "RESULT_BENCHMARK_HARM_CI_LOW": f"{benchmark_metrics['harm_delta_ci']['ci_low']:.3f}",
        "RESULT_BENCHMARK_HARM_CI_HIGH": f"{benchmark_metrics['harm_delta_ci']['ci_high']:.3f}",
        "RESULT_BENCHMARK_CI_METHOD": str(
            benchmark_metrics["confidence_interval_method"]
        ),
        "RESULT_BENCHMARK_CI_LEVEL": f"{100 * float(benchmark_metrics['confidence_interval_level']):.0f}",
        "RESULT_BENCHMARK_CASE_MANIFEST_SHA256": _display_identifier(
            str(benchmark_metrics["case_manifest_sha256"])
        ),
        "RESULT_BENCHMARK_EXECUTIONS_BASELINE": str(
            int(
                benchmark_metrics["execution_volume_by_condition"][
                    "baseline_always_execute"
                ]
            )
        ),
        "RESULT_BENCHMARK_EXECUTIONS_MEDIATED": str(
            int(benchmark_metrics["execution_volume_by_condition"]["gate_mediated"])
        ),
        "RESULT_PERSISTENCE_RESTART_STRENGTH": f"{persistence_restart_strength:.3f}",
        "RESULT_PERSISTENCE_ARTIFACT_SHA256": _display_identifier(
            persistence_artifact_hash
        ),
        "RESULT_FORMAL_CROSSWALK_IMPLEMENTED": str(
            formal_status_counts.get("implemented", 0)
        ),
        "RESULT_FORMAL_CROSSWALK_PARTIAL": str(formal_status_counts.get("partial", 0)),
        "RESULT_FORMAL_CROSSWALK_RESEARCH": str(
            formal_status_counts.get("research", 0)
        ),
        "RESULT_FORMAL_CROSSWALK_TOTAL": str(len(formalism_crosswalk)),
        "RESULT_CALIBRATION_STATUS": calibration_status,
        "RESULT_CALIBRATION_ECE": "not_run",
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
        "ARTIFACT_COMBINED_PDF_PATH": (f"output/pdf/{project_root.name}_combined.pdf"),
        # Platform tokens
        "PYTHON_VERSION": python_version,
        "PLATFORM": platform_name,
        "GENERATION_TIMESTAMP": generation_timestamp,
    }

    # Resolve configured figure metadata only after the complete base map exists.
    # Captions therefore share exactly the same live values as prose, tables, and
    # figure annotations, while the source Markdown contains no duplicated caption
    # text or filenames.
    for key, spec in figure_config.items():
        slug = re.sub(r"[^A-Z0-9]+", "_", str(key).upper()).strip("_")
        variables[f"FIGURE_FILENAME_{slug}"] = str(spec["filename"])
        variables[f"FIGURE_LABEL_{slug}"] = str(spec["label"])
        variables[f"FIGURE_WIDTH_{slug}"] = str(spec["width"])
        variables[f"FIGURE_EVIDENCE_{slug}"] = str(spec["evidence_class"])
        variables[f"FIGURE_CAPTION_{slug}"] = _render_template(
            str(spec["caption"]),
            variables,
            source_label=f"figure metadata {key}",
        )

    return variables
