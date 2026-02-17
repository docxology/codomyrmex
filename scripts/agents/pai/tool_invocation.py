#!/usr/bin/env python3
"""
PAI Tool Invocation Patterns

Demonstrate every tool invocation pattern: direct call_tool, trust-gated
trusted_call_tool, dynamic module proxy tools, and error handling.

Usage:
    python scripts/agents/pai/tool_invocation.py                    # All patterns
    python scripts/agents/pai/tool_invocation.py --pattern direct   # Direct calls only
    python scripts/agents/pai/tool_invocation.py --pattern trusted  # Trust-gated only
    python scripts/agents/pai/tool_invocation.py --json             # JSON output

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
    call_tool,
    trusted_call_tool,
    verify_capabilities,
    trust_all,
    reset_trust,
)
from codomyrmex.utils.cli_helpers import (
    setup_logging, print_info, print_success, print_warning, print_error,
)

PATTERNS = ["direct", "trusted", "dynamic", "errors"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PAI Tool Invocation Patterns — direct, trusted, dynamic, error handling",
    )
    parser.add_argument("--pattern", "-p", choices=PATTERNS, help="Show specific pattern")
    parser.add_argument("--json", "-j", action="store_true", dest="json_output", help="JSON output")
    return parser.parse_args()


def _header(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


def _timed_call(tool_name: str, **kwargs) -> tuple[dict, float]:
    """Call a tool and measure execution time."""
    start = time.monotonic()
    result = call_tool(tool_name, **kwargs)
    elapsed = time.monotonic() - start
    return result, elapsed


def pattern_direct() -> dict:
    """Direct tool invocation via call_tool()."""
    _header("Pattern 1: Direct Tool Calls (call_tool)")

    calls = [
        ("codomyrmex.list_modules", {}),
        ("codomyrmex.pai_status", {}),
        ("codomyrmex.module_info", {"module_name": "agents"}),
        ("codomyrmex.git_status", {}),
    ]

    results = {}
    for tool_name, kwargs in calls:
        try:
            result, elapsed = _timed_call(tool_name, **kwargs)
            status = result.get("status", "ok") if isinstance(result, dict) else "ok"
            print(f"  ✅ {tool_name:40s}  {elapsed:.3f}s  status={status}")
            results[tool_name] = {"status": "ok", "elapsed": elapsed}
        except Exception as e:
            print(f"  ❌ {tool_name:40s}  error: {e}")
            results[tool_name] = {"status": "error", "error": str(e)}

    return results


def pattern_trusted() -> dict:
    """Trust-gated tool invocation via trusted_call_tool()."""
    _header("Pattern 2: Trust-Gated Calls (trusted_call_tool)")

    # Start fresh
    reset_trust()
    print_info("  Trust reset to UNTRUSTED")

    # Verify — promotes safe tools to VERIFIED
    report = verify_capabilities()
    promoted = report.get("promoted", []) if isinstance(report, dict) else []
    print_success(f"  Verified: {len(promoted)} safe tools promoted to VERIFIED")

    # Try a safe tool (should succeed at VERIFIED)
    try:
        result = trusted_call_tool("codomyrmex.list_modules")
        print_success("  ✅ trusted_call_tool('list_modules') — PASSED (VERIFIED is sufficient)")
    except PermissionError as e:
        print_error(f"  ❌ Unexpected PermissionError on safe tool: {e}")

    # Try a destructive tool (should fail at VERIFIED)
    try:
        trusted_call_tool("codomyrmex.run_command", command="echo test")
        print_warning("  ⚠️ destructive tool succeeded without TRUSTED — unexpected")
    except PermissionError:
        print_success("  ✅ trusted_call_tool('run_command') — BLOCKED (requires TRUSTED)")

    # Trust all — promotes everything
    trust_all()
    print_success("  All tools promoted to TRUSTED")

    # Now destructive should work
    try:
        trusted_call_tool("codomyrmex.list_modules")
        print_success("  ✅ trusted_call_tool('list_modules') — PASSED at TRUSTED")
    except Exception as e:
        print_error(f"  ❌ Unexpected error at TRUSTED: {e}")

    return {"verified_promoted": len(promoted), "trust_enforcement": "working"}


def pattern_dynamic() -> dict:
    """Dynamic module proxy tool calls."""
    _header("Pattern 3: Dynamic Module Proxy")

    # List functions in a module
    print_info("  Listing functions in agents.pai module:")
    try:
        result = call_tool("codomyrmex.list_module_functions", module="agents.pai")
        functions = result.get("functions", []) if isinstance(result, dict) else []
        for fn in functions[:8]:
            name = fn.get("name", str(fn)) if isinstance(fn, dict) else str(fn)
            print(f"    • {name}")
        if len(functions) > 8:
            print(f"    ... and {len(functions) - 8} more")
    except Exception as e:
        print_warning(f"  Could not list functions: {e}")
        functions = []

    # Get module readme
    print_info("\n  Getting module README for agents.pai:")
    try:
        result = call_tool("codomyrmex.get_module_readme", module="agents.pai")
        content = result.get("content", "") if isinstance(result, dict) else ""
        lines = content.split("\n")[:5] if content else []
        for line in lines:
            print(f"    {line}")
        if len(content.split("\n")) > 5:
            print(f"    ... ({len(content)} chars total)")
    except Exception as e:
        print_warning(f"  Could not get readme: {e}")

    return {"functions_found": len(functions)}


def pattern_errors() -> dict:
    """Error handling patterns."""
    _header("Pattern 4: Error Handling")

    errors_caught = 0

    # Unknown tool
    print_info("  Calling nonexistent tool:")
    try:
        call_tool("nonexistent.tool.name")
        print_warning("  ⚠️ No error raised — unexpected")
    except (KeyError, Exception) as e:
        print_success(f"  ✅ Caught {type(e).__name__}: {str(e)[:60]}")
        errors_caught += 1

    # Invalid module
    print_info("  Calling tool with nonexistent module:")
    try:
        result = call_tool("codomyrmex.module_info", module_name="nonexistent_xyz")
        status = result.get("status", "") if isinstance(result, dict) else ""
        if "error" in str(result).lower() or status == "error":
            print_success(f"  ✅ Got error in result: {status}")
            errors_caught += 1
        else:
            print_info(f"  ℹ️ Result: {str(result)[:80]}")
    except Exception as e:
        print_success(f"  ✅ Caught {type(e).__name__}: {str(e)[:60]}")
        errors_caught += 1

    # Trust-gated without trust
    print_info("  Calling destructive tool without trust:")
    reset_trust()
    try:
        trusted_call_tool("codomyrmex.write_file", path="/tmp/test.txt", content="test")
        print_warning("  ⚠️ No PermissionError raised — unexpected")
    except PermissionError:
        print_success("  ✅ PermissionError raised correctly")
        errors_caught += 1

    print(f"\n  Errors correctly caught: {errors_caught}/3")
    return {"errors_caught": errors_caught, "expected": 3}


def main() -> int:
    args = parse_args()
    setup_logging()

    results: dict = {}
    fns = {
        "direct": pattern_direct,
        "trusted": pattern_trusted,
        "dynamic": pattern_dynamic,
        "errors": pattern_errors,
    }

    try:
        if args.pattern:
            results[args.pattern] = fns[args.pattern]()
        else:
            for name, fn in fns.items():
                results[name] = fn()
    finally:
        # Always reset trust state
        try:
            reset_trust()
            print_info("\n  Trust state reset on exit.")
        except Exception:
            pass

    if args.json_output:
        print("\n" + json.dumps(results, indent=2, default=str))

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
