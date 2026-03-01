#!/usr/bin/env python3
"""
PAI Trust Lifecycle Demo

Complete three-tier trust model from cold start to full execution:
UNTRUSTED → VERIFIED → TRUSTED, with permission enforcement at each tier.

Usage:
    python scripts/agents/pai/trust_lifecycle.py                   # Full lifecycle
    python scripts/agents/pai/trust_lifecycle.py --phase verify    # Single phase
    python scripts/agents/pai/trust_lifecycle.py --json            # JSON output

Upstream: https://github.com/danielmiessler/Personal_AI_Infrastructure
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.agents.pai import (
    TrustLevel,
    DESTRUCTIVE_TOOLS,
    SAFE_TOOL_COUNT,
    DESTRUCTIVE_TOOL_COUNT,
    verify_capabilities,
    trust_tool,
    trust_all,
    trusted_call_tool,
    get_trust_report,
    is_trusted,
    reset_trust,
)
from codomyrmex.utils.cli_helpers import (
    setup_logging, print_info, print_success, print_warning, print_error,
)

PHASES = ["reset", "verify", "trust-one", "trust-all", "execute"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PAI Trust Lifecycle — UNTRUSTED → VERIFIED → TRUSTED cycle",
    )
    parser.add_argument("--phase", choices=PHASES, help="Run a specific phase only")
    parser.add_argument("--json", "-j", action="store_true", dest="json_output", help="JSON output")
    return parser.parse_args()


def _header(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


def phase_reset() -> dict:
    """Phase 1: Reset all trust to UNTRUSTED."""
    _header("Phase 1: RESET — All tools to UNTRUSTED")

    reset_trust()
    report = get_trust_report()

    print(f"  Trust levels: {', '.join(t.value for t in TrustLevel)}")
    print(f"  Safe tool count      : {SAFE_TOOL_COUNT}")
    print(f"  Destructive tool count: {DESTRUCTIVE_TOOL_COUNT}")

    by_level = report.get("by_level", {}) if isinstance(report, dict) else {}
    for level, tools in by_level.items():
        count = len(tools) if isinstance(tools, list) else tools
        print(f"  {level:15s}: {count}")

    print_success("  All tools reset to UNTRUSTED")
    return {"status": "reset", "report": report}


def phase_verify() -> dict:
    """Phase 2: Verify capabilities — promote safe tools."""
    _header("Phase 2: VERIFY — Promote safe tools to VERIFIED")

    result = verify_capabilities()

    promoted = result.get("promoted", []) if isinstance(result, dict) else []
    print_success(f"  Promoted {len(promoted)} safe tools to VERIFIED:")
    for tool in promoted[:10]:
        print(f"    ✅ {tool}")
    if len(promoted) > 10:
        print(f"    ... and {len(promoted) - 10} more")

    # Show destructive tools still UNTRUSTED
    destructive = sorted(DESTRUCTIVE_TOOLS) if DESTRUCTIVE_TOOLS else []
    print(f"\n  Destructive tools still UNTRUSTED ({len(destructive)}):")
    for t in destructive:
        print(f"    🔒 {t}")

    # Test: safe tool should work at VERIFIED
    try:
        trusted_call_tool("codomyrmex.list_modules")
        print_success("\n  ✅ Safe tool works at VERIFIED level")
    except PermissionError:
        print_error("  ❌ Safe tool blocked unexpectedly")

    # Test: destructive tool should fail at VERIFIED
    try:
        trusted_call_tool("codomyrmex.write_file", path="/tmp/test.txt", content="x")
        print_warning("  ⚠️ Destructive tool allowed at VERIFIED — unexpected")
    except PermissionError:
        print_success("  ✅ Destructive tool correctly blocked at VERIFIED")

    return {"promoted": len(promoted), "enforcement": "working"}


def phase_trust_one() -> dict:
    """Phase 3: Trust a single destructive tool."""
    _header("Phase 3: TRUST ONE — Selective promotion")

    target = "codomyrmex.write_file"
    print(f"  Trusting single tool: {target}")

    before = is_trusted(target)
    print(f"  Before: is_trusted('{target}') = {before}")

    trust_tool(target)

    after = is_trusted(target)
    print(f"  After:  is_trusted('{target}') = {after}")

    report = get_trust_report()
    by_level = report.get("by_level", {}) if isinstance(report, dict) else {}
    for level, tools in by_level.items():
        count = len(tools) if isinstance(tools, list) else tools
        print(f"  {level:15s}: {count}")

    print_success(f"  {target} promoted to TRUSTED")
    return {"tool": target, "before": before, "after": after}


def phase_trust_all() -> dict:
    """Phase 4: Trust all tools."""
    _header("Phase 4: TRUST ALL — Full promotion")

    promoted = trust_all()
    promoted_list = promoted if isinstance(promoted, list) else []
    print_success(f"  Promoted {len(promoted_list)} tools to TRUSTED")

    report = get_trust_report()
    by_level = report.get("by_level", {}) if isinstance(report, dict) else {}
    for level, tools in by_level.items():
        count = len(tools) if isinstance(tools, list) else tools
        print(f"  {level:15s}: {count}")

    return {"promoted": len(promoted_list), "report": report}


def phase_execute() -> dict:
    """Phase 5: Execute tools at full trust."""
    _header("Phase 5: EXECUTE — Tools at full trust")

    tools_to_test = [
        ("codomyrmex.list_modules", {}),
        ("codomyrmex.pai_status", {}),
        ("codomyrmex.git_status", {}),
    ]

    results = {}
    for tool_name, kwargs in tools_to_test:
        try:
            result = trusted_call_tool(tool_name, **kwargs)
            status = result.get("status", "ok") if isinstance(result, dict) else "ok"
            print(f"  ✅ {tool_name:40s}  status={status}")
            results[tool_name] = "ok"
        except Exception as e:
            print(f"  ❌ {tool_name:40s}  error: {e}")
            results[tool_name] = str(e)

    return results


def main() -> int:
    args = parse_args()
    setup_logging()

    print(f"🔐 PAI Trust Lifecycle Demo")
    print(f"   Trust model: {' → '.join(t.value for t in TrustLevel)}")

    results: dict = {}

    try:
        if args.phase:
            fn = {
                "reset": phase_reset,
                "verify": phase_verify,
                "trust-one": phase_trust_one,
                "trust-all": phase_trust_all,
                "execute": phase_execute,
            }[args.phase]
            results[args.phase] = fn()
        else:
            # Full lifecycle
            results["reset"] = phase_reset()
            results["verify"] = phase_verify()
            results["trust_one"] = phase_trust_one()
            results["trust_all"] = phase_trust_all()
            results["execute"] = phase_execute()
    finally:
        # Always reset trust state on exit
        try:
            reset_trust()
            print_info("\n  Trust state reset on exit (cleanup).")
        except Exception:
            pass

    if args.json_output:
        print("\n" + json.dumps(results, indent=2, default=str))

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
