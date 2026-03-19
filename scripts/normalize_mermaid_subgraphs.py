#!/usr/bin/env python3
"""Rewrite `subgraph \"Label\"` to `subgraph sg_<hash> [Label]` inside docs/ Mermaid blocks.

Quoted subgraph titles are fragile; explicit ids with bracket labels match project conventions.
Idempotent. Run from repo root:

    uv run python scripts/normalize_mermaid_subgraphs.py
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SUBGRAPH_QUOTED = re.compile(r'subgraph\s+"([^"]+)"')
BLOCK = re.compile(r"```mermaid\s*\r?\n(.*?)```", re.DOTALL)


def fix_inner(inner: str) -> str:
    def repl(m: re.Match[str]) -> str:
        label = m.group(1)
        sid = "sg_" + hashlib.sha256(label.encode("utf-8")).hexdigest()[:10]
        return f"subgraph {sid} [{label}]"

    return SUBGRAPH_QUOTED.sub(repl, inner)


def process_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "```mermaid" not in text or 'subgraph "' not in text:
        return False

    def block_repl(m: re.Match[str]) -> str:
        return "```mermaid\n" + fix_inner(m.group(1)) + "```"

    new_text = BLOCK.sub(block_repl, text)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


def main() -> int:
    if not DOCS.is_dir():
        print("docs/ not found", file=sys.stderr)
        return 1
    n = 0
    for path in sorted(DOCS.rglob("*.md")):
        if process_file(path):
            print(path.relative_to(ROOT))
            n += 1
    print(f"Updated {n} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
