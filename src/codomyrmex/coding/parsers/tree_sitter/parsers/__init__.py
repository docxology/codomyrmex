"""Tree-sitter parser utilities."""

from .base import Parser
from .javascript_parser import JavaScriptParser
from .models import ASTNode, NodeType, Position, Range
from .python_parser import PythonParser


def get_parser(language: str) -> Parser:
    """Get a parser for the specified language."""
    parsers: dict[str, type[Parser]] = {
        "python": PythonParser,
        "py": PythonParser,
        "javascript": JavaScriptParser,
        "js": JavaScriptParser,
    }
    parser_class = parsers.get(language.lower())
    if not parser_class:
        raise ValueError(f"Unsupported language: {language}")
    return parser_class()


def parse_file(filepath: str) -> ASTNode:
    """Parse a file and return its AST."""
    with open(filepath) as f:
        source = f.read()
    if filepath.endswith(".py"):
        parser: Parser = PythonParser()
    elif filepath.endswith((".js", ".jsx", ".ts", ".tsx")):
        parser = JavaScriptParser()
    else:
        raise ValueError(f"Unknown file type: {filepath}")
    return parser.parse(source)


__all__ = [
    "ASTNode",
    "JavaScriptParser",
    "NodeType",
    "Parser",
    "Position",
    "PythonParser",
    "Range",
    "get_parser",
    "parse_file",
]
