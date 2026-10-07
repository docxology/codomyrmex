"""Language management for tree-sitter."""

import ctypes
import importlib
import os
from typing import Any

from codomyrmex.logging_monitoring import get_logger

# Import the external tree-sitter package explicitly to avoid shadowing
# by the local codomyrmex.tree_sitter package.
_tree_sitter = importlib.import_module("tree_sitter")

logger = get_logger(__name__)


class LanguageManager:
    """Manages tree-sitter language libraries."""

    _languages: dict[str, Any] = {}

    @classmethod
    def register_language(cls, lang_name: str, language: Any) -> Any:
        """Register a grammar shipped as a Python package.

        Args:
            lang_name: Name to register the language under (e.g. ``"python"``).
            language: A ``tree_sitter.Language`` or the object returned by a
                grammar package's ``language()`` function, e.g.
                ``tree_sitter_python.language()``.

        Returns:
            The registered ``tree_sitter.Language``.
        """
        if not isinstance(language, _tree_sitter.Language):
            language = _tree_sitter.Language(language)
        cls._languages[lang_name] = language
        return language

    @classmethod
    def load_language(cls, library_path: str, lang_name: str) -> bool:
        """Load a language from a compiled grammar (.so, .dll, .dylib).

        The library must export ``tree_sitter_<lang_name>()``, the entry point
        every tree-sitter grammar provides.
        """
        try:
            library = ctypes.cdll.LoadLibrary(library_path)
            entry_point = getattr(library, f"tree_sitter_{lang_name}")
            entry_point.restype = ctypes.c_void_p
            lang = _tree_sitter.Language(entry_point())
            cls._languages[lang_name] = lang
            return True
        except Exception as e:
            logger.error(
                "Failed to load tree-sitter language %s from %s: %s",
                lang_name,
                library_path,
                e,
            )
            return False

    @classmethod
    def get_language(cls, lang_name: str) -> Any | None:
        """Get a loaded language instance."""
        return cls._languages.get(lang_name)

    @classmethod
    def discover_languages(cls, search_path: str) -> None:
        """Discovers and loads all .so files in a directory as languages."""
        if not os.path.exists(search_path):
            return

        for root, _, files in os.walk(search_path):
            for file in files:
                if file.endswith((".so", ".dylib", ".dll")):
                    # Try to infer lang name from filename (e.g. tree-sitter-python.so)
                    lang_name = file.replace("tree-sitter-", "").split(".")[0]
                    cls.load_language(os.path.join(root, file), lang_name)
