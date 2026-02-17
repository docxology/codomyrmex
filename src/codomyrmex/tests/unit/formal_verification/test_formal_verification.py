"""Unit tests for the formal_verification module.

Tests cover solver creation, model manipulation, solving, error handling,
ISC verification bridge, backend abstraction, MCP tools, regex extraction,
edge cases, and CLI commands.
"""

import pytest

# Check if z3-solver is available
z3_available = True
try:
    import z3
except ImportError:
    z3_available = False

skip_no_z3 = pytest.mark.skipif(not z3_available, reason="z3-solver not installed")


@pytest.mark.unit
class TestConstraintSolver:
    """Tests for the ConstraintSolver high-level API."""

    @skip_no_z3
    def test_solver_creation(self):
        """Create solver with z3 backend."""
        from codomyrmex.formal_verification import ConstraintSolver
        solver = ConstraintSolver(backend="z3")
        assert solver.backend_name == "Z3 SMT Solver"

    @skip_no_z3
    def test_add_item_returns_index(self):
        """Add items and verify sequential indices."""
        from codomyrmex.formal_verification import ConstraintSolver
        solver = ConstraintSolver()
        idx = solver.add_item("x = Int('x')")
        assert idx == 0
        idx2 = solver.add_item("y = Int('y')")
        assert idx2 == 1

    @skip_no_z3
    def test_add_item_at_index(self):
        """Insert item at specific index."""
        from codomyrmex.formal_verification import ConstraintSolver
        solver = ConstraintSolver()
        solver.add_item("a = 1")
        solver.add_item("c = 3")
        solver.add_item("b = 2", index=1)
        model = solver.get_model()
        assert model[1][1] == "b = 2"

    @skip_no_z3
    def test_delete_item(self):
        """Delete item and verify removal."""
        from codomyrmex.formal_verification import ConstraintSolver
        solver = ConstraintSolver()
        solver.add_item("x = Int('x')")
        solver.add_item("y = Int('y')")
        removed = solver.delete_item(0)
        assert removed == "x = Int('x')"
        assert solver.item_count() == 1

    @skip_no_z3
    def test_replace_item(self):
        """Replace item and verify old value returned."""
        from codomyrmex.formal_verification import ConstraintSolver
        solver = ConstraintSolver()
        solver.add_item("old = 1")
        old = solver.replace_item(0, "new = 2")
        assert old == "old = 1"
        assert solver.get_model()[0][1] == "new = 2"

    @skip_no_z3
    def test_clear_model(self):
        """Clear model and verify empty."""
        from codomyrmex.formal_verification import ConstraintSolver
        solver = ConstraintSolver()
        solver.add_item("x = 1")
        solver.add_item("y = 2")
        solver.clear_model()
        assert solver.item_count() == 0

    @skip_no_z3
    def test_get_model(self):
        """Get model returns indexed tuples."""
        from codomyrmex.formal_verification import ConstraintSolver
        solver = ConstraintSolver()
        solver.add_item("x = Int('x')")
        solver.add_item("solver.add(x > 0)")
        model = solver.get_model()
        assert len(model) == 2
        assert model[0] == (0, "x = Int('x')")
        assert model[1] == (1, "solver.add(x > 0)")

    @skip_no_z3
    def test_solve_sat(self):
        """Solve satisfiable model."""
        from codomyrmex.formal_verification import ConstraintSolver, SolverStatus
        solver = ConstraintSolver()
        solver.add_item("x = Int('x')")
        solver.add_item("solver.add(x > 0)")
        solver.add_item("solver.add(x < 10)")
        result = solver.solve()
        assert result.status == SolverStatus.SAT
        assert result.is_sat
        assert "x" in result.model

    @skip_no_z3
    def test_solve_unsat(self):
        """Solve unsatisfiable model."""
        from codomyrmex.formal_verification import ConstraintSolver, SolverStatus
        solver = ConstraintSolver()
        solver.add_item("x = Int('x')")
        solver.add_item("solver.add(x > 10)")
        solver.add_item("solver.add(x < 5)")
        result = solver.solve()
        assert result.status == SolverStatus.UNSAT
        assert result.is_unsat
        assert result.model is None

    @skip_no_z3
    def test_is_satisfiable(self):
        """Quick satisfiability check returns True."""
        from codomyrmex.formal_verification import ConstraintSolver
        solver = ConstraintSolver()
        solver.add_item("x = Int('x')")
        solver.add_item("solver.add(x == 42)")
        assert solver.is_satisfiable() is True

    @skip_no_z3
    def test_is_unsatisfiable(self):
        """Quick satisfiability check returns False."""
        from codomyrmex.formal_verification import ConstraintSolver
        solver = ConstraintSolver()
        solver.add_item("x = Bool('x')")
        solver.add_item("solver.add(x == True)")
        solver.add_item("solver.add(x == False)")
        assert solver.is_satisfiable() is False

    def test_unknown_backend_raises(self):
        """Unknown backend raises BackendNotAvailableError."""
        from codomyrmex.formal_verification import ConstraintSolver, BackendNotAvailableError
        with pytest.raises(BackendNotAvailableError):
            ConstraintSolver(backend="nonexistent")

    @skip_no_z3
    def test_invalid_constraint_raises(self):
        """Invalid Python in constraint raises ModelBuildError."""
        from codomyrmex.formal_verification import ConstraintSolver
        from codomyrmex.formal_verification.exceptions import ModelBuildError
        solver = ConstraintSolver()
        solver.add_item("this is not valid python!!!")
        with pytest.raises(ModelBuildError):
            solver.solve()

    @skip_no_z3
    def test_delete_out_of_range_raises(self):
        """Delete from empty model raises ModelBuildError."""
        from codomyrmex.formal_verification import ConstraintSolver
        from codomyrmex.formal_verification.exceptions import ModelBuildError
        solver = ConstraintSolver()
        with pytest.raises(ModelBuildError):
            solver.delete_item(0)

    @skip_no_z3
    def test_add_constraints_batch(self):
        """Batch add returns correct indices."""
        from codomyrmex.formal_verification import ConstraintSolver
        solver = ConstraintSolver()
        indices = solver.add_constraints("a = 1", "b = 2", "c = 3")
        assert indices == [0, 1, 2]
        assert solver.item_count() == 3


@pytest.mark.unit
class TestISCVerification:
    """Tests for the PAI ISC verification bridge."""

    @skip_no_z3
    def test_consistent_criteria(self):
        """Consistent criteria return consistent=True."""
        from codomyrmex.formal_verification import verify_criteria_consistency
        result = verify_criteria_consistency([
            {"id": "ISC-C1", "description": "Response time under 200"},
            {"id": "ISC-C2", "description": "At least 10 concurrent users"},
        ])
        assert result.consistent is True
        assert result.criteria_analyzed == 2

    @skip_no_z3
    def test_inconsistent_criteria(self):
        """Independent variable criteria are satisfiable."""
        from codomyrmex.formal_verification import verify_criteria_consistency
        result = verify_criteria_consistency([
            {"id": "ISC-C1", "description": "Value under 5"},
            {"id": "ISC-C2", "description": "Value at least 10"},
        ])
        # Different variables (isc_c1 and isc_c2), so independent
        assert result.consistent is True

    @skip_no_z3
    def test_direct_constraint_override(self):
        """Direct Z3 constraints override description extraction."""
        from codomyrmex.formal_verification import verify_criteria_consistency
        result = verify_criteria_consistency([
            {"id": "ISC-C1", "description": "X constraint",
             "constraint": "x = Int('x')\nsolver.add(x > 10)"},
            {"id": "ISC-C2", "description": "X constraint",
             "constraint": "solver.add(x < 5)"},
        ])
        assert result.consistent is False

    @skip_no_z3
    def test_no_translatable_criteria(self):
        """Non-numeric criteria are skipped."""
        from codomyrmex.formal_verification import verify_criteria_consistency
        result = verify_criteria_consistency([
            {"id": "ISC-C1", "description": "Code is well-structured"},
            {"id": "ISC-C2", "description": "Tests pass reliably"},
        ])
        assert result.consistent is None
        assert result.criteria_skipped == 2

    @skip_no_z3
    def test_returns_result_never_raises(self):
        """Advisory behavior — never raises on UNSAT."""
        from codomyrmex.formal_verification import verify_criteria_consistency
        result = verify_criteria_consistency([
            {"id": "ISC-C1", "description": "impossible",
             "constraint": "x = Bool('x')\nsolver.add(x == True)\nsolver.add(x == False)"},
        ])
        assert result.consistent is False
        assert result.solver_status == "unsat"

    def test_graceful_without_z3(self):
        """ISCVerificationResult is always importable."""
        from codomyrmex.formal_verification.verify_isc import ISCVerificationResult
        assert ISCVerificationResult is not None


@pytest.mark.unit
class TestSolverBackendBase:
    """Tests for backend abstraction."""

    def test_solver_status_enum(self):
        """SolverStatus enum has correct values."""
        from codomyrmex.formal_verification import SolverStatus
        assert SolverStatus.SAT.value == "sat"
        assert SolverStatus.UNSAT.value == "unsat"
        assert SolverStatus.UNKNOWN.value == "unknown"

    def test_solver_result_properties(self):
        """SolverResult convenience properties work correctly."""
        from codomyrmex.formal_verification import SolverResult, SolverStatus
        sat_result = SolverResult(status=SolverStatus.SAT, model={"x": "5"})
        assert sat_result.is_sat
        assert not sat_result.is_unsat

        unsat_result = SolverResult(status=SolverStatus.UNSAT)
        assert not unsat_result.is_sat
        assert unsat_result.is_unsat

    def test_exceptions_hierarchy(self):
        """All exceptions inherit from SolverError."""
        from codomyrmex.formal_verification import (
            SolverError, SolverTimeoutError, ModelBuildError,
            BackendNotAvailableError, InvalidConstraintError,
        )
        assert issubclass(SolverTimeoutError, SolverError)
        assert issubclass(ModelBuildError, SolverError)
        assert issubclass(BackendNotAvailableError, SolverError)
        assert issubclass(InvalidConstraintError, SolverError)

    @skip_no_z3
    def test_z3_backend_name(self):
        """Z3 backend reports correct name."""
        from codomyrmex.formal_verification.backends.z3_backend import Z3Backend
        backend = Z3Backend()
        assert backend.backend_name() == "Z3 SMT Solver"


@pytest.mark.unit
class TestMCPTools:
    """Tests for MCP tool functions."""

    def setup_method(self):
        """Reset module-level solver before each test."""
        from codomyrmex.formal_verification import mcp_tools
        mcp_tools._solver = None

    @skip_no_z3
    def test_mcp_clear_model(self):
        """MCP clear_model returns ok status."""
        from codomyrmex.formal_verification import mcp_tools
        result = mcp_tools.clear_model()
        assert result["status"] == "ok"

    @skip_no_z3
    def test_mcp_add_and_get(self):
        """MCP add_item and get_model work together."""
        from codomyrmex.formal_verification import mcp_tools
        mcp_tools.clear_model()
        mcp_tools.add_item("x = Int('x')")
        result = mcp_tools.get_model()
        assert result["item_count"] == 1

    @skip_no_z3
    def test_mcp_solve(self):
        """MCP solve_model returns sat result."""
        from codomyrmex.formal_verification import mcp_tools
        mcp_tools.clear_model()
        mcp_tools.add_item("x = Int('x')")
        mcp_tools.add_item("solver.add(x == 42)")
        result = mcp_tools.solve_model()
        assert result["status"] == "sat"
        assert result["satisfiable"] is True


@pytest.mark.unit
class TestCLICommands:
    """Tests for CLI command functions."""

    def test_cli_status(self):
        """Status command returns z3 availability."""
        from codomyrmex.formal_verification import _cmd_status
        result = _cmd_status()
        assert "z3_available" in result
        assert "version" in result

    def test_cli_backends(self):
        """Backends command lists at least one backend."""
        from codomyrmex.formal_verification import _cmd_backends
        result = _cmd_backends()
        assert "backends" in result
        assert len(result["backends"]) >= 1


# ────────────────────────────────────────────────────────────
# NEW TEST CLASSES — Bug fix validation and coverage expansion
# ────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestModulePublicAPI:
    """Tests for module-level exports and metadata."""

    def test_all_exports_valid(self):
        """Every name in __all__ is importable."""
        import codomyrmex.formal_verification as fv
        for name in fv.__all__:
            assert hasattr(fv, name), f"{name} in __all__ but not importable"

    def test_version_string(self):
        """Module version is a non-empty string."""
        from codomyrmex.formal_verification import __version__
        assert isinstance(__version__, str)
        assert len(__version__) > 0


@pytest.mark.unit
class TestRegexPatterns:
    """Isolation tests for _extract_numeric_constraint patterns."""

    def _extract(self, cid, desc):
        from codomyrmex.formal_verification.verify_isc import _extract_numeric_constraint
        return _extract_numeric_constraint(cid, desc)

    def test_under_pattern(self):
        """'under X' extracts < constraint."""
        items = self._extract("ISC-C1", "Response time under 200ms")
        assert items is not None
        assert any("< 200" in i for i in items)

    def test_below_pattern(self):
        """'below X' extracts < constraint."""
        items = self._extract("ISC-C1", "Latency below 50")
        assert items is not None
        assert any("< 50" in i for i in items)

    def test_at_least_pattern(self):
        """'at least X' extracts >= constraint."""
        items = self._extract("ISC-C1", "At least 10 users")
        assert items is not None
        assert any(">= 10" in i for i in items)

    def test_at_most_pattern(self):
        """'at most X' extracts <= constraint."""
        items = self._extract("ISC-C1", "At most 100 connections")
        assert items is not None
        assert any("<= 100" in i for i in items)

    def test_between_pattern(self):
        """'between X and Y' extracts range constraints."""
        items = self._extract("ISC-C1", "Score between 0 and 100")
        assert items is not None
        assert any(">= 0" in i for i in items)
        assert any("<= 100" in i for i in items)

    def test_exactly_pattern(self):
        """'exactly X' extracts == constraint."""
        items = self._extract("ISC-C1", "Exactly 5 retries")
        assert items is not None
        assert any("== 5" in i for i in items)

    def test_float_uses_real(self):
        """Float value 0.5 produces Real() not Int()."""
        items = self._extract("ISC-C1", "Error rate under 0.5")
        assert items is not None
        assert any("Real(" in i for i in items)
        assert not any("Int(" in i for i in items)

    def test_int_uses_int(self):
        """Integer value produces Int()."""
        items = self._extract("ISC-C1", "Count under 10")
        assert items is not None
        assert any("Int(" in i for i in items)

    def test_no_match_returns_none(self):
        """Non-numeric description returns None."""
        items = self._extract("ISC-C1", "Code quality is excellent")
        assert items is None

    def test_var_sanitization(self):
        """Variable name sanitizes special characters."""
        items = self._extract("ISC-C1", "Value under 10")
        assert items is not None
        # Variable name should not contain hyphens
        var_line = items[0]
        var_name = var_line.split("=")[0].strip()
        assert "-" not in var_name


@pytest.mark.unit
class TestISCEdgeCases:
    """Edge case tests for ISC verification."""

    @skip_no_z3
    def test_empty_criteria_list(self):
        """Empty criteria list returns no_constraints status."""
        from codomyrmex.formal_verification import verify_criteria_consistency
        result = verify_criteria_consistency([])
        assert result.consistent is None
        assert result.criteria_analyzed == 0

    @skip_no_z3
    def test_skipped_reasons_populated(self):
        """Skipped criteria have reasons in skipped_reasons dict."""
        from codomyrmex.formal_verification import verify_criteria_consistency
        result = verify_criteria_consistency([
            {"id": "ISC-C1", "description": "Quality is good"},
        ])
        assert "ISC-C1" in result.skipped_reasons

    @skip_no_z3
    def test_mixed_analyzable_and_skipped(self):
        """Mix of numeric and non-numeric criteria counts correctly."""
        from codomyrmex.formal_verification import verify_criteria_consistency
        result = verify_criteria_consistency([
            {"id": "ISC-C1", "description": "Response under 200ms"},
            {"id": "ISC-C2", "description": "Code is clean"},
        ])
        assert result.criteria_analyzed == 1
        assert result.criteria_skipped == 1

    @skip_no_z3
    def test_idless_criteria_no_collision(self):
        """Criteria without IDs get unique keys in skipped_reasons."""
        from codomyrmex.formal_verification import verify_criteria_consistency
        result = verify_criteria_consistency([
            {"description": "Quality is good"},
            {"description": "Tests are stable"},
        ])
        assert result.criteria_skipped == 2
        # Must have 2 distinct keys, not collision at "unknown"
        assert len(result.skipped_reasons) == 2

    @skip_no_z3
    def test_multiline_constraint(self):
        """Direct constraint with newlines works correctly."""
        from codomyrmex.formal_verification import verify_criteria_consistency
        result = verify_criteria_consistency([
            {"id": "ISC-C1", "description": "multi",
             "constraint": "x = Int('x')\ny = Int('y')\nsolver.add(x + y == 10)\nsolver.add(x > 0)\nsolver.add(y > 0)"},
        ])
        assert result.consistent is True
        assert result.satisfying_assignment is not None


@pytest.mark.unit
class TestMCPToolsExtended:
    """Extended MCP tool tests covering error paths."""

    def setup_method(self):
        """Reset module-level solver before each test."""
        from codomyrmex.formal_verification import mcp_tools
        mcp_tools._solver = None

    @skip_no_z3
    def test_mcp_delete_item(self):
        """MCP delete_item removes and returns the item."""
        from codomyrmex.formal_verification import mcp_tools
        mcp_tools.clear_model()
        mcp_tools.add_item("x = Int('x')")
        result = mcp_tools.delete_item(0)
        assert result["status"] == "ok"
        assert result["removed_item"] == "x = Int('x')"

    @skip_no_z3
    def test_mcp_replace_item(self):
        """MCP replace_item swaps and returns old item."""
        from codomyrmex.formal_verification import mcp_tools
        mcp_tools.clear_model()
        mcp_tools.add_item("old = 1")
        result = mcp_tools.replace_item(0, "new = 2")
        assert result["status"] == "ok"
        assert result["old_item"] == "old = 1"

    @skip_no_z3
    def test_mcp_delete_out_of_range_error(self):
        """MCP delete_item on empty model returns error dict."""
        from codomyrmex.formal_verification import mcp_tools
        mcp_tools.clear_model()
        result = mcp_tools.delete_item(5)
        assert result["status"] == "error"
        assert "empty" in result["error"].lower() or "range" in result["error"].lower()

    @skip_no_z3
    def test_mcp_replace_out_of_range_error(self):
        """MCP replace_item on empty model returns error dict."""
        from codomyrmex.formal_verification import mcp_tools
        mcp_tools.clear_model()
        result = mcp_tools.replace_item(5, "new = 1")
        assert result["status"] == "error"
        assert "empty" in result["error"].lower() or "range" in result["error"].lower()

    @skip_no_z3
    def test_mcp_solve_unsat(self):
        """MCP solve_model returns unsat status."""
        from codomyrmex.formal_verification import mcp_tools
        mcp_tools.clear_model()
        mcp_tools.add_item("x = Int('x')")
        mcp_tools.add_item("solver.add(x > 10)")
        mcp_tools.add_item("solver.add(x < 5)")
        result = mcp_tools.solve_model()
        assert result["status"] == "unsat"
        assert result["satisfiable"] is False

    @skip_no_z3
    def test_mcp_solve_empty_model(self):
        """MCP solve_model on empty model returns sat (vacuously true)."""
        from codomyrmex.formal_verification import mcp_tools
        mcp_tools.clear_model()
        result = mcp_tools.solve_model()
        assert result["status"] == "sat"

    @skip_no_z3
    def test_mcp_add_with_explicit_index(self):
        """MCP add_item with explicit index inserts correctly."""
        from codomyrmex.formal_verification import mcp_tools
        mcp_tools.clear_model()
        mcp_tools.add_item("a = 1")
        mcp_tools.add_item("c = 3")
        result = mcp_tools.add_item("b = 2", index=1)
        assert result["index"] == 1
        model = mcp_tools.get_model()
        assert model["items"][1]["content"] == "b = 2"


@pytest.mark.unit
class TestCLICommandsExtended:
    """Extended CLI command tests."""

    @skip_no_z3
    def test_cmd_check_empty_expression(self):
        """Check with empty expression returns error."""
        from codomyrmex.formal_verification import _cmd_check
        result = _cmd_check(expression="")
        assert "error" in result

    @skip_no_z3
    def test_cmd_check_valid_expression(self):
        """Check with valid expression returns status."""
        from codomyrmex.formal_verification import _cmd_check
        result = _cmd_check(expression="x = Int('x')\nsolver.add(x == 42)")
        assert "status" in result

    @skip_no_z3
    def test_cmd_check_invalid_expression(self):
        """Check with invalid expression returns error."""
        from codomyrmex.formal_verification import _cmd_check
        result = _cmd_check(expression="this is not valid!!!")
        assert "error" in result


@pytest.mark.unit
class TestZ3BackendEmptyModel:
    """Tests for z3_backend empty model error messages (Fix 1)."""

    @skip_no_z3
    def test_delete_empty_model_clean_message(self):
        """Delete on empty model says 'model is empty', not '0--1'."""
        from codomyrmex.formal_verification.backends.z3_backend import Z3Backend
        from codomyrmex.formal_verification.exceptions import ModelBuildError
        backend = Z3Backend()
        with pytest.raises(ModelBuildError, match="model is empty"):
            backend.delete_item(0)

    @skip_no_z3
    def test_replace_empty_model_clean_message(self):
        """Replace on empty model says 'model is empty', not '0--1'."""
        from codomyrmex.formal_verification.backends.z3_backend import Z3Backend
        from codomyrmex.formal_verification.exceptions import ModelBuildError
        backend = Z3Backend()
        with pytest.raises(ModelBuildError, match="model is empty"):
            backend.replace_item(0, "new = 1")
