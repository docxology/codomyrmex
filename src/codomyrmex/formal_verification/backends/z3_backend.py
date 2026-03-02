"""Z3 SMT solver backend.

Wraps the z3-solver pip package to provide constraint solving over
booleans, integers, reals, bitvectors, and arrays with quantifier support.

References:
    - Z3 Prover: https://github.com/Z3Prover/z3
    - mcp-solver Z3 mode: https://github.com/szeider/mcp-solver
"""

from __future__ import annotations

from typing import Any

try:
    import z3
except ImportError:
    z3 = None  # type: ignore[assignment]

from codomyrmex.formal_verification.exceptions import (
    BackendNotAvailableError,
    ModelBuildError,
    SolverTimeoutError,
)

from .base import SolverBackend, SolverResult, SolverStatus


def _require_z3() -> None:
    """require Z3 ."""
    if z3 is None:
        raise BackendNotAvailableError(
            "z3-solver is not installed. Install with: pip install z3-solver"
        )


class Z3Backend(SolverBackend):
    """Z3 SMT solver backend implementing the mcp-solver 6-tool interface.

    Items are Z3 Python expressions stored as strings that get exec'd into
    a namespace containing z3 imports. This mirrors mcp-solver's approach
    where users build models incrementally via code strings.
    """

    def __init__(self) -> None:
        _require_z3()
        self._items: list[str] = []

    def clear_model(self) -> None:
        self._items.clear()

    def add_item(self, item: str, index: int | None = None) -> int:
        if index is None:
            self._items.append(item)
            return len(self._items) - 1
        self._items.insert(index, item)
        return index

    def delete_item(self, index: int) -> str:
        if not self._items:
            raise ModelBuildError(f"Cannot delete index {index}: model is empty")
        if not 0 <= index < len(self._items):
            raise ModelBuildError(f"Index {index} out of range (0-{len(self._items) - 1})")
        return self._items.pop(index)

    def replace_item(self, index: int, new_item: str) -> str:
        if not self._items:
            raise ModelBuildError(f"Cannot replace index {index}: model is empty")
        if not 0 <= index < len(self._items):
            raise ModelBuildError(f"Index {index} out of range (0-{len(self._items) - 1})")
        old = self._items[index]
        self._items[index] = new_item
        return old

    def get_model(self) -> list[tuple[int, str]]:
        return list(enumerate(self._items))

    def solve_model(self, timeout_ms: int = 30000) -> SolverResult:
        _require_z3()

        # Build a namespace with z3 imports for executing model items
        namespace: dict[str, Any] = {"z3": z3}
        # Pre-populate common z3 types for convenience
        for name in [
            "Int", "Real", "Bool", "BitVec", "Array", "IntSort", "RealSort",
            "BoolSort", "BitVecSort", "ArraySort", "Solver", "Optimize",
            "And", "Or", "Not", "Implies", "If", "Xor",
            "ForAll", "Exists", "Sum", "Product",
            "sat", "unsat", "unknown",
        ]:
            if hasattr(z3, name):
                namespace[name] = getattr(z3, name)

        # Execute all items to build the model
        solver = z3.Solver()
        solver.set("timeout", timeout_ms)
        namespace["solver"] = solver

        # Also provide an optimizer alias
        optimizer = z3.Optimize()
        optimizer.set("timeout", timeout_ms)
        namespace["optimizer"] = optimizer

        try:
            for idx, item in enumerate(self._items):
                try:
                    exec(item, namespace)  # noqa: S102
                except Exception as exc:
                    raise ModelBuildError(
                        f"Error executing item {idx}: {item!r}: {exc}"
                    ) from exc

            # Check if user added constraints to solver
            result = solver.check()

            if result == z3.sat:
                z3_model = solver.model()
                model_dict = {}
                for decl in z3_model.decls():
                    val = z3_model[decl]
                    model_dict[str(decl)] = str(val)
                return SolverResult(
                    status=SolverStatus.SAT,
                    model=model_dict,
                    statistics={"num_constraints": len(solver.assertions())},
                )
            elif result == z3.unsat:
                return SolverResult(
                    status=SolverStatus.UNSAT,
                    statistics={"num_constraints": len(solver.assertions())},
                )
            else:
                return SolverResult(
                    status=SolverStatus.UNKNOWN,
                    statistics={"num_constraints": len(solver.assertions())},
                )

        except ModelBuildError:
            raise
        except z3.Z3Exception as exc:
            if "timeout" in str(exc).lower():
                raise SolverTimeoutError(f"Z3 timeout after {timeout_ms}ms") from exc
            return SolverResult(
                status=SolverStatus.ERROR,
                error_message=str(exc),
            )

    def backend_name(self) -> str:
        return "Z3 SMT Solver"
