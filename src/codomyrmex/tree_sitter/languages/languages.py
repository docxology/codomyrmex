"""Language management for tree-sitter."""

import importlib
import logging
import os
from typing import Any

# Import the external tree-sitter package explicitly to avoid shadowing
# by the local codomyrmex.coding.parsers.tree_sitter package.
_tree_sitter = importlib.import_module("tree_sitter")

logger = logging.getLogger(__name__)

class LanguageManager:
    """Manages tree-sitter language libraries."""

    _languages: dict[str, Any] = {}

    @classmethod
    def load_language(cls, library_path: str, lang_name: str) -> bool:
        """Load a language from a shared library (.so, .dll, .dylib)."""
        try:
            # Note: tree-sitter 0.20+ uses Language(library_path, lang_name)
            # This is a common wrapper pattern.
            lang = _tree_sitter.Language(library_path, lang_name)
            cls._languages[lang_name] = lang
            return True
        except Exception as e:
            logger.error(f"Failed to load tree-sitter language {lang_name} from {library_path}: {e}")
            return False

    @classmethod
    def get_language(cls, lang_name: str) -> Any | None:
        """Get a loaded language instance."""
        return cls._languages.get(lang_name)

    @classmethod
    def discover_languages(cls, search_path: str):
        """Discovers and loads all .so files in a directory as languages."""
        if not os.path.exists(search_path):
            return

        for root, _, files in os.walk(search_path):
            for file in files:
                if file.endswith((".so", ".dylib", ".dll")):
                    # Try to infer lang name from filename (e.g. tree-sitter-python.so)
                    lang_name = file.replace("tree-sitter-", "").split(".")[0]
                    cls.load_language(os.path.join(root, file), lang_name)
