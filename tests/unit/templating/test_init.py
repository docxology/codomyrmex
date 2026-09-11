"""Tests for templating __init__.py."""

import sys
from importlib import reload

import pytest

from codomyrmex.templating import get_default_engine
from codomyrmex.templating.engines.template_engine import TemplateEngine


@pytest.mark.unit
class TestGetDefaultEngine:
    """Tests for get_default_engine function."""

    @pytest.fixture(autouse=True)
    def reset_default_engine(self):
        """Reset the global _default_engine before and after each test."""
        import codomyrmex.templating as t

        original = t._default_engine
        t._default_engine = None
        yield
        t._default_engine = original

    def test_get_default_engine_jinja2(self):
        """Test get_default_engine returns Jinja2 engine by default."""
        engine = get_default_engine()
        assert isinstance(engine, TemplateEngine)
        assert engine.engine == "jinja2"

    def test_get_default_engine_caching(self):
        """Test get_default_engine caches the engine instance."""
        engine1 = get_default_engine()
        engine2 = get_default_engine()
        assert engine1 is engine2

    def test_get_default_engine_different_type(self):
        """Test get_default_engine with different engine type creates new instance."""
        engine1 = get_default_engine("jinja2")
        # Ensure we reset for the different type request if needed or just get a new one
        engine2 = get_default_engine("mako")
        assert engine1 is not engine2
        assert engine2.engine == "mako"

    def test_get_default_engine_import_error(self, monkeypatch):
        """Test get_default_engine raises ImportError if TemplateEngine is not available."""
        import codomyrmex.templating as t

        # Mock TemplateEngine to be None to simulate import failure
        monkeypatch.setattr(t, "TemplateEngine", None)

        with pytest.raises(ImportError, match="TemplateEngine not available"):
            get_default_engine()
