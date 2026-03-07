#!/usr/bin/env uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

import ast
import os
import sys
from collections import defaultdict
from pathlib import Path

# Thresholds
GOD_CLASS_METHOD_COUNT = 20
GOD_CLASS_LINE_COUNT = 500


class DesloppifyVisitor(ast.NodeVisitor):
    def __init__(self, filename: str):
        self.filename = filename
        self.classes: list[ast.ClassDef] = []
        self.functions: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
        self.missing_docstrings: list[str] = []
        self.god_classes: list[str] = []
        self.patterns = defaultdict(list)

    def visit_ClassDef(self, node: ast.ClassDef):
        self.classes.append(node)

        # Check docstring
        if not ast.get_docstring(node):
            self.missing_docstrings.append(f"Class '{node.name}' (line {node.lineno})")

        # Check God Class (Method Count)
        methods = [
            n
            for n in node.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        # Line count approximation
        end_lineno = getattr(node, "end_lineno", node.lineno)
        line_count = end_lineno - node.lineno

        if len(methods) > GOD_CLASS_METHOD_COUNT or line_count > GOD_CLASS_LINE_COUNT:
            self.god_classes.append(
                f"Class '{node.name}' (line {node.lineno}): {len(methods)} methods, {line_count} lines"
            )

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._check_func(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._check_func(node)

    def _check_func(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
        self.functions.append(node)

        # Check docstring
        if not node.name.startswith("__") and not ast.get_docstring(node):
            self.missing_docstrings.append(
                f"Function/Method '{node.name}' (line {node.lineno})"
            )

        # Extract AST structure (ignoring concrete names/values) to detect duplication
        pattern_hash = self._hash_ast(node)
        self.patterns[pattern_hash].append(f"{self.filename}:{node.name}:{node.lineno}")

        self.generic_visit(node)

    def _hash_ast(self, node: ast.AST, depth=0) -> str:
        if depth > 5:  # Limit depth to avoid explosion
            return type(node).__name__

        fields = []
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                fields.append(
                    f"{field}:["
                    + ",".join(
                        self._hash_ast(n, depth + 1)
                        for n in value
                        if isinstance(n, ast.AST)
                    )
                    + "]"
                )
            elif isinstance(value, ast.AST):
                fields.append(f"{field}:" + self._hash_ast(value, depth + 1))
        return type(node).__name__ + "(" + ",".join(fields) + ")"


def analyze_file(filepath: Path) -> DesloppifyVisitor:
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(filepath))
        visitor = DesloppifyVisitor(str(filepath))
        visitor.visit(tree)
        return visitor
    except Exception as e:
        print(f"Error parsing {filepath}: {e}", file=sys.stderr)
        return DesloppifyVisitor(str(filepath))


def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "src/codomyrmex"
    root_path = Path(target_dir)

    if not root_path.exists():
        print(f"Directory {target_dir} does not exist.")
        sys.exit(1)

    print(f"Scanning {target_dir} for technical debt...")

    total_files = 0
    total_god_classes = 0
    total_missing_docs = 0

    global_patterns = defaultdict(list)

    for py_file in root_path.rglob("*.py"):
        # Ignore tests and auto-generated
        if "tests" in py_file.parts or py_file.name.startswith("test_"):
            continue

        total_files += 1
        visitor = analyze_file(py_file)

        for k, v in visitor.patterns.items():
            if len(v) > 0:
                global_patterns[k].extend(v)

        if visitor.god_classes or visitor.missing_docstrings:
            print(f"\n--- {py_file} ---")

            if visitor.god_classes:
                print("[!] God Classes Detected:")
                for gc in visitor.god_classes:
                    print(f"    - {gc}")
                total_god_classes += len(visitor.god_classes)

            if visitor.missing_docstrings:
                print("[!] Missing Docstrings:")
                for md in visitor.missing_docstrings[:5]:  # Limit output
                    print(f"    - {md}")
                if len(visitor.missing_docstrings) > 5:
                    print(f"    ... and {len(visitor.missing_docstrings) - 5} more")
                total_missing_docs += len(visitor.missing_docstrings)

    print("\n--- Structural Duplication Analysis ---")
    duplicate_count = 0
    for pattern, locations in global_patterns.items():
        if (
            len(locations) > 2 and len(pattern) > 200
        ):  # Heuristic for non-trivial duplication
            print(f"[!] Structural AST clone detected in {len(locations)} locations:")
            for loc in locations[:3]:
                print(f"    - {loc}")
            if len(locations) > 3:
                print(f"    ... and {len(locations) - 3} more")
            duplicate_count += 1
            if duplicate_count >= 5:  # Limit output
                print("    ... more duplicates hidden")
                break

    print("\nSummary:")
    print(f"Files Scanned: {total_files}")
    print(f"God Classes: {total_god_classes}")
    print(f"Missing Docstrings: {total_missing_docs}")


if __name__ == "__main__":
    main()
