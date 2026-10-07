#!/usr/bin/env python3
"""Check that MCP_TOOL_SPECIFICATION.md files only document real MCP tools.

A module's ``MCP_TOOL_SPECIFICATION.md`` drifts when tools are renamed or
were only ever planned: agents read the spec, call ``codomyrmex.<name>`` and
get "unknown tool". This gate compares the tool names each specification
documents with the tools the code actually defines.

Real tools are found statically (nothing is imported) by parsing every Python
file under ``src/codomyrmex/`` with :mod:`ast`:

* functions and methods decorated with ``@mcp_tool`` — the registered name
  is the ``name=`` argument when given, else the function name;
* functions registered FastMCP-style with ``@<server>.tool()`` inside a
  module's ``register_mcp_tools`` helper;
* the keys of the dict literal returned by a ``get_tool_definitions()``
  method (class-based adapters such as ``OrchestrationMCPTools``);
* the static PAI bridge tools in ``agents/pai/mcp/definitions.py``
  (``TOOL_DEFINITIONS``).

The PAI bridge surfaces names as ``codomyrmex.<name>``; documented names are
compared with that prefix removed, so ``codomyrmex.list_modules`` and
``list_modules`` are the same tool.

Documented tools are taken from, outside fenced code blocks:

* headings that name a tool: ``## Tool: `name` ``, ``### `name` ``,
  ``### `a` / `b` ``, or a bare lower-case identifier such as ``## name``;
* the line after a ``### 2. Invocation Name`` heading;
* the first column of tables headed ``Tool``, ``Tool Name``,
  ``Invocation``, ``Exposed name`` or ``Implemented Tool Function``.

A documented name is *broken* (``--fail-on-broken`` exits 1) unless code in
the specification's own package defines it. A specification in
``src/codomyrmex/<package>/`` (trailing ``docs/`` folders ignored) covers
tools defined anywhere under that package, and the mirror in
``docs/modules/<module>/`` covers ``src/codomyrmex/<module>/``. The PAI
bridge's static tools are valid in every specification, and a specification
that maps to no package accepts any real tool. Real tools that no
specification in their package (or a parent package) mentions are reported
as *undocumented*; that is informational and never fails the check.

A specification that intentionally documents planned tools is skipped when
it contains::

    <!-- docs-check: skip-mcp-tools -->

Usage::

    uv run python scripts/documentation/validate_mcp_tool_specs.py \\
        --repo-root . --fail-on-broken
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

SKIP_MARKER = "<!-- docs-check: skip-mcp-tools -->"
SPEC_FILENAME = "MCP_TOOL_SPECIFICATION.md"
PACKAGE_DIR = Path("src") / "codomyrmex"
STATIC_DEFINITIONS = PACKAGE_DIR / "agents" / "pai" / "mcp" / "definitions.py"
TOOL_PREFIX = "codomyrmex."

# Third-party checkouts, generated output, caches and test trees are not
# sources of tools or documentation. Hidden directories (``.git``, ``.venv``,
# ``.claude/worktrees`` ...) are always pruned.
EXCLUDED_PARTS = frozenset(
    {
        "node_modules",
        "vendor",
        "vendors",
        "upstream",
        "htmlcov",
        "output",
        "site",
        "__pycache__",
    }
)
EXCLUDED_SOURCE_PARTS = EXCLUDED_PARTS | {"test", "tests"}
EXCLUDED_PREFIXES = (
    "src/codomyrmex/agents/hermes/evolution/",
    "src/codomyrmex/agents/open_gauss/",
)

_IDENT = r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*"
_CODE_ITEM = rf"`(?:{_IDENT})(?:\(\))?`"
_BARE_ITEM = r"[a-z_][a-z0-9_]*(?:\.[a-z_][a-z0-9_]*)*(?:\(\))?"
_SEPARATOR = r"\s*(?:/|,|&|\band\b)\s*"
_HEADING = re.compile(r"^(#{2,6})\s+(?P<text>.+?)\s*#*\s*$")
_TOOL_PREFIX_RE = re.compile(r"^(?:mcp\s+)?tool\s*:\s*", re.IGNORECASE)
_CODE_LIST = re.compile(rf"^{_CODE_ITEM}(?:{_SEPARATOR}{_CODE_ITEM})*$")
_BARE_LIST = re.compile(rf"^{_BARE_ITEM}(?:{_SEPARATOR}{_BARE_ITEM})*$")
_ANY_LIST = re.compile(
    rf"^(?:{_CODE_ITEM}|{_IDENT}(?:\(\))?)"
    rf"(?:{_SEPARATOR}(?:{_CODE_ITEM}|{_IDENT}(?:\(\))?))*$"
)
_CODE_SPAN = re.compile(r"`([^`]+)`")
_IDENT_RE = re.compile(rf"^{_IDENT}$")
_INVOCATION_HEADING = re.compile(r"^(?:\d+\.\s*)?invocation name$", re.IGNORECASE)
_TABLE_SEPARATOR = re.compile(r"^\s*\|?\s*:?-{2,}")
TOOL_TABLE_HEADERS = frozenset(
    {
        "tool",
        "tools",
        "tool name",
        "mcp tool",
        "invocation",
        "invocation name",
        "exposed name",
        "implemented tool function",
    }
)


def normalize(name: str) -> str:
    """Return the comparable form of a tool name (no backticks, ``()``, prefix)."""
    return name.strip().strip("`").strip().removesuffix("()").removeprefix(TOOL_PREFIX)


@dataclass(frozen=True)
class Tool:
    """A tool defined in code."""

    name: str
    path: str
    line: int


@dataclass(frozen=True)
class DocumentedTool:
    """A tool name a specification documents."""

    name: str
    path: str
    line: int


@dataclass(frozen=True)
class Broken:
    """A documented tool the specification's module does not define."""

    tool: DocumentedTool
    reason: str


@dataclass
class Report:
    specs_scanned: int = 0
    specs_skipped: list[str] = field(default_factory=list)
    tools: dict[str, list[Tool]] = field(default_factory=dict)
    documented: list[DocumentedTool] = field(default_factory=list)
    broken: list[Broken] = field(default_factory=list)
    undocumented: list[tuple[Tool, str | None]] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "specs_scanned": self.specs_scanned,
            "specs_skipped": sorted(self.specs_skipped),
            "real_tools": len(self.tools),
            "documented_tools": len({(d.path, d.name) for d in self.documented}),
            "broken_tools": len(self.broken),
            "undocumented_tools": len(self.undocumented),
            "broken": [
                {
                    "tool": b.tool.name,
                    "location": f"{b.tool.path}:{b.tool.line}",
                    "reason": b.reason,
                }
                for b in self.broken
            ],
            "undocumented": [
                {
                    "tool": tool.name,
                    "defined_at": f"{tool.path}:{tool.line}",
                    "spec": spec,
                }
                for tool, spec in self.undocumented
            ],
        }


# ── Discovery helpers ────────────────────────────────────────────────


def _walk(root: Path, excluded: frozenset[str], repo_root: Path) -> Iterator[Path]:
    """Yield files under ``root`` (sorted), pruning excluded directories."""
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        rel = current.relative_to(repo_root).as_posix() + "/"
        dirnames[:] = sorted(
            d
            for d in dirnames
            if not d.startswith(".")
            and d not in excluded
            and not (rel + d + "/").startswith(EXCLUDED_PREFIXES)
        )
        for filename in sorted(filenames):
            yield current / filename


def iter_spec_files(repo_root: Path) -> Iterator[Path]:
    for path in _walk(repo_root, EXCLUDED_PARTS, repo_root):
        if path.name == SPEC_FILENAME:
            yield path


def iter_python_sources(repo_root: Path) -> Iterator[Path]:
    package = repo_root / PACKAGE_DIR
    if not package.is_dir():
        return
    for path in _walk(package, EXCLUDED_SOURCE_PARTS, repo_root):
        if path.suffix == ".py":
            yield path


def _decorator_tool_name(
    decorator: ast.expr, func: ast.FunctionDef | ast.AsyncFunctionDef
) -> str | None:
    """Return the registered name if ``decorator`` registers an MCP tool."""
    call = decorator if isinstance(decorator, ast.Call) else None
    target = call.func if call is not None else decorator
    if isinstance(target, ast.Name):
        is_tool = target.id == "mcp_tool"
    elif isinstance(target, ast.Attribute):
        # ``@x.mcp_tool(...)`` or FastMCP's ``@server.tool(...)``.
        is_tool = target.attr in {"mcp_tool", "tool"}
    else:
        is_tool = False
    if not is_tool:
        return None
    if call is not None:
        for keyword in call.keywords:
            if (
                keyword.arg == "name"
                and isinstance(keyword.value, ast.Constant)
                and isinstance(keyword.value.value, str)
            ):
                return normalize(keyword.value.value)
        if (
            call.args
            and isinstance(call.args[0], ast.Constant)
            and isinstance(call.args[0].value, str)
        ):
            return normalize(call.args[0].value)
    return func.name


def _adapter_tools(
    func: ast.FunctionDef | ast.AsyncFunctionDef, rel_path: str
) -> list[Tool]:
    """Return the string keys of dict literals returned by ``func``."""
    tools = []
    for node in ast.walk(func):
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict):
            for key in node.value.keys:
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    tools.append(Tool(normalize(key.value), rel_path, key.lineno))
    return tools


def tools_in_source(text: str, rel_path: str) -> list[Tool]:
    """Return the MCP tools defined in one Python source."""
    if (
        "mcp_tool" not in text
        and ".tool" not in text
        and "get_tool_definitions" not in text
    ):
        return []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    tools = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name == "get_tool_definitions":
            tools.extend(_adapter_tools(node, rel_path))
        for decorator in node.decorator_list:
            name = _decorator_tool_name(decorator, node)
            if name is not None:
                tools.append(Tool(name, rel_path, node.lineno))
                break
    return tools


def static_definition_tools(text: str, rel_path: str) -> list[Tool]:
    """Return the names listed in a ``TOOL_DEFINITIONS = [(name, ...), ...]``."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    tools = []
    for node in tree.body:
        if isinstance(node, ast.AnnAssign):
            targets = [node.target]
        elif isinstance(node, ast.Assign):
            targets = node.targets
        else:
            continue
        if not any(
            isinstance(t, ast.Name) and t.id == "TOOL_DEFINITIONS" for t in targets
        ):
            continue
        if not isinstance(node.value, ast.List):
            continue
        for element in node.value.elts:
            if (
                isinstance(element, ast.Tuple)
                and element.elts
                and isinstance(element.elts[0], ast.Constant)
                and isinstance(element.elts[0].value, str)
            ):
                tools.append(
                    Tool(normalize(element.elts[0].value), rel_path, element.lineno)
                )
    return tools


def discover_tools(repo_root: Path) -> dict[str, list[Tool]]:
    """Map every real tool name to where it is defined."""
    found: dict[str, list[Tool]] = {}
    for path in iter_python_sources(repo_root):
        rel = path.relative_to(repo_root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        tools = tools_in_source(text, rel)
        if path == repo_root / STATIC_DEFINITIONS:
            tools += static_definition_tools(text, rel)
        for tool in tools:
            found.setdefault(tool.name, []).append(tool)
    return found


# ── Specification parsing ────────────────────────────────────────────


def _names_from_heading(text: str) -> list[str]:
    """Return tool names if a heading's text names one or more tools."""
    stripped = _TOOL_PREFIX_RE.sub("", text, count=1)
    has_prefix = stripped != text
    if (
        _CODE_LIST.match(stripped)
        or _BARE_LIST.match(stripped)
        or (has_prefix and _ANY_LIST.match(stripped))
    ):
        parts = re.split(_SEPARATOR, stripped)
        return [normalize(p) for p in parts if p.strip()]
    return []


def _names_from_cell(cell: str) -> list[str]:
    spans = _CODE_SPAN.findall(cell)
    candidates = spans or [cell.strip("*_ ")]
    names = []
    for candidate in candidates:
        name = normalize(candidate)
        if _IDENT_RE.match(name):
            names.append(name)
    return names


def _split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def extract_documented_tools(text: str, rel_path: str) -> list[DocumentedTool]:
    """Return the tools a specification documents, in document order."""
    lines = text.splitlines()
    out: list[DocumentedTool] = []
    fence: str | None = None
    in_comment = False
    in_tool_table = False
    expect_invocation = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        lineno = index + 1
        if fence is not None:
            if stripped.startswith(fence):
                fence = None
            continue
        if stripped.startswith(("```", "~~~")):
            fence = stripped[:3]
            in_tool_table = False
            continue
        if in_comment:
            in_comment = "-->" not in stripped
            continue
        if stripped.startswith("<!--") and "-->" not in stripped:
            in_comment = True
            continue

        if in_tool_table:
            if stripped.startswith("|"):
                if not _TABLE_SEPARATOR.match(stripped):
                    for name in _names_from_cell(_split_row(stripped)[0]):
                        out.append(DocumentedTool(name, rel_path, lineno))
                continue
            in_tool_table = False

        heading = _HEADING.match(stripped)
        if heading:
            expect_invocation = bool(_INVOCATION_HEADING.match(heading["text"]))
            for name in _names_from_heading(heading["text"]):
                out.append(DocumentedTool(name, rel_path, lineno))
            continue

        if expect_invocation and stripped:
            expect_invocation = False
            spans = _CODE_SPAN.findall(stripped)
            candidate = spans[0] if spans else stripped
            name = normalize(candidate)
            if _IDENT_RE.match(name):
                out.append(DocumentedTool(name, rel_path, lineno))
            continue

        if (
            stripped.startswith("|")
            and index + 1 < len(lines)
            and _TABLE_SEPARATOR.match(lines[index + 1])
        ):
            header = _split_row(stripped)[0].strip("*_` ").lower()
            in_tool_table = header in TOOL_TABLE_HEADERS
    return out


def spec_scope(rel_spec: str, repo_root: Path) -> str | None:
    """Return the package directory (``src/codomyrmex/<module>/``) a spec covers.

    ``None`` means the specification belongs to no module, so any real tool
    may be documented in it.
    """
    parts = Path(rel_spec).parts[:-1]
    candidate: Path | None = None
    if "docs" in parts and "modules" in parts[parts.index("docs") :]:
        # docs/modules/<module>/ mirrors and nested copies of them.
        index = len(parts) - 1 - parts[::-1].index("modules")
        if index + 1 < len(parts):
            candidate = PACKAGE_DIR / parts[index + 1]
    elif parts[:2] == PACKAGE_DIR.parts:
        trimmed = list(parts)
        while len(trimmed) > 2 and trimmed[-1] == "docs":
            trimmed.pop()
        candidate = Path(*trimmed)
    if candidate is None or candidate == PACKAGE_DIR:
        return None
    if not (repo_root / candidate).is_dir():
        return None
    return candidate.as_posix() + "/"


def check_documented(
    doc: DocumentedTool, scope: str | None, tools: dict[str, list[Tool]]
) -> str | None:
    """Return None when ``doc`` names a real tool of its module, else why not."""
    definitions = tools.get(doc.name)
    if not definitions:
        return "no tool with this name is defined in code"
    static = STATIC_DEFINITIONS.as_posix()
    if scope is None or any(
        t.path.startswith(scope) or t.path == static for t in definitions
    ):
        return None
    where = ", ".join(sorted({t.path for t in definitions}))
    return f"defined outside {scope.rstrip('/')} (in {where})"


def _owning_specs(tool: Tool, scanned_specs: Iterable[str]) -> list[str]:
    """Return scanned specs in the tool's directory or a parent, nearest first."""
    scanned = set(scanned_specs)
    owners = []
    parent = Path(tool.path).parent
    package = PACKAGE_DIR.as_posix()
    while parent.as_posix().startswith(package):
        spec = (parent / SPEC_FILENAME).as_posix()
        if spec in scanned:
            owners.append(spec)
        parent = parent.parent
    return owners


def scan(repo_root: Path, files: Iterable[Path] | None = None) -> Report:
    report = Report(tools=discover_tools(repo_root))
    documented_by_spec: dict[str, set[str]] = {}
    specs = list(files) if files is not None else list(iter_spec_files(repo_root))
    for path in specs:
        rel = path.relative_to(repo_root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        report.specs_scanned += 1
        if SKIP_MARKER in text:
            report.specs_skipped.append(rel)
            documented_by_spec[rel] = set()
            continue
        documented = extract_documented_tools(text, rel)
        report.documented.extend(documented)
        documented_by_spec[rel] = {d.name for d in documented}
        scope = spec_scope(rel, repo_root)
        seen: set[str] = set()
        for doc in documented:
            if doc.name in seen:
                continue
            seen.add(doc.name)
            reason = check_documented(doc, scope, report.tools)
            if reason is not None:
                report.broken.append(Broken(doc, reason))

    if files is None:  # undocumented tools need every specification
        static = STATIC_DEFINITIONS.as_posix()
        seen_pairs: set[tuple[str, str | None]] = set()
        for name in sorted(report.tools):
            for tool in report.tools[name]:
                if tool.path == static:
                    continue  # the bridge's own static tools, not a module's
                owners = _owning_specs(tool, documented_by_spec)
                if any(name in documented_by_spec[o] for o in owners):
                    continue
                owner = owners[0] if owners else None
                if (name, owner) not in seen_pairs:
                    seen_pairs.add((name, owner))
                    report.undocumented.append((tool, owner))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--output", type=Path, help="Also write the JSON report here")
    parser.add_argument(
        "--fail-on-broken",
        action="store_true",
        help="Exit 1 when a specification documents a tool its module does not define",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help=f"{SPEC_FILENAME} files to check (default: all; undocumented "
        "tools are only reported for a full scan)",
    )
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
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
            f"Scanned {data['specs_scanned']} MCP tool specifications "
            f"({len(report.specs_skipped)} skipped): "
            f"{data['documented_tools']} documented tools, "
            f"{data['broken_tools']} broken; "
            f"{data['real_tools']} real tools, "
            f"{data['undocumented_tools']} undocumented (informational)."
        )
        if report.broken:
            print("\nDocumented tools that their module does not define:")
            for broken in report.broken:
                doc = broken.tool
                print(f"  {doc.path}:{doc.line}  {doc.name}\n    {broken.reason}")
        if report.undocumented:
            print("\nReal tools missing from their module's specification:")
            by_spec: dict[str, list[str]] = {}
            for tool, spec in report.undocumented:
                by_spec.setdefault(spec or "(no specification)", []).append(tool.name)
            for spec, names in sorted(by_spec.items()):
                print(f"  {spec}: {', '.join(sorted(set(names)))}")
    return 1 if args.fail_on_broken and report.broken else 0


if __name__ == "__main__":
    sys.exit(main())
