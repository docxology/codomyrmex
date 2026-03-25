#!/usr/bin/env python3
"""Report mcp_tools.py files without a sibling MCP_TOOL_SPECIFICATION.md.

Convention: each `mcp_tools.py` under `src/codomyrmex/` (excluding tests) should
have `MCP_TOOL_SPECIFICATION.md` in the same directory for RASP/MCP parity.

Run from repo root:
    uv run python scripts/mcp_spec_gap.py
"""

from __future__ import annotations

import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def main() -> int:
    root = repo_root()
    base = root / "src" / "codomyrmex"
    missing: list[Path] = []
    for p in sorted(base.rglob("mcp_tools.py")):
        s = str(p).replace("\\", "/")
        if "/tests/" in s:
            continue
        d = p.parent
        if not (d / "MCP_TOOL_SPECIFICATION.md").is_file():
            missing.append(p.relative_to(root))

    print(f"mcp_tools.py without sibling MCP_TOOL_SPECIFICATION.md: {len(missing)}")
    for rel in missing:
        print(f"  {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
