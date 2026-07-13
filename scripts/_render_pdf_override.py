#!/usr/bin/env python3
"""Render Codomyrmex with its project compiler and normalize pipeline artifacts."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _project_python(project_root: Path) -> Path:
    candidates = (
        project_root / ".venv" / "bin" / "python",
        project_root / ".venv" / "Scripts" / "python.exe",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "Project interpreter not found; create .venv before running the render pipeline"
    )


def _copy_required_artifact(source: Path, destination: Path) -> None:
    if not source.is_file() or source.stat().st_size == 0:
        raise FileNotFoundError(f"Required render artifact missing or empty: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def main() -> int:
    project_root = _project_root()
    compiler = project_root / "scripts" / "compile_manuscript.py"
    try:
        python = _project_python(project_root)
        completed = subprocess.run(  # nosec B603 - fixed project-local command
            [str(python), str(compiler), "--pdf", "--bookends", "--skip-generate"],
            cwd=project_root,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"Render override failed: {exc}", file=sys.stderr)
        return 1
    if completed.returncode != 0:
        return completed.returncode

    output_dir = project_root / "output"
    try:
        _copy_required_artifact(
            output_dir / "paper.pdf",
            output_dir / "pdf" / f"{project_root.name}_combined.pdf",
        )
        _copy_required_artifact(
            output_dir / "paper.html",
            output_dir / "web" / "index.html",
        )
    except OSError as exc:
        print(f"Render artifact normalization failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
