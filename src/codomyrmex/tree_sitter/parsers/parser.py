"""Tree-sitter parser implementation."""

import importlib
from typing import Optional, Any
import logging
import os

# Import the external tree-sitter package explicitly to avoid shadowing
# by the local codomyrmex.tree_sitter package.
_tree_sitter = importlib.import_module("tree_sitter")

logger = logging.getLogger(__name__)

class TreeSitterParser:
    """Wrapper for tree-sitter Parser."""

    def __init__(self, language: Any):
        """Initialize parser with a language.

        Args:
            language: tree_sitter.Language instance
        """
        self.parser = _tree_sitter.Parser()
        self.parser.set_language(language)

    def parse(self, source_code: str) -> "_tree_sitter.Tree":
        """Parse source code into a syntax tree."""
        if isinstance(source_code, str):
            source_code = source_code.encode("utf8")
        return self.parser.parse(source_code)

    def query(self, tree: "_tree_sitter.Tree", query_str: str) -> list:
        """Execute a query against the syntax tree."""
        query = self.parser.language.query(query_str)
        captures = query.captures(tree.root_node)
        return captures
