#!/usr/bin/env python3
"""
Orchestrator for formal_verification module.

This script demonstrates the full lifecycle of formal verification:
1. Basic constraint solving with Z3.
2. Incremental solving using push/pop.
3. ISC (Ideal State Criteria) consistency verification.
4. Conflict detection and unsat core extraction.
5. Optimization using Z3's Optimize solver.
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.formal_verification import ConstraintSolver, verify_criteria_consistency
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_section,
    print_success,
    setup_logging,
)


def run_basic_demo():
    print_section("Demo 1: Basic Constraint Solving")
    solver = ConstraintSolver()
    solver.add_constraints(
        "x = Int('x')",
        "y = Int('y')",
        "solver.add(x + y == 10)",
        "solver.add(x > 0)",
        "solver.add(y > 0)",
        "solver.add(x != y)",
    )
    result = solver.solve()
    print_info(f"Status: {result.status.value}")
    if result.is_sat:
        print_success(f"Satisfying assignment: {result.model}")
    else:
        print_error("Failed to find a satisfying assignment")


def run_incremental_demo():
    print_section("Demo 2: Incremental Solving with Push/Pop")
    solver = ConstraintSolver()
    solver.add_item("x = Int('x')")
    solver.add_item("solver.add(x > 0)")

    print_info("Checking x > 0...")
    result = solver.solve()
    print_info(f"Status: {result.status.value}")

    print_info("Pushing scope and adding x < 5...")
    solver.push()
    solver.add_item("solver.add(x < 5)")
    result = solver.solve()
    print_info(f"Status: {result.status.value}, Model: {result.model}")

    print_info("Pushing scope and adding x > 10 (causing UNSAT)...")
    solver.push()
    solver.add_item("solver.add(x > 10)")
    result = solver.solve()
    print_info(f"Status: {result.status.value}")

    print_info("Popping scope (back to x > 0 and x < 5)...")
    solver.pop()
    result = solver.solve()
    print_info(f"Status: {result.status.value}, Model: {result.model}")


def run_isc_demo():
    print_section("Demo 3: ISC Criteria Consistency")
    criteria = [
        {"id": "ISC-C1", "description": "Response time under 200ms"},
        {"id": "ISC-C2", "description": "Throughput at least 100 req/s"},
        {"id": "ISC-C3", "description": "Error rate below 0.1%"},
    ]
    print_info(f"Verifying {len(criteria)} criteria...")
    result = verify_criteria_consistency(criteria)
    print_info(f"Consistent: {result.consistent}")
    if result.consistent:
        print_success(f"Satisfying assignment: {result.satisfying_assignment}")

    print_info("\nAdding a conflicting criterion...")
    criteria.append({"id": "ISC-C4", "description": "Response time above 500ms"})
    result = verify_criteria_consistency(criteria)
    print_info(f"Consistent: {result.consistent}")
    if not result.consistent:
        print_error(f"Conflict detected between: {result.conflicts}")


def run_optimization_demo():
    print_section("Demo 4: Optimization")
    solver = ConstraintSolver()
    solver.add_constraints(
        "x = Int('x')",
        "y = Int('y')",
        "optimizer.add(x + y == 10)",
        "optimizer.add(x >= 0)",
        "optimizer.add(y >= 0)",
        "optimizer.maximize(x)",
    )
    result = solver.solve()
    print_info(f"Status: {result.status.value}")
    print_info(f"Engine used: {result.statistics.get('engine')}")
    if result.is_sat:
        print_success(f"Optimized model: {result.model}")
        # x should be 10 if we maximized it
        assert int(result.model["x"]) == 10


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "formal_verification"
        / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print(f"Loaded config from {config_path.name}")

    setup_logging()
    print_section("Codomyrmex Formal Verification Orchestrator", separator="=")

    try:
        import z3  # noqa: F401
    except ImportError:
        print_error("z3-solver not installed. Cannot run demos.")
        return 1

    run_basic_demo()
    run_incremental_demo()
    run_isc_demo()
    run_optimization_demo()

    print_section("Demos completed successfully", separator="=")
    return 0


if __name__ == "__main__":
    sys.exit(main())
