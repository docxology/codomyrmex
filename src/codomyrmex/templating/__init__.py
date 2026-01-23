"""
Templating module for Codomyrmex.

This module provides template engine support (Jinja2, Mako) for code generation,
documentation templates, and dynamic content.
"""

from codomyrmex.exceptions import CodomyrmexError

from .engines.template_engine import Template, TemplateEngine
from .loaders.template_manager import TemplateManager

# Submodule exports
from . import engines
from . import loaders
from . import filters
from . import context

__all__ = [
    "TemplateEngine",
    "TemplateManager",
    "Template",
    "render",
    "get_template_engine",
    "engines",
    "loaders",
    "filters",
    "context",
]

__version__ = "0.1.0"


class TemplatingError(CodomyrmexError):
    """Raised when templating operations fail."""

    pass


def render(template: str, context: dict, engine: str = "jinja2") -> str:
    """Render a template string with context."""
    engine_obj = TemplateEngine(engine=engine)
    return engine_obj.render(template, context)


def get_template_engine(engine: str = "jinja2") -> TemplateEngine:
    """Get a template engine instance."""
    return TemplateEngine(engine=engine)
