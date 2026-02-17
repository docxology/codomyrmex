#!/usr/bin/env python3
"""
Z3 PAI Agent -- ISC Verification Example

Demonstrates how a PAI Algorithm agent uses Z3 constraint solving
to verify Ideal State Criteria consistency during OBSERVE phase.

Usage:
    python scripts/agents/z3_pai_example.py              # Full demo
    python scripts/agents/z3_pai_example.py --demo isc    # Single demo
    python scripts/agents/z3_pai_example.py --json        # JSON output
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error


DEMOS = ["isc", "conflict", "mcp"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Z3 PAI Agent -- ISC verification demos",
    )
    parser.add_argument(
        "--demo", "-d",
        choices=DEMOS,
        help="Run a single demo (default: all)",
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )
    return parser.parse_args()


# -- Demos ----------------------------------------------------------------


def demo_isc_verification() -> dict:
    """OBSERVE-phase integration: verify ISC criteria are mutually satisfiable."""
    print_info("Demo 1: ISC Criteria Consistency (OBSERVE phase)")
    from codomyrmex.formal_verification import verify_criteria_consistency

    # Realistic PAI ISC set -- performance SLA criteria
    criteria = [
        {"id": "ISC-C1", "description": "Response time under 200ms for API calls"},
        {"id": "ISC-C2", "description": "Throughput at least 100 requests per second"},
        {"id": "ISC-C3", "description": "Error rate under 0.5 percent"},
        {"id": "ISC-C4", "description": "Memory usage below 512 megabytes"},
        {"id": "ISC-C5", "description": "Code quality is maintainable"},  # qualitative -- skipped
    ]

    result = verify_criteria_consistency(criteria)
    print_info(f"  Consistent: {result.consistent}")
    print_info(f"  Analyzed: {result.criteria_analyzed}, Skipped: {result.criteria_skipped}")
    if result.satisfying_assignment:
        print_info(f"  Satisfying assignment: {result.satisfying_assignment}")
    if result.skipped_reasons:
        print_info(f"  Skipped: {result.skipped_reasons}")
    assert result.consistent, "Expected consistent ISC set"
    print_success("  ISC criteria are mutually satisfiable!")

    return {
        "demo": "isc_verification",
        "consistent": result.consistent,
        "analyzed": result.criteria_analyzed,
        "skipped": result.criteria_skipped,
        "assignment": result.satisfying_assignment,
    }


def demo_conflict_detection() -> dict:
    """Catch conflicting ISC before wasting tokens on BUILD/EXECUTE."""
    print_info("Demo 2: Conflict Detection (early token savings)")
    from codomyrmex.formal_verification import verify_criteria_consistency

    # Conflicting criteria: fast response + heavy computation
    criteria = [
        {"id": "ISC-C1", "description": "Response time under 50ms",
         "constraint": "response_time = Int('response_time')\nsolver.add(response_time < 50)"},
        {"id": "ISC-C2", "description": "Minimum 10 database joins per request",
         "constraint": "db_joins = Int('db_joins')\nsolver.add(db_joins >= 10)"},
        {"id": "ISC-C3", "description": "Each join adds at least 8ms latency",
         "constraint": "solver.add(response_time >= db_joins * 8)"},
    ]

    result = verify_criteria_consistency(criteria)
    print_info(f"  Consistent: {result.consistent}")
    print_info(f"  Status: {result.solver_status}")
    assert result.consistent is False, "Expected conflict detected"
    print_success("  Conflict caught! Agent can fix ISC before BUILD phase.")

    return {
        "demo": "conflict_detection",
        "consistent": result.consistent,
        "solver_status": result.solver_status,
    }


def demo_mcp_agent_workflow() -> dict:
    """Interactive model-building via MCP tools (Claude Code agent pattern)."""
    print_info("Demo 3: MCP Agent Workflow (interactive model building)")
    from codomyrmex.formal_verification import mcp_tools

    # Step 1: Fresh model
    mcp_tools._solver = None
    mcp_tools.clear_model()
    print_info("  [agent] clear_model()")

    # Step 2: Build incrementally
    mcp_tools.add_item("x = Int('x')")
    mcp_tools.add_item("y = Int('y')")
    mcp_tools.add_item("solver.add(x + y == 100)")
    mcp_tools.add_item("solver.add(x >= 0)")
    mcp_tools.add_item("solver.add(y >= 0)")
    print_info("  [agent] add_item() x5 -- built initial model")

    # Step 3: Check model state
    model = mcp_tools.get_model()
    print_info(f"  [agent] get_model() -- {model['item_count']} items")

    # Step 4: Solve
    result1 = mcp_tools.solve_model()
    print_info(f"  [agent] solve_model() -- {result1['status']}, model: {result1['model']}")
    assert result1["satisfiable"], "Expected SAT"

    # Step 5: Tighten constraint (agent refines ISC)
    mcp_tools.replace_item(2, "solver.add(x + y == 100)")
    mcp_tools.add_item("solver.add(x > 60)")
    print_info("  [agent] replace_item() + add_item() -- refined constraint")

    # Step 6: Re-solve with tighter model
    result2 = mcp_tools.solve_model()
    print_info(f"  [agent] solve_model() -- {result2['status']}, model: {result2['model']}")
    assert result2["satisfiable"], "Expected SAT after refinement"
    print_success("  MCP workflow complete -- incremental model building works!")

    return {
        "demo": "mcp_agent_workflow",
        "initial_solve": result1["status"],
        "refined_solve": result2["status"],
        "final_model": result2["model"],
    }


# -- Main ----------------------------------------------------------------


DEMO_FNS = {
    "isc": demo_isc_verification,
    "conflict": demo_conflict_detection,
    "mcp": demo_mcp_agent_workflow,
}


def main() -> int:
    setup_logging()
    args = parse_args()

    print_info("Z3 PAI Agent -- ISC Verification Example")
    print_info("=" * 55)

    # Z3 availability check
    try:
        import z3  # noqa: F401
    except ImportError:
        print_error("z3-solver not installed. Install with: pip install z3-solver")
        return 1

    results: dict = {}

    if args.demo:
        fn = DEMO_FNS[args.demo]
        results[args.demo] = fn()
    else:
        for name, fn in DEMO_FNS.items():
            try:
                results[name] = fn()
            except Exception as exc:
                print_error(f"  FAILED: {exc}")
                return 1
            print_info("")

    if args.json_output:
        print("\n" + json.dumps(results, indent=2, default=str))

    print_info("=" * 55)
    print_success("All demos passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
