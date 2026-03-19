#!/usr/bin/env python3
"""Remove Mermaid `style <node> …` lines from fenced ```mermaid blocks under docs/.

Hard-coded colors break light/dark theme rendering. Run from repo root:

    uv run python scripts/strip_mermaid_style_lines.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
STYLE_LINE = re.compile(r"^\s*style\s+\S+.*(?:\r?\n|$)", re.MULTILINE)
BLOCK = re.compile(r"```mermaid\s*\r?\n(.*?)```", re.DOTALL)


def strip_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "```mermaid" not in text:
        return False

    def repl(m: re.Match[str]) -> str:
        inner = m.group(1)
        cleaned = STYLE_LINE.sub("", inner)
        return "```mermaid\n" + cleaned + "```"

    new_text = BLOCK.sub(repl, text)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


def main() -> int:
    if not DOCS.is_dir():
        print("docs/ not found", file=sys.stderr)
        return 1
    changed = 0
    for path in sorted(DOCS.rglob("*.md")):
        if strip_file(path):
            changed += 1
            print(path.relative_to(ROOT))
    print(f"Updated {changed} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
