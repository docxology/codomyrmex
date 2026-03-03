#!/usr/bin/env python3
"""
scripts/maintenance/audit_stubs.py

Scans the codomyrmex source tree for concrete stub methods (pass, ..., bare
NotImplementedError) and writes a Markdown report listing each one with a
link back to the source file and line number.

Usage:
    python audit_stubs.py [--src SRC_DIR] [--output OUTPUT_FILE]

    --src     Path to codomyrmex source directory
              (default: <repo_root>/src/codomyrmex)
    --output  Path to write the Markdown report
              (default: <repo_root>/reports/stub_audit.md)
"""

import argparse
import ast
from pathlib import Path

from codomyrmex.utils.cli_helpers import print_info, print_success


def is_stub_node(node) -> bool:
    """Return True if *node* is a stub function/method body.

    A stub is defined as a function whose effective body (after stripping an
    optional leading docstring) consists of exactly one of:
    - a bare ``pass`` statement
    - a ``...`` (Ellipsis) expression
    - a bare ``raise NotImplementedError`` (with or without a message)

    Args:
        node: An ``ast.FunctionDef`` or ``ast.AsyncFunctionDef`` node.

    Returns:
        ``True`` if the node qualifies as a stub.
    """
    if not node.body:
        return True
    body = node.body
    # Strip leading docstring
    if (
        len(body) > 1
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        body = body[1:]
    if not body:
        return True
    if len(body) == 1:
        stmt = body[0]
        if isinstance(stmt, ast.Pass):
            return True
        if (
            isinstance(stmt, ast.Expr)
            and isinstance(stmt.value, ast.Constant)
            and stmt.value.value is Ellipsis
        ):
            return True
        if isinstance(stmt, ast.Raise):
            if isinstance(stmt.exc, ast.Name) and stmt.exc.id == "NotImplementedError":
                return True
            if (
                isinstance(stmt.exc, ast.Call)
                and getattr(stmt.exc.func, "id", "") == "NotImplementedError"
            ):
                return True
    return False


def audit_stubs_better(src_dir: Path) -> list:
    """Walk *src_dir* and collect stub function/method definitions.

    Skips protocol/interface/base files, test files, ``__init__.py``, and
    functions that are abstract, in error-class parents, or are common
    lifecycle methods (``__init__``, ``setup``, ``close``, etc.).

    Args:
        src_dir: Root path of the codomyrmex source tree to scan.

    Returns:
        A list of Markdown bullet strings, one per stub found.
    """
    issues = []
    skip_names = {
        "__init__", "__post_init__", "__enter__", "__exit__",
        "close", "shutdown", "cleanup", "update", "setup",
    }
    abstract_decorators = {"abstractmethod", "overload", "property"}
    abstract_bases = {"ABC", "Protocol", "Interface", "Exception", "Error", "BaseException"}

    for filepath in sorted(src_dir.rglob("*.py")):
        # Skip __pycache__ and tests subtrees
        parts = filepath.parts
        if any(p in ("__pycache__", "tests") for p in parts):
            continue
        fname = filepath.name
        if fname.startswith("test_") or fname == "__init__.py":
            continue
        if any(kw in fname.lower() for kw in ("interface", "protocol")) or fname in ("base.py", "abc.py"):
            continue

        try:
            content = filepath.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except Exception:
            continue

        # Attach parent pointers for class-membership checks
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node  # type: ignore[attr-defined]

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not is_stub_node(node):
                continue

            # Check decorators
            is_abstract = any(
                (getattr(d, "id", "") or getattr(d, "attr", "")) in abstract_decorators
                for d in node.decorator_list
            )

            parent = getattr(node, "parent", None)
            if not is_abstract and isinstance(parent, ast.ClassDef):
                for base in parent.bases:
                    if (getattr(base, "id", "") or getattr(base, "attr", "")) in abstract_bases:
                        is_abstract = True
                        break
                if parent.name.endswith(("Error", "Exception", "Base")):
                    is_abstract = True

            if is_abstract:
                continue
            if node.name in skip_names:
                continue

            try:
                rel = filepath.relative_to(src_dir.parent.parent)
            except ValueError:
                rel = filepath
            issues.append(f"- `{node.name}` in [{filepath}](../../{rel}#L{node.lineno})")

    return issues


def main() -> int:
    """Parse arguments, run the stub audit, and write the Markdown report."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    parser = argparse.ArgumentParser(
        description=(
            "Audit codomyrmex source for concrete stub methods and write a Markdown report."
        )
    )
    parser.add_argument(
        "--src",
        default=str(repo_root / "src" / "codomyrmex"),
        help="Path to codomyrmex source directory (default: <repo_root>/src/codomyrmex)",
    )
    parser.add_argument(
        "--output",
        default=str(repo_root / "reports" / "stub_audit.md"),
        help="Path to write the Markdown report (default: <repo_root>/reports/stub_audit.md)",
    )
    args = parser.parse_args()

    src_dir = Path(args.src).resolve()
    output_path = Path(args.output).resolve()

    print_info(f"Scanning {src_dir} for stub methods...")
    issues = audit_stubs_better(src_dir)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        f.write(
            f"# Stub Audit Findings\n\n"
            f"Found {len(issues)} concrete stub methods requiring implementation:\n\n"
        )
        for issue in issues:
            f.write(issue + "\n")

    print_success(f"Written {len(issues)} stubs to {output_path}")
    return 0


if __name__ == "__main__":
    main()
