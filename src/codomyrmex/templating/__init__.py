"""
Templating module for Codomyrmex.

This module provides template engine support (Jinja2, Mako) for code generation,
documentation templates, and dynamic content.
"""

from codomyrmex.exceptions import CodomyrmexError

from .template_engine import Template, TemplateEngine
from .template_manager import TemplateManager

__all__ = [
    "TemplateEngine",
    "TemplateManager",
    "Template",
    "render",
    "get_template_engine",
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

