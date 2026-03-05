"""Tree-sitter parsing module for Codomyrmex."""

# Submodule exports
from . import languages, parsers, queries, transformers
from .languages.languages import LanguageManager
from .parsers.parser import TreeSitterParser

__all__ = [
    "LanguageManager",
    "TreeSitterParser",
    "languages",
    "parsers",
    "queries",
    "transformers",
]

__version__ = "0.1.0"
