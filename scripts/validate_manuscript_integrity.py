#!/usr/bin/env python3
"""Validate the manuscript's generated evidence and rendered-artifact contract.

This validator is intentionally stricter than a token check.  It verifies that
the current variable snapshot, figure registry, hydrated Markdown, claim ledger,
bibliography audit, and (when requested) HTML/PDF outputs describe the same
source/configuration state.  It never regenerates files and never infers missing
evidence.

Examples:

    uv run python scripts/validate_manuscript_integrity.py
    uv run python scripts/validate_manuscript_integrity.py --require-rendered
    uv run python scripts/validate_manuscript_integrity.py --require-source-current
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, cast

import yaml

from codomyrmex.manuscript.bibliography import (
    audit_bibliography,
    write_bibliography_audit,
)

TOKEN_PATTERN = re.compile(r"\{\{[A-Z0-9_]+\}\}")
IMAGE_PATTERN = re.compile(
    r"!\[(.*?)\]\(figures/([^\)]+\.png)\)\{([^}]*)\}",
    re.DOTALL,
)
ATTRIBUTE_PATTERN = re.compile(r'([A-Za-z_:][-A-Za-z0-9_:.]*)="([^"]*)"')
HEX_PATTERN = re.compile(r"[0-9a-fA-F]+")
NUMERIC_LITERAL_PATTERN = re.compile(r"(?<![A-Za-z_])\d+(?:\.\d+)?%?(?![A-Za-z_])")
ALLOWED_CLAIM_CLASSES = {
    "definition",
    "implementation_contract",
    "local_measurement",
    "hypothesis",
    "analogy",
    "external_scholarship",
}
ALLOWED_CLAIM_STATUSES = {"supported", "conditional", "not_run", "historical"}


class _ImageParser(HTMLParser):
    """Collect HTML image metadata and associated extended descriptions."""

    def __init__(self) -> None:
        super().__init__()
        self.images: list[dict[str, str]] = []
        self.descriptions: dict[str, str] = {}
        self.duplicate_description_ids: set[str] = set()
        self._description_id = ""
        self._description_depth = 0
        self._description_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag_name = tag.lower()
        values = {key.lower(): value or "" for key, value in attrs}
        if self._description_id:
            self._description_depth += 1
        if (
            tag_name == "div"
            and "figure-long-description" in values.get("class", "").split()
        ):
            self._description_id = values.get("id", "")
            self._description_depth = 1
            self._description_parts = []
            return
        if tag_name != "img":
            return
        self.images.append(
            {
                "src": values.get("src", ""),
                "alt": values.get("alt", ""),
                "aria_describedby": values.get("aria-describedby", ""),
            }
        )

    def handle_endtag(self, tag: str) -> None:
        if not self._description_id:
            return
        self._description_depth -= 1
        if self._description_depth > 0:
            return
        description_id = self._description_id
        if description_id in self.descriptions:
            self.duplicate_description_ids.add(description_id)
        self.descriptions[description_id] = " ".join(
            "".join(self._description_parts).split()
        )
        self._description_id = ""
        self._description_parts = []

    def handle_data(self, data: str) -> None:
        if self._description_id:
            self._description_parts.append(data)


def _normalise_text(value: object) -> str:
    """Canonicalise presentation-only typography for semantic comparisons."""

    text = str(value or "").translate(
        str.maketrans(
            {
                "\u00a0": " ",
                "\u2018": "'",
                "\u2019": "'",
                "\u201c": '"',
                "\u201d": '"',
            }
        )
    )
    return " ".join(text.split())


def _rendered_figure_filename(
    image: dict[str, str],
    *,
    filename_by_description_id: dict[str, str],
    issues: list[str],
) -> str:
    """Resolve a rendered image without logging an embedded binary payload.

    Pandoc may preserve repository-relative figure paths or embed PNGs as data
    URIs. Embedded images intentionally have no filename, so their explicit
    ``aria-describedby`` relationship is the stable identity carried from the
    figure registry into HTML.
    """

    src = image["src"]
    if src.startswith("figures/") and src.endswith(".png"):
        return src.removeprefix("figures/")
    if src.startswith("data:image/png;base64,"):
        matching_ids = [
            description_id
            for description_id in image["aria_describedby"].split()
            if description_id in filename_by_description_id
        ]
        if len(matching_ids) == 1:
            return filename_by_description_id[matching_ids[0]]
        issues.append(
            "rendered HTML embedded PNG cannot be associated with exactly one "
            "configured extended-description id"
        )
        return ""
    source_kind = src.split(":", 1)[0] if ":" in src else "relative"
    issues.append(
        "rendered HTML contains an unsupported image source "
        f"(kind={source_kind!r}, characters={len(src)})"
    )
    return ""


def _validate_figure_reference(
    *,
    filename: str,
    alt_text: str,
    describedby: str,
    descriptions: dict[str, str],
    registry_by_name: dict[str, dict[str, Any]],
    context: str,
    issues: list[str],
) -> str:
    """Validate one figure's explicit alternative and extended-description link."""

    entry = registry_by_name.get(filename)
    if entry is None:
        issues.append(f"{context} references unconfigured figure: {filename}")
        return ""
    expected_alt = _normalise_text(entry.get("alt_text"))
    actual_alt = _normalise_text(alt_text)
    if not actual_alt:
        issues.append(f"{context} has empty explicit alt text: {filename}")
    elif actual_alt != expected_alt:
        issues.append(f"{context} alt text is stale: {filename}")
    expected_description_id = f"{entry.get('label', '')}-description"
    if describedby != expected_description_id:
        issues.append(f"{context} aria-describedby is stale: {filename}")
        return ""
    actual_description = _normalise_text(descriptions.get(describedby, ""))
    expected_description = _normalise_text(entry.get("long_description"))
    if not actual_description:
        issues.append(f"{context} has no linked extended description: {filename}")
    elif actual_description != expected_description:
        issues.append(f"{context} extended description is stale: {filename}")
    return describedby


def _hardcoded_numeric_literals(manuscript_dir: Path) -> list[str]:
    """Find non-token numeric prose values that could drift between builds.

    Mathematical constants, ordinal/list labels, layout dimensions, immutable
    standards/hash names, and pipeline stage identifiers are intentionally
    allowed. Empirical/configuration values must instead be represented by a
    generated ``{{TOKEN}}``; this check is a guardrail rather than a parser for
    all possible Markdown or LaTeX.
    """
    findings: list[str] = []
    allowed_line_patterns = (
        re.compile(r"^\s*(?:#{1,6}\s*)?(?:DR-)?\d+\b"),
        re.compile(r"^\s*\d+\.\s"),
        re.compile(r"^\s*\*\*Algorithm\s+\d+"),
        re.compile(r"^\s*\\(?:vspace|includegraphics)"),
    )
    allowed_phrases = (
        "SHA-256",
        "NIST SP 800-207",
        "Stage 02",
        "Stage 03",
    )
    for path in sorted(manuscript_dir.glob("[0-9]*.md")):
        in_fence = False
        in_math_block = False
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_fence = not in_fence
                continue
            if stripped.startswith("$$"):
                in_math_block = not in_math_block
                continue
            if in_fence or in_math_block or "{{" in line:
                continue
            # Citation keys commonly contain publication years; they are
            # immutable bibliography identifiers, not drifting result values.
            prose = re.sub(r"@[A-Za-z][A-Za-z0-9_-]*", "", line)
            if not NUMERIC_LITERAL_PATTERN.search(prose):
                continue
            if any(pattern.search(line) for pattern in allowed_line_patterns):
                continue
            if any(phrase in line for phrase in allowed_phrases):
                continue
            if re.search(r"\b(?:Lemma|Proposition|Theorem)\s+\d+", line):
                continue
            if re.search(r"\bConditions?\s+\d+(?:\s*[–-]\s*\d+)?", line):
                continue
            if "$" in line or stripped.startswith("$$"):
                continue
            findings.append(f"{path}:{line_number}: {stripped}")
    return findings


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalise_digest(value: object) -> str:
    return re.sub(r"\s+", "", str(value or ""))


def _git_snapshot(project_root: Path) -> tuple[str, bool, str]:
    """Return the current commit, dirty state, and canonical status digest."""

    try:
        commit_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        status_result = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except OSError:
        return "", False, ""
    commit = commit_result.stdout.strip() if commit_result.returncode == 0 else ""
    lines = tuple(line for line in status_result.stdout.splitlines() if line)
    status_digest = hashlib.sha256("\n".join(lines).encode()).hexdigest()
    return commit, bool(lines), status_digest


def _kernel_source_hash(project_root: Path) -> str:
    """Match the source digest used by manuscript variable generation."""

    digest = hashlib.sha256()
    source_root = project_root / "src" / "codomyrmex" / "colony_kernel"
    paths = sorted(source_root.rglob("*.py"))
    paths.append(project_root / "src" / "codomyrmex" / "manuscript" / "variables.py")
    try:
        for path in paths:
            digest.update(str(path.relative_to(project_root)).encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
    except OSError:
        return ""
    return digest.hexdigest()


def _compact_contains(content: str, expected: object) -> bool:
    """Compare a generated digest despite presentation-only whitespace grouping."""

    expected_digest = _normalise_digest(expected)
    return bool(expected_digest) and expected_digest in _normalise_digest(content)


def _release_artifact_hashes(
    release_root: Path,
    manifest: dict[str, Any],
    project_root: Path,
    issues: list[str],
) -> None:
    """Ensure released report files are byte-identical to current output files."""

    source_by_role = {
        "content-pdf": project_root / "output" / "paper-content.pdf",
        "distribution-pdf": project_root / "output" / "paper.pdf",
        "semantic-html": project_root / "output" / "paper.html",
    }
    artifacts = manifest.get("artifacts", [])
    if not isinstance(artifacts, list):
        issues.append("publication manifest artifacts must be a list")
        return
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        role = str(artifact.get("role", ""))
        source = source_by_role.get(role)
        if source is None:
            continue
        released = release_root / str(artifact.get("path", ""))
        if not source.is_file() or not released.is_file():
            issues.append(f"release artifact is missing for role {role}")
            continue
        if _sha256(source) != _sha256(released):
            issues.append(f"release artifact is stale for role {role}")


def _resolve_tokens(value: object, variables: dict[str, Any]) -> str:
    """Resolve configured display tokens for registry comparisons."""

    text = str(value or "")
    return TOKEN_PATTERN.sub(
        lambda match: str(variables.get(match.group(0)[2:-2], match.group(0))),
        text,
    )


def _load_json(path: Path, issues: list[str]) -> dict[str, Any]:
    if not path.is_file():
        issues.append(f"missing JSON artifact: {path}")
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        issues.append(f"invalid JSON artifact {path}: {exc}")
        return {}
    if not isinstance(value, dict):
        issues.append(f"JSON artifact is not an object: {path}")
        return {}
    return value


def _validate_render_receipts(
    project_root: Path,
    variables: dict[str, Any],
    issues: list[str],
    *,
    require_current: bool,
    require_rendered: bool,
) -> None:
    """Verify the ordered render inputs and output hashes as one co-snapshot."""
    reports_dir = project_root / "output" / "reports"
    composition = _load_json(reports_dir / "manuscript_composition.json", issues)
    artifact_manifest = _load_json(reports_dir / "artifact_manifest.json", issues)
    rendered = _load_json(reports_dir / "rendered_provenance.json", issues)
    if not composition or not artifact_manifest or not rendered:
        return

    expected_values = {
        "source_commit": variables.get("REPRO_GIT_COMMIT", ""),
        "worktree_dirty": variables.get("REPRO_WORKTREE_DIRTY", ""),
        "config_sha256": variables.get("CONFIG_HASH", ""),
        "kernel_source_sha256": variables.get("REPRO_KERNEL_SOURCE_HASH", ""),
        "template_repository": variables.get("REPRO_TEMPLATE_REPOSITORY", ""),
        "template_revision": variables.get("REPRO_TEMPLATE_REVISION", ""),
        "template_hydration_mode": variables.get("REPRO_TEMPLATE_HYDRATION_MODE", ""),
    }
    for artifact_name, artifact in (
        ("composition", composition),
        ("artifact manifest", artifact_manifest),
        ("rendered provenance", rendered),
    ):
        for key, expected in expected_values.items():
            if key in artifact and _normalise_digest(
                artifact.get(key)
            ) != _normalise_digest(expected):
                issues.append(f"{artifact_name} is stale: {key}")

    variables_digest = hashlib.sha256(
        json.dumps(variables, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if composition.get("variable_sha256") != variables_digest:
        issues.append("render composition variable snapshot is stale")
    if rendered.get("variable_sha256") != variables_digest:
        issues.append("rendered provenance variable snapshot is stale")

    groups = composition.get("groups")
    if not isinstance(groups, dict) or not groups:
        issues.append("render composition has no ordered input groups")
        groups = {}
    for group_name, group in groups.items():
        if not isinstance(group, dict) or not isinstance(group.get("files"), list):
            issues.append(f"render composition group is invalid: {group_name}")
            continue
        current_entries: list[dict[str, Any]] = []
        combined = hashlib.sha256()
        for raw_entry in group["files"]:
            if not isinstance(raw_entry, dict):
                issues.append(
                    f"render composition has invalid file entry: {group_name}"
                )
                continue
            relative = str(raw_entry.get("path", ""))
            candidate = (project_root / relative).resolve()
            try:
                candidate.relative_to(project_root.resolve())
            except ValueError:
                issues.append(f"render composition path escapes repository: {relative}")
                continue
            if not candidate.is_file():
                issues.append(f"render composition input is missing: {relative}")
                continue
            content = candidate.read_bytes()
            digest = hashlib.sha256(content).hexdigest()
            current_entries.append(
                {"path": relative, "bytes": len(content), "sha256": digest}
            )
            combined.update(relative.encode("utf-8"))
            combined.update(b"\0")
            combined.update(content)
            combined.update(b"\0")
        if current_entries != group["files"]:
            issues.append(f"render composition inputs are stale: {group_name}")
        if group.get("combined_sha256") != combined.hexdigest():
            issues.append(f"render composition digest is stale: {group_name}")

    composition_without_digest = dict(composition)
    recorded_composition_digest = composition_without_digest.pop(
        "composition_sha256", ""
    )
    recomputed_composition_digest = hashlib.sha256(
        json.dumps(
            composition_without_digest, sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()
    if recorded_composition_digest != recomputed_composition_digest:
        issues.append("render composition self-digest is invalid")
    if artifact_manifest.get("composition_sha256") != recorded_composition_digest:
        issues.append("artifact manifest is bound to a different composition")
    if rendered.get("composition_sha256") != recorded_composition_digest:
        issues.append("rendered provenance is bound to a different composition")

    artifact_entries = artifact_manifest.get("artifacts")
    if not isinstance(artifact_entries, list):
        issues.append("artifact manifest artifacts must be a list")
        artifact_entries = []
    roles = set()
    for raw_entry in artifact_entries:
        if not isinstance(raw_entry, dict):
            issues.append("artifact manifest contains an invalid entry")
            continue
        role = str(raw_entry.get("role", ""))
        roles.add(role)
        relative = str(raw_entry.get("path", ""))
        candidate = (project_root / relative).resolve()
        try:
            candidate.relative_to(project_root.resolve())
        except ValueError:
            issues.append(f"artifact manifest path escapes repository: {relative}")
            continue
        if not candidate.is_file():
            issues.append(f"artifact manifest output is missing: {relative}")
            continue
        if raw_entry.get("bytes") != candidate.stat().st_size:
            issues.append(f"artifact manifest byte count is stale: {relative}")
        if raw_entry.get("sha256") != _sha256(candidate):
            issues.append(f"artifact manifest SHA-256 is stale: {relative}")
    if require_rendered and not {"html", "distribution_pdf"}.issubset(roles):
        issues.append("artifact manifest lacks required rendered HTML/PDF outputs")
    artifact_digest = _sha256(reports_dir / "artifact_manifest.json")
    if rendered.get("artifact_manifest_sha256") != artifact_digest:
        issues.append("rendered provenance artifact manifest digest is stale")

    if require_current:
        current_commit, current_dirty, current_status_sha256 = _git_snapshot(
            project_root
        )
        current_kernel_hash = _kernel_source_hash(project_root)
        current_config_hash = _sha256(project_root / "docs/manuscript/config.yaml")
        for key, actual, expected in (
            ("source_commit", composition.get("source_commit"), current_commit),
            (
                "worktree_dirty",
                str(composition.get("worktree_dirty", "")).lower(),
                str(current_dirty).lower(),
            ),
            ("config_sha256", composition.get("config_sha256"), current_config_hash),
            (
                "kernel_source_sha256",
                composition.get("kernel_source_sha256"),
                current_kernel_hash,
            ),
            (
                "status_sha256",
                variables.get("REPRO_STATUS_SHA256", ""),
                current_status_sha256,
            ),
        ):
            if _normalise_digest(actual) != _normalise_digest(expected):
                issues.append(f"render composition is not current: {key}")
        if variables.get("REPRO_TEMPLATE_HYDRATION_MODE") != "canonical-pinned":
            issues.append(
                "source-current render requires canonical-pinned template hydration"
            )


def _safe_path(root: Path, relative: object, issues: list[str]) -> Path | None:
    raw = Path(str(relative))
    if raw.is_absolute() or ".." in raw.parts:
        issues.append(f"unsafe repository-relative path in claim ledger: {relative}")
        return None
    path = (root / raw).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        issues.append(f"claim ledger path escapes repository root: {relative}")
        return None
    return path


def _validate_claim_ledger(
    root: Path, issues: list[str]
) -> tuple[int, dict[str, list[str]]]:
    path = root / "docs/manuscript/claim_ledger.yaml"
    if not path.is_file():
        issues.append(f"missing claim ledger: {path}")
        return 0, {"covered": [], "excluded": [], "unaccounted": []}
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        issues.append(f"invalid claim ledger {path}: {exc}")
        return 0, {"covered": [], "excluded": [], "unaccounted": []}
    if not isinstance(document, dict) or document.get("schema_version") != "1.0":
        issues.append("claim ledger must declare schema_version 1.0")
        return 0, {"covered": [], "excluded": [], "unaccounted": []}
    document = cast("dict[str, Any]", document)
    claims = document.get("claims")
    if not isinstance(claims, list) or not claims:
        issues.append("claim ledger must contain a non-empty claims list")
        return 0, {"covered": [], "excluded": [], "unaccounted": []}
    citation_text = (root / "docs/manuscript/references.bib").read_text(
        encoding="utf-8"
    )
    seen: set[str] = set()
    claim_source_paths: set[str] = set()
    for index, claim in enumerate(claims):
        prefix = f"claim {index}"
        if not isinstance(claim, dict):
            issues.append(f"{prefix} is not a mapping")
            continue
        claim = cast("dict[str, Any]", claim)
        claim_id = str(claim.get("id", ""))
        if not claim_id or claim_id in seen:
            issues.append(f"{prefix} has a missing or duplicate id: {claim_id!r}")
        seen.add(claim_id)
        claim_class = claim.get("class")
        if claim_class not in ALLOWED_CLAIM_CLASSES:
            issues.append(f"{prefix} has unsupported class: {claim_class!r}")
        status = claim.get("status")
        if status not in ALLOWED_CLAIM_STATUSES:
            issues.append(f"{prefix} has unsupported status: {status!r}")
        if not str(claim.get("statement", "")).strip():
            issues.append(f"{prefix} has no statement")
        if not str(claim.get("boundary", "")).strip():
            issues.append(f"{prefix} has no claim boundary")
        sources = claim.get("source", [])
        evidence = claim.get("evidence", [])
        citations = claim.get("citations", [])
        if not isinstance(sources, list) or not sources:
            issues.append(f"{prefix} must list at least one source document")
        if not isinstance(evidence, list) or not evidence:
            issues.append(f"{prefix} must list at least one evidence path")
        for entry in [
            *(sources if isinstance(sources, list) else []),
            *(evidence if isinstance(evidence, list) else []),
        ]:
            resolved = _safe_path(root, entry, issues)
            if resolved is not None and not resolved.exists():
                issues.append(f"{prefix} references missing path: {entry}")
        if isinstance(sources, list):
            claim_source_paths.update(str(entry) for entry in sources)
        if claim_class in {"analogy", "external_scholarship"} and (
            not isinstance(citations, list) or not citations
        ):
            issues.append(f"{prefix} requires citation keys for class {claim_class}")
        for citation in citations if isinstance(citations, list) else []:
            if not re.search(
                rf"@[A-Za-z]+\{{\s*{re.escape(str(citation))}\s*,", citation_text
            ):
                issues.append(f"{prefix} cites missing bibliography key: {citation}")

    source_audit = document.get("source_audit")
    if not isinstance(source_audit, dict):
        issues.append("claim ledger must declare source_audit coverage")
        return len(claims), {
            "covered": [],
            "excluded": [],
            "unaccounted": [],
        }
    covered_raw = source_audit.get("covered", [])
    excluded_raw = source_audit.get("excluded", {})
    if not isinstance(covered_raw, list):
        issues.append("claim ledger source_audit.covered must be a list")
        covered_raw = []
    if not isinstance(excluded_raw, dict):
        issues.append(
            "claim ledger source_audit.excluded must be a path-to-reason mapping"
        )
        excluded_raw = {}
    covered = {str(entry) for entry in covered_raw}
    excluded = {str(entry) for entry in excluded_raw}
    overlap = sorted(covered & excluded)
    if overlap:
        issues.append(
            "claim ledger source_audit overlaps covered and excluded paths: "
            + ", ".join(overlap)
        )
    declared = covered | excluded
    for entry in sorted(declared):
        resolved = _safe_path(root, entry, issues)
        if resolved is not None and not resolved.exists():
            issues.append(f"claim ledger source_audit references missing path: {entry}")
    active_sources = {
        str(path.relative_to(root))
        for path in (root / "docs/manuscript").glob("[0-9]*.md")
    }
    unaccounted = sorted(active_sources - declared)
    unexpected = sorted(declared - active_sources - {"docs/manuscript/source.md"})
    if unaccounted:
        issues.append(
            "claim ledger leaves active manuscript sources unaccounted: "
            + ", ".join(unaccounted)
        )
    if unexpected:
        issues.append(
            "claim ledger source_audit names unexpected paths: " + ", ".join(unexpected)
        )
    uncovered_claim_sources = sorted(claim_source_paths - declared)
    if uncovered_claim_sources:
        issues.append(
            "claim sources are absent from source_audit: "
            + ", ".join(uncovered_claim_sources)
        )
    for path in excluded:
        if not str(excluded_raw.get(path, "")).strip():
            issues.append(f"claim ledger excluded source has no reason: {path}")
    return len(claims), {
        "covered": sorted(covered),
        "excluded": sorted(excluded),
        "unaccounted": unaccounted,
    }


def validate_manuscript_integrity(
    root: str | Path = ".",
    *,
    require_rendered: bool = False,
    verify_bibliography_online: bool = False,
    require_source_current: bool = False,
    persist_bibliography_audit: bool = False,
) -> dict[str, Any]:
    """Return a machine-readable integrity report for the current repository."""

    project_root = Path(root).resolve()
    issues: list[str] = []
    variables_path = project_root / "output/data/manuscript_variables.json"
    manifest_path = project_root / "output/data/manuscript_variable_manifest.json"
    config_path = project_root / "docs/manuscript/config.yaml"
    variables = _load_json(variables_path, issues)
    manifest = _load_json(manifest_path, issues)
    config = (
        yaml.safe_load(config_path.read_text(encoding="utf-8"))
        if config_path.is_file()
        else {}
    )
    if not isinstance(config, dict):
        issues.append(f"manuscript config is not a mapping: {config_path}")
        config = {}

    config_hash = _sha256(config_path) if config_path.is_file() else ""
    if _normalise_digest(variables.get("CONFIG_HASH")) != config_hash:
        issues.append("variable snapshot CONFIG_HASH does not match manuscript config")
    if _normalise_digest(manifest.get("config_sha256")) != config_hash:
        issues.append(
            "variable manifest config_sha256 does not match manuscript config"
        )
    if manifest.get("status") != "valid":
        issues.append("variable manifest is not valid")
    expected_variable_hash = hashlib.sha256(
        json.dumps(variables, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if manifest.get("variable_sha256") != expected_variable_hash:
        issues.append("variable manifest variable_sha256 does not match snapshot")
    manifest_provenance = manifest.get("provenance", {})
    if not isinstance(manifest_provenance, dict):
        issues.append("variable manifest provenance must be an object")
        manifest_provenance = {}
    for manifest_key, variable_key in (
        ("source_commit", "REPRO_GIT_COMMIT"),
        ("worktree_dirty", "REPRO_WORKTREE_DIRTY"),
        ("status_sha256", "REPRO_STATUS_SHA256"),
        ("config_sha256", "CONFIG_HASH"),
        ("kernel_source_sha256", "REPRO_KERNEL_SOURCE_HASH"),
    ):
        if _normalise_digest(
            manifest_provenance.get(manifest_key)
        ) != _normalise_digest(variables.get(variable_key)):
            issues.append(
                "variable manifest provenance is stale: "
                f"{manifest_key} does not match {variable_key}"
            )

    variable_registry_path = (
        project_root / "output" / "data" / "manuscript_variable_registry.json"
    )
    if require_rendered or require_source_current:
        variable_registry = _load_json(variable_registry_path, issues)
        registry_entries = variable_registry.get("entries", [])
        if not isinstance(registry_entries, list):
            issues.append("typed variable registry entries must be a list")
            registry_entries = []
        registry_names = set()
        for entry in registry_entries:
            if not isinstance(entry, dict):
                issues.append("typed variable registry contains an invalid entry")
                continue
            name = str(entry.get("name", ""))
            registry_names.add(name)
            for field in (
                "source_type",
                "render_type",
                "unit",
                "missing_policy",
                "producer",
                "consumers",
            ):
                if field not in entry:
                    issues.append(
                        f"typed variable registry entry {name!r} lacks {field}"
                    )
        if registry_names != set(variables):
            issues.append(
                "typed variable registry does not cover the variable snapshot"
            )
        expected_variable_hash = hashlib.sha256(
            json.dumps(variables, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        if variable_registry.get("variable_sha256") != expected_variable_hash:
            issues.append("typed variable registry variable_sha256 is stale")

    configured_figures = config.get("figures", {})
    if not isinstance(configured_figures, dict) or not configured_figures:
        issues.append("manuscript config has no figures mapping")
        configured_figures = {}
    registry_path = project_root / "output/figures/figure_registry.json"
    registry = _load_json(registry_path, issues)
    registry_entries = registry.get("figures", [])
    if not isinstance(registry_entries, list):
        issues.append("figure registry figures must be a list")
        registry_entries = []
    if registry.get("count") != len(configured_figures) or registry.get("count") != len(
        registry_entries
    ):
        issues.append(
            "figure registry count does not match configured and emitted figures"
        )
    if _normalise_digest(registry.get("config_hash")) != _normalise_digest(
        variables.get("CONFIG_HASH")
    ):
        issues.append("figure registry config_hash does not match variable snapshot")
    configured_names = {
        str(spec.get("filename"))
        for spec in configured_figures.values()
        if isinstance(spec, dict) and spec.get("filename")
    }
    try:
        declared_figure_count = int(str(variables.get("ARTIFACT_FIGURE_COUNT", "")))
    except ValueError:
        declared_figure_count = -1
    if declared_figure_count != len(configured_names):
        issues.append(
            "variable snapshot ARTIFACT_FIGURE_COUNT does not match configured figures"
        )
    registry_names: set[str] = set()
    registry_by_name: dict[str, dict[str, Any]] = {}
    figure_dir = project_root / "output/figures"
    if registry.get("schema_version") != 4:
        issues.append("figure registry must declare schema_version 4")
    for registry_key, variable_key in (
        ("source_commit", "REPRO_GIT_COMMIT"),
        ("worktree_dirty", "REPRO_WORKTREE_DIRTY"),
        ("kernel_source_hash", "REPRO_KERNEL_SOURCE_HASH"),
    ):
        if not str(registry.get(registry_key, "")).strip():
            issues.append(f"figure registry is missing {registry_key}")
        elif _normalise_digest(registry.get(registry_key)) != _normalise_digest(
            variables.get(variable_key)
        ):
            issues.append(
                "figure registry provenance is stale: "
                f"{registry_key} does not match {variable_key}"
            )
    for entry in registry_entries:
        if not isinstance(entry, dict):
            issues.append("figure registry contains a non-mapping entry")
            continue
        filename = str(entry.get("filename", ""))
        if not filename or filename in registry_names:
            issues.append(
                f"figure registry has missing or duplicate filename: {filename!r}"
            )
        registry_names.add(filename)
        registry_by_name[filename] = entry
        figure_path = figure_dir / filename
        if not figure_path.is_file():
            issues.append(f"figure registry references missing PNG: {filename}")
            continue
        if entry.get("bytes") != figure_path.stat().st_size:
            issues.append(f"figure byte count is stale: {filename}")
        if entry.get("sha256") != _sha256(figure_path):
            issues.append(f"figure SHA-256 is stale: {filename}")
        matching_specs = [
            spec
            for spec in configured_figures.values()
            if isinstance(spec, dict) and spec.get("filename") == filename
        ]
        if not matching_specs:
            issues.append(f"figure registry contains unconfigured PNG: {filename}")
        else:
            spec = matching_specs[0]
            for key in (
                "label",
                "width",
                "evidence_class",
                "caption",
                "alt_text",
                "long_description",
            ):
                expected = _resolve_tokens(spec.get(key, ""), variables)
                if str(entry.get(key, "")) != expected:
                    issues.append(f"figure registry {key} is stale: {filename}")
            for key in ("caption", "alt_text", "long_description"):
                if not str(entry.get(key, "")).strip():
                    issues.append(f"figure registry has empty {key}: {filename}")
            if _normalise_text(entry.get("caption")) == _normalise_text(
                entry.get("alt_text")
            ):
                issues.append(
                    f"figure registry caption and alt text are duplicated: {filename}"
                )
            if len(_normalise_text(entry.get("long_description")).split()) <= len(
                _normalise_text(entry.get("alt_text")).split()
            ):
                issues.append(
                    f"figure registry extended description adds no detail: {filename}"
                )
    if registry_names != configured_names:
        issues.append("configured figure filenames and registry filenames differ")

    hydrated_dir = project_root / "output/manuscript"
    markdown_files = sorted(hydrated_dir.glob("*.md")) if hydrated_dir.is_dir() else []
    if not markdown_files:
        issues.append(f"hydrated manuscript directory is empty: {hydrated_dir}")
    referenced_figures: set[str] = set()
    referenced_description_ids: set[str] = set()
    for path in markdown_files:
        content = path.read_text(encoding="utf-8")
        if TOKEN_PATTERN.search(content):
            issues.append(f"unresolved token in hydrated manuscript: {path}")
        parser = _ImageParser()
        parser.feed(content)
        for duplicate_id in sorted(parser.duplicate_description_ids):
            issues.append(
                f"duplicate extended-description id in hydrated manuscript: "
                f"{path} -> {duplicate_id}"
            )
        for _caption, filename, attribute_text in IMAGE_PATTERN.findall(content):
            referenced_figures.add(filename)
            attributes = dict(ATTRIBUTE_PATTERN.findall(attribute_text))
            description_id = _validate_figure_reference(
                filename=filename,
                alt_text=attributes.get("alt", ""),
                describedby=attributes.get("aria-describedby", ""),
                descriptions=parser.descriptions,
                registry_by_name=registry_by_name,
                context=f"hydrated Markdown {path}",
                issues=issues,
            )
            if description_id:
                referenced_description_ids.add(description_id)
        for image in parser.images:
            filename = image["src"].removeprefix("figures/")
            if image["src"].startswith("figures/") and filename.endswith(".png"):
                referenced_figures.add(filename)
                description_id = _validate_figure_reference(
                    filename=filename,
                    alt_text=image["alt"],
                    describedby=image["aria_describedby"],
                    descriptions=parser.descriptions,
                    registry_by_name=registry_by_name,
                    context=f"hydrated HTML {path}",
                    issues=issues,
                )
                if description_id:
                    referenced_description_ids.add(description_id)
    if referenced_figures != configured_names:
        issues.append(
            "hydrated manuscript figure references do not cover the figure registry"
        )
    expected_description_ids = {
        f"{entry.get('label', '')}-description"
        for entry in registry_by_name.values()
        if entry.get("label")
    }
    filename_by_description_id = {
        f"{entry.get('label', '')}-description": filename
        for filename, entry in registry_by_name.items()
        if entry.get("label")
    }
    if referenced_description_ids != expected_description_ids:
        issues.append(
            "hydrated manuscript extended descriptions do not cover the figure registry"
        )

    claim_count, claim_source_audit = _validate_claim_ledger(project_root, issues)
    manuscript_sources = sorted((project_root / "docs/manuscript").glob("[0-9]*.md"))
    bibliography_audit = audit_bibliography(
        project_root / "docs/manuscript/references.bib",
        manuscript_sources,
        verify_online=verify_bibliography_online,
        workers=2,
    )
    if persist_bibliography_audit:
        write_bibliography_audit(
            project_root / "output/data/bibliography_audit.json",
            bibliography_audit,
        )
    for field, label in (
        ("missing_citations", "missing bibliography citations"),
        ("unused_bibliography_keys", "unused bibliography keys"),
        ("duplicate_bibliography_keys", "duplicate bibliography keys"),
        ("unresolved_locators", "bibliography records without primary locators"),
    ):
        values = bibliography_audit[field]
        if values:
            issues.append(f"{label}: {', '.join(values)}")
    if verify_bibliography_online:
        for field, label in (
            ("online_failures", "unresolved online bibliography records"),
            ("title_mismatches", "bibliography DOI title mismatches"),
        ):
            values = bibliography_audit[field]
            if values:
                issues.append(f"{label}: {', '.join(values)}")
    hardcoded_numeric_literals = _hardcoded_numeric_literals(
        project_root / "docs/manuscript"
    )
    issues.extend(
        "hardcoded numeric literal outside an allowed mathematical/metadata context: "
        + finding
        for finding in hardcoded_numeric_literals
    )

    html_path = project_root / "output/paper.html"
    html_images = 0
    if html_path.is_file():
        parser = _ImageParser()
        html_content = html_path.read_text(encoding="utf-8")
        parser.feed(html_content)
        html_images = len(parser.images)
        if html_images != len(configured_names):
            issues.append("rendered HTML image count does not match configured figures")
        if parser.duplicate_description_ids:
            issues.append("rendered HTML contains duplicate extended-description ids")
        html_description_ids: set[str] = set()
        html_figure_names: set[str] = set()
        for image in parser.images:
            filename = _rendered_figure_filename(
                image,
                filename_by_description_id=filename_by_description_id,
                issues=issues,
            )
            if not filename:
                continue
            html_figure_names.add(filename)
            description_id = _validate_figure_reference(
                filename=filename,
                alt_text=image["alt"],
                describedby=image["aria_describedby"],
                descriptions=parser.descriptions,
                registry_by_name=registry_by_name,
                context="rendered HTML",
                issues=issues,
            )
            if description_id:
                html_description_ids.add(description_id)
        if html_figure_names != configured_names:
            issues.append("rendered HTML figures do not cover the figure registry")
        if html_description_ids != expected_description_ids:
            issues.append(
                "rendered HTML extended descriptions do not cover the figure registry"
            )
        if TOKEN_PATTERN.search(html_content):
            issues.append("rendered HTML contains unresolved manuscript tokens")
    elif require_rendered:
        issues.append(f"missing rendered HTML: {html_path}")

    pdf_path = project_root / "output/paper.pdf"
    pdf_pages = 0
    if pdf_path.is_file():
        if shutil.which("pdfinfo"):
            info = subprocess.run(
                ["pdfinfo", str(pdf_path)], capture_output=True, text=True, check=False
            )
            page_match = re.search(r"^Pages:\s+(\d+)", info.stdout, re.MULTILINE)
            pdf_pages = int(page_match.group(1)) if page_match else 0
            if info.returncode != 0 or pdf_pages <= 0:
                issues.append(f"pdfinfo could not validate rendered PDF: {pdf_path}")
        elif require_rendered:
            issues.append("pdfinfo is required for --require-rendered")
        if shutil.which("pdftotext"):
            text = subprocess.run(
                ["pdftotext", str(pdf_path), "-"],
                capture_output=True,
                text=True,
                check=False,
            )
            if text.returncode != 0:
                issues.append(f"pdftotext could not inspect rendered PDF: {pdf_path}")
            elif TOKEN_PATTERN.search(text.stdout):
                issues.append("rendered PDF contains unresolved manuscript tokens")
        elif require_rendered:
            issues.append("pdftotext is required for --require-rendered")
    elif require_rendered:
        issues.append(f"missing rendered PDF: {pdf_path}")

    if require_rendered or require_source_current:
        _validate_render_receipts(
            project_root,
            variables,
            issues,
            require_current=require_source_current,
            require_rendered=require_rendered,
        )

    source_current: dict[str, Any] = {
        "checked": require_source_current,
        "status": "not_checked",
    }
    if require_source_current:
        source_issue_start = len(issues)
        current_commit, current_dirty, current_status_sha256 = _git_snapshot(
            project_root
        )
        current_kernel_hash = _kernel_source_hash(project_root)
        source_current.update(
            {
                "current_commit": current_commit,
                "current_dirty": current_dirty,
                "current_status_sha256": current_status_sha256,
                "current_kernel_source_sha256": current_kernel_hash,
            }
        )
        if not current_commit:
            issues.append("--require-source-current could not resolve git HEAD")
        if not current_kernel_hash:
            issues.append(
                "--require-source-current could not hash Colony Kernel/manuscript sources"
            )
        for label, actual, expected in (
            ("REPRO_GIT_COMMIT", variables.get("REPRO_GIT_COMMIT"), current_commit),
            (
                "REPRO_KERNEL_SOURCE_HASH",
                variables.get("REPRO_KERNEL_SOURCE_HASH"),
                current_kernel_hash,
            ),
            (
                "REPRO_WORKTREE_DIRTY",
                variables.get("REPRO_WORKTREE_DIRTY"),
                str(current_dirty).lower(),
            ),
            (
                "REPRO_STATUS_SHA256",
                variables.get("REPRO_STATUS_SHA256"),
                current_status_sha256,
            ),
        ):
            if _normalise_digest(actual) != _normalise_digest(expected):
                issues.append(
                    f"generated variable {label} does not match current source state"
                )

        hydrated_text = "\n".join(
            path.read_text(encoding="utf-8") for path in markdown_files
        )
        for label, expected in (
            ("commit", current_commit),
            ("config hash", config_hash),
            ("kernel source hash", current_kernel_hash),
        ):
            if not _compact_contains(hydrated_text, expected):
                issues.append(f"hydrated Markdown is missing current {label}")

        if not html_path.is_file():
            issues.append("--require-source-current requires rendered HTML")
        else:
            html_text = html_path.read_text(encoding="utf-8")
            for label, expected in (
                ("commit", current_commit),
                ("config hash", config_hash),
                ("kernel source hash", current_kernel_hash),
            ):
                if not _compact_contains(html_text, expected):
                    issues.append(f"rendered HTML is missing current {label}")

        if not pdf_path.is_file():
            issues.append("--require-source-current requires rendered PDF")
        elif not shutil.which("pdftotext"):
            issues.append("pdftotext is required for --require-source-current")
        else:
            pdf_text_result = subprocess.run(
                ["pdftotext", str(pdf_path), "-"],
                capture_output=True,
                text=True,
                check=False,
            )
            if pdf_text_result.returncode != 0:
                issues.append("pdftotext could not inspect PDF source provenance")
            else:
                for label, expected in (
                    ("commit", current_commit),
                    ("config hash", config_hash),
                    ("kernel source hash", current_kernel_hash),
                ):
                    if not _compact_contains(pdf_text_result.stdout, expected):
                        issues.append(f"rendered PDF is missing current {label}")

        release_version = str(variables.get("CONFIG_VERSION", "")).strip()
        release_root = (
            project_root / "output" / "release" / f"codomyrmex-{release_version}"
            if release_version
            else project_root / "output" / "release" / "__missing-version__"
        )
        if not release_root.is_dir():
            issues.append(f"missing source-current release bundle: {release_root}")
        else:
            source_state = _load_json(
                release_root / "receipts" / "source-state.json", issues
            )
            release_variables = _load_json(
                release_root / "reproducibility" / "manuscript_variables.json",
                issues,
            )
            release_manifest = _load_json(
                release_root / "publication_manifest.json", issues
            )
            for label, actual, expected in (
                ("source receipt commit", source_state.get("commit"), current_commit),
                (
                    "source receipt dirty state",
                    str(source_state.get("dirty", "")).lower(),
                    str(current_dirty).lower(),
                ),
                (
                    "source receipt status digest",
                    source_state.get("status_sha256"),
                    current_status_sha256,
                ),
                (
                    "source receipt rendered commit",
                    source_state.get("rendered_commit"),
                    variables.get("REPRO_GIT_COMMIT"),
                ),
                (
                    "source receipt config hash",
                    source_state.get("config_sha256"),
                    config_hash,
                ),
                (
                    "source receipt kernel hash",
                    source_state.get("kernel_source_sha256"),
                    current_kernel_hash,
                ),
            ):
                if _normalise_digest(actual) != _normalise_digest(expected):
                    issues.append(f"{label} is stale")
            for label, actual, expected in (
                (
                    "release variables commit",
                    release_variables.get("REPRO_GIT_COMMIT"),
                    current_commit,
                ),
                (
                    "release variables config hash",
                    release_variables.get("CONFIG_HASH"),
                    config_hash,
                ),
                (
                    "release variables kernel hash",
                    release_variables.get("REPRO_KERNEL_SOURCE_HASH"),
                    current_kernel_hash,
                ),
            ):
                if _normalise_digest(actual) != _normalise_digest(expected):
                    issues.append(f"{label} is stale")
            source = release_manifest.get("source", {})
            if not isinstance(source, dict):
                issues.append("publication manifest source must be an object")
            else:
                for label, actual, expected in (
                    (
                        "publication manifest commit",
                        source.get("commit"),
                        current_commit,
                    ),
                    (
                        "publication manifest dirty state",
                        str(source.get("dirty", "")).lower(),
                        str(current_dirty).lower(),
                    ),
                    (
                        "publication manifest status digest",
                        source.get("status_sha256"),
                        current_status_sha256,
                    ),
                ):
                    if _normalise_digest(actual) != _normalise_digest(expected):
                        issues.append(f"{label} is stale")
            _release_artifact_hashes(
                release_root, release_manifest, project_root, issues
            )
        source_current["status"] = (
            "valid" if len(issues) == source_issue_start else "invalid"
        )
        source_current["errors_added"] = len(issues) - source_issue_start

    return {
        "schema_version": "1.0",
        "status": "valid" if not issues else "invalid",
        "config_sha256": config_hash,
        "figure_count": len(configured_names),
        "html_image_count": html_images,
        "pdf_pages": pdf_pages,
        "claim_count": claim_count,
        "claim_source_audit": claim_source_audit,
        "bibliography_audit": {
            "record_count": bibliography_audit["record_count"],
            "cited_count": bibliography_audit["cited_count"],
            "cross_reference_count": bibliography_audit["cross_reference_count"],
            "online_verification": bibliography_audit["online_verification"],
            "access_limited": [
                record["key"]
                for record in bibliography_audit["records"]
                if record["access_limited"]
            ],
        },
        "hardcoded_numeric_literals": hardcoded_numeric_literals,
        "source_current": source_current,
        "errors": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--require-rendered",
        action="store_true",
        help="Require and inspect output/paper.html and output/paper.pdf.",
    )
    parser.add_argument(
        "--online-bibliography",
        action="store_true",
        help="Resolve cited DOI, arXiv, ISBN, and official-URL metadata online.",
    )
    parser.add_argument(
        "--require-source-current",
        action="store_true",
        help=(
            "Fail closed unless generated variables, figures, rendered artifacts, "
            "and the release bundle match the current commit/config/source hashes."
        ),
    )
    parser.add_argument(
        "--write-bibliography-audit",
        action="store_true",
        help="Persist bibliography_audit.json; validation is read-only by default.",
    )
    args = parser.parse_args()
    report = validate_manuscript_integrity(
        args.repo_root,
        require_rendered=args.require_rendered,
        verify_bibliography_online=args.online_bibliography,
        require_source_current=args.require_source_current,
        persist_bibliography_audit=args.write_bibliography_audit,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
