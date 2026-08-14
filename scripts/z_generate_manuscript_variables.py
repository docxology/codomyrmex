#!/usr/bin/env python3
"""Manuscript variable injection orchestrator for Codomyrmex.

Thin orchestrator: all computation logic lives in ``codomyrmex.manuscript.variables``.
This script drives the pipeline:
  1. Resolve project root and config paths.
  2. Delegate variable computation to ``codomyrmex.manuscript.variables``.
  3. Write output/data/manuscript_variables.json.
  4. Inject tokens into manuscript section Markdown → output/manuscript/.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path


def _find_project_root() -> Path:
    """Walk up from this script's location to the project root (contains pyproject.toml)."""
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        if (candidate / "pyproject.toml").exists():
            return candidate
    # Fallback: parent of scripts/
    return here.parent


def _ensure_src_on_path(project_root: Path) -> None:
    src = str(project_root / "src")
    if src not in sys.path:
        sys.path.insert(0, src)


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    )
    temporary_path = Path(temporary.name)
    try:
        with temporary:
            json.dump(data, temporary, indent=2, sort_keys=True)
            temporary.write("\n")
            temporary.flush()
            os.fsync(temporary.fileno())
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)


def _variable_registry(
    variables: dict[str, str],
    contract: dict[str, object],
) -> dict[str, object]:
    """Emit the typed render-boundary contract for every generated variable."""
    references_value = contract.get("references", {})
    references: dict[str, object]
    if isinstance(references_value, dict):
        references = {str(key): value for key, value in references_value.items()}
    else:
        references = {}

    def source_type(name: str, value: str) -> str:
        if name.endswith(("_HASH", "_SHA256", "_COMMIT", "_REVISION")):
            return "identifier"
        if value.lower() in {"true", "false"}:
            return "boolean"
        try:
            float(value)
        except ValueError:
            return "markdown" if "\n" in value else "string"
        return "number"

    def unit(name: str, value: str) -> str:
        if name.endswith(("_HASH", "_SHA256", "_COMMIT", "_REVISION")):
            return "identifier"
        if name.endswith(("_PCT", "_PERCENT")):
            return "percent"
        if name.endswith("_COUNT") or name.startswith(("ARTIFACT_", "RESULT_TEST")):
            return "count"
        if source_type(name, value) == "number":
            return "configured-or-derived scalar"
        return "text"

    entries = []
    for name, value in sorted(variables.items()):
        consumers = references.get(name, [])
        if not isinstance(consumers, list):
            consumers = []
        entries.append(
            {
                "name": name,
                "rendered_value": value,
                "source_type": source_type(name, value),
                "render_type": "markdown-string",
                "unit": unit(name, value),
                "precision": "source-defined"
                if source_type(name, value) == "number"
                else None,
                "missing_policy": "fail-closed",
                "producer": "codomyrmex.manuscript.variables.compute_variables",
                "source": (
                    "docs/manuscript/config.yaml"
                    if name.startswith("CONFIG_")
                    else "runtime/source-derived"
                ),
                "consumers": sorted(str(path) for path in consumers),
            }
        )
    return {
        "schema_version": "1.0",
        "status": contract.get("status", "invalid"),
        "variable_sha256": contract.get("variable_sha256", ""),
        "config_sha256": contract.get("config_sha256", ""),
        "provenance": contract.get("provenance", {}),
        "entries": entries,
    }


def _clean_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for pattern in ("*.md", "*.bib", "config.yaml"):
        for path in output_dir.glob(pattern):
            if path.is_file():
                path.unlink()


# Make direct script execution independent of whether the editable package has
# already been installed into the invoking interpreter.
_ensure_src_on_path(_find_project_root())


from codomyrmex.manuscript.variables import (
    compute_variables,
    inject_manuscript_variables,
    validate_variable_contract,
)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute source-bound manuscript variables and hydrate the manuscript tree."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Override the repository root (default: discover from this script).",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Override the manuscript config path (default: <project-root>/docs/manuscript/config.yaml).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    project_root = (
        args.project_root.expanduser().resolve()
        if args.project_root is not None
        else _find_project_root()
    )

    config_path = (
        args.config.expanduser().resolve()
        if args.config is not None
        else project_root / "docs" / "manuscript" / "config.yaml"
    )
    if not config_path.exists():
        print(f"ERROR: manuscript config not found: {config_path}", file=sys.stderr)
        return 1

    variables: dict[str, str] = compute_variables(
        config_path=config_path,
        project_root=project_root,
    )

    contract = validate_variable_contract(
        manuscript_dir=project_root / "docs" / "manuscript",
        variables=variables,
        figure_source_dir=project_root
        / "src"
        / "codomyrmex"
        / "manuscript"
        / "figures",
    )
    if contract["errors"]:
        print(
            "ERROR: manuscript variable contract failed:\n"
            + "\n".join(f"- {error}" for error in contract["errors"]),
            file=sys.stderr,
        )
        return 1

    manuscript_dir = project_root / "docs" / "manuscript"
    # Write JSON snapshot.
    json_out = project_root / "output" / "data" / "manuscript_variables.json"
    _write_json(json_out, variables)
    print(f"[z_generate] wrote {json_out.relative_to(project_root)}")
    contract_out = (
        project_root / "output" / "data" / "manuscript_variable_manifest.json"
    )
    _write_json(contract_out, contract)
    print(f"[z_generate] wrote {contract_out.relative_to(project_root)}")
    registry_out = (
        project_root / "output" / "data" / "manuscript_variable_registry.json"
    )
    _write_json(registry_out, _variable_registry(variables, contract))
    print(f"[z_generate] wrote {registry_out.relative_to(project_root)}")

    # Inject into manuscript markdown files.
    output_manuscript = project_root / "output" / "manuscript"
    _clean_output_dir(output_manuscript)

    written = inject_manuscript_variables(
        manuscript_dir,
        output_manuscript,
        variables,
        project_root=project_root,
    )
    for path in written:
        print(f"[z_generate] injected → {path.relative_to(project_root)}")

    # Copy config.yaml and *.bib so the rendering infrastructure can find them.
    # resolve_manuscript_dir() in _manuscript_source.py only copies these when
    # project_root/manuscript/ exists, but codomyrmex uses docs/manuscript/ —
    # so we handle the copy here.
    import shutil

    for copy_src in [config_path, *sorted(manuscript_dir.glob("*.bib"))]:
        copy_dst = output_manuscript / copy_src.name
        shutil.copy2(copy_src, copy_dst)
        print(
            f"[z_generate] copied {copy_src.name} → {copy_dst.relative_to(project_root)}"
        )

    print(f"[z_generate] done — {len(variables)} variables computed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
