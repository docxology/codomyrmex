"""Python source code parser."""

import re

from .base import Parser
from .models import ASTNode, Position, Range


class PythonParser(Parser):
    """Parser for Python source code."""

    @property
    def language(self) -> str:
        return "python"

    def parse(self, source: str) -> ASTNode:
        lines = source.split("\n")
        root = ASTNode(
            type="module",
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

    def _parse_functions(self, source: str, lines: list[str]) -> list[ASTNode]:
        functions = []
        pattern = re.compile(
            r"^(\s*)def\s+(\w+)\s*\((.*?)\)\s*(?:->.*?)?:", re.MULTILINE
        )
        for match in pattern.finditer(source):
            indent = len(match.group(1))
            name = match.group(2)
            params = match.group(3)
            line_num = source[: match.start()].count("\n")
            end_line = self._find_block_end(lines, line_num, indent)
            func_text = "\n".join(lines[line_num : end_line + 1])
            functions.append(
                ASTNode(
                    type="function_definition",
                    text=func_text,
                    range=Range(
                        Position(line_num, indent),
                        Position(
                            end_line,
                            len(lines[end_line]) if end_line < len(lines) else 0,
                        ),
                    ),
                    metadata={
                        "name": name,
                        "parameters": [
                            p.strip() for p in params.split(",") if p.strip()
                        ],
                    },
                )
            )
        return functions

    def _parse_classes(self, source: str, lines: list[str]) -> list[ASTNode]:
        classes = []
        pattern = re.compile(r"^(\s*)class\s+(\w+)\s*(?:\((.*?)\))?\s*:", re.MULTILINE)
        for match in pattern.finditer(source):
            indent = len(match.group(1))
            name = match.group(2)
            bases = match.group(3) or ""
            line_num = source[: match.start()].count("\n")
            end_line = self._find_block_end(lines, line_num, indent)
            class_text = "\n".join(lines[line_num : end_line + 1])
            classes.append(
                ASTNode(
                    type="class_definition",
                    text=class_text,
                    range=Range(
                        Position(line_num, indent),
                        Position(
                            end_line,
                            len(lines[end_line]) if end_line < len(lines) else 0,
                        ),
                    ),
                    metadata={
                        "name": name,
                        "bases": [b.strip() for b in bases.split(",") if b.strip()],
                    },
                )
            )
        return classes

    def _parse_imports(self, source: str, lines: list[str]) -> list[ASTNode]:
        imports = []
        pattern1 = re.compile(r"^import\s+(.+)$", re.MULTILINE)
        pattern2 = re.compile(r"^from\s+(\S+)\s+import\s+(.+)$", re.MULTILINE)
        for match in pattern1.finditer(source):
            line_num = source[: match.start()].count("\n")
            imports.append(
                ASTNode(
                    type="import_statement",
                    text=match.group(0),
                    range=Range(
                        Position(line_num, 0), Position(line_num, len(match.group(0)))
                    ),
                    metadata={
                        "modules": [m.strip() for m in match.group(1).split(",")]
                    },
                )
            )
        for match in pattern2.finditer(source):
            line_num = source[: match.start()].count("\n")
            imports.append(
                ASTNode(
                    type="import_from_statement",
                    text=match.group(0),
                    range=Range(
                        Position(line_num, 0), Position(line_num, len(match.group(0)))
                    ),
                    metadata={
                        "module": match.group(1),
                        "names": [n.strip() for n in match.group(2).split(",")],
                    },
                )
            )
        return imports

    def _find_block_end(
        self, lines: list[str], start_line: int, base_indent: int
    ) -> int:
        end_line = start_line
        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            if not line.strip() or line.lstrip().startswith("#"):
                end_line = i
                continue
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
