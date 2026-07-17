"""JavaScript source code parser."""

import re

from .base import Parser
from .models import ASTNode, Position, Range


class JavaScriptParser(Parser):
    """Parser for JavaScript source code."""

    @property
    def language(self) -> str:
        return "javascript"

    def parse(self, source: str) -> ASTNode:
        lines = source.split("\n")
        root = ASTNode(
            type="program",
            text=source,
            range=Range(
                Position(0, 0),
                Position(len(lines) - 1, len(lines[-1]) if lines else 0),
            ),
        )
        root.children = self._parse_functions(source, lines)
        root.children.extend(self._parse_classes(source, lines))
        root.children.extend(self._parse_imports(source, lines))
        return root

    # Bolt optimization: Hoisted regex compilation to class level to prevent recompiling on every parse call
    _FUNC_PATTERNS = [
        re.compile(r"function\s+(\w+)\s*\((.*?)\)\s*\{"),
        re.compile(r"(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\((.*?)\)\s*=>"),
        re.compile(r"(\w+)\s*:\s*function\s*\((.*?)\)\s*\{"),
    ]

    def _parse_functions(self, source: str, lines: list[str]) -> list[ASTNode]:
        functions = []
        for pattern in self._FUNC_PATTERNS:
            for match in pattern.finditer(source):
                name = match.group(1)
                params = match.group(2)
                line_num = source[: match.start()].count("\n")
                functions.append(
                    ASTNode(
                        type="function_declaration",
                        text=source[match.start() : match.end() + 50],
                        range=Range(Position(line_num, 0), Position(line_num + 5, 0)),
                        metadata={
                            "name": name,
                            "parameters": [
                                p.strip() for p in params.split(",") if p.strip()
                            ],
                        },
                    )
                )
        return functions

    _CLASS_PATTERN = re.compile(r"class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{")

    def _parse_classes(self, source: str, lines: list[str]) -> list[ASTNode]:
        classes = []
        for match in self._CLASS_PATTERN.finditer(source):
            name = match.group(1)
            extends = match.group(2)
            line_num = source[: match.start()].count("\n")
            classes.append(
                ASTNode(
                    type="class_declaration",
                    text=source[match.start() : match.end() + 100],
                    range=Range(Position(line_num, 0), Position(line_num + 10, 0)),
                    metadata={"name": name, "extends": extends},
                )
            )
        return classes

    _IMPORT_PATTERN = re.compile(
        r'import\s+(?:\{([^}]+)\}|(\w+))?\s*(?:,\s*(?:\{([^}]+)\}|(\w+)))?\s*from\s+[\'"]([^\'"]+)[\'"]'
    )

    def _parse_imports(self, source: str, lines: list[str]) -> list[ASTNode]:
        imports = []
        for match in self._IMPORT_PATTERN.finditer(source):
            line_num = source[: match.start()].count("\n")
            imports.append(
                ASTNode(
                    type="import_declaration",
                    text=match.group(0),
                    range=Range(
                        Position(line_num, 0), Position(line_num, len(match.group(0)))
                    ),
                    metadata={"source": match.group(5)},
                )
            )
        return imports

    def get_functions(self, root: ASTNode) -> list[ASTNode]:
        return root.find_children("function_declaration")

    def get_classes(self, root: ASTNode) -> list[ASTNode]:
        return root.find_children("class_declaration")

    def get_imports(self, root: ASTNode) -> list[ASTNode]:
        return root.find_children("import_declaration")
