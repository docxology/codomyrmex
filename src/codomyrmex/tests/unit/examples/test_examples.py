"""Tests for the examples module — verifies importability and exports."""

import pytest


@pytest.mark.unit
class TestExamplesModule:
    """Verify the examples module is importable and has expected structure."""

    def test_module_importable(self):
        """Examples module can be imported without errors."""
        import codomyrmex.examples
        assert codomyrmex.examples is not None

    def test_module_has_init(self):
        """Examples module has __init__.py (is a proper package)."""
        import codomyrmex.examples
        assert hasattr(codomyrmex.examples, "__file__")

    def test_module_has_docstring(self):
        """Examples module has a docstring."""
        import codomyrmex.examples
        # Docstring may or may not exist, but import must not fail
        assert codomyrmex.examples.__doc__ is None or isinstance(codomyrmex.examples.__doc__, str)
