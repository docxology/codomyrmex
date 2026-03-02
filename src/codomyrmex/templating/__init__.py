"""
Templating module for Codomyrmex.

This module provides template engine support (Jinja2, Mako) for code generation,
documentation templates, and dynamic content.
"""

logger = get_logger(__name__)

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

# Submodule exports - import first to make available
from . import context, engines, filters
from codomyrmex.logging_monitoring.core.logger_config import get_logger

# Try to import optional submodules
try:
    from . import loaders
except ImportError as e:
    logger.debug("Optional templating submodule 'loaders' not available: %s", e)
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


def cli_commands():
    """Return CLI commands for the templating module."""
    def _list_engines():
        """List template engines."""
        print("Templating Module - Engines:")
        print("  jinja2 - Jinja2 template engine (default)")
        print("  mako   - Mako template engine")
        print(f"  TemplateEngine: {'available' if TemplateEngine else 'unavailable'}")
        print(f"  TemplateManager: {'available' if TemplateManager else 'unavailable'}")

    def _render_template():
        """Render a template (shows render capabilities)."""
        print(f"Templating module v{__version__}")
        print("Render functions:")
        print("  render(template, context, engine)     - render a template string")
        print("  render_file(path, context, engine)     - render a template file")
        print("  get_default_engine(engine_type)        - get engine instance")
        if TemplateEngine:
            try:
                result = render("Hello {{ name }}!", {"name": "Codomyrmex"})
                print(f"  Test render: {result}")
            except Exception as e:
                print(f"  Test render failed: {e}")

    return {
        "engines": _list_engines,
        "render": _render_template,
    }


__all__ = [
    "engines",
    "filters",
    "context",
    "render",
    "render_file",
    "get_default_engine",
    "cli_commands",
]

if TemplateEngine:
    __all__.extend(["TemplateEngine", "Template"])
if TemplateManager:
    __all__.append("TemplateManager")

__version__ = "0.1.0"


class TemplatingError(CodomyrmexError):
    """Raised when templating operations fail."""
    pass

