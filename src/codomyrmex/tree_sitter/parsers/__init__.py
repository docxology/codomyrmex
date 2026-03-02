"""
Tree-sitter parser utilities.

Provides utilities for parsing and analyzing source code using tree-sitter patterns.
"""

import re
from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


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

    def __lt__(self, other: 'Position') -> bool:
        """lt ."""
        if self.line != other.line:
            return self.line < other.line
        return self.column < other.column


@dataclass
class Range:
    """Source code range."""
    start: Position
    end: Position

    @property
    def line_count(self) -> int:
        return self.end.line - self.start.line + 1

    def contains(self, pos: Position) -> bool:
        """contains ."""
        return self.start <= pos <= self.end


@dataclass
class ASTNode:
    """Representation of an AST node."""
    type: str
    text: str
    range: Range
    children: list['ASTNode'] = field(default_factory=list)
    parent: Optional['ASTNode'] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def find_children(self, node_type: str) -> list['ASTNode']:
        """Find all children of a specific type."""
        return [c for c in self.children if c.type == node_type]

    def find_descendants(self, node_type: str) -> list['ASTNode']:
        """Find all descendants of a specific type."""
        result = []

        def search(node: ASTNode):
            """search ."""
            if node.type == node_type:
                result.append(node)
            for child in node.children:
                search(child)

        for child in self.children:
            search(child)

        return result

    def walk(self) -> Iterator['ASTNode']:
        """Walk the tree in pre-order."""
        yield self
        for child in self.children:
            yield from child.walk()

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "type": self.type,
            "text": self.text[:100] if len(self.text) > 100 else self.text,
            "range": {
                "start": {"line": self.range.start.line, "column": self.range.start.column},
                "end": {"line": self.range.end.line, "column": self.range.end.column},
            },
            "children": [c.to_dict() for c in self.children],
        }


class Parser(ABC):
    """Abstract base class for source code parsers."""

    @property
    @abstractmethod
    def language(self) -> str:
        """Get the language this parser handles."""
        pass

    @abstractmethod
    def parse(self, source: str) -> ASTNode:
        """Parse source code into an AST."""
        pass

    @abstractmethod
    def get_functions(self, root: ASTNode) -> list[ASTNode]:
        """Extract function definitions."""
        pass

    @abstractmethod
    def get_classes(self, root: ASTNode) -> list[ASTNode]:
        """Extract class definitions."""
        pass

    @abstractmethod
    def get_imports(self, root: ASTNode) -> list[ASTNode]:
        """Extract imports."""
        pass


class PythonParser(Parser):
    """Parser for Python source code."""

    @property
    def language(self) -> str:
        """language ."""
        return "python"

    def parse(self, source: str) -> ASTNode:
        """Parse Python source code."""
        lines = source.split('\n')
        root = ASTNode(
            type="module",
            text=source,
            range=Range(
                Position(0, 0),
                Position(len(lines) - 1, len(lines[-1]) if lines else 0)
            ),
        )

        # Simple regex-based parsing
        root.children = self._parse_functions(source, lines)
        root.children.extend(self._parse_classes(source, lines))
        root.children.extend(self._parse_imports(source, lines))

        return root

    def _parse_functions(self, source: str, lines: list[str]) -> list[ASTNode]:
        """Parse function definitions."""
        functions = []
        pattern = re.compile(r'^(\s*)def\s+(\w+)\s*\((.*?)\)\s*(?:->.*?)?:', re.MULTILINE)

        for match in pattern.finditer(source):
            indent = len(match.group(1))
            name = match.group(2)
            params = match.group(3)

            # Find line number
            line_num = source[:match.start()].count('\n')

            # Find function end
            end_line = self._find_block_end(lines, line_num, indent)

            func_text = '\n'.join(lines[line_num:end_line + 1])

            functions.append(ASTNode(
                type="function_definition",
                text=func_text,
                range=Range(
                    Position(line_num, indent),
                    Position(end_line, len(lines[end_line]) if end_line < len(lines) else 0)
                ),
                metadata={
                    "name": name,
                    "parameters": [p.strip() for p in params.split(',') if p.strip()],
                },
            ))

        return functions

    def _parse_classes(self, source: str, lines: list[str]) -> list[ASTNode]:
        """Parse class definitions."""
        classes = []
        pattern = re.compile(r'^(\s*)class\s+(\w+)\s*(?:\((.*?)\))?\s*:', re.MULTILINE)

        for match in pattern.finditer(source):
            indent = len(match.group(1))
            name = match.group(2)
            bases = match.group(3) or ""

            line_num = source[:match.start()].count('\n')
            end_line = self._find_block_end(lines, line_num, indent)

            class_text = '\n'.join(lines[line_num:end_line + 1])

            classes.append(ASTNode(
                type="class_definition",
                text=class_text,
                range=Range(
                    Position(line_num, indent),
                    Position(end_line, len(lines[end_line]) if end_line < len(lines) else 0)
                ),
                metadata={
                    "name": name,
                    "bases": [b.strip() for b in bases.split(',') if b.strip()],
                },
            ))

        return classes

    def _parse_imports(self, source: str, lines: list[str]) -> list[ASTNode]:
        """Parse import statements."""
        imports = []

        # import x, y, z
        pattern1 = re.compile(r'^import\s+(.+)$', re.MULTILINE)
        # from x import y
        pattern2 = re.compile(r'^from\s+(\S+)\s+import\s+(.+)$', re.MULTILINE)

        for match in pattern1.finditer(source):
            line_num = source[:match.start()].count('\n')
            imports.append(ASTNode(
                type="import_statement",
                text=match.group(0),
                range=Range(
                    Position(line_num, 0),
                    Position(line_num, len(match.group(0)))
                ),
                metadata={"modules": [m.strip() for m in match.group(1).split(',')]},
            ))

        for match in pattern2.finditer(source):
            line_num = source[:match.start()].count('\n')
            imports.append(ASTNode(
                type="import_from_statement",
                text=match.group(0),
                range=Range(
                    Position(line_num, 0),
                    Position(line_num, len(match.group(0)))
                ),
                metadata={
                    "module": match.group(1),
                    "names": [n.strip() for n in match.group(2).split(',')],
                },
            ))

        return imports

    def _find_block_end(self, lines: list[str], start_line: int, base_indent: int) -> int:
        """Find the end of an indented block."""
        end_line = start_line

        for i in range(start_line + 1, len(lines)):
            line = lines[i]

            # Skip empty lines and comments
            if not line.strip() or line.lstrip().startswith('#'):
                end_line = i
                continue

            # Check indentation
            line_indent = len(line) - len(line.lstrip())
            if line_indent <= base_indent:
                break

            end_line = i

        return end_line

    def get_functions(self, root: ASTNode) -> list[ASTNode]:
        return root.find_children("function_definition")

    def get_classes(self, root: ASTNode) -> list[ASTNode]:
        return root.find_children("class_definition")

    def get_imports(self, root: ASTNode) -> list[ASTNode]:
        imports = root.find_children("import_statement")
        imports.extend(root.find_children("import_from_statement"))
        return imports


class JavaScriptParser(Parser):
    """Parser for JavaScript source code."""

    @property
    def language(self) -> str:
        """language ."""
        return "javascript"

    def parse(self, source: str) -> ASTNode:
        """Parse the input and return a structured result."""
        lines = source.split('\n')
        root = ASTNode(
            type="program",
            text=source,
            range=Range(
                Position(0, 0),
                Position(len(lines) - 1, len(lines[-1]) if lines else 0)
            ),
        )

        root.children = self._parse_functions(source, lines)
        root.children.extend(self._parse_classes(source, lines))
        root.children.extend(self._parse_imports(source, lines))

        return root

    def _parse_functions(self, source: str, lines: list[str]) -> list[ASTNode]:
        functions = []

        # function name() {}
        pattern1 = re.compile(r'function\s+(\w+)\s*\((.*?)\)\s*\{')
        # const name = () => {}
        pattern2 = re.compile(r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\((.*?)\)\s*=>')
        # name: function() {}
        pattern3 = re.compile(r'(\w+)\s*:\s*function\s*\((.*?)\)\s*\{')

        for pattern in [pattern1, pattern2, pattern3]:
            for match in pattern.finditer(source):
                name = match.group(1)
                params = match.group(2)
                line_num = source[:match.start()].count('\n')

                functions.append(ASTNode(
                    type="function_declaration",
                    text=source[match.start():match.end() + 50],
                    range=Range(
                        Position(line_num, 0),
                        Position(line_num + 5, 0)
                    ),
                    metadata={
                        "name": name,
                        "parameters": [p.strip() for p in params.split(',') if p.strip()],
                    },
                ))

        return functions

    def _parse_classes(self, source: str, lines: list[str]) -> list[ASTNode]:
        classes = []
        pattern = re.compile(r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{')

        for match in pattern.finditer(source):
            name = match.group(1)
            extends = match.group(2)
            line_num = source[:match.start()].count('\n')

            classes.append(ASTNode(
                type="class_declaration",
                text=source[match.start():match.end() + 100],
                range=Range(
                    Position(line_num, 0),
                    Position(line_num + 10, 0)
                ),
                metadata={
                    "name": name,
                    "extends": extends,
                },
            ))

        return classes

    def _parse_imports(self, source: str, lines: list[str]) -> list[ASTNode]:
        imports = []
        pattern = re.compile(r'import\s+(?:\{([^}]+)\}|(\w+))?\s*(?:,\s*(?:\{([^}]+)\}|(\w+)))?\s*from\s+[\'"]([^\'"]+)[\'"]')

        for match in pattern.finditer(source):
            line_num = source[:match.start()].count('\n')

            imports.append(ASTNode(
                type="import_declaration",
                text=match.group(0),
                range=Range(
                    Position(line_num, 0),
                    Position(line_num, len(match.group(0)))
                ),
                metadata={
                    "source": match.group(5),
                },
            ))

        return imports

    def get_functions(self, root: ASTNode) -> list[ASTNode]:
        return root.find_children("function_declaration")

    def get_classes(self, root: ASTNode) -> list[ASTNode]:
        return root.find_children("class_declaration")

    def get_imports(self, root: ASTNode) -> list[ASTNode]:
        return root.find_children("import_declaration")


def get_parser(language: str) -> Parser:
    """Get a parser for the specified language."""
    parsers = {
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

    # Detect language from extension
    if filepath.endswith('.py'):
        parser = PythonParser()
    elif filepath.endswith(('.js', '.jsx', '.ts', '.tsx')):
        parser = JavaScriptParser()
    else:
        raise ValueError(f"Unknown file type: {filepath}")

    return parser.parse(source)


__all__ = [
    "NodeType",
    "Position",
    "Range",
    "ASTNode",
    "Parser",
    "PythonParser",
    "JavaScriptParser",
    "get_parser",
    "parse_file",
]
