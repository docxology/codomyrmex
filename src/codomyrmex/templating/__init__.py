"""
Templating module for Codomyrmex.

This module provides template engine support (Jinja2, Mako) for code generation,
documentation templates, and dynamic content.
"""

# Submodule exports - import first to make available
from . import engines
from . import filters
from . import context

# Try to import optional submodules
try:
    from . import loaders
except ImportError:
    pass

# Try to import from existing modules, but don't fail if they don't exist
try:
    from codomyrmex.exceptions import CodomyrmexError
except ImportError:
    CodomyrmexError = Exception

try:
    from .engines.template_engine import Template, TemplateEngine
except ImportError:
    Template = None
    TemplateEngine = None

try:
    from .loaders.template_manager import TemplateManager
except ImportError:
    TemplateManager = None

# Default engine instance for convenience functions
_default_engine = None

def get_default_engine(engine_type: str = "jinja2"):
    """Get or create default template engine instance."""
    global _default_engine
    if _default_engine is None or _default_engine.engine != engine_type:
        if TemplateEngine:
            _default_engine = TemplateEngine(engine=engine_type)
        else:
            raise ImportError("TemplateEngine not available")
    return _default_engine


def render(template: str, context: dict = None, engine: str = "jinja2") -> str:
    """
    Render a template string with context data.
    
    This is a convenience function that uses the default template engine.
    
    Args:
        template: Template string (e.g., "Hello {{ name }}!")
        context: Dictionary of data to pass to template
        engine: Template engine to use ('jinja2' or 'mako')
    
    Returns:
        Rendered string
    
    Example:
        >>> render("Hello {{ name }}!", {"name": "World"})
        'Hello World!'
    """
    if context is None:
        context = {}
    
    eng = get_default_engine(engine)
    return eng.render(template, context)


def render_file(path: str, context: dict = None, engine: str = "jinja2") -> str:
    """
    Load and render a template file.
    
    Args:
        path: Path to template file
        context: Dictionary of data to pass to template
        engine: Template engine to use ('jinja2' or 'mako')
    
    Returns:
        Rendered string
    """
    if context is None:
        context = {}
    
    eng = get_default_engine(engine)
    template = eng.load_template(path)
    return template.render(context)


__all__ = [
    "engines",
    "filters",
    "context",
    "render",
    "render_file",
    "get_default_engine",
]

if TemplateEngine:
    __all__.extend(["TemplateEngine", "Template"])
if TemplateManager:
    __all__.append("TemplateManager")

__version__ = "0.1.0"


class TemplatingError(CodomyrmexError):
    """Raised when templating operations fail."""
    pass

