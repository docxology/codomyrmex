"""Z3 Formal Verifier bridge.

This module provides an abstraction over the Z3 SMT solver for mathematically
proving state invariants and constraints directly with Z3 native objects,
offering a more robust proving layer than string-based evaluation constraint solvers.
"""

from typing import Any, Optional

import z3


class Z3Verifier:
    """A bridge for Z3-based formal verification and invariant proving.

    This class works directly with Z3 AST nodes (e.g., `z3.Int`, `z3.Bool`)
    to verify satisfiability and prove theorems.
    """

    def __init__(self) -> None:
        """Initialize the Z3 verifier and its underlying solver."""
        self.solver = z3.Solver()

    def add_constraint(self, constraint: Any) -> None:
        """Add a constraint to the solver.

        Args:
            constraint: A Z3 boolean expression.
        """
        self.solver.add(constraint)

    def check_sat(self) -> str:
        """Check the satisfiability of the current constraints.

        Returns:
            "sat" if satisfiable, "unsat" if unsatisfiable, "unknown" otherwise.
        """
        result = self.solver.check()
        if result == z3.sat:
            return "sat"
        if result == z3.unsat:
            return "unsat"
        return "unknown"

    def get_model(self) -> Optional[z3.ModelRef]:
        """Get the model (satisfying assignment) if the constraints are sat.

        Returns:
            A Z3 model if satisfiable, None otherwise.
        """
        if self.solver.check() == z3.sat:
            return self.solver.model()
        return None

    def prove_invariant(self, current_state_constraints: list[Any], invariant: Any) -> bool:
        """Prove that an invariant holds given the current state constraints.

        This is done by showing that the current state AND the negation of the
        invariant is unsatisfiable.

        Args:
            current_state_constraints: List of Z3 boolean expressions representing the state.
            invariant: A Z3 boolean expression to prove.

        Returns:
            True if the invariant is mathematically proven, False otherwise.
        """
        temp_solver = z3.Solver()
        for c in current_state_constraints:
            temp_solver.add(c)

        # Add the negation of the invariant. If the negation is unsat,
        # the invariant must be true.
        temp_solver.add(z3.Not(invariant))

        return temp_solver.check() == z3.unsat
