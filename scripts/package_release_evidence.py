#!/usr/bin/env python3
"""Build a deterministic candidate evidence archive.

The archive is a transport bundle, not an immutable release.  The final
``output/release_manifest.json`` remains the sidecar source of truth because a
tarball cannot contain a hash of itself without becoming self-referential.
"""

from __future__ import annotations

import argparse
import os
import tarfile
from pathlib import Path


def _files(root: Path) -> list[Path]:
    exact = [
        "output/paper.pdf",
        "output/paper.html",
        "output/release_manifest.json",
        "output/data/manuscript_variables.json",
        "output/data/colony_kernel_coverage.json",
        "output/data/colony_kernel_test_report.xml",
        "output/data/colony_kernel_test_status.json",
        "docs/manuscript/RELEASE_PROVENANCE.md",
        "evaluations/colony_kernel/benchmark_manifest.json",
        "evaluations/colony_kernel/RESEARCH_PROTOCOL.md",
        "evaluations/colony_kernel/truth_tables.json",
        "evaluations/colony_kernel/truth_tables.md",
        "review_artifacts/Codomyrmex_Reproduction_Evidence_Follow_Up_2026-07-13.md",
        "review_artifacts/Codomyrmex_Action_Register_2026-07-13_Follow_Up.xlsx",
        "review_artifacts/Codomyrmex_RedTeam_FirstPrinciples_Science_Follow_Up_2026-07-14.md",
    ]
    paths = [root / relative for relative in exact]
    paths.extend(sorted((root / "output" / "figures").glob("*")))
    paths.extend(sorted((root / "output" / "manuscript").glob("*")))
    missing = [str(path.relative_to(root)) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("required evidence is missing: " + ", ".join(missing))
    return sorted(paths)


def package(root: Path, output: Path) -> Path:
    """Write a reproducible gzip tar archive and atomically publish it."""

    paths = _files(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.{os.getpid()}.tmp")
    try:
        with tarfile.open(temporary, mode="w:gz", compresslevel=9) as archive:
            for path in paths:
                relative = path.relative_to(root).as_posix()
                info = archive.gettarinfo(str(path), arcname=relative)
                info.uid = 0
                info.gid = 0
                info.uname = ""
                info.gname = ""
                info.mtime = 0
                with path.open("rb") as handle:
                    archive.addfile(info, handle)
        temporary.replace(output)
    finally:
        if temporary.exists():
            temporary.unlink()
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("output/release_package.tar.gz"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.output if args.output.is_absolute() else root / args.output
    print(package(root, output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
