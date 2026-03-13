"""AST node models for tree-sitter parser utilities."""

from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class NodeType(Enum):
    """Common AST node types."""

    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    VARIABLE = "variable"
    IMPORT = "import"
    COMMENT = "comment"
    STRING = "string"
    PARAMETER = "parameter"
    RETURN = "return"
    CALL = "call"
    ASSIGNMENT = "assignment"
    IF = "if"
    FOR = "for"
    WHILE = "while"
    TRY = "try"


@dataclass
class Position:
    """Source code position."""

    line: int
    column: int

    def __lt__(self, other: "Position") -> bool:
        if self.line != other.line:
            return self.line < other.line
        return self.column < other.column

    def __le__(self, other: "Position") -> bool:
        return self == other or self < other


@dataclass
class Range:
    """Source code range."""

    start: Position
    end: Position

    @property
    def line_count(self) -> int:
        return self.end.line - self.start.line + 1

    def contains(self, pos: Position) -> bool:
        return self.start <= pos <= self.end


@dataclass
class ASTNode:
    """Representation of an AST node."""

    type: str
    text: str
    range: Range
    children: list["ASTNode"] = field(default_factory=list)
    parent: Optional["ASTNode"] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def find_children(self, node_type: str) -> list["ASTNode"]:
        return [c for c in self.children if c.type == node_type]

    def find_descendants(self, node_type: str) -> list["ASTNode"]:
        result = []

        def search(node: "ASTNode") -> None:
            if node.type == node_type:
                result.append(node)
            for child in node.children:
                search(child)

        for child in self.children:
            search(child)
        return result

    def walk(self) -> Iterator["ASTNode"]:
        yield self
        for child in self.children:
            yield from child.walk()

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "text": self.text[:100] if len(self.text) > 100 else self.text,
            "range": {
                "start": {
                    "line": self.range.start.line,
                    "column": self.range.start.column,
                },
                "end": {"line": self.range.end.line, "column": self.range.end.column},
            },
            "children": [c.to_dict() for c in self.children],
        }
