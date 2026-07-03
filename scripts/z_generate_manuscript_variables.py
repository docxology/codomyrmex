#!/usr/bin/env python3
"""Manuscript variable injection orchestrator for Codomyrmex.

Thin orchestrator: all computation logic lives in src/manuscript_variables.py.
This script drives the pipeline:
  1. Resolve project root and config paths.
  2. Delegate variable computation to manuscript_variables.py.
  3. Write output/data/manuscript_variables.json.
  4. Inject tokens into manuscript section Markdown → output/manuscript/.
"""

from __future__ import annotations

import json
import os
import sys
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
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _clean_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for pattern in ("*.md", "*.bib", "config.yaml"):
        for path in output_dir.glob(pattern):
            if path.is_file():
                path.unlink()


def _manuscript_sources(manuscript_dir: Path) -> list[Path]:
    sources = sorted(manuscript_dir.glob("[0-9]*.md"))
    preamble = manuscript_dir / "preamble.md"
    if preamble.exists():
        sources.append(preamble)
    return sources


def _inject_tokens(
    manuscript_dir: Path, output_dir: Path, variables: dict[str, str]
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for src_file in _manuscript_sources(manuscript_dir):
        content = src_file.read_text(encoding="utf-8")
        for key, value in variables.items():
            content = content.replace("{{" + key + "}}", str(value))
        dest = output_dir / src_file.name
        dest.write_text(content, encoding="utf-8")
        written.append(dest)
    return written


def main() -> int:
    project_root = _find_project_root()
    _ensure_src_on_path(project_root)

    # Delegate all computation to the library module.
    try:
        import manuscript_variables as mv  # type: ignore[import]
    except ImportError as exc:
        print(f"ERROR: cannot import manuscript_variables: {exc}", file=sys.stderr)
        print("  Expected at: src/manuscript_variables.py", file=sys.stderr)
        return 1

    config_path = project_root / "docs" / "manuscript" / "config.yaml"
    if not config_path.exists():
        print(f"ERROR: manuscript config not found: {config_path}", file=sys.stderr)
        return 1

    variables: dict[str, str] = mv.compute_variables(
        config_path=config_path,
        project_root=project_root,
    )

    # Write JSON snapshot.
    json_out = project_root / "output" / "data" / "manuscript_variables.json"
    _write_json(json_out, variables)
    print(f"[z_generate] wrote {json_out.relative_to(project_root)}")

    # Inject into manuscript markdown files.
    manuscript_dir = project_root / "docs" / "manuscript"
    output_manuscript = project_root / "output" / "manuscript"
    _clean_output_dir(output_manuscript)

    # Try infrastructure rendering injection first.
    injected_via_infra = False
    try:
        import manuscript_variables as mv2  # already imported

        if hasattr(mv2, "inject_via_infrastructure"):
            mv2.inject_via_infrastructure(
                manuscript_dir=manuscript_dir,
                output_dir=output_manuscript,
                variables=variables,
            )
            injected_via_infra = True
            print("[z_generate] injection delegated to infrastructure renderer")
    except Exception:
        pass

    if not injected_via_infra:
        written = _inject_tokens(manuscript_dir, output_manuscript, variables)
        for p in written:
            print(f"[z_generate] injected → {p.relative_to(project_root)}")

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
