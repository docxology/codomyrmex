#!/usr/bin/env python3
"""Print repository metrics documented in docs/reference/inventory.md.

Run from repo root: uv run python scripts/doc_inventory.py

Optional: pass --pytest to also run pytest --collect-only (slower, ~30s).
Optional: pass --manifest for runtime merged MCP tool count via get_skill_manifest() (imports codomyrmex).
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def count_top_level_modules(root: Path) -> int:
    pkg = root / "src" / "codomyrmex"
    skip = {"tests", "__pycache__"}
    n = 0
    for name in os.listdir(pkg):
        if name in skip:
            continue
        d = pkg / name
        if d.is_dir() and (d / "__init__.py").is_file():
            n += 1
    return n


def iter_py_files_under_codomyrmex(root: Path) -> list[Path]:
    base = root / "src" / "codomyrmex"
    out: list[Path] = []
    for p in base.rglob("*.py"):
        if "/tests/" in str(p).replace("\\", "/"):
            continue
        out.append(p)
    return out


def count_mcp_tool_decorators(root: Path) -> int:
    """Match `rg '^@mcp_tool'`: physical lines starting with @mcp_tool."""
    n = 0
    for p in iter_py_files_under_codomyrmex(root):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            if line.startswith("@mcp_tool"):
                n += 1
    return n


def count_mcp_tools_py(root: Path) -> int:
    base = root / "src" / "codomyrmex"
    return sum(
        1
        for p in base.rglob("mcp_tools.py")
        if "/tests/" not in str(p).replace("\\", "/")
    )


def pytest_collect_count(root: Path) -> int | None:
    try:
        # --no-cov keeps the count independent of optional coverage instrumentation.
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "--collect-only",
                "-q",
                "--no-cov",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    out = (proc.stdout or "") + (proc.stderr or "")
    m = re.search(r"(\d+)\s+tests?\s+collected", out)
    if m:
        return int(m.group(1))
    return None


def manifest_tool_count() -> int | None:
    """Runtime merged static+dynamic MCP tool count (requires package import)."""
    try:
        from codomyrmex.agents.pai import get_skill_manifest
    except ImportError:
        return None
    try:
        m = get_skill_manifest()
        tools = m.get("tools")
        if isinstance(tools, list):
            return len(tools)
    except Exception:
        return None
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--pytest",
        action="store_true",
        help="Run pytest --collect-only (slow)",
    )
    ap.add_argument(
        "--manifest",
        action="store_true",
        help="Print get_skill_manifest() tool count (imports codomyrmex)",
    )
    args = ap.parse_args()
    root = repo_root()

    mods = count_top_level_modules(root)
    mcp_files = count_mcp_tools_py(root)
    decorators = count_mcp_tool_decorators(root)

    print("Codomyrmex inventory (see docs/reference/inventory.md)")
    print(f"  top_level_modules:        {mods}")
    print(f"  mcp_tools.py (non-test):  {mcp_files}")
    print(f"  @mcp_tool (production):   {decorators}")
    if args.manifest:
        n = manifest_tool_count()
        if n is not None:
            print(f"  manifest tools (runtime): {n}")
        else:
            print("  manifest tools (runtime): (import or get_skill_manifest failed)")
    if args.pytest:
        n = pytest_collect_count(root)
        if n is not None:
            print(f"  pytest collected:         {n}")
        else:
            print("  pytest collected:         (failed to run or parse)")
    else:
        print("  pytest collected:         (omit --pytest for speed; see inventory.md)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
