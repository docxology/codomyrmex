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

__all__ = [
    "engines",
    "filters",
    "context",
]

if TemplateEngine:
    __all__.extend(["TemplateEngine", "Template"])
if TemplateManager:
    __all__.append("TemplateManager")

__version__ = "0.1.0"


class TemplatingError(CodomyrmexError):
    """Raised when templating operations fail."""
    pass
