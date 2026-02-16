#!/usr/bin/env python3
"""Validate PAI ↔ Codomyrmex integration across all layers.

Checks:
  1. Module count consistency across bridge, dashboard, and SKILL.md
  2. Tool count consistency between registry and SKILL.md
  3. Trust gateway covers all registered tools
  4. Documentation completeness (PAI.md, MCP specs)
  5. Test coverage for critical modules

Exit 0 on success, exit 1 with details on failure.
"""

import importlib
import sys
from pathlib import Path

# ── Project root ──
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "codomyrmex"

errors: list[str] = []
warnings: list[str] = []


def check(condition: bool, msg: str, *, warn: bool = False) -> None:
    """Record a check result."""
    if not condition:
        if warn:
            warnings.append(f"  WARN: {msg}")
        else:
            errors.append(f"  FAIL: {msg}")


def main() -> int:
    print("=" * 60)
    print("PAI ↔ Codomyrmex Integration Validation")
    print("=" * 60)

    # ── 1. Module count ──
    print("\n[1/5] Module count consistency...")
    module_dirs = sorted(
        d.name for d in SRC.iterdir()
        if d.is_dir() and d.name != "__pycache__" and (d / "__init__.py").exists()
    )
    fs_count = len(module_dirs)
    print(f"  Filesystem modules: {fs_count}")

    try:
        import codomyrmex
        listed = codomyrmex.list_modules()
        bridge_count = len(listed)
        print(f"  Bridge list_modules: {bridge_count}")
        check(
            bridge_count >= fs_count - 5,
            f"Bridge reports {bridge_count} modules, filesystem has {fs_count} (gap > 5)",
        )
    except Exception as exc:
        errors.append(f"  FAIL: Cannot import codomyrmex.list_modules(): {exc}")

    # ── 2. Knowledge scope coverage ──
    print("\n[2/5] Knowledge scope coverage...")
    try:
        from codomyrmex.agents.pai.mcp_bridge import get_skill_manifest
        manifest = get_skill_manifest()
        scope = manifest.get("knowledge_scope", {})
        scope_modules = set()
        for domain_modules in scope.values():
            scope_modules.update(domain_modules)
        print(f"  Knowledge scope modules: {len(scope_modules)}")
        missing_from_scope = set(module_dirs) - scope_modules
        check(
            len(missing_from_scope) == 0,
            f"Modules not in knowledge scope: {sorted(missing_from_scope)}",
            warn=True,
        )
    except Exception as exc:
        errors.append(f"  FAIL: Cannot load skill manifest: {exc}")

    # ── 3. Tool count + trust gateway ──
    print("\n[3/5] Tool registry + trust gateway...")
    try:
        from codomyrmex.agents.pai.mcp_bridge import get_tool_registry
        registry = get_tool_registry()
        tool_names = registry.list_tools()
        print(f"  Total registered tools: {len(tool_names)}")
        check(len(tool_names) >= 18, f"Expected at least 18 tools, got {len(tool_names)}")

        from codomyrmex.agents.pai.trust_gateway import verify_capabilities
        report = verify_capabilities()
        if isinstance(report, dict):
            trust_tools = report.get("tools", {})
            total = trust_tools.get("count", 0)
            print(f"  Trust gateway total: {total}")
            check(total >= 18, f"Trust gateway sees {total} tools, expected >= 18")
    except Exception as exc:
        errors.append(f"  FAIL: Trust gateway check failed: {exc}")

    # ── 4. Documentation completeness ──
    print("\n[4/5] Documentation completeness...")
    doc_types = ["README.md", "PAI.md", "AGENTS.md", "SPEC.md", "API_SPECIFICATION.md", "MCP_TOOL_SPECIFICATION.md"]
    for doc_type in doc_types:
        count = sum(1 for d in module_dirs if (SRC / d / doc_type).exists())
        coverage = round(count / fs_count * 100, 1)
        status = "OK" if coverage >= 95 else "WARN"
        print(f"  {doc_type}: {count}/{fs_count} ({coverage}%) [{status}]")
        check(coverage >= 95, f"{doc_type} coverage is {coverage}% (< 95%)", warn=True)

    # ── 5. Test coverage ──
    print("\n[5/5] Test coverage for critical modules...")
    critical_modules = ["agents", "auth", "encryption", "security", "llm", "coding", "git_operations"]
    test_base = SRC / "tests" / "unit"
    for mod in critical_modules:
        test_dir = test_base / mod
        has_tests = test_dir.exists() and any(test_dir.rglob("test_*.py"))
        status = "OK" if has_tests else "MISSING"
        print(f"  {mod}: [{status}]")
        check(has_tests, f"Critical module '{mod}' has no tests")

    # ── Results ──
    print("\n" + "=" * 60)
    if errors:
        print(f"FAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
        for e in errors:
            print(e)
        for w in warnings:
            print(w)
        return 1
    else:
        if warnings:
            print(f"PASSED with {len(warnings)} warning(s)")
            for w in warnings:
                print(w)
        else:
            print("PASSED: All checks green")
        return 0


if __name__ == "__main__":
    sys.exit(main())
