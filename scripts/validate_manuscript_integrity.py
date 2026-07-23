#!/usr/bin/env python3
"""Validate the manuscript's generated evidence and rendered-artifact contract.

This validator is intentionally stricter than a token check.  It verifies that
the current variable snapshot, figure registry, hydrated Markdown, claim ledger,
and (when requested) HTML/PDF outputs describe the same source/configuration
state.  It never regenerates files and never infers missing evidence.

Examples:

    uv run python scripts/validate_manuscript_integrity.py
    uv run python scripts/validate_manuscript_integrity.py --require-rendered
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
from typing import Any

import yaml

TOKEN_PATTERN = re.compile(r"\{\{[A-Z0-9_]+\}\}")
IMAGE_PATTERN = re.compile(r"!\[(.*?)\]\(figures/([^\)]+\.png)\)")
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
    """Collect HTML image alt attributes without depending on a DOM package."""

    def __init__(self) -> None:
        super().__init__()
        self.images: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "img":
            return
        values = {key.lower(): value or "" for key, value in attrs}
        self.images.append({"src": values.get("src", ""), "alt": values.get("alt", "")})


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
        return 0
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
    root: str | Path = ".", *, require_rendered: bool = False
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
    registry_names: set[str] = set()
    figure_dir = project_root / "output/figures"
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
            for key in ("label", "width", "evidence_class", "caption"):
                expected = _resolve_tokens(spec.get(key, ""), variables)
                if str(entry.get(key, "")) != expected:
                    issues.append(f"figure registry {key} is stale: {filename}")
            if not str(entry.get("caption", "")).strip():
                issues.append(f"figure registry has empty caption: {filename}")
    if registry_names != configured_names:
        issues.append("configured figure filenames and registry filenames differ")

    hydrated_dir = project_root / "output/manuscript"
    markdown_files = sorted(hydrated_dir.glob("*.md")) if hydrated_dir.is_dir() else []
    if not markdown_files:
        issues.append(f"hydrated manuscript directory is empty: {hydrated_dir}")
    referenced_figures: set[str] = set()
    for path in markdown_files:
        content = path.read_text(encoding="utf-8")
        if TOKEN_PATTERN.search(content):
            issues.append(f"unresolved token in hydrated manuscript: {path}")
        for alt, filename in IMAGE_PATTERN.findall(content):
            referenced_figures.add(filename)
            if not alt.strip():
                issues.append(
                    f"figure has empty Markdown alt text: {path} -> {filename}"
                )
            if filename not in configured_names:
                issues.append(
                    f"hydrated manuscript references unconfigured figure: {filename}"
                )
        parser = _ImageParser()
        parser.feed(content)
        for image in parser.images:
            filename = image["src"].removeprefix("figures/")
            if image["src"].startswith("figures/") and filename.endswith(".png"):
                referenced_figures.add(filename)
                if not image["alt"].strip():
                    issues.append(
                        f"figure has empty HTML alt text: {path} -> {filename}"
                    )
                if filename not in configured_names:
                    issues.append(
                        f"hydrated manuscript references unconfigured figure: {filename}"
                    )
    if referenced_figures != configured_names:
        issues.append(
            "hydrated manuscript figure references do not cover the figure registry"
        )

    claim_count, claim_source_audit = _validate_claim_ledger(project_root, issues)
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
        parser.feed(html_path.read_text(encoding="utf-8"))
        html_images = len(parser.images)
        if html_images != len(configured_names):
            issues.append("rendered HTML image count does not match configured figures")
        if any(not image["alt"].strip() for image in parser.images):
            issues.append("rendered HTML contains an image without non-empty alt text")
        if TOKEN_PATTERN.search(html_path.read_text(encoding="utf-8")):
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

    return {
        "schema_version": "1.0",
        "status": "valid" if not issues else "invalid",
        "config_sha256": config_hash,
        "figure_count": len(configured_names),
        "html_image_count": html_images,
        "pdf_pages": pdf_pages,
        "claim_count": claim_count,
        "claim_source_audit": claim_source_audit,
        "hardcoded_numeric_literals": hardcoded_numeric_literals,
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
    args = parser.parse_args()
    report = validate_manuscript_integrity(
        args.repo_root, require_rendered=args.require_rendered
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
