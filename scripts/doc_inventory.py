#!/usr/bin/env python3
"""Print repository metrics documented in docs/reference/inventory.md.

Run from repo root: uv run python scripts/doc_inventory.py

Always prints a ``.github/workflows`` ``*.yml`` file count (for inventory and
``.github/README.md`` workflow tables).

Optional: pass --pytest to also run pytest --collect-only (slower, ~30s).
Optional: pass --manifest for runtime merged MCP tool count via get_skill_manifest() (imports codomyrmex).
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import ModuleType


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_module_catalog(root: Path) -> ModuleType:
    """Load the pure filesystem module catalog without importing codomyrmex."""
    catalog_path = (
        root / "src" / "codomyrmex" / "system_discovery" / "module_catalog.py"
    )
    spec = importlib.util.spec_from_file_location(
        "_codomyrmex_module_catalog",
        catalog_path,
    )
    if spec is None or spec.loader is None:
        msg = f"Could not load module catalog from {catalog_path}"
        raise RuntimeError(msg)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def count_top_level_modules(root: Path) -> int:
    catalog_module = load_module_catalog(root)
    catalog = catalog_module.build_module_catalog(root)
    return int(catalog.runtime_module_count)


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


def count_github_workflow_yml(root: Path) -> int:
    """Count ``.github/workflows/*.yml`` (matches inventory and .github/README)."""
    wf = root / ".github" / "workflows"
    if not wf.is_dir():
        return 0
    return sum(1 for p in wf.glob("*.yml") if p.is_file())


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
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            m = get_skill_manifest()
        tools = m.get("tools")
        if isinstance(tools, list):
            return len(tools)
    except Exception:
        return None
    return None


def collect_inventory(root: Path, *, include_pytest: bool = False, include_manifest: bool = False) -> dict[str, int | None]:
    """Return the measured inventory as a JSON-serializable mapping."""

    metrics: dict[str, int | None] = {
        "top_level_modules": count_top_level_modules(root),
        "mcp_tools_py": count_mcp_tools_py(root),
        "production_mcp_tool_decorators": count_mcp_tool_decorators(root),
        "github_workflows": count_github_workflow_yml(root),
        "markdown_docs_under_docs": sum(
            1 for path in (root / "docs").rglob("*.md") if path.is_file()
        ),
    }
    metrics["runtime_mcp_tools"] = manifest_tool_count() if include_manifest else None
    metrics["pytest_collected"] = pytest_collect_count(root) if include_pytest else None
    return metrics


def reference_consistency(root: Path, metrics: dict[str, int | None]) -> list[str]:
    """Check canonical inventory values against freshly measured values."""

    path = root / "docs" / "reference" / "inventory.md"
    if not path.is_file():
        return [f"missing canonical inventory: {path}"]
    text = path.read_text(encoding="utf-8")
    expected = {
        "Top-level modules": metrics["top_level_modules"],
        "`mcp_tools.py` files (non-test)": metrics["mcp_tools_py"],
        "Runtime MCP tools": metrics["runtime_mcp_tools"],
        "Production `@mcp_tool` decorators": metrics["production_mcp_tool_decorators"],
        "Pytest tests collected": metrics["pytest_collected"],
        "GitHub Actions workflow files (`.github/workflows/*.yml`)": metrics["github_workflows"],
        "Markdown files under `docs/`": metrics["markdown_docs_under_docs"],
    }
    errors: list[str] = []
    for label, value in expected.items():
        if value is None:
            continue
        pattern = re.compile(rf"\|\s*{re.escape(label)}\s*\|\s*{value:,}(?:\s|\|)")
        if not pattern.search(text):
            errors.append(f"{label}: expected {value:,}")
    return errors


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
    ap.add_argument(
        "--json",
        action="store_true",
        help="Emit the measured inventory as JSON",
    )
    ap.add_argument(
        "--check-reference",
        action="store_true",
        help="Fail if docs/reference/inventory.md disagrees with measured values",
    )
    args = ap.parse_args()
    root = repo_root()

    metrics = collect_inventory(
        root,
        include_pytest=args.pytest,
        include_manifest=args.manifest,
    )
    reference_errors = reference_consistency(root, metrics) if args.check_reference else []

    if args.json:
        payload = {
            "schema_version": "doc-inventory-v1",
            "metrics": metrics,
            "reference_check": {
                "enabled": args.check_reference,
                "passed": not reference_errors,
                "errors": reference_errors,
            },
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1 if reference_errors else 0

    mods = metrics["top_level_modules"]
    mcp_files = metrics["mcp_tools_py"]
    decorators = metrics["production_mcp_tool_decorators"]

    print("Codomyrmex inventory (see docs/reference/inventory.md)")
    print(f"  top_level_modules:        {mods}")
    print(f"  mcp_tools.py (non-test):  {mcp_files}")
    print(f"  @mcp_tool (production):   {decorators}")
    print(f"  .github/workflows *.yml:  {count_github_workflow_yml(root)}")
    if args.manifest:
        n = metrics["runtime_mcp_tools"]
        if n is not None:
            print(f"  manifest tools (runtime): {n}")
        else:
            print("  manifest tools (runtime): (import or get_skill_manifest failed)")
    if args.pytest:
        n = metrics["pytest_collected"]
        if n is not None:
            print(f"  pytest collected:         {n}")
        else:
            print("  pytest collected:         (failed to run or parse)")
    else:
        print("  pytest collected:         (omit --pytest for speed; see inventory.md)")
    if args.check_reference:
        if reference_errors:
            print("  reference check:          FAILED")
            for error in reference_errors:
                print(f"    - {error}")
            return 1
        print("  reference check:          passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
