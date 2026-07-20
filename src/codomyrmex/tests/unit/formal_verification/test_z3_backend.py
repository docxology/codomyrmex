import pytest

z3 = pytest.importorskip(
    "z3",
    reason="Z3 backend tests require z3-solver",
)

from codomyrmex.formal_verification.backends.z3_backend import Z3Backend
from codomyrmex.formal_verification.exceptions import ModelBuildError


@pytest.mark.unit
def test_z3_backend_safe_eval_valid():
    """Test that safe_eval successfully parses and executes typical z3 setup."""
    backend = Z3Backend()
    backend.add_item("x = Int('x')")
    backend.add_item("y = Int('y')")
    backend.add_item("solver.add(x > 5)")
    backend.add_item("solver.add(y < 10)")
    backend.add_item("solver.add(x + y == 12)")

    result = backend.solve_model()
    assert result.status.value == "sat"
    assert result.model is not None
    assert "x" in result.model
    assert "y" in result.model


@pytest.mark.unit
def test_z3_backend_safe_eval_blocks_malicious():
    """Test that safe_eval blocks arbitrary python execution like imports."""
    backend = Z3Backend()
    backend.add_item("import os; os.system('echo pwned')")

    with pytest.raises(ModelBuildError) as exc_info:
        backend.solve_model()

    assert "Unsupported statement type" in str(exc_info.value)


@pytest.mark.unit
def test_z3_backend_safe_eval_blocks_private_access():
    """Test that safe_eval blocks access to private attributes."""
    backend = Z3Backend()
    backend.add_item("solver._items")

    with pytest.raises(ModelBuildError) as exc_info:
        backend.solve_model()

    assert "Access to private attributes is forbidden" in str(exc_info.value)
