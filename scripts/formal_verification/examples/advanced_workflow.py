#!/usr/bin/env python3
"""
Advanced formal_verification Workflow

Demonstrates Z3 constraint solving, ISC verification, and MCP tool usage.
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error


def demo_basic_solving():
    """Demo 1: Basic constraint satisfaction."""
    print_info("Demo 1: Basic Constraint Satisfaction")
    from codomyrmex.formal_verification import ConstraintSolver

    solver = ConstraintSolver()
    solver.add_item("x = Int('x')")
    solver.add_item("y = Int('y')")
    solver.add_item("solver.add(x + y == 10)")
    solver.add_item("solver.add(x > 0)")
    solver.add_item("solver.add(y > 0)")
    solver.add_item("solver.add(x != y)")

    result = solver.solve()
    print_info(f"  Status: {result.status.value}")
    print_info(f"  Model: {result.model}")
    assert result.is_sat, "Expected SAT"
    print_success("  Basic solving works!")


def demo_scheduling():
    """Demo 2: Simple scheduling constraint problem."""
    print_info("Demo 2: Scheduling Constraint Problem")
    from codomyrmex.formal_verification import ConstraintSolver

    solver = ConstraintSolver()
    # Three tasks with start times, each takes 2 hours, non-overlapping
    solver.add_item("t1 = Int('t1')")
    solver.add_item("t2 = Int('t2')")
    solver.add_item("t3 = Int('t3')")
    # All start within 0-8 hour window
    for t in ["t1", "t2", "t3"]:
        solver.add_item(f"solver.add({t} >= 0)")
        solver.add_item(f"solver.add({t} <= 6)")  # max start = 6 so task ends by 8
    # Non-overlapping (each task takes 2 hours)
    solver.add_item("solver.add(Or(t1 + 2 <= t2, t2 + 2 <= t1))")
    solver.add_item("solver.add(Or(t1 + 2 <= t3, t3 + 2 <= t1))")
    solver.add_item("solver.add(Or(t2 + 2 <= t3, t3 + 2 <= t2))")

    result = solver.solve()
    print_info(f"  Status: {result.status.value}")
    print_info(f"  Schedule: {result.model}")
    assert result.is_sat, "Expected SAT"
    print_success("  Scheduling demo works!")


def demo_isc_consistency():
    """Demo 3: ISC criteria consistency check."""
    print_info("Demo 3: ISC Criteria Consistency Check")
    from codomyrmex.formal_verification import verify_criteria_consistency

    criteria = [
        {"id": "ISC-C1", "description": "Response time under 200ms"},
        {"id": "ISC-C2", "description": "Throughput at least 100 requests per second"},
        {"id": "ISC-C3", "description": "Error rate under 0.5 percent"},
        {"id": "ISC-C4", "description": "Code quality is maintainable"},  # non-numeric, skipped
    ]

    result = verify_criteria_consistency(criteria)
    print_info(f"  Consistent: {result.consistent}")
    print_info(f"  Analyzed: {result.criteria_analyzed}, Skipped: {result.criteria_skipped}")
    print_info(f"  Skipped reasons: {result.skipped_reasons}")
    if result.satisfying_assignment:
        print_info(f"  Example assignment: {result.satisfying_assignment}")
    print_success("  ISC consistency check works!")


def demo_conflict_detection():
    """Demo 4: Detecting conflicting ISC criteria."""
    print_info("Demo 4: ISC Conflict Detection")
    from codomyrmex.formal_verification import verify_criteria_consistency

    criteria = [
        {"id": "ISC-C1", "description": "Conflicting",
         "constraint": "x = Int('x')\nsolver.add(x > 100)"},
        {"id": "ISC-C2", "description": "Conflicting",
         "constraint": "solver.add(x < 50)"},
    ]

    result = verify_criteria_consistency(criteria)
    print_info(f"  Consistent: {result.consistent}")
    print_info(f"  Status: {result.solver_status}")
    assert result.consistent is False, "Expected inconsistency"
    print_success("  Conflict detection works!")


def demo_mcp_workflow():
    """Demo 5: Stateful MCP tool workflow."""
    print_info("Demo 5: MCP Tool Stateful Workflow")
    from codomyrmex.formal_verification import mcp_tools

    mcp_tools._solver = None  # Fresh start
    mcp_tools.clear_model()
    mcp_tools.add_item("x = Int('x')")
    mcp_tools.add_item("solver.add(x >= 1)")
    mcp_tools.add_item("solver.add(x <= 100)")

    model = mcp_tools.get_model()
    print_info(f"  Model has {model['item_count']} items")

    # Replace constraint to narrow range
    mcp_tools.replace_item(2, "solver.add(x <= 10)")

    result = mcp_tools.solve_model()
    print_info(f"  Status: {result['status']}")
    print_info(f"  Model: {result['model']}")
    assert result["satisfiable"], "Expected SAT"
    print_success("  MCP workflow works!")


def main():
    setup_logging()
    print_info("Running Advanced formal_verification Workflow...")
    print_info("=" * 60)

    try:
        import z3  # noqa: F401
    except ImportError:
        print_error("z3-solver not installed. Install with: pip install z3-solver")
        return 1

    demos = [
        demo_basic_solving,
        demo_scheduling,
        demo_isc_consistency,
        demo_conflict_detection,
        demo_mcp_workflow,
    ]

    for demo in demos:
        try:
            demo()
        except Exception as exc:
            print_error(f"  FAILED: {exc}")
            return 1
        print_info("")

    print_info("=" * 60)
    print_success("Advanced formal_verification Workflow completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
