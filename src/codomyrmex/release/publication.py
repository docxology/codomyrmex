"""Portable publication bundles, verification, and dry-run release plans."""

from __future__ import annotations

import hashlib
import json
import mimetypes
import platform
import shutil
import subprocess
import sys
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

MANIFEST_SCHEMA_VERSION = "1"
REMOTE_PUBLICATION_TARGETS = frozenset({"github", "zenodo-sandbox"})


@dataclass(frozen=True)
class PublicationMetadata:
    """Shared metadata for the report and its archival records."""

    title: str
    version: str
    authors: tuple[str, ...]
    publication_type: str = "technical-report"
    subtitle: str = ""
    abstract: str = ""
    keywords: tuple[str, ...] = ()
    repository_url: str = ""
    license: str = "MIT"
    doi: str | None = None


@dataclass(frozen=True)
class PublicationArtifact:
    """Portable identity for one file in a publication bundle."""

    path: str
    role: str
    media_type: str
    size_bytes: int
    sha256: str
    sha512: str


@dataclass(frozen=True)
class PublicationManifest:
    """Versioned, detached publication manifest."""

    schema_version: str
    metadata: PublicationMetadata
    source_commit: str
    source_dirty: bool
    source_status_sha256: str
    source_date_epoch: int
    producer_versions: tuple[tuple[str, str], ...]
    input_hashes: tuple[PublicationArtifact, ...]
    artifacts: tuple[PublicationArtifact, ...]
    validation_outcomes: tuple[tuple[str, bool, str], ...]


@dataclass(frozen=True)
class PublicationBundle:
    """Prepared bundle location and immutable manifest view."""

    root: Path
    manifest_path: Path
    manifest: PublicationManifest


@dataclass(frozen=True)
class PublicationVerification:
    """Verification outcome for a prepared publication bundle."""

    valid: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    verified_artifacts: tuple[str, ...]


@dataclass(frozen=True)
class PublicationPlan:
    """Non-mutating remote publication plan and its receipt."""

    target: str
    dry_run: bool
    executed: bool
    receipt_path: Path
    receipt_sha256: str
    artifact_count: int


def _hash_file(path: Path, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact(path: Path, root: Path, role: str) -> PublicationArtifact:
    relative = path.resolve().relative_to(root.resolve()).as_posix()
    media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return PublicationArtifact(
        path=relative,
        role=role,
        media_type=media_type,
        size_bytes=path.stat().st_size,
        sha256=_hash_file(path, "sha256"),
        sha512=_hash_file(path, "sha512"),
    )


def _copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() != destination.resolve():
        shutil.copy2(source, destination)


def _run_version(command: list[str]) -> str:
    executable = shutil.which(command[0])
    if executable is None:
        return "not-installed"
    result = subprocess.run(
        [executable, *command[1:]],
        capture_output=True,
        text=True,
        check=False,
    )
    text = (result.stdout or result.stderr).strip().splitlines()
    return text[0] if text else f"exit-{result.returncode}"


def _git_state(project_root: Path) -> tuple[str, bool, str, tuple[str, ...]]:
    commit_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if commit_result.returncode != 0:
        return "not-a-git-checkout", False, hashlib.sha256(b"").hexdigest(), ()
    status_result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )
    lines = tuple(line for line in status_result.stdout.splitlines() if line)
    canonical = "\n".join(lines).encode()
    return (
        commit_result.stdout.strip(),
        bool(lines),
        hashlib.sha256(canonical).hexdigest(),
        lines,
    )


def _metadata_dict(metadata: PublicationMetadata) -> dict[str, Any]:
    value = asdict(metadata)
    value["authors"] = list(metadata.authors)
    value["keywords"] = list(metadata.keywords)
    return value


def _artifact_dict(artifact: PublicationArtifact) -> dict[str, Any]:
    return asdict(artifact)


def _manifest_dict(manifest: PublicationManifest) -> dict[str, Any]:
    return {
        "schema_version": manifest.schema_version,
        "metadata": _metadata_dict(manifest.metadata),
        "source": {
            "commit": manifest.source_commit,
            "dirty": manifest.source_dirty,
            "status_sha256": manifest.source_status_sha256,
        },
        "source_date_epoch": manifest.source_date_epoch,
        "producer_versions": dict(manifest.producer_versions),
        "input_hashes": [_artifact_dict(item) for item in manifest.input_hashes],
        "artifacts": [_artifact_dict(item) for item in manifest.artifacts],
        "validation_outcomes": [
            {"name": name, "passed": passed, "detail": detail}
            for name, passed, detail in manifest.validation_outcomes
        ],
    }


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _write_citation(path: Path, metadata: PublicationMetadata) -> None:
    citation: dict[str, Any] = {
        "cff-version": "1.2.0",
        "message": "If you use this technical report or software, cite this record.",
        "type": "software",
        "title": metadata.title,
        "version": metadata.version,
        "license": metadata.license,
        "authors": [{"name": author} for author in metadata.authors],
    }
    if metadata.repository_url:
        citation["repository-code"] = metadata.repository_url
    if metadata.doi:
        citation["doi"] = metadata.doi
    path.write_text(
        yaml.safe_dump(citation, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def _write_zenodo(path: Path, metadata: PublicationMetadata) -> None:
    record: dict[str, Any] = {
        "metadata": {
            "title": metadata.title,
            "upload_type": "publication",
            "publication_type": "report",
            "description": metadata.abstract or metadata.subtitle,
            "creators": [{"name": author} for author in metadata.authors],
            "version": metadata.version,
            "license": metadata.license,
            "keywords": list(metadata.keywords),
        }
    }
    if metadata.repository_url:
        record["metadata"]["related_identifiers"] = [
            {
                "identifier": metadata.repository_url,
                "relation": "isSupplementTo",
                "resource_type": "software",
            }
        ]
    if metadata.doi:
        record["metadata"]["doi"] = metadata.doi
    _write_json(path, record)


def _producer_versions() -> tuple[tuple[str, str], ...]:
    return tuple(
        sorted(
            {
                "codomyrmex-python": platform.python_version(),
                "implementation": sys.implementation.name,
                "lualatex": _run_version(["lualatex", "--version"]),
                "pandoc": _run_version(["pandoc", "--version"]),
                "qpdf": _run_version(["qpdf", "--version"]),
                "uv": _run_version(["uv", "--version"]),
            }.items()
        )
    )


def prepare_publication_bundle(
    *,
    metadata: PublicationMetadata,
    content_pdf: str | Path,
    distribution_pdf: str | Path,
    semantic_html: str | Path,
    output_dir: str | Path,
    project_root: str | Path = ".",
    reproducibility_inputs: Iterable[str | Path] = (),
    validation_receipts: Iterable[str | Path] = (),
    validation_outcomes: Iterable[tuple[str, bool, str]] = (),
    source_date_epoch: int = 0,
) -> PublicationBundle:
    """Create a portable, detached-hash publication bundle.

    The three rendered report files must already exist. This function never
    invokes a remote service and never mutates DOI metadata.
    """
    if metadata.publication_type != "technical-report":
        message = "publication_type must be 'technical-report'"
        raise ValueError(message)
    if metadata.doi is not None and not metadata.doi.strip():
        message = "Use doi=None for an unassigned DOI"
        raise ValueError(message)
    if (
        not metadata.title.strip()
        or not metadata.version.strip()
        or not metadata.authors
    ):
        message = "Title, version, and at least one author are required"
        raise ValueError(message)
    if any(character in metadata.version for character in ("/", "\\", "\0")):
        message = "Version must be safe for a portable directory name"
        raise ValueError(message)

    root = Path(output_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    project = Path(project_root).resolve()
    required_sources = {
        "content-pdf": Path(content_pdf).resolve(),
        "distribution-pdf": Path(distribution_pdf).resolve(),
        "semantic-html": Path(semantic_html).resolve(),
    }
    missing = [str(path) for path in required_sources.values() if not path.is_file()]
    if missing:
        message = f"Required publication artifacts are missing: {', '.join(missing)}"
        raise FileNotFoundError(message)

    stem = f"codomyrmex-{metadata.version}"
    destinations = {
        "content-pdf": root / f"{stem}-content.pdf",
        "distribution-pdf": root / f"{stem}.pdf",
        "semantic-html": root / f"{stem}.html",
    }
    for role, source in required_sources.items():
        _copy(source, destinations[role])

    citation_path = root / "CITATION.cff"
    zenodo_path = root / ".zenodo.json"
    metadata_path = root / "publication_metadata.json"
    _write_citation(citation_path, metadata)
    _write_zenodo(zenodo_path, metadata)
    _write_json(metadata_path, _metadata_dict(metadata))

    copied_inputs: list[Path] = []
    for item in reproducibility_inputs:
        source = Path(item).resolve()
        if not source.is_file():
            message = f"Reproducibility input does not exist: {source}"
            raise FileNotFoundError(message)
        destination = root / "reproducibility" / source.name
        _copy(source, destination)
        copied_inputs.append(destination)

    copied_receipts: list[Path] = []
    for item in validation_receipts:
        source = Path(item).resolve()
        if not source.is_file():
            message = f"Validation receipt does not exist: {source}"
            raise FileNotFoundError(message)
        destination = root / "receipts" / source.name
        _copy(source, destination)
        copied_receipts.append(destination)

    commit, dirty, status_sha256, status_lines = _git_state(project)
    source_provenance: dict[str, str] = {}
    variables_copy = root / "reproducibility" / "manuscript_variables.json"
    if variables_copy.is_file():
        try:
            variables_payload = json.loads(variables_copy.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(
                "reproducibility/manuscript_variables.json is not valid JSON"
            ) from exc
        if not isinstance(variables_payload, dict):
            raise ValueError(
                "reproducibility/manuscript_variables.json must contain an object"
            )
        source_provenance = {
            "rendered_commit": str(variables_payload.get("REPRO_GIT_COMMIT", "")),
            "config_sha256": str(variables_payload.get("CONFIG_HASH", "")),
            "kernel_source_sha256": str(
                variables_payload.get("REPRO_KERNEL_SOURCE_HASH", "")
            ),
        }
    source_receipt_path = root / "receipts" / "source-state.json"
    _write_json(
        source_receipt_path,
        {
            "schema_version": "2",
            "commit": commit,
            "dirty": dirty,
            "status_sha256": status_sha256,
            "status": list(status_lines),
            **source_provenance,
        },
    )
    copied_receipts.append(source_receipt_path)

    input_artifacts = tuple(
        _artifact(path, root, "reproducibility-input") for path in sorted(copied_inputs)
    )
    artifact_items: list[PublicationArtifact] = [
        _artifact(path, root, role) for role, path in destinations.items()
    ]
    artifact_items.extend(
        (
            _artifact(citation_path, root, "citation-metadata"),
            _artifact(zenodo_path, root, "zenodo-metadata"),
            _artifact(metadata_path, root, "publication-metadata"),
        )
    )
    artifact_items.extend(
        _artifact(path, root, "validation-receipt") for path in sorted(copied_receipts)
    )
    artifact_items.extend(input_artifacts)

    manifest = PublicationManifest(
        schema_version=MANIFEST_SCHEMA_VERSION,
        metadata=metadata,
        source_commit=commit,
        source_dirty=dirty,
        source_status_sha256=status_sha256,
        source_date_epoch=source_date_epoch,
        producer_versions=_producer_versions(),
        input_hashes=input_artifacts,
        artifacts=tuple(sorted(artifact_items, key=lambda item: item.path)),
        validation_outcomes=tuple(validation_outcomes),
    )
    manifest_path = root / "publication_manifest.json"
    _write_json(manifest_path, _manifest_dict(manifest))

    checksum_paths = [root / item.path for item in manifest.artifacts]
    checksum_paths.append(manifest_path)
    sha256_path = root / "SHA256SUMS"
    sha512_path = root / "SHA512SUMS"
    sha256_path.write_text(
        "".join(
            f"{_hash_file(path, 'sha256')}  {path.relative_to(root).as_posix()}\n"
            for path in sorted(checksum_paths)
        ),
        encoding="utf-8",
    )
    sha512_path.write_text(
        "".join(
            f"{_hash_file(path, 'sha512')}  {path.relative_to(root).as_posix()}\n"
            for path in sorted(checksum_paths)
        ),
        encoding="utf-8",
    )
    logger.info("Prepared publication bundle at %s", root)
    return PublicationBundle(
        root=root,
        manifest_path=manifest_path,
        manifest=manifest,
    )


def _read_manifest(path: Path) -> PublicationManifest:
    raw = json.loads(path.read_text(encoding="utf-8"))
    metadata_raw = raw["metadata"]
    metadata = PublicationMetadata(
        title=metadata_raw["title"],
        version=metadata_raw["version"],
        authors=tuple(metadata_raw["authors"]),
        publication_type=metadata_raw["publication_type"],
        subtitle=metadata_raw.get("subtitle", ""),
        abstract=metadata_raw.get("abstract", ""),
        keywords=tuple(metadata_raw.get("keywords", [])),
        repository_url=metadata_raw.get("repository_url", ""),
        license=metadata_raw.get("license", "MIT"),
        doi=metadata_raw.get("doi"),
    )
    artifacts = tuple(PublicationArtifact(**item) for item in raw["artifacts"])
    inputs = tuple(PublicationArtifact(**item) for item in raw["input_hashes"])
    outcomes = tuple(
        (item["name"], item["passed"], item.get("detail", ""))
        for item in raw["validation_outcomes"]
    )
    return PublicationManifest(
        schema_version=raw["schema_version"],
        metadata=metadata,
        source_commit=raw["source"]["commit"],
        source_dirty=raw["source"]["dirty"],
        source_status_sha256=raw["source"]["status_sha256"],
        source_date_epoch=raw["source_date_epoch"],
        producer_versions=tuple(sorted(raw["producer_versions"].items())),
        input_hashes=inputs,
        artifacts=artifacts,
        validation_outcomes=outcomes,
    )


def _verify_checksum_file(
    root: Path,
    filename: str,
    algorithm: str,
    *,
    expected_paths: set[str] | None = None,
) -> list[str]:
    path = root / filename
    if not path.is_file():
        return [f"Missing checksum file: {filename}"]
    errors: list[str] = []
    seen: set[str] = set()
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return [f"Unable to read checksum file {filename}: {exc}"]
    if not any(line.strip() for line in lines):
        return [f"Checksum file is empty: {filename}"]
    expected_length = hashlib.new(algorithm).digest_size * 2
    root_resolved = root.resolve()
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            expected, relative = line.split("  ", maxsplit=1)
        except ValueError:
            errors.append(f"{filename}:{line_number}: malformed checksum line")
            continue
        relative = relative.strip()
        relative_path = Path(relative)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            errors.append(f"{filename}:{line_number}: non-portable path {relative}")
            continue
        if len(expected) != expected_length or any(
            character not in "0123456789abcdefABCDEF" for character in expected
        ):
            errors.append(f"{filename}:{line_number}: malformed digest for {relative}")
            continue
        if relative in seen:
            errors.append(f"{filename}:{line_number}: duplicate entry for {relative}")
            continue
        seen.add(relative)
        target = root / relative_path
        try:
            target.resolve().relative_to(root_resolved)
        except ValueError:
            errors.append(f"{filename}:{line_number}: path escapes bundle: {relative}")
            continue
        if not target.is_file():
            errors.append(f"{filename}:{line_number}: missing {relative}")
        elif _hash_file(target, algorithm) != expected.lower():
            errors.append(f"{filename}:{line_number}: digest mismatch for {relative}")
    if expected_paths is not None:
        missing = sorted(expected_paths - seen)
        unexpected = sorted(seen - expected_paths)
        errors.extend(f"{filename}: missing expected entry {item}" for item in missing)
        errors.extend(f"{filename}: unexpected entry {item}" for item in unexpected)
    return errors


def verify_publication_bundle(
    bundle: PublicationBundle | str | Path,
) -> PublicationVerification:
    """Verify manifest schema, portable paths, file sizes, and both hash sets."""
    if isinstance(bundle, PublicationBundle):
        root = bundle.root.resolve()
        manifest_path = bundle.manifest_path.resolve()
    else:
        candidate = Path(bundle).resolve()
        root = candidate if candidate.is_dir() else candidate.parent
        manifest_path = (
            candidate / "publication_manifest.json" if candidate.is_dir() else candidate
        )

    errors: list[str] = []
    warnings: list[str] = []
    verified: list[str] = []
    if not manifest_path.is_file():
        return PublicationVerification(
            valid=False,
            errors=("publication_manifest.json is missing",),
            warnings=(),
            verified_artifacts=(),
        )

    try:
        manifest = _read_manifest(manifest_path)
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return PublicationVerification(
            valid=False,
            errors=(f"Manifest parse failed: {exc}",),
            warnings=(),
            verified_artifacts=(),
        )

    if manifest.schema_version != MANIFEST_SCHEMA_VERSION:
        errors.append(
            f"Unsupported manifest schema: {manifest.schema_version}; "
            f"expected {MANIFEST_SCHEMA_VERSION}"
        )
    required_roles = {
        "citation-metadata",
        "content-pdf",
        "distribution-pdf",
        "semantic-html",
        "zenodo-metadata",
    }
    roles = {artifact.role for artifact in manifest.artifacts}
    for role in sorted(required_roles - roles):
        errors.append(f"Missing required artifact role: {role}")

    outcome_names: set[str] = set()
    for name, passed, detail in manifest.validation_outcomes:
        normalized_name = name.strip()
        if not normalized_name:
            errors.append("Validation outcome has an empty name")
            continue
        if normalized_name in outcome_names:
            errors.append(f"Duplicate validation outcome: {normalized_name}")
            continue
        outcome_names.add(normalized_name)
        if not isinstance(passed, bool):
            errors.append(
                f"Validation outcome {normalized_name} has a non-boolean status"
            )
        elif not passed:
            errors.append(
                f"Validation outcome failed: {normalized_name}"
                + (f" ({detail})" if detail else "")
            )

    for artifact in manifest.artifacts:
        relative = Path(artifact.path)
        if relative.is_absolute() or ".." in relative.parts:
            errors.append(f"Non-portable artifact path: {artifact.path}")
            continue
        path = root / relative
        if not path.is_file():
            errors.append(f"Missing artifact: {artifact.path}")
            continue
        if path.stat().st_size != artifact.size_bytes:
            errors.append(f"Size mismatch: {artifact.path}")
            continue
        if _hash_file(path, "sha256") != artifact.sha256:
            errors.append(f"SHA-256 mismatch: {artifact.path}")
            continue
        if _hash_file(path, "sha512") != artifact.sha512:
            errors.append(f"SHA-512 mismatch: {artifact.path}")
            continue
        verified.append(artifact.path)

    checksum_paths = {artifact.path for artifact in manifest.artifacts}
    checksum_paths.add("publication_manifest.json")
    errors.extend(
        _verify_checksum_file(
            root,
            "SHA256SUMS",
            "sha256",
            expected_paths=checksum_paths,
        )
    )
    errors.extend(
        _verify_checksum_file(
            root,
            "SHA512SUMS",
            "sha512",
            expected_paths=checksum_paths,
        )
    )

    content = next(
        (artifact for artifact in manifest.artifacts if artifact.role == "content-pdf"),
        None,
    )
    distribution = next(
        (
            artifact
            for artifact in manifest.artifacts
            if artifact.role == "distribution-pdf"
        ),
        None,
    )
    pdftotext = shutil.which("pdftotext")
    if content and distribution and pdftotext:
        result = subprocess.run(
            [pdftotext, str(root / distribution.path), "-"],
            capture_output=True,
            text=True,
            check=False,
        )
        compact_text = "".join(result.stdout.split())
        if result.returncode != 0:
            errors.append("Distribution PDF text extraction failed")
        elif content.sha256 not in compact_text:
            errors.append("Distribution PDF bookends do not expose the content SHA-256")
    elif content and distribution:
        warnings.append(
            "pdftotext is unavailable; visible content hash was not checked"
        )

    return PublicationVerification(
        valid=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
        verified_artifacts=tuple(sorted(verified)),
    )


def plan_publication(
    bundle: PublicationBundle | str | Path,
    *,
    target: str,
    dry_run: bool = True,
    receipt_path: str | Path | None = None,
) -> PublicationPlan:
    """Write a remote publication plan; execution is intentionally forbidden."""
    if target not in REMOTE_PUBLICATION_TARGETS:
        message = f"Unsupported remote publication target: {target}"
        raise ValueError(message)
    if not dry_run:
        message = "Remote publication plans require dry_run=True"
        raise ValueError(message)

    verification = verify_publication_bundle(bundle)
    if not verification.valid:
        message = f"Publication bundle verification failed: {verification.errors}"
        raise ValueError(message)

    if isinstance(bundle, PublicationBundle):
        root = bundle.root.resolve()
        manifest_path = bundle.manifest_path.resolve()
    else:
        candidate = Path(bundle).resolve()
        root = candidate if candidate.is_dir() else candidate.parent
        manifest_path = (
            candidate / "publication_manifest.json" if candidate.is_dir() else candidate
        )
    manifest = _read_manifest(manifest_path)
    destination = (
        Path(receipt_path).resolve()
        if receipt_path is not None
        else root / "receipts" / f"{target}-publication-plan.json"
    )
    body: dict[str, Any] = {
        "schema_version": "1",
        "target": target,
        "dry_run": True,
        "executed": False,
        "release": {
            "title": manifest.metadata.title,
            "version": manifest.metadata.version,
            "doi": manifest.metadata.doi,
        },
        "manifest_sha256": _hash_file(manifest_path, "sha256"),
        "artifacts": [
            {
                "path": artifact.path,
                "role": artifact.role,
                "sha256": artifact.sha256,
                "sha512": artifact.sha512,
            }
            for artifact in manifest.artifacts
        ],
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    receipt_sha256 = hashlib.sha256(canonical).hexdigest()
    body["receipt_sha256"] = receipt_sha256
    _write_json(destination, body)
    logger.info("Wrote %s dry-run publication plan to %s", target, destination)
    return PublicationPlan(
        target=target,
        dry_run=True,
        executed=False,
        receipt_path=destination,
        receipt_sha256=receipt_sha256,
        artifact_count=len(manifest.artifacts),
    )


__all__ = [
    "MANIFEST_SCHEMA_VERSION",
    "PublicationArtifact",
    "PublicationBundle",
    "PublicationManifest",
    "PublicationMetadata",
    "PublicationPlan",
    "PublicationVerification",
    "plan_publication",
    "prepare_publication_bundle",
    "verify_publication_bundle",
]
