"""Codomyrmex CLI Doctor — self-diagnostics for the Codomyrmex ecosystem.

Usage::

    codomyrmex doctor              # Quick module import check
    codomyrmex doctor --pai        # PAI bridge health
    codomyrmex doctor --mcp        # MCP tool registry health
    codomyrmex doctor --rasp       # README/AGENTS/SPEC completeness
    codomyrmex doctor --workflows  # Workflow file validity
    codomyrmex doctor --all        # All checks
    codomyrmex doctor --fix        # Auto-fix detected issues
    codomyrmex doctor --json       # Machine-readable output

Exit codes:
    0  — all checks passed
    1  — warnings detected
    2  — errors detected
"""

from __future__ import annotations

import importlib
import json as json_mod
import shutil
import time
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parents[3]  # cli → codomyrmex → src → repo
_SRC_CODOMYRMEX = Path(__file__).resolve().parents[1]  # cli → codomyrmex


# ─── Result types ────────────────────────────────────────────────────


class CheckResult:
    """Single diagnostic check result."""

    __slots__ = ("details", "message", "name", "status")

    OK = "ok"
    WARN = "warn"
    ERROR = "error"

    def __init__(
        self,
        name: str,
        status: str = OK,
        message: str = "",
        details: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.status = status
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"name": self.name, "status": self.status}
        if self.message:
            d["message"] = self.message
        if self.details:
            d["details"] = self.details
        return d


# ─── Individual checks ───────────────────────────────────────────────


def check_module_imports() -> list[CheckResult]:
    """Try importing every submodule of codomyrmex."""
    results: list[CheckResult] = []
    try:
        from codomyrmex import list_modules

        module_names = list_modules()
    except Exception as exc:
        return [CheckResult("module_discovery", CheckResult.ERROR, str(exc))]

    ok = 0
    failed: list[str] = []
    for name in sorted(module_names):
        try:
            importlib.import_module(f"codomyrmex.{name}")
            ok += 1
        except Exception as exc:
            failed.append(f"{name}: {exc}")

    results.append(
        CheckResult(
            "module_imports",
            CheckResult.ERROR if failed else CheckResult.OK,
            f"{ok} ok, {len(failed)} failed",
            {"total": ok + len(failed), "ok": ok, "failed": failed},
        )
    )
    return results


def check_pai() -> list[CheckResult]:
    """Check PAI bridge health."""
    results: list[CheckResult] = []
    try:
        from codomyrmex.agents.pai.trust_gateway import verify_capabilities

        t0 = time.monotonic()
        report = verify_capabilities()
        elapsed_ms = (time.monotonic() - t0) * 1000

        modules = report.get("modules", {})
        if isinstance(modules, dict):
            count = modules.get("count", modules.get("loaded", modules.get("total", 0)))
        elif isinstance(modules, list):
            count = len(modules)
        else:
            count = 0

        results.append(
            CheckResult(
                "pai_verify_capabilities",
                CheckResult.OK if count >= 82 else CheckResult.WARN,
                f"{count} modules, {elapsed_ms:.0f}ms",
                {"module_count": count, "elapsed_ms": round(elapsed_ms, 1)},
            )
        )
    except Exception as exc:
        results.append(
            CheckResult("pai_verify_capabilities", CheckResult.ERROR, str(exc))
        )

    return results


def check_mcp() -> list[CheckResult]:
    """Check MCP tool registry health."""
    results: list[CheckResult] = []
    try:
        from codomyrmex.agents.pai.mcp_bridge import get_tool_registry

        t0 = time.monotonic()
        registry = get_tool_registry()
        elapsed_ms = (time.monotonic() - t0) * 1000

        tools = registry.list_tools() if hasattr(registry, "list_tools") else []
        tool_count = len(tools) if isinstance(tools, (list, dict)) else 0

        results.append(
            CheckResult(
                "mcp_tool_registry",
                CheckResult.OK if tool_count >= 10 else CheckResult.WARN,
                f"{tool_count} tools registered, {elapsed_ms:.0f}ms",
                {"tool_count": tool_count, "elapsed_ms": round(elapsed_ms, 1)},
            )
        )
    except Exception as exc:
        results.append(CheckResult("mcp_tool_registry", CheckResult.ERROR, str(exc)))

    try:
        from codomyrmex.agents.pai.mcp_bridge import create_codomyrmex_mcp_server

        server = create_codomyrmex_mcp_server(name="doctor-test", transport="stdio")
        results.append(
            CheckResult(
                "mcp_server_creation",
                CheckResult.OK if server is not None else CheckResult.ERROR,
                "Server created" if server else "Server creation failed",
            )
        )
    except Exception as exc:
        results.append(CheckResult("mcp_server_creation", CheckResult.ERROR, str(exc)))

    return results


def check_rasp() -> list[CheckResult]:
    """Check README/AGENTS/SPEC completeness across all modules."""
    results: list[CheckResult] = []
    missing: list[str] = []
    complete = 0

    try:
        from codomyrmex import list_modules

        module_names = list_modules()
    except Exception as exc:
        return [CheckResult("rasp_discovery", CheckResult.ERROR, str(exc))]

    for name in sorted(module_names):
        mod_dir = _SRC_CODOMYRMEX / name
        if not mod_dir.is_dir():
            continue
        mod_missing = False
        for doc in ("README.md", "AGENTS.md", "SPEC.md"):
            if not (mod_dir / doc).exists():
                missing.append(f"{name}/{doc}")
                mod_missing = True
        if not mod_missing:
            complete += 1

    results.append(
        CheckResult(
            "rasp_completeness",
            CheckResult.OK if not missing else CheckResult.WARN,
            f"{complete} complete, {len(missing)} missing docs",
            {
                "complete": complete,
                "missing_count": len(missing),
                "missing": missing[:20],
            },
        )
    )
    return results


def check_workflows() -> list[CheckResult]:
    """Check workflow file validity."""
    results: list[CheckResult] = []
    workflow_dir = _PROJECT_ROOT / ".agent" / "workflows"

    if not workflow_dir.exists():
        return [
            CheckResult("workflows_dir", CheckResult.ERROR, "Missing .agent/workflows/")
        ]

    valid = 0
    invalid: list[str] = []

    for wf in sorted(workflow_dir.glob("*.md")):
        content = wf.read_text(encoding="utf-8")
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3 and "description:" in parts[1]:
                valid += 1
                continue
        invalid.append(wf.name)

    results.append(
        CheckResult(
            "workflow_files",
            CheckResult.OK if not invalid else CheckResult.WARN,
            f"{valid} valid, {len(invalid)} invalid",
            {"valid": valid, "invalid": invalid},
        )
    )
    return results


# ─── Fix functions ───────────────────────────────────────────────────

_RASP_TEMPLATES: dict[str, str] = {
    "README.md": (
        "# {module}\n\n**Status**: Active\n\n## Overview\n\n"
        "TODO: Add module description.\n\n## Navigation\n\n"
        "- **Parent**: [../README.md](../README.md)\n"
    ),
    "AGENTS.md": (
        "# {module} — Agent Guidelines\n\n## Overview\n\n"
        "Guidelines for AI agents working with the `{module}` module.\n\n"
        "## Key Files\n\n- `__init__.py` — Public API\n- `mcp_tools.py` — MCP tool definitions\n\n"
        "## Rules\n\n- Follow Zero-Mock testing policy\n- Maintain RASP documentation\n"
    ),
    "SPEC.md": (
        "# {module} — Specification\n\n## Purpose\n\n"
        "TODO: Add functional specification.\n\n## Public API\n\n"
        "TODO: Document public API.\n\n## Dependencies\n\nTODO: List dependencies.\n"
    ),
    "PAI.md": (
        "# {module} — PAI Context\n\n## Algorithm Phase Mapping\n\n"
        "TODO: Map to PAI Algorithm phases.\n\n## MCP Tools\n\n"
        "See `mcp_tools.py` for available tools.\n"
    ),
}


def fix_rasp() -> list[CheckResult]:
    """Auto-create missing RASP documentation files from templates.

    Returns:
        List of results indicating what was fixed.
    """
    results: list[CheckResult] = []
    created: list[str] = []

    try:
        from codomyrmex import list_modules

        module_names = list_modules()
    except Exception as exc:
        return [CheckResult("fix_rasp", CheckResult.ERROR, str(exc))]

    for name in sorted(module_names):
        mod_dir = _SRC_CODOMYRMEX / name
        if not mod_dir.is_dir():
            continue
        for doc, template in _RASP_TEMPLATES.items():
            doc_path = mod_dir / doc
            if not doc_path.exists():
                doc_path.write_text(template.format(module=name), encoding="utf-8")
                created.append(f"{name}/{doc}")

    results.append(
        CheckResult(
            "fix_rasp",
            CheckResult.OK,
            f"Created {len(created)} missing docs" if created else "No missing docs",
            {"created": created},
        )
    )
    return results


def fix_env() -> list[CheckResult]:
    """Auto-create .env from .env.example if missing.

    Returns:
        List of results indicating what was fixed.
    """
    results: list[CheckResult] = []
    env_path = _PROJECT_ROOT / ".env"
    example_path = _PROJECT_ROOT / ".env.example"

    if env_path.exists():
        results.append(CheckResult("fix_env", CheckResult.OK, ".env already exists"))
        return results

    if example_path.exists():
        shutil.copy2(example_path, env_path)
        results.append(
            CheckResult(
                "fix_env",
                CheckResult.OK,
                "Created .env from .env.example",
                {"source": str(example_path)},
            )
        )
    else:
        env_path.write_text(
            "# Codomyrmex Environment Configuration\n"
            "# See docs/getting-started/setup.md for details\n"
            "\n"
            "# CODOMYRMEX_ENV=development\n"
            "# OPENROUTER_API_KEY=\n"
            "# OPENAI_API_KEY=\n",
            encoding="utf-8",
        )
        results.append(
            CheckResult(
                "fix_env",
                CheckResult.OK,
                "Created minimal .env (no .env.example found)",
            )
        )

    return results


def fix_optional_deps() -> list[CheckResult]:
    """Check and suggest optional dependency installation.

    Returns:
        List of results with install suggestions.
    """
    results: list[CheckResult] = []
    extras_to_check = [
        ("psutil", "performance"),
        ("redis", "cache"),
        ("docker", "containerization"),
        ("matplotlib", "data_visualization"),
    ]

    missing: list[str] = []
    for module_name, extra_name in extras_to_check:
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing.append(extra_name)

    if missing:
        suggestions = [f"uv sync --extra {e}" for e in missing]
        results.append(
            CheckResult(
                "fix_optional_deps",
                CheckResult.WARN,
                f"{len(missing)} optional extras not installed",
                {"missing": missing, "install_commands": suggestions},
            )
        )
    else:
        results.append(
            CheckResult(
                "fix_optional_deps",
                CheckResult.OK,
                "All checked optional deps installed",
            )
        )

    return results


# ─── Runner ──────────────────────────────────────────────────────────


def run_doctor(
    *,
    pai: bool = False,
    mcp: bool = False,
    rasp: bool = False,
    workflows: bool = False,
    imports: bool = False,
    all_checks: bool = False,
    fix: bool = False,
    output_json: bool = False,
) -> bool:
    """Run selected diagnostic checks.

    Args:
        pai: Run PAI bridge health check.
        mcp: Run MCP tool registry health check.
        rasp: Run RASP documentation completeness check.
        workflows: Run workflow file validity check.
        imports: Run module import check.
        all_checks: Run all checks.
        fix: Auto-fix detected issues (creates missing docs, .env, etc.).
        output_json: Output results as JSON.

    Returns:
        True if all checks passed, False otherwise.
    """
    checks: list[CheckResult] = []

    if not any([pai, mcp, rasp, workflows, imports, all_checks, fix]):
        imports = True

    if imports or all_checks:
        checks.extend(check_module_imports())
    if pai or all_checks:
        checks.extend(check_pai())
    if mcp or all_checks:
        checks.extend(check_mcp())
    if rasp or all_checks:
        checks.extend(check_rasp())
    if workflows or all_checks:
        checks.extend(check_workflows())

    if fix:
        checks.extend(fix_rasp())
        checks.extend(fix_env())
        checks.extend(fix_optional_deps())

    has_errors = any(c.status == CheckResult.ERROR for c in checks)
    has_warnings = any(c.status == CheckResult.WARN for c in checks)

    if output_json:
        print(
            json_mod.dumps(
                {
                    "status": "error"
                    if has_errors
                    else "warn"
                    if has_warnings
                    else "ok",
                    "checks": [c.to_dict() for c in checks],
                },
                indent=2,
            )
        )
    else:
        icons = {CheckResult.OK: "✅", CheckResult.WARN: "⚠️", CheckResult.ERROR: "❌"}
        print("\n🔬 Codomyrmex Doctor\n")
        for c in checks:
            icon = icons.get(c.status, "?")
            print(f"  {icon} {c.name}: {c.message}")
            if c.status != CheckResult.OK and c.details:
                for k, v in c.details.items():
                    if k not in ("missing", "failed", "install_commands"):
                        continue
                    if isinstance(v, list) and v:
                        for item in v[:5]:
                            print(f"      - {item}")
                        if len(v) > 5:
                            print(f"      ... and {len(v) - 5} more")

        total = len(checks)
        ok_count = sum(1 for c in checks if c.status == CheckResult.OK)
        print(f"\n  {ok_count}/{total} checks passed\n")

    return not has_errors and not has_warnings
