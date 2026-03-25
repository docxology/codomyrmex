"""Unit tests for the Z3 Formal Verifier bridge.

Zero-Mock Policy: These tests use the real `z3` dependency to concretely
evaluate and prove theorems natively.
"""

import pytest

z3 = pytest.importorskip(
    "z3",
    reason="Z3 bridge tests require z3-solver (uv sync --extra formal_verification)",
)

from codomyrmex.formal_verification.z3_bridge import Z3Verifier


@pytest.mark.unit
def test_z3_verifier_sat():
    """Test that satisfiable constraints return 'sat'."""
    verifier = Z3Verifier()
    x = z3.Int("x")
    verifier.add_constraint(x > 5)
    assert verifier.check_sat() == "sat"


@pytest.mark.unit
def test_z3_verifier_unsat():
    """Test that unsatisfiable constraints return 'unsat'."""
    verifier = Z3Verifier()
    y = z3.Int("y")
    verifier.add_constraint(y > 5)
    verifier.add_constraint(y < 2)
    assert verifier.check_sat() == "unsat"


@pytest.mark.unit
def test_z3_verifier_model():
    """Test retrieving a satisfying model."""
    verifier = Z3Verifier()
    z = z3.Int("z")
    verifier.add_constraint(z == 42)

    assert verifier.check_sat() == "sat"
    model = verifier.get_model()
    assert model is not None
    assert model[z].as_long() == 42


@pytest.mark.unit
def test_prove_invariant():
    """Test mathematically proving an invariant.

    Theorem: If a > 0 and b > 0, then a + b > 0.
    """
    verifier = Z3Verifier()

    a = z3.Int("a")
    b = z3.Int("b")

    current_state = [a > 0, b > 0]
    invariant = (a + b) > 0

    is_proven = verifier.prove_invariant(current_state, invariant)
    assert is_proven is True


@pytest.mark.unit
def test_prove_invariant_fails():
    """Test proving an invalid invariant fails."""
    verifier = Z3Verifier()

    a = z3.Int("a")
    b = z3.Int("b")

    current_state = [a > 0, b > 0]
    invalid_invariant = (a + b) < 0

    # Cannot prove that a+b < 0 if a>0, b>0
    is_proven = verifier.prove_invariant(current_state, invalid_invariant)
    assert is_proven is False
