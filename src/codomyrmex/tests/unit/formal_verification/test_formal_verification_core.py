"""Zero-mock tests for formal_verification module core components.

Covers:
- SolverStatus enum: all five values
- SolverResult: is_sat, is_unsat, field defaults, statistics dict
- Exception hierarchy: SolverError, BackendNotAvailableError, ModelBuildError, etc.
- ConstraintSolver: unknown backend raises, clear_model, add_item, delete_item,
  replace_item, get_model, item_count, add_constraints, is_satisfiable, push, pop
- MCP tools: clear_model, add_item, get_model, solve_model, delete_item,
  replace_item, push, pop (all guarded by Z3 skip)

Zero-Mock Policy: no unittest.mock, MagicMock, monkeypatch, or pytest-mock.
Z3-dependent tests are guarded with module-level skipif.
"""

from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# Z3 availability guard — module-level, single check
# ---------------------------------------------------------------------------
_HAS_Z3 = False
try:
    import z3
    _HAS_Z3 = True
except ImportError:
    pass

skip_no_z3 = pytest.mark.skipif(not _HAS_Z3, reason="z3-solver not installed")


# ===========================================================================
# SolverStatus enum
# ===========================================================================


@pytest.mark.unit
class TestSolverStatusEnum:
    """SolverStatus enum coverage — no Z3 required."""

    def _status(self):
        from codomyrmex.formal_verification.backends.base import SolverStatus
        return SolverStatus

    def test_sat_value(self):
        assert self._status().SAT.value == "sat"

    def test_unsat_value(self):
        assert self._status().UNSAT.value == "unsat"

    def test_unknown_value(self):
        assert self._status().UNKNOWN.value == "unknown"

    def test_timeout_value(self):
        assert self._status().TIMEOUT.value == "timeout"

    def test_error_value(self):
        assert self._status().ERROR.value == "error"

    def test_five_members(self):
        assert len(list(self._status())) == 5

    def test_members_are_distinct(self):
        s = self._status()
        values = {s.SAT, s.UNSAT, s.UNKNOWN, s.TIMEOUT, s.ERROR}
        assert len(values) == 5


# ===========================================================================
# SolverResult dataclass
# ===========================================================================


@pytest.mark.unit
class TestSolverResultCore:
    """SolverResult dataclass — no Z3 required."""

    def _make(self, status_str: str = "sat", model=None, error=None):
        from codomyrmex.formal_verification.backends.base import (
            SolverResult,
            SolverStatus,
        )
        status = SolverStatus(status_str)
        return SolverResult(status=status, model=model, error_message=error)

    def test_is_sat_true_for_sat(self):
        result = self._make("sat")
        assert result.is_sat is True

    def test_is_sat_false_for_unsat(self):
        result = self._make("unsat")
        assert result.is_sat is False

    def test_is_unsat_true_for_unsat(self):
        result = self._make("unsat")
        assert result.is_unsat is True

    def test_is_unsat_false_for_sat(self):
        result = self._make("sat")
        assert result.is_unsat is False

    def test_is_sat_false_for_timeout(self):
        result = self._make("timeout")
        assert result.is_sat is False

    def test_model_none_by_default(self):
        result = self._make("unknown")
        assert result.model is None

    def test_model_stored(self):
        result = self._make("sat", model={"x": 5})
        assert result.model == {"x": 5}

    def test_statistics_empty_dict_by_default(self):
        result = self._make("sat")
        assert result.statistics == {}

    def test_error_message_none_by_default(self):
        result = self._make("sat")
        assert result.error_message is None

    def test_error_message_stored(self):
        result = self._make("error", error="parse failure")
        assert result.error_message == "parse failure"

    def test_objective_value_none_by_default(self):
        result = self._make("sat")
        assert result.objective_value is None


# ===========================================================================
# Exception hierarchy
# ===========================================================================


@pytest.mark.unit
class TestFormalVerificationExceptions:
    """Exception class hierarchy — no Z3 required."""

    def test_solver_error_is_exception(self):
        from codomyrmex.formal_verification.exceptions import SolverError
        assert issubclass(SolverError, Exception)

    def test_solver_timeout_error_inherits_solver_error(self):
        from codomyrmex.formal_verification.exceptions import (
            SolverError,
            SolverTimeoutError,
        )
        assert issubclass(SolverTimeoutError, SolverError)

    def test_model_build_error_inherits_solver_error(self):
        from codomyrmex.formal_verification.exceptions import (
            ModelBuildError,
            SolverError,
        )
        assert issubclass(ModelBuildError, SolverError)

    def test_backend_not_available_inherits_solver_error(self):
        from codomyrmex.formal_verification.exceptions import (
            BackendNotAvailableError,
            SolverError,
        )
        assert issubclass(BackendNotAvailableError, SolverError)

    def test_invalid_constraint_error_inherits_solver_error(self):
        from codomyrmex.formal_verification.exceptions import (
            InvalidConstraintError,
            SolverError,
        )
        assert issubclass(InvalidConstraintError, SolverError)

    def test_unsatisfiable_error_inherits_solver_error(self):
        from codomyrmex.formal_verification.exceptions import (
            SolverError,
            UnsatisfiableError,
        )
        assert issubclass(UnsatisfiableError, SolverError)

    def test_backend_not_available_can_be_raised(self):
        from codomyrmex.formal_verification.exceptions import BackendNotAvailableError
        with pytest.raises(BackendNotAvailableError, match="z3"):
            raise BackendNotAvailableError("z3 missing")

    def test_model_build_error_can_be_raised(self):
        from codomyrmex.formal_verification.exceptions import ModelBuildError
        with pytest.raises(ModelBuildError):
            raise ModelBuildError("bad model")


# ===========================================================================
# ConstraintSolver — backend selection (no Z3 needed for error path)
# ===========================================================================


@pytest.mark.unit
class TestConstraintSolverBackend:
    """ConstraintSolver backend selection — mixed Z3/no-Z3."""

    def test_unknown_backend_raises_backend_not_available(self):
        from codomyrmex.formal_verification.exceptions import BackendNotAvailableError
        from codomyrmex.formal_verification.solver import ConstraintSolver

        with pytest.raises(BackendNotAvailableError, match="Unknown backend"):
            ConstraintSolver(backend="nonexistent_xyz")

    @skip_no_z3
    def test_z3_backend_name(self):
        from codomyrmex.formal_verification.solver import ConstraintSolver

        solver = ConstraintSolver(backend="z3")
        assert "Z3" in solver.backend_name


# ===========================================================================
# ConstraintSolver — model manipulation (Z3 required)
# ===========================================================================


@pytest.mark.unit
class TestConstraintSolverModelManipulation:
    """ConstraintSolver: clear_model, add_item, delete_item, replace_item, get_model."""

    @skip_no_z3
    def test_empty_model_on_creation(self):
        from codomyrmex.formal_verification.solver import ConstraintSolver

        solver = ConstraintSolver()
        assert solver.item_count() == 0

    @skip_no_z3
    def test_add_item_returns_index_zero(self):
        from codomyrmex.formal_verification.solver import ConstraintSolver

        solver = ConstraintSolver()
        idx = solver.add_item("x = Int('x')")
        assert idx == 0

    @skip_no_z3
    def test_add_multiple_items_returns_sequential_indices(self):
        from codomyrmex.formal_verification.solver import ConstraintSolver

        solver = ConstraintSolver()
        i0 = solver.add_item("x = Int('x')")
        i1 = solver.add_item("y = Int('y')")
        assert i0 == 0
        assert i1 == 1

    @skip_no_z3
    def test_item_count_after_adds(self):
        from codomyrmex.formal_verification.solver import ConstraintSolver

        solver = ConstraintSolver()
        solver.add_item("x = Int('x')")
        solver.add_item("y = Int('y')")
        assert solver.item_count() == 2

    @skip_no_z3
    def test_get_model_returns_list_of_tuples(self):
        from codomyrmex.formal_verification.solver import ConstraintSolver

        solver = ConstraintSolver()
        solver.add_item("x = Int('x')")
        items = solver.get_model()
        assert isinstance(items, list)
        assert len(items) == 1
        assert isinstance(items[0], tuple)

    @skip_no_z3
    def test_get_model_contains_content(self):
        from codomyrmex.formal_verification.solver import ConstraintSolver

        solver = ConstraintSolver()
        solver.add_item("x = Int('x')")
        items = solver.get_model()
        assert items[0][1] == "x = Int('x')"

    @skip_no_z3
    def test_clear_model_empties_items(self):
        from codomyrmex.formal_verification.solver import ConstraintSolver

        solver = ConstraintSolver()
        solver.add_item("x = Int('x')")
        solver.clear_model()
        assert solver.item_count() == 0

    @skip_no_z3
    def test_delete_item_removes_entry(self):
        from codomyrmex.formal_verification.solver import ConstraintSolver

        solver = ConstraintSolver()
        solver.add_item("x = Int('x')")
        solver.add_item("y = Int('y')")
        removed = solver.delete_item(0)
        assert "x = Int('x')" in removed
        assert solver.item_count() == 1

    @skip_no_z3
    def test_replace_item_changes_content(self):
        from codomyrmex.formal_verification.solver import ConstraintSolver

        solver = ConstraintSolver()
        solver.add_item("x = Int('x')")
        old = solver.replace_item(0, "z = Int('z')")
        assert "x = Int('x')" in old
        items = solver.get_model()
        assert "z = Int('z')" in items[0][1]

    @skip_no_z3
    def test_add_constraints_returns_list_of_indices(self):
        from codomyrmex.formal_verification.solver import ConstraintSolver

        solver = ConstraintSolver()
        indices = solver.add_constraints("x = Int('x')", "y = Int('y')")
        assert indices == [0, 1]


# ===========================================================================
# ConstraintSolver — solving (Z3 required)
# ===========================================================================


@pytest.mark.unit
class TestConstraintSolverSolving:
    """ConstraintSolver: solve, is_satisfiable, push/pop."""

    @skip_no_z3
    def test_sat_simple_model(self):
        from codomyrmex.formal_verification.backends.base import SolverStatus
        from codomyrmex.formal_verification.solver import ConstraintSolver

        solver = ConstraintSolver()
        solver.add_item("x = Int('x')")
        solver.add_item("solver.add(x > 0)")
        result = solver.solve()
        assert result.status == SolverStatus.SAT

    @skip_no_z3
    def test_sat_result_has_model(self):
        from codomyrmex.formal_verification.solver import ConstraintSolver

        solver = ConstraintSolver()
        solver.add_item("x = Int('x')")
        solver.add_item("solver.add(x == 42)")
        result = solver.solve()
        assert result.model is not None
        assert isinstance(result.model, dict)

    @skip_no_z3
    def test_unsat_simple_model(self):
        from codomyrmex.formal_verification.backends.base import SolverStatus
        from codomyrmex.formal_verification.solver import ConstraintSolver

        solver = ConstraintSolver()
        solver.add_item("x = Int('x')")
        solver.add_item("solver.add(x > 10)")
        solver.add_item("solver.add(x < 5)")
        result = solver.solve()
        assert result.status == SolverStatus.UNSAT

    @skip_no_z3
    def test_is_satisfiable_true_for_sat(self):
        from codomyrmex.formal_verification.solver import ConstraintSolver

        solver = ConstraintSolver()
        solver.add_item("x = Bool('x')")
        assert solver.is_satisfiable() is True

    @skip_no_z3
    def test_is_satisfiable_false_for_unsat(self):
        from codomyrmex.formal_verification.solver import ConstraintSolver

        solver = ConstraintSolver()
        solver.add_item("x = Bool('x')")
        solver.add_item("solver.add(x == True)")
        solver.add_item("solver.add(x == False)")
        assert solver.is_satisfiable() is False

    @skip_no_z3
    def test_push_pop_scopes(self):
        from codomyrmex.formal_verification.backends.base import SolverStatus
        from codomyrmex.formal_verification.solver import ConstraintSolver

        solver = ConstraintSolver()
        solver.add_item("x = Int('x')")
        solver.add_item("solver.add(x > 0)")
        solver.push()
        solver.add_item("solver.add(x < 0)")
        # In this scope: x > 0 AND x < 0 → UNSAT
        result_unsat = solver.solve()
        assert result_unsat.status == SolverStatus.UNSAT
        solver.pop()
        # Back to outer scope: x > 0 only → SAT
        result_sat = solver.solve()
        assert result_sat.status == SolverStatus.SAT

    @skip_no_z3
    def test_empty_model_solve_is_sat(self):
        from codomyrmex.formal_verification.backends.base import SolverStatus
        from codomyrmex.formal_verification.solver import ConstraintSolver

        solver = ConstraintSolver()
        result = solver.solve()
        assert result.status == SolverStatus.SAT


# ===========================================================================
# MCP tools (Z3 required for most)
# ===========================================================================


@pytest.mark.unit
class TestFormalVerificationMcpTools:
    """MCP tool functions — reset module-level singleton per test class."""

    def setup_method(self):
        import codomyrmex.formal_verification.mcp_tools as mcp
        mcp._solver = None

    @skip_no_z3
    def test_clear_model_returns_success(self):
        from codomyrmex.formal_verification.mcp_tools import clear_model

        result = clear_model()
        assert result["status"] == "success"

    @skip_no_z3
    def test_add_item_returns_index(self):
        from codomyrmex.formal_verification.mcp_tools import add_item

        result = add_item("x = Int('x')")
        assert result["status"] == "success"
        assert "index" in result
        assert result["index"] == 0

    @skip_no_z3
    def test_add_item_stores_content(self):
        from codomyrmex.formal_verification.mcp_tools import add_item

        content = "y = Int('y')"
        result = add_item(content)
        assert result["item"] == content

    @skip_no_z3
    def test_get_model_returns_items(self):
        from codomyrmex.formal_verification.mcp_tools import add_item, get_model

        add_item("x = Int('x')")
        result = get_model()
        assert result["status"] == "success"
        assert result["item_count"] == 1
        assert len(result["items"]) == 1

    @skip_no_z3
    def test_get_model_empty(self):
        from codomyrmex.formal_verification.mcp_tools import get_model

        result = get_model()
        assert result["item_count"] == 0
        assert result["items"] == []

    @skip_no_z3
    def test_solve_model_sat(self):
        from codomyrmex.formal_verification.mcp_tools import add_item, solve_model

        add_item("x = Int('x')")
        add_item("solver.add(x > 0)")
        result = solve_model()
        assert result["status"] == "sat"
        assert result["satisfiable"] is True

    @skip_no_z3
    def test_solve_model_unsat(self):
        from codomyrmex.formal_verification.mcp_tools import add_item, solve_model

        add_item("x = Int('x')")
        add_item("solver.add(x > 10)")
        add_item("solver.add(x < 0)")
        result = solve_model()
        assert result["status"] == "unsat"
        assert result["satisfiable"] is False

    @skip_no_z3
    def test_delete_item_removes_entry(self):
        from codomyrmex.formal_verification.mcp_tools import (
            add_item,
            delete_item,
            get_model,
        )

        add_item("x = Int('x')")
        add_item("y = Int('y')")
        del_result = delete_item(0)
        assert del_result["status"] == "success"
        model_result = get_model()
        assert model_result["item_count"] == 1

    @skip_no_z3
    def test_replace_item_changes_content(self):
        from codomyrmex.formal_verification.mcp_tools import add_item, replace_item

        add_item("x = Int('x')")
        result = replace_item(0, "z = Int('z')")
        assert result["status"] == "success"
        assert result["new_item"] == "z = Int('z')"

    @skip_no_z3
    def test_push_and_pop_return_success(self):
        from codomyrmex.formal_verification.mcp_tools import pop, push

        push_result = push()
        assert push_result["status"] == "success"
        pop_result = pop(1)
        assert pop_result["status"] == "success"

    @skip_no_z3
    def test_solve_model_has_statistics_key(self):
        from codomyrmex.formal_verification.mcp_tools import solve_model

        result = solve_model()
        assert "statistics" in result

    @skip_no_z3
    def test_solve_model_has_model_key(self):
        from codomyrmex.formal_verification.mcp_tools import solve_model

        result = solve_model()
        assert "model" in result

    def test_clear_model_without_z3_returns_error_or_success(self):
        """When Z3 is absent the tool returns an error dict; when present, success."""
        from codomyrmex.formal_verification.mcp_tools import clear_model

        result = clear_model()
        assert "status" in result
        assert result["status"] in ("success", "error")
