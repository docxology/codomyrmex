"""High-level constraint solver interface.

Provides ConstraintSolver as the primary API for building and solving
constraint models. Wraps backend implementations with a user-friendly
interface modeled after szeider/mcp-solver's interaction pattern.
"""

from __future__ import annotations

from .backends.base import SolverBackend, SolverResult, SolverStatus
from .exceptions import BackendNotAvailableError


class ConstraintSolver:
    """Unified constraint solver wrapping pluggable backends.

    Default backend is Z3. The solver exposes the mcp-solver 6-tool
    interface plus convenience methods for common constraint patterns.

    Example::

        solver = ConstraintSolver()
        solver.add_item("x = Int('x')")
        solver.add_item("y = Int('y')")
        solver.add_item("solver.add(x + y == 10)")
        solver.add_item("solver.add(x > 0)")
        solver.add_item("solver.add(y > 0)")
        result = solver.solve()
        print(result.model)  # e.g. {'x': '5', 'y': '5'}
    """

    def __init__(self, backend: str = "z3") -> None:
        """Initialize solver with the specified backend.

        Args:
            backend: Backend name. Currently supports "z3".

        Raises:
            BackendNotAvailableError: If the backend is not installed.
        """
        self._backend = self._create_backend(backend)

    @staticmethod
    def _create_backend(name: str) -> SolverBackend:
        """Execute  Create Backend operations natively."""
        if name == "z3":
            try:
                from .backends.z3_backend import Z3Backend
                return Z3Backend()
            except (ImportError, BackendNotAvailableError) as exc:
                raise BackendNotAvailableError(
                    "z3-solver not installed. Install with: pip install z3-solver"
                ) from exc
        raise BackendNotAvailableError(f"Unknown backend: {name!r}")

    @property
    def backend_name(self) -> str:
        """Execute Backend Name operations natively."""
        return self._backend.backend_name()

    # --- mcp-solver 6-tool interface ---

    def clear_model(self) -> None:
        """Remove all items from the model."""
        self._backend.clear_model()

    def add_item(self, item: str, index: int | None = None) -> int:
        """Add a constraint or declaration to the model.

        Args:
            item: Z3 Python expression as a string.
            index: Optional insertion index. Appends if None.

        Returns:
            Index where the item was placed.
        """
        return self._backend.add_item(item, index)

    def delete_item(self, index: int) -> str:
        """Delete item at index, returning it."""
        return self._backend.delete_item(index)

    def replace_item(self, index: int, new_item: str) -> str:
        """Replace item at index, returning the old item."""
        return self._backend.replace_item(index, new_item)

    def get_model(self) -> list[tuple[int, str]]:
        """Return all items as (index, content) pairs."""
        return self._backend.get_model()

    def solve(self, timeout_ms: int = 30000) -> SolverResult:
        """Solve the current model.

        Args:
            timeout_ms: Maximum time in milliseconds.

        Returns:
            SolverResult with status, model, and statistics.
        """
        return self._backend.solve_model(timeout_ms)

    # --- Convenience methods ---

    def add_constraints(self, *items: str) -> list[int]:
        """Add multiple items at once."""
        return [self.add_item(item) for item in items]

    def item_count(self) -> int:
        """Return number of items in the model."""
        return len(self.get_model())

    def is_satisfiable(self, timeout_ms: int = 30000) -> bool | None:
        """Quick check: is the model satisfiable?

        Returns True/False, or None if unknown/timeout.
        """
        result = self.solve(timeout_ms)
        if result.status == SolverStatus.SAT:
            return True
        if result.status == SolverStatus.UNSAT:
            return False
        return None
