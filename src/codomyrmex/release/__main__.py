"""Command-line entry point for release and publication operations."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tomllib
from pathlib import Path
from typing import Any

import yaml

from codomyrmex.release.publication import (
    PublicationMetadata,
    plan_publication,
    prepare_publication_bundle,
    verify_publication_bundle,
)


def _project_metadata(project_root: Path) -> PublicationMetadata:
    config_path = project_root / "docs" / "manuscript" / "config.yaml"
    pyproject_path = project_root / "pyproject.toml"
    config: dict[str, Any] = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    with pyproject_path.open("rb") as handle:
        pyproject = tomllib.load(handle)
    paper = config["paper"]
    publication = config["publication"]
    package = pyproject["project"]
    doi = str(publication.get("doi", "")).strip() or None
    repository = str(publication.get("github_repository", "")).strip()
    if repository and not repository.startswith(("http://", "https://")):
        repository = f"https://github.com/{repository}"
    return PublicationMetadata(
        title=str(paper["title"]),
        subtitle=str(paper.get("subtitle", "")),
        version=str(package["version"]),
        authors=tuple(str(author["name"]) for author in config["authors"]),
        publication_type=str(publication.get("type", "technical-report")),
        keywords=tuple(str(keyword) for keyword in config.get("keywords", [])),
        repository_url=repository,
        license=str(config.get("metadata", {}).get("license", "MIT")),
        doi=doi,
    )


def _default_reproducibility_inputs(project_root: Path) -> list[Path]:
    candidates = [
        project_root / "pyproject.toml",
        project_root / "uv.lock",
        project_root / "docs" / "manuscript" / "config.yaml",
        project_root / "docs" / "manuscript" / "references.bib",
        project_root / "docs" / "manuscript" / "claim_ledger.yaml",
        project_root / "output" / "data" / "manuscript_variables.json",
    ]
    return [path for path in candidates if path.is_file()]


def _prepare(args: argparse.Namespace) -> int:
    project_root = args.project_root.resolve()
    metadata = _project_metadata(project_root)
    output_dir = (
        args.output_dir.resolve()
        if args.output_dir is not None
        else (project_root / "output" / "release" / f"codomyrmex-{metadata.version}")
    )
    bundle = prepare_publication_bundle(
        metadata=metadata,
        content_pdf=args.content_pdf or project_root / "output" / "paper-content.pdf",
        distribution_pdf=args.distribution_pdf or project_root / "output" / "paper.pdf",
        semantic_html=args.semantic_html or project_root / "output" / "paper.html",
        output_dir=output_dir,
        project_root=project_root,
        reproducibility_inputs=[
            *_default_reproducibility_inputs(project_root),
            *args.reproducibility_input,
        ],
        validation_receipts=args.validation_receipt,
        source_date_epoch=args.source_date_epoch,
    )
    verification = verify_publication_bundle(bundle)
    print(
        json.dumps(
            {
                "bundle": str(bundle.root),
                "manifest": str(bundle.manifest_path),
                "valid": verification.valid,
                "errors": verification.errors,
                "warnings": verification.warnings,
            },
            indent=2,
        )
    )
    return 0 if verification.valid else 1


def _verify(args: argparse.Namespace) -> int:
    result = verify_publication_bundle(args.bundle)
    print(
        json.dumps(
            {
                "valid": result.valid,
                "errors": result.errors,
                "warnings": result.warnings,
                "verified_artifacts": result.verified_artifacts,
            },
            indent=2,
        )
    )
    return 0 if result.valid else 1


def _plan(args: argparse.Namespace) -> int:
    plan = plan_publication(
        args.bundle,
        target=args.target,
        dry_run=True,
        receipt_path=args.receipt,
    )
    print(
        json.dumps(
            {
                "target": plan.target,
                "dry_run": plan.dry_run,
                "executed": plan.executed,
                "receipt": str(plan.receipt_path),
                "receipt_sha256": plan.receipt_sha256,
                "artifact_count": plan.artifact_count,
            },
            indent=2,
        )
    )
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m codomyrmex.release")
    commands = parser.add_subparsers(dest="command", required=True)
    publication = commands.add_parser("publication")
    actions = publication.add_subparsers(dest="publication_command", required=True)

    prepare = actions.add_parser("prepare")
    prepare.add_argument("--project-root", type=Path, default=Path.cwd())
    prepare.add_argument("--output-dir", type=Path)
    prepare.add_argument("--content-pdf", type=Path)
    prepare.add_argument("--distribution-pdf", type=Path)
    prepare.add_argument("--semantic-html", type=Path)
    prepare.add_argument(
        "--reproducibility-input",
        action="append",
        type=Path,
        default=[],
    )
    prepare.add_argument(
        "--validation-receipt",
        action="append",
        type=Path,
        default=[],
    )
    prepare.add_argument(
        "--source-date-epoch",
        type=int,
        default=int(os.environ.get("SOURCE_DATE_EPOCH", "0")),
    )
    prepare.set_defaults(handler=_prepare)

    verify = actions.add_parser("verify")
    verify.add_argument("bundle", type=Path)
    verify.set_defaults(handler=_verify)

    plan = actions.add_parser("plan")
    plan.add_argument("bundle", type=Path)
    plan.add_argument(
        "--target",
        required=True,
        choices=("github", "zenodo-sandbox"),
    )
    plan.add_argument("--receipt", type=Path)
    plan.set_defaults(handler=_plan)
    return parser


def main() -> int:
    """Run the release CLI."""
    args = _parser().parse_args()
    return int(args.handler(args))


if __name__ == "__main__":
    sys.exit(main())
