#!/usr/bin/env python3
"""Lightweight structural checks for Python sources (no external analyzers)."""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Issue:
    kind: str
    severity: str
    path: str
    line: int
    detail: str


def max_nesting(node: ast.AST, depth: int = 0) -> int:
    nest_types = (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.Match)
    if isinstance(node, nest_types):
        depth += 1
    best = depth
    for child in ast.iter_child_nodes(node):
        best = max(best, max_nesting(child, depth))
    return best


def check_file(path: Path) -> list[Issue]:
    issues: list[Issue] = []
    try:
        src = path.read_text(encoding="utf-8")
    except OSError as e:
        issues.append(Issue("read_error", "high", str(path), 0, str(e)))
        return issues
    lines = src.count("\n") + (1 if src else 0)
    if lines > 500:
        issues.append(
            Issue("large_file", "medium", str(path), 1, f"~{lines} lines (>500)")
        )
    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError as e:
        issues.append(
            Issue(
                "syntax_error",
                "high",
                str(path),
                e.lineno or 0,
                e.msg or "syntax error",
            )
        )
        return issues

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            end = getattr(node, "end_lineno", None) or node.lineno
            fn_lines = end - node.lineno + 1
            if fn_lines > 50:
                issues.append(
                    Issue(
                        "long_function",
                        "medium",
                        str(path),
                        node.lineno,
                        f"{node.name}: {fn_lines} lines (>50)",
                    )
                )
            nargs = len(node.args.args) + len(node.args.kwonlyargs)
            if node.args.vararg:
                nargs += 1
            if node.args.kwarg:
                nargs += 1
            if nargs > 5:
                issues.append(
                    Issue(
                        "many_parameters",
                        "low",
                        str(path),
                        node.lineno,
                        f"{node.name}: {nargs} parameters (>5)",
                    )
                )
            nest = max_nesting(node, 0)
            if nest > 4:
                issues.append(
                    Issue(
                        "deep_nesting",
                        "medium",
                        str(path),
                        node.lineno,
                        f"{node.name}: nesting depth {nest} (>4)",
                    )
                )
        if isinstance(node, ast.ClassDef):
            methods = sum(
                1
                for n in node.body
                if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)
            )
            if methods > 20:
                issues.append(
                    Issue(
                        "large_class",
                        "medium",
                        str(path),
                        node.lineno,
                        f"{node.name}: {methods} methods (>20)",
                    )
                )
    return issues


def iter_py_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob("*.py"):
        if any(part.startswith(".") for part in p.parts):
            continue
        files.append(p)
    return sorted(files)


def main() -> int:
    parser = argparse.ArgumentParser(description="Python structural quality checker")
    parser.add_argument("path", type=Path, nargs="+", help="Files or directories")
    parser.add_argument(
        "--language",
        default="python",
        choices=["python"],
        help="Language (python only)",
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()
    if args.language != "python":
        print("Only --language python is supported.", file=sys.stderr)
        return 2
    all_issues: list[Issue] = []
    for raw in args.path:
        p = raw.resolve()
        if p.is_file():
            if p.suffix == ".py":
                all_issues.extend(check_file(p))
        elif p.is_dir():
            for f in iter_py_files(p):
                all_issues.extend(check_file(f))
        else:
            print(f"Not found: {p}", file=sys.stderr)
            return 1
    payload = {
        "language": args.language,
        "issues_count": len(all_issues),
        "issues": [asdict(i) for i in all_issues],
    }
    if args.json:
        print(json.dumps(payload, indent=2))
        return 0
    print(f"Issues: {len(all_issues)}")
    for i in all_issues[:100]:
        print(f"  [{i.severity}] {i.kind} {i.path}:{i.line} — {i.detail}")
    if len(all_issues) > 100:
        print(f"  ... and {len(all_issues) - 100} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
