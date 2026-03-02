"""Repo indexer for symbol extraction and import graph.

Scans Python files to extract function/class symbols and build
an import dependency graph.
"""

from __future__ import annotations

import ast
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class Symbol:
    """A code symbol (function or class).

    Attributes:
        name: Symbol name.
        kind: ``function`` or ``class``.
        file: Source file path.
        line: Line number.
        docstring: First line of docstring.
    """

    name: str
    kind: str = "function"
    file: str = ""
    line: int = 0
    docstring: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "name": self.name,
            "kind": self.kind,
            "file": self.file,
            "line": self.line,
            "docstring": self.docstring[:80],
        }


@dataclass
class ImportEdge:
    """An import dependency edge.

    Attributes:
        source: Importing file.
        target: Imported module.
        names: Specific names imported.
    """

    source: str
    target: str
    names: list[str] = field(default_factory=list)


@dataclass
class RepoIndex:
    """Repository symbol index and import graph.

    Attributes:
        symbols: All extracted symbols.
        imports: Import dependency edges.
        files_indexed: Number of files processed.
    """

    symbols: list[Symbol] = field(default_factory=list)
    imports: list[ImportEdge] = field(default_factory=list)
    files_indexed: int = 0

    @property
    def symbol_count(self) -> int:
        return len(self.symbols)

    def symbols_in_file(self, file_path: str) -> list[Symbol]:
        return [s for s in self.symbols if s.file == file_path]

    def functions(self) -> list[Symbol]:
        """functions ."""
        return [s for s in self.symbols if s.kind == "function"]

    def classes(self) -> list[Symbol]:
        """classes ."""
        return [s for s in self.symbols if s.kind == "class"]

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "files_indexed": self.files_indexed,
            "symbol_count": self.symbol_count,
            "functions": len(self.functions()),
            "classes": len(self.classes()),
            "imports": len(self.imports),
        }


class RepoIndexer:
    """Index a repository for symbols and imports.

    Usage::

        indexer = RepoIndexer()
        index = indexer.index_file("path/to/module.py")
        print(f"Found {index.symbol_count} symbols")
    """

    def index_file(self, file_path: str | Path) -> RepoIndex:
        """Index a single Python file.

        Args:
            file_path: Path to Python file.

        Returns:
            ``RepoIndex`` with symbols and imports from that file.
        """
        path = Path(file_path)
        if not path.exists() or path.suffix != ".py":
            return RepoIndex()

        try:
            source = path.read_text()
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError):
            return RepoIndex()

        symbols: list[Symbol] = []
        imports: list[ImportEdge] = []
        rel_path = str(path)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                doc = ast.get_docstring(node) or ""
                symbols.append(Symbol(
                    name=node.name,
                    kind="function",
                    file=rel_path,
                    line=node.lineno,
                    docstring=doc.split("\n")[0] if doc else "",
                ))
            elif isinstance(node, ast.ClassDef):
                doc = ast.get_docstring(node) or ""
                symbols.append(Symbol(
                    name=node.name,
                    kind="class",
                    file=rel_path,
                    line=node.lineno,
                    docstring=doc.split("\n")[0] if doc else "",
                ))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(ImportEdge(
                        source=rel_path,
                        target=alias.name,
                    ))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                names = [alias.name for alias in node.names]
                imports.append(ImportEdge(
                    source=rel_path,
                    target=module,
                    names=names,
                ))

        return RepoIndex(
            symbols=symbols,
            imports=imports,
            files_indexed=1,
        )

    def index_directory(self, root: str | Path) -> RepoIndex:
        """Index all Python files in a directory.

        Args:
            root: Root directory.

        Returns:
            Merged ``RepoIndex`` for the entire directory.
        """
        merged = RepoIndex()
        root_path = Path(root)

        for dirpath, dirnames, filenames in os.walk(root_path):
            dirnames[:] = [d for d in dirnames if d not in {"__pycache__", ".venv", ".git"}]
            for fname in filenames:
                if fname.endswith(".py"):
                    idx = self.index_file(os.path.join(dirpath, fname))
                    merged.symbols.extend(idx.symbols)
                    merged.imports.extend(idx.imports)
                    merged.files_indexed += idx.files_indexed

        logger.info(
            "Directory indexed",
            extra={"files": merged.files_indexed, "symbols": merged.symbol_count},
        )

        return merged


__all__ = [
    "ImportEdge",
    "RepoIndex",
    "RepoIndexer",
    "Symbol",
]
