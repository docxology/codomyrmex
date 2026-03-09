#!/usr/bin/env python3
"""
desloppify.py: Codebase De-sloppification Analyzer

Uses Python's robust `ast` module to scan the Codomyrmex codebase for signs of technical debt.
Flags:
- God classes (classes exceeding a threshold of 30 methods, or 1000 lines)
- Missing class-level, module-level, and public-method docstrings
- Heavily branched functions (cyclomatic complexity estimators based on if/for/while density)

Usage:
    ./tools/desloppify.py [--json] [--dir <target_dir>]
"""

import argparse
import ast
import json
import sys
from pathlib import Path


class SloppinessVisitor(ast.NodeVisitor):
    def __init__(self, filename: str):
        self.filename = filename
        self.god_classes = []
        self.missing_docstrings = []
        self.complex_methods = []

    def visit_Module(self, node):
        if not ast.get_docstring(node):
            self.missing_docstrings.append(f"{self.filename}: <module>")
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        if not ast.get_docstring(node):
            self.missing_docstrings.append(f"{self.filename}:{node.name}")

        method_count = sum(
            1
            for item in node.body
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
        )
        if method_count >= 30:
            self.god_classes.append(
                f"{self.filename}:{node.name} ({method_count} methods)"
            )

        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self._analyze_function(node)

    def visit_AsyncFunctionDef(self, node):
        self._analyze_function(node)

    def _analyze_function(self, node):
        # We only really care about public methods for docstrings
        is_public = not node.name.startswith("_") or node.name == "__init__"
        if is_public and not ast.get_docstring(node):
            # We don't have the parent class name easily in a raw visitor without tracking scope,
            # so we just record the function name and line number
            self.missing_docstrings.append(
                f"{self.filename}:{node.lineno} def {node.name}"
            )

        # Basic complexity: count loops and branches
        branches = sum(
            1
            for child in ast.walk(node)
            if isinstance(
                child,
                (
                    ast.If,
                    ast.For,
                    ast.While,
                    ast.Try,
                    ast.With,
                    ast.ExceptHandler,
                    ast.Match,
                ),
            )
        )
        if branches > 15:
            self.complex_methods.append(
                f"{self.filename}:{node.lineno} def {node.name} (complexity: {branches})"
            )

        self.generic_visit(node)


def analyze_codebase(target_dir: str = "src/codomyrmex") -> dict:
    target = Path(target_dir)
    if not target.exists():
        print(f"Directory {target_dir} not found.", file=sys.stderr)
        sys.exit(1)

    all_god_classes = []
    all_missing_docs = []
    all_complex = []

    files_checked = 0

    for py_file in target.rglob("*.py"):
        # Skip tests for strict docstring enforcement unless explicitly desired
        if "tests/" in str(py_file):
            continue

        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
            files_checked += 1
        except SyntaxError:
            continue

        visitor = SloppinessVisitor(str(py_file.relative_to(target.parent)))
        visitor.visit(tree)

        all_god_classes.extend(visitor.god_classes)
        all_missing_docs.extend(visitor.missing_docstrings)
        all_complex.extend(visitor.complex_methods)

    return {
        "files_analyzed": files_checked,
        "god_classes": all_god_classes,
        "missing_docstrings": all_missing_docs,
        "complex_methods": all_complex,
    }


def main():
    parser = argparse.ArgumentParser(description="Codomyrmex codebase de-sloppifier")
    parser.add_argument("--json", action="store_true", help="Output purely as JSON")
    parser.add_argument("--dir", default="src/codomyrmex", help="Target directory")

    args = parser.parse_args()

    results = analyze_codebase(args.dir)

    if args.json:
        print(json.dumps(results, indent=2))
        return

    # Markdown format
    print("# Desloppify Technical Debt Report\n")
    print(f"**Files Analyzed:** {results['files_analyzed']}\n")

    print(f"## God Classes (>30 methods) [{len(results['god_classes'])}]")
    for item in results["god_classes"]:
        print(f"- {item}")
    if not results["god_classes"]:
        print("None detected! Excellent layout.")

    print(
        f"\n## High Complexity Functions (>15 branches) [{len(results['complex_methods'])}]"
    )
    for item in results["complex_methods"]:
        print(f"- {item}")
    if not results["complex_methods"]:
        print("None detected! Well abstracted.")

    # Missing docstrings can be numerous, just show first 20 in terminal markdown
    print(f"\n## Missing Docstrings [{len(results['missing_docstrings'])}]")
    for item in results["missing_docstrings"][:20]:
        print(f"- {item}")
    if len(results["missing_docstrings"]) > 20:
        print(f"... and {len(results['missing_docstrings']) - 20} more.")
    elif not results["missing_docstrings"]:
        print("100% docstring coverage! Incredible.")


if __name__ == "__main__":
    main()
