#!/usr/bin/env python3
"""Reject case/Unicode-equivalent Git paths on case-insensitive filesystems.

Read the Git index, including staged additions and removals. Foreign submodule
contents are excluded. This command does not rename or modify any files.
"""

from __future__ import annotations

import argparse
import subprocess
import unicodedata
from pathlib import Path


def find_collisions(paths: list[str]) -> list[tuple[str, ...]]:
    """Check full paths and directory components, preserving original spellings."""
    spellings: dict[str, set[str]] = {}
    for path in paths:
        parts = path.split("/")
        for count in range(1, len(parts) + 1):
            prefix = "/".join(parts[:count])
            key = unicodedata.normalize("NFC", prefix).casefold()
            spellings.setdefault(key, set()).add(prefix)
    return sorted(
        tuple(sorted(names)) for names in spellings.values() if len(names) > 1
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    root = args.root.resolve()
    repository = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if repository.returncode or Path(repository.stdout.strip()).resolve() != root:
        parser.exit(2, "The requested root must be the Git repository root.\n")
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--cached", "-z"],
        capture_output=True,
        check=False,
    )
    if result.returncode:
        parser.exit(2, "Cannot read the Git index for the requested root.\n")
    paths = result.stdout.decode("utf-8", errors="surrogateescape").split("\0")[:-1]
    collisions = find_collisions(paths)
    for names in collisions:
        print("Path collision: " + " / ".join(repr(name) for name in names))
    print(f"Path portability: {len(paths)} tracked paths; {len(collisions)} collisions")
    return int(bool(collisions))


if __name__ == "__main__":
    raise SystemExit(main())
