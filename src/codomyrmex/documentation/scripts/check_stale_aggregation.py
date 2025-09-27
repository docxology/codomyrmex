#!/usr/bin/env python3
"""Check for stale aggregation: ensure aggregated docs mirror module docs.

Exit code 1 if any module docs changed but aggregation was not updated.
"""
import filecmp
import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
source_root = project_root / "code"
dest_root = project_root / "code" / "documentation" / "docs" / "modules"


def main():
    """Main.

        Returns:        The result of the operation.
        """
    problems = []
    if not dest_root.exists():
        print(f"Destination aggregated docs not found: {dest_root}")
        sys.exit(1)

    for module_dir in sorted(p for p in source_root.iterdir() if p.is_dir()):
        name = module_dir.name
        src_docs = list(module_dir.rglob("*.md"))
        if not src_docs:
            continue
        dest_module = dest_root / name
        if not dest_module.exists():
            problems.append(f"Module {name}: aggregated folder missing")
            continue
        # For each source md file, find counterpart in dest_module
        for src in src_docs:
            rel = src.relative_to(module_dir)
            dest_file = dest_module / rel
            if not dest_file.exists():
                problems.append(f"Module {name}: {rel} not aggregated")
            else:
                # shallow compare
                if not filecmp.cmp(src, dest_file, shallow=False):
                    problems.append(
                        f"Module {name}: {rel} differs from aggregated copy"
                    )

    if problems:
        print("Stale aggregation detected:\n" + "\n".join(problems))
        sys.exit(1)
    print("Aggregation is up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
