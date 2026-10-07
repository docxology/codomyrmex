#!/usr/bin/env python3
"""Check that ``codomyrmex`` imports shown in Markdown code blocks resolve.

Documentation drifts when modules move or functions are renamed: a README
that shows ``from codomyrmex.validation import is_valid`` keeps "working" in
review while every reader who copies it gets an ImportError. This gate
extracts every ``import codomyrmex…`` / ``from codomyrmex… import …``
statement from fenced Python blocks and imports it for real.

Blocks that intentionally show code that does not exist yet (for example a
tutorial that builds a new module step by step) are skipped when the line
before the opening fence is::

    <!-- docs-check: skip-imports -->

Usage::

    uv run python scripts/documentation/validate_code_references.py \\
        --repo-root . --fail-on-broken
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import importlib
import json
import sys
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

SKIP_MARKER = "<!-- docs-check: skip-imports -->"
PYTHON_FENCE_LANGS = frozenset({"python", "py", "python3", "pycon"})

# Third-party checkouts, generated output and caches are not our docs.
EXCLUDED_PARTS = frozenset(
    {
        ".git",
        ".venv",
        "node_modules",
        "vendor",
        "upstream",
        "htmlcov",
        "output",
        "site",
        "__pycache__",
        ".pytest_cache",
    }
)
EXCLUDED_PREFIXES = ("src/codomyrmex/agents/hermes/evolution/",)


@dataclass(frozen=True)
class Reference:
    """One imported name (``name`` is None for ``import module``)."""

    module: str
    name: str | None


@dataclass
class Occurrence:
    path: str
    line: int


@dataclass
class Report:
    files_scanned: int = 0
    references: dict[Reference, list[Occurrence]] = field(default_factory=dict)
    broken: dict[Reference, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "files_scanned": self.files_scanned,
            "unique_references": len(self.references),
            "broken_references": len(self.broken),
            "broken": [
                {
                    "module": ref.module,
                    "name": ref.name,
                    "error": error,
                    "locations": [f"{o.path}:{o.line}" for o in self.references[ref]],
                }
                for ref, error in sorted(
                    self.broken.items(), key=lambda kv: (kv[0].module, kv[0].name or "")
                )
            ],
        }


def iter_markdown_files(repo_root: Path) -> Iterator[Path]:
    for path in sorted(repo_root.rglob("*.md")):
        rel = path.relative_to(repo_root)
        if EXCLUDED_PARTS.intersection(rel.parts):
            continue
        if rel.as_posix().startswith(EXCLUDED_PREFIXES):
            continue
        yield path


def iter_python_blocks(text: str) -> Iterator[tuple[int, list[str]]]:
    """Yield ``(first_line_number, lines)`` for each fenced Python block."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith("```"):
            lang = stripped.lstrip("`").strip().split(" ")[0].lower()
            skip = i > 0 and lines[i - 1].strip() == SKIP_MARKER
            start = i + 1
            j = start
            while j < len(lines) and not lines[j].strip().startswith("```"):
                j += 1
            if lang in PYTHON_FENCE_LANGS and not skip:
                yield start + 1, lines[start:j]
            i = j + 1
            continue
        i += 1


def _strip_prompt(line: str) -> str:
    for prompt in (">>> ", "... "):
        if line.lstrip().startswith(prompt):
            return line.lstrip()[len(prompt) :]
    return line


def extract_references(block: list[str]) -> Iterator[tuple[int, Reference]]:
    """Yield ``(offset, Reference)`` for codomyrmex imports in a code block.

    Statements are parsed individually (joining parenthesised and
    backslash-continued imports) so one invalid line elsewhere in an
    illustrative snippet does not hide the imports.
    """
    lines = [_strip_prompt(line) for line in block]
    k = 0
    while k < len(lines):
        stripped = lines[k].strip()
        if not stripped.startswith(("from codomyrmex", "import codomyrmex")):
            k += 1
            continue
        offset = k
        statement = stripped
        if "(" in statement and ")" not in statement:
            while k + 1 < len(lines) and ")" not in statement:
                k += 1
                statement += " " + lines[k].strip()
        while statement.endswith("\\") and k + 1 < len(lines):
            k += 1
            statement = statement[:-1] + " " + lines[k].strip()
        k += 1
        try:
            tree = ast.parse(statement)
        except SyntaxError:
            continue
        for node in tree.body:
            if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                for alias in node.names:
                    if alias.name != "*":
                        yield offset, Reference(node.module, alias.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    yield offset, Reference(alias.name, None)


def resolve(ref: Reference) -> str | None:
    """Return None if the reference imports, else a short error description."""
    try:
        module = importlib.import_module(ref.module)
    except Exception as exc:  # report any import-time failure
        return f"{type(exc).__name__}: {exc}"[:200]
    if ref.name is None or hasattr(module, ref.name):
        return None
    try:
        importlib.import_module(f"{ref.module}.{ref.name}")
    except ModuleNotFoundError:
        return f"{ref.module} has no attribute or submodule {ref.name!r}"
    except Exception as exc:
        return f"{type(exc).__name__}: {exc}"[:200]
    return None


def scan(repo_root: Path, files: Iterable[Path] | None = None) -> Report:
    report = Report()
    for path in files if files is not None else iter_markdown_files(repo_root):
        report.files_scanned += 1
        rel = path.relative_to(repo_root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        for first_line, block in iter_python_blocks(text):
            for offset, ref in extract_references(block):
                report.references.setdefault(ref, []).append(
                    Occurrence(rel, first_line + offset)
                )
    # Some modules print on import; keep stdout clean for --format json.
    with contextlib.redirect_stdout(sys.stderr):
        for ref in report.references:
            error = resolve(ref)
            if error is not None:
                report.broken[ref] = error
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--output", type=Path, help="Also write the JSON report here")
    parser.add_argument(
        "--fail-on-broken",
        action="store_true",
        help="Exit 1 when any documented import does not resolve",
    )
    parser.add_argument(
        "paths", nargs="*", type=Path, help="Markdown files to check (default: all)"
    )
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    src = repo_root / "src"
    if src.is_dir() and str(src) not in sys.path:
        sys.path.insert(0, str(src))
    files = [p.resolve() for p in args.paths] if args.paths else None
    report = scan(repo_root, files)
    data = report.to_dict()

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    if args.format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(
            f"Scanned {data['files_scanned']} Markdown files: "
            f"{data['unique_references']} codomyrmex imports, "
            f"{data['broken_references']} broken."
        )
        for ref, error in sorted(
            report.broken.items(), key=lambda kv: (kv[0].module, kv[0].name or "")
        ):
            target = ref.module + (f".{ref.name}" if ref.name else "")
            print(f"\n  {target}\n    {error}")
            for occurrence in report.references[ref]:
                print(f"    - {occurrence.path}:{occurrence.line}")
    return 1 if args.fail_on_broken and report.broken else 0


if __name__ == "__main__":
    sys.exit(main())
