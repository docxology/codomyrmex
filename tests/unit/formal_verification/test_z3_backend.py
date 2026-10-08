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


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.parametrize(
    "item",
    [
        "z3.os.system('echo pwned')",
        "z3.sys.modules",
        "z3.builtins.eval('1')",
        "z3.ctypes.memmove",
        "z3.importlib_resources",
        "z3.z3core",
    ],
)
def test_z3_backend_blocks_modules_reachable_from_z3(item, tmp_path):
    """Regression: ``z3.os.system(...)`` ran shell commands from a model item."""
    marker = tmp_path / "pwned"
    backend = Z3Backend()
    backend.add_item(item.replace("echo pwned", f"touch {marker}"))

    with pytest.raises(ModelBuildError, match="forbidden"):
        backend.solve_model()
    assert not marker.exists()


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.parametrize(
    "item",
    [
        "z3.string_at(0)",
        "z3.cast(0, z3.c_char_p)",
        "z3.CFUNCTYPE(None)",
        "z3.create_string_buffer(8)",
    ],
)
def test_z3_backend_blocks_ctypes_helpers_reexported_by_z3(item):
    """z3 re-exports ctypes functions that read and execute raw memory."""
    backend = Z3Backend()
    backend.add_item(item)

    with pytest.raises(ModelBuildError, match="forbidden"):
        backend.solve_model()


@pytest.mark.unit
def test_z3_backend_allows_z3_api_through_the_module():
    """The z3 API itself stays reachable as ``z3.<name>``."""
    backend = Z3Backend()
    backend.add_item("x = z3.Int('x')")
    backend.add_item("solver.add(z3.And(x > 1, x < 3))")

    result = backend.solve_model()
    assert result.status.value == "sat"
    assert result.model == {"x": 2} or str(result.model.get("x")) == "2"
