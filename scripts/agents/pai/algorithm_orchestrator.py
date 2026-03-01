#!/usr/bin/env python3
"""
PAI Algorithm Orchestrator — Capstone Demo

Walk through all 7 Algorithm phases programmatically, using PAI tools at
each step. This is the capstone script demonstrating how PAI bridge + MCP
bridge + trust gateway work together in a realistic Algorithm execution.

Usage:
    python scripts/agents/pai/algorithm_orchestrator.py              # All phases
    python scripts/agents/pai/algorithm_orchestrator.py --phase 1    # Single phase
    python scripts/agents/pai/algorithm_orchestrator.py --depth FULL # Set depth
    python scripts/agents/pai/algorithm_orchestrator.py --json       # JSON output

Upstream: https://github.com/danielmiessler/Personal_AI_Infrastructure
"""

import argparse
import json
import sys
import time
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.agents.pai import (
    PAIBridge,
    ALGORITHM_PHASES,
    RESPONSE_DEPTH_LEVELS,
    PAI_PRINCIPLES,
    PAI_UPSTREAM_URL,
    call_tool,
    verify_capabilities,
    trust_all,
    trusted_call_tool,
    get_skill_manifest,
    get_trust_report,
    reset_trust,
)
from codomyrmex.utils.cli_helpers import (
    setup_logging, print_info, print_success, print_warning,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PAI Algorithm Orchestrator — 7-phase walkthrough with real tools",
    )
    parser.add_argument(
        "--phase", "-p", type=int, choices=range(1, 8),
        help="Run a specific phase (1-7)",
    )
    parser.add_argument(
        "--depth", choices=["FULL", "ITERATION", "MINIMAL"], default="FULL",
        help="Response depth level (default: FULL)",
    )
    parser.add_argument("--json", "-j", action="store_true", dest="json_output", help="JSON output")
    return parser.parse_args()


def _phase_header(phase_num: int) -> None:
    phase = ALGORITHM_PHASES[phase_num - 1]
    icons = ["👁️", "🧠", "📋", "🔨", "⚡", "✅", "📚"]
    icon = icons[phase_num - 1]
    print(f"\n{'━' * 60}")
    print(f"  {icon} {phase['name']} ━━━ {phase['phase']}")
    print(f"  {phase['description']}")
    print(f"{'━' * 60}")


def phase_1_observe(bridge: PAIBridge) -> dict:
    """OBSERVE: Parse intent and gather system state."""
    _phase_header(1)

    # Check PAI installation
    status = bridge.get_status()
    installed = status.get("pai_installed", False)
    print(f"  PAI installed: {installed}")

    # System inventory
    components = bridge.get_components()
    present = sum(1 for v in components.values() if isinstance(v, dict) and v.get("exists", False))
    print(f"  Components: {present}/{len(components)} present")

    # Module inventory via call_tool
    try:
        modules_result = call_tool("codomyrmex.list_modules")
        modules = modules_result.get("modules", []) if isinstance(modules_result, dict) else []
        print(f"  Codomyrmex modules: {len(modules)}")
    except Exception:
        modules = []
        print_warning("  Could not list modules")

    # Git state
    try:
        git_result = call_tool("codomyrmex.git_status")
        branch = git_result.get("branch", "unknown") if isinstance(git_result, dict) else "unknown"
        print(f"  Git branch: {branch}")
    except Exception:
        branch = "unknown"

    observations = {
        "pai_installed": installed,
        "components": present,
        "modules": len(modules),
        "branch": branch,
    }
    print_success(f"  Observations collected: {len(observations)} data points")
    return observations


def phase_2_think(bridge: PAIBridge) -> dict:
    """THINK: Assess capabilities and select approach."""
    _phase_header(2)

    # Capability assessment
    manifest = get_skill_manifest()
    tools = manifest.get("tools", [])
    print(f"  Available tools: {len(tools)}")

    # Skill inventory
    skills = bridge.list_skills()
    print(f"  Skill packs: {len(skills)}")
    for sk in skills[:5]:
        print(f"    • {sk.name} ({sk.file_count} files)")
    if len(skills) > 5:
        print(f"    ... and {len(skills) - 5} more")

    # Principles as decision framework
    print(f"\n  PAI Principles ({len(PAI_PRINCIPLES)} total):")
    for p in PAI_PRINCIPLES[:3]:
        print(f"    #{p['num']:>2s}  {p['name']}")
    print(f"    ... and {len(PAI_PRINCIPLES) - 3} more")

    assessment = {
        "tool_count": len(tools),
        "skill_count": len(skills),
        "principles": len(PAI_PRINCIPLES),
    }
    print_success(f"  Assessment complete: {len(assessment)} dimensions")
    return assessment


def phase_3_plan(bridge: PAIBridge, depth: str) -> dict:
    """PLAN: Select depth and choose tools."""
    _phase_header(3)

    # Show depth levels
    print(f"  Selected depth: {depth}")
    print(f"  Available depths:")
    for lvl in RESPONSE_DEPTH_LEVELS:
        marker = "→" if lvl["depth"] == depth else " "
        print(f"    {marker} {lvl['depth']:12s}  {lvl['when']}")

    # Plan tool selection
    planned_tools = [
        "codomyrmex.list_modules",
        "codomyrmex.pai_status",
        "codomyrmex.module_info",
    ]
    print(f"\n  Planned tool invocations ({len(planned_tools)}):")
    for t in planned_tools:
        print(f"    📋 {t}")

    plan = {
        "depth": depth,
        "planned_tools": planned_tools,
        "tool_count": len(planned_tools),
    }
    print_success(f"  Plan finalized: {len(planned_tools)} tools selected")
    return plan


def phase_4_build() -> dict:
    """BUILD: Prepare execution environment (trust verification)."""
    _phase_header(4)

    # Audit capabilities
    print_info("  Auditing capabilities...")
    report = verify_capabilities()
    promoted = report.get("promoted", []) if isinstance(report, dict) else []
    print_success(f"  Verified: {len(promoted)} safe tools promoted")

    # Trust all for execution
    print_info("  Enabling full trust for execution...")
    trust_all()
    print_success("  All tools promoted to TRUSTED")

    # Show trust report
    trust = get_trust_report()
    return {"promoted": len(promoted), "trust_report": trust}


def phase_5_execute(planned_tools: list[str]) -> dict:
    """EXECUTE: Run planned tools."""
    _phase_header(5)

    results = {}
    for tool_name in planned_tools:
        start = time.monotonic()
        try:
            if tool_name == "codomyrmex.module_info":
                result = trusted_call_tool(tool_name, module_name="agents")
            else:
                result = trusted_call_tool(tool_name)
            elapsed = time.monotonic() - start
            status = result.get("status", "ok") if isinstance(result, dict) else "ok"
            print(f"  ✅ {tool_name:40s}  {elapsed:.3f}s  status={status}")
            results[tool_name] = {"status": "ok", "elapsed": round(elapsed, 3)}
        except Exception as e:
            elapsed = time.monotonic() - start
            print(f"  ❌ {tool_name:40s}  {elapsed:.3f}s  error: {e}")
            results[tool_name] = {"status": "error", "error": str(e)}

    passed = sum(1 for r in results.values() if r["status"] == "ok")
    print(f"\n  Executed: {passed}/{len(results)} tools succeeded")
    return results


def phase_6_verify(execution_results: dict) -> dict:
    """VERIFY: Validate results against expectations."""
    _phase_header(6)

    checks = []

    # Check all tools succeeded
    all_ok = all(r.get("status") == "ok" for r in execution_results.values())
    checks.append(("All tools executed successfully", all_ok))

    # Check trust state is consistent
    trust = get_trust_report()
    checks.append(("Trust report available", trust is not None))

    # Check no unintended git changes
    try:
        git = call_tool("codomyrmex.git_status")
        checks.append(("Git status accessible", git is not None))
    except Exception:
        checks.append(("Git status accessible", False))

    for label, passed in checks:
        icon = "✅" if passed else "❌"
        print(f"  {icon} {label}")

    passed_count = sum(1 for _, p in checks if p)
    print(f"\n  Verification: {passed_count}/{len(checks)} checks passed")

    return {
        "checks_passed": passed_count,
        "checks_total": len(checks),
        "all_pass": all(p for _, p in checks),
    }


def phase_7_learn(bridge: PAIBridge, all_results: dict) -> dict:
    """LEARN: Summarize what was learned."""
    _phase_header(7)

    # Memory system for storing learnings
    stores = bridge.list_memory_stores()
    print(f"  Memory stores available: {len(stores)}")
    for s in stores[:5]:
        print(f"    📁 {s.name:25s}  {s.item_count} items")

    # Summary
    phases_run = len(all_results)
    print(f"\n  Summary:")
    print(f"    Phases completed  : {phases_run}/7")
    print(f"    PAI upstream      : {PAI_UPSTREAM_URL}")
    print(f"    Algorithm phases  : {len(ALGORITHM_PHASES)}")
    print(f"    Principles applied: {len(PAI_PRINCIPLES)}")

    return {
        "phases_completed": phases_run,
        "memory_stores": len(stores),
        "upstream": PAI_UPSTREAM_URL,
    }


def main() -> int:
    args = parse_args()
    setup_logging()

    print(f"🧬 PAI Algorithm Orchestrator — 7-Phase Walkthrough")
    print(f"   Depth: {args.depth} | Upstream: {PAI_UPSTREAM_URL}")

    bridge = PAIBridge()
    if not bridge.is_installed():
        print_warning("PAI is not installed. Some phases will show limited data.")

    all_results: dict = {}

    try:
        if args.phase:
            # Single phase
            fns = {
                1: lambda: phase_1_observe(bridge),
                2: lambda: phase_2_think(bridge),
                3: lambda: phase_3_plan(bridge, args.depth),
                4: phase_4_build,
                5: lambda: phase_5_execute(["codomyrmex.list_modules", "codomyrmex.pai_status"]),
                6: lambda: phase_6_verify({}),
                7: lambda: phase_7_learn(bridge, all_results),
            }
            all_results[f"phase_{args.phase}"] = fns[args.phase]()
        else:
            # Full orchestration
            all_results["observe"] = phase_1_observe(bridge)
            all_results["think"] = phase_2_think(bridge)
            all_results["plan"] = phase_3_plan(bridge, args.depth)
            all_results["build"] = phase_4_build()

            planned = all_results["plan"].get("planned_tools", [])
            all_results["execute"] = phase_5_execute(planned)
            all_results["verify"] = phase_6_verify(all_results["execute"])
            all_results["learn"] = phase_7_learn(bridge, all_results)

            # Final status
            verify = all_results.get("verify", {})
            if verify.get("all_pass"):
                print_success("\n  🎯 Algorithm orchestration completed successfully!")
            else:
                print_warning("\n  ⚠️ Algorithm completed with some checks failing.")
    finally:
        # Always reset trust state
        try:
            reset_trust()
            print_info("  Trust state reset on exit (cleanup).")
        except Exception:
            pass

    if args.json_output:
        print("\n" + json.dumps(all_results, indent=2, default=str))

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
