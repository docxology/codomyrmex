"""Tree-sitter parsing module for Codomyrmex."""

from .parsers.parser import TreeSitterParser
from .languages.languages import LanguageManager

# Submodule exports
from . import parsers
from . import languages
from . import queries
from . import transformers

__all__ = [
    "TreeSitterParser",
    "LanguageManager",
    "parsers",
    "languages",
    "queries",
    "transformers",
]

__version__ = "0.1.0"

