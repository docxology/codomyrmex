"""Tree-sitter parser implementation."""

import importlib
from typing import Any

from codomyrmex.logging_monitoring import get_logger

# Import the external tree-sitter package explicitly to avoid shadowing
# by the local codomyrmex.tree_sitter package.
_tree_sitter = importlib.import_module("tree_sitter")

logger = get_logger(__name__)


class TreeSitterParser:
    """Wrapper for tree-sitter Parser (py-tree-sitter >= 0.25)."""

    def __init__(self, language: Any):
        """Initialize parser with a language.

        Args:
            language: tree_sitter.Language instance
        """
        self.language = language
        self.parser = _tree_sitter.Parser(language)

    def parse(self, source_code: str | bytes) -> "_tree_sitter.Tree":
        """Parse source code into a syntax tree."""
        if isinstance(source_code, str):
            source_code = source_code.encode("utf8")
        return self.parser.parse(source_code)

    def query(
        self, tree: "_tree_sitter.Tree", query_str: str
    ) -> "dict[str, list[_tree_sitter.Node]]":
        """Run an S-expression query against the tree.

        Returns:
            Mapping of capture name (without ``@``) to the captured nodes.
        """
        query = _tree_sitter.Query(self.language, query_str)
        return _tree_sitter.QueryCursor(query).captures(tree.root_node)
