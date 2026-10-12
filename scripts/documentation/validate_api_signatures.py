#!/usr/bin/env python3
"""Check that signatures in API_SPECIFICATION.md files match the real code.

Module API specifications show call signatures in headings such as::

    ### Function: `create_pipeline(config: Mapping | str) -> Pipeline`

and in declaration-style Python blocks (``def name(...): ...`` or a block
that holds only ``ClassName(param: type, ...)``). Those signatures drift when
a function gains, loses or renames a parameter, and a reader who copies them
gets a ``TypeError``. This gate resolves every documented callable inside the
specification's own package (``codomyrmex.<module>``; methods as
``Class.method``, or a bare method name under a heading that names the class)
and compares parameter *names* with :func:`inspect.signature`. It reports:

* a documented parameter that the callable does not accept (not reported when
  the callable takes ``**kwargs``), and
* a required parameter of the callable that the documentation leaves out.

Annotations, defaults and parameter order are not compared. Anything the
checker cannot parse or resolve with confidence is skipped rather than
guessed: a name defined in several submodules, a heading that is not valid
Python, ``name()`` used as a plain reference, a method of a class that does
not resolve, or an illustrative ``def`` with a real body. Skipped signatures
are listed under ``unresolved`` in the JSON report but never fail the gate.

A heading (with everything nested under it) or a fenced block is skipped when
the line directly above it is::

    <!-- docs-check: skip-signatures -->

Usage::

    uv run python scripts/documentation/validate_api_signatures.py \\
        --repo-root . --fail-on-broken
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import importlib
import importlib.util
import inspect
import json
import re
import sys
import textwrap
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType

SKIP_MARKER = "<!-- docs-check: skip-signatures -->"
SPEC_NAME = "API_SPECIFICATION.md"
# ``pycon`` sessions show calls, not declarations.
PYTHON_FENCE_LANGS = frozenset({"python", "py", "python3"})
SELF_NAMES = frozenset({"self", "cls"})

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
EXCLUDED_PREFIXES = (
    "src/codomyrmex/agents/hermes/evolution/",
    "src/codomyrmex/agents/open_gauss/",
)
EXCLUDED_MODULES = (
    "codomyrmex.agents.hermes.evolution",
    "codomyrmex.agents.open_gauss",
)

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
CODE_SPAN_RE = re.compile(r"`([^`]+)`")
SIG_NAME_RE = re.compile(
    r"^(?:async\s+)?(?:def\s+)?([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*\("
)
IDENT_RE = re.compile(r"^[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*$")
# ``### `create_line_plot()` `` names a function; it does not claim "no arguments".
BARE_REFERENCE_RE = re.compile(r"^[A-Za-z_][\w.]*\(\s*\)$")
NUMBERING_RE = re.compile(r"^\d+(?:\.\d+)*\.?\s+")
LABEL_RE = re.compile(r"^[A-Za-z][\w /-]*?(?:\s+\d+)?:\s*")
TRAILING_PAREN_RE = re.compile(r"\s*\([^)]*\)\s*$")
TRAILING_KIND_RE = re.compile(r"\s+(?:[Cc]lass|[Ee]num|[Dd]ataclass)$")

# Why the signatures under a heading are not checked.
SKIPPED = "skip marker"
UNRESOLVED_SECTION = "section names unresolved code"


# ---------------------------------------------------------------------------
# Documented signatures
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DocParams:
    """Parameter names as documented (a leading ``self``/``cls`` included)."""

    names: tuple[str, ...]
    var_positional: str | None = None
    var_keyword: str | None = None

    @property
    def leading_self(self) -> str | None:
        if self.names and self.names[0] in SELF_NAMES:
            return self.names[0]
        return None

    def without_self(self) -> DocParams:
        return DocParams(self.names[1:], self.var_positional, self.var_keyword)


@dataclass(frozen=True)
class DocSignature:
    """One documented call signature.

    ``target`` is the dotted name as written. ``context`` is the class or
    module named by the enclosing heading (None at module level) and
    ``blocked`` is set when the signature sits under a heading that names
    code the checker could not resolve.
    """

    line: int
    target: str
    params: DocParams
    text: str
    context: str | None = None
    blocked: str | None = None


def _params_from_arguments(args: ast.arguments) -> DocParams:
    return DocParams(
        names=tuple(a.arg for a in (*args.posonlyargs, *args.args, *args.kwonlyargs)),
        var_positional=args.vararg.arg if args.vararg else None,
        var_keyword=args.kwarg.arg if args.kwarg else None,
    )


@dataclass(frozen=True)
class _Parsed:
    name: str
    args: ast.arguments
    returns: bool

    @property
    def annotated(self) -> bool:
        """True when the text is unmistakably a declaration, not a call."""
        if self.returns:
            return True
        every = (
            *self.args.posonlyargs,
            *self.args.args,
            *self.args.kwonlyargs,
            self.args.vararg,
            self.args.kwarg,
        )
        return any(a is not None and a.annotation is not None for a in every)


def _parse_signature(text: str) -> _Parsed | None:
    text = text.strip()
    match = SIG_NAME_RE.match(text)
    if match is None:
        return None
    open_at = match.end() - 1
    depth = 0
    close_at = -1
    for index in range(open_at, len(text)):
        char = text[index]
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
            if depth == 0:
                close_at = index
                break
    if close_at < 0:
        return None
    rest = text[close_at + 1 :].strip().removesuffix(":").strip()
    if rest and not rest.startswith("->"):
        return None
    try:
        if rest:
            ast.parse(rest[2:].strip(), mode="eval")
        tree = ast.parse(f"def _documented({text[open_at + 1 : close_at]}): pass")
    except SyntaxError:
        return None
    func = tree.body[0]
    if not isinstance(func, ast.FunctionDef):
        return None
    return _Parsed(match.group(1), func.args, bool(rest))


def parse_signature_text(text: str) -> tuple[str, DocParams] | None:
    """Parse ``name(params) -> ret`` into ``(name, DocParams)``.

    Returns None for anything that is not a plain call signature, e.g.
    ``name(...)``, prose in the parameter list or trailing text after the
    closing parenthesis other than a return annotation.
    """
    parsed = _parse_signature(text)
    if parsed is None:
        return None
    return parsed.name, _params_from_arguments(parsed.args)


def _is_declaration(body: list[ast.stmt]) -> bool:
    """True when a ``def`` body is only a docstring, ``...``, ``pass`` or
    ``raise NotImplementedError``: a declaration, not an example."""
    for stmt in body:
        if isinstance(stmt, ast.Pass):
            continue
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
            if stmt.value.value is Ellipsis or isinstance(stmt.value.value, str):
                continue
        if isinstance(stmt, ast.Raise) and stmt.exc is not None:
            exc = stmt.exc.func if isinstance(stmt.exc, ast.Call) else stmt.exc
            if isinstance(exc, ast.Name) and exc.id == "NotImplementedError":
                continue
        return False
    return True


def _decorator_names(func: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    names = set()
    for deco in func.decorator_list:
        node = deco.func if isinstance(deco, ast.Call) else deco
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
    return names


def _block_signatures(
    block: list[str], first_line: int, context: str | None, blocked: str | None
) -> Iterator[DocSignature]:
    """Yield the signatures declared in one fenced Python block."""
    source = textwrap.dedent("\n".join(block))
    try:
        tree = ast.parse(source)
    except SyntaxError:
        for offset, parsed, text in _listing_signatures(source.splitlines()):
            yield DocSignature(
                line=first_line + offset,
                target=parsed.name,
                params=_params_from_arguments(parsed.args),
                text=text,
                context=context,
                blocked=blocked,
            )
        return

    def emit(
        func: ast.FunctionDef | ast.AsyncFunctionDef,
        target: str,
        ctx: str | None,
        is_blocked: str | None,
    ) -> Iterator[DocSignature]:
        if not _is_declaration(func.body):
            return
        # Properties and overloads are not call signatures to compare.
        if _decorator_names(func) & {"property", "setter", "deleter", "overload"}:
            return
        yield DocSignature(
            line=first_line + func.lineno - 1,
            target=target,
            params=_params_from_arguments(func.args),
            text=block[func.lineno - 1].strip(),
            context=ctx,
            blocked=is_blocked,
        )

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield from emit(node, node.name, context, blocked)
        elif isinstance(node, ast.ClassDef):
            # ``class Name:`` names its own target, whatever the heading says.
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    yield from emit(item, f"{node.name}.{item.name}", None, None)


def _listing_signatures(lines: list[str]) -> list[tuple[int, _Parsed, str]]:
    """Parse a block that only lists signatures without ``def``.

    For example ``ClassName(param: type = 1)``, a bodiless
    ``def name(param: type) -> ret`` or a sequence of
    ``name(param: type) -> ret`` lines, each optionally followed by an
    indented docstring. Every column-0 statement must be such a signature
    carrying an annotation (so an example call such as ``run(path)`` is never
    mistaken for one); otherwise the whole block is ignored.
    """
    found: list[tuple[int, _Parsed, str]] = []
    k = 0
    while k < len(lines):
        line = lines[k]
        if not line.strip() or line.lstrip().startswith("#"):
            k += 1
            continue
        if line[0].isspace():
            if not found:
                return []
            k += 1  # docstring or continuation of the previous entry
            continue
        if not SIG_NAME_RE.match(line):
            return []
        start = k
        text = line.strip()
        while text.count("(") > text.count(")") and k + 1 < len(lines):
            k += 1
            text += " " + lines[k].strip()
        parsed = _parse_signature(text)
        if parsed is None or not parsed.annotated:
            return []
        found.append((start, parsed, text.replace("( ", "(").replace(", )", ")")))
        k += 1
    return found


@dataclass
class _Section:
    level: int
    context: str | None = None
    blocked: str | None = None


def _heading_class_candidate(text: str) -> tuple[str, bool] | None:
    """Return ``(name, strong)`` when a heading names one class or module.

    ``strong`` is True when the heading clearly names code (a code span, a
    ``Class:`` style label, a ``Foo Class`` suffix or a CamelCase identifier)
    rather than a plain word such as "Methods".
    """
    spans = CODE_SPAN_RE.findall(text)
    if spans:
        if len(spans) == 1 and IDENT_RE.match(spans[0].strip()):
            return spans[0].strip(), True
        return None
    stripped = NUMBERING_RE.sub("", text.strip())
    labelled = LABEL_RE.match(stripped) is not None
    stripped = LABEL_RE.sub("", stripped)
    stripped = TRAILING_PAREN_RE.sub("", stripped).strip()
    suffixed = TRAILING_KIND_RE.search(stripped) is not None
    stripped = TRAILING_KIND_RE.sub("", stripped)
    if not IDENT_RE.match(stripped):
        return None
    camel = sum(ch.isupper() for ch in stripped) >= 2 and any(
        ch.islower() for ch in stripped
    )
    return stripped, labelled or suffixed or camel


def extract_signatures(
    text: str, resolve_context: Callable[[str], str | None] | None = None
) -> Iterator[DocSignature]:
    """Yield documented signatures from Markdown ``text``.

    ``resolve_context`` returns ``"class"``, ``"module"``, ``"other"`` or
    None (unresolved) for a name. It decides whether a heading such as
    ``### Pipeline`` opens a class section whose bare method headings belong
    to ``Pipeline``; a heading that clearly names code which does not resolve
    blocks the signatures nested under it.
    """
    lines = text.splitlines()
    sections: list[_Section] = []

    def current() -> tuple[str | None, str | None]:
        for section in reversed(sections):
            if section.blocked is not None:
                return None, section.blocked
            if section.context is not None:
                return section.context, None
        return None, None

    def kind_of(name: str) -> str | None:
        return resolve_context(name) if resolve_context is not None else None

    i = 0
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        skip = i > 0 and lines[i - 1].strip() == SKIP_MARKER
        if stripped.startswith("```"):
            lang = stripped.lstrip("`").strip().split(" ")[0].lower()
            start = i + 1
            j = start
            while j < len(lines) and not lines[j].strip().startswith("```"):
                j += 1
            context, blocked = current()
            if lang in PYTHON_FENCE_LANGS and not skip and blocked != SKIPPED:
                yield from _block_signatures(
                    lines[start:j], start + 1, context, blocked
                )
            i = j + 1
            continue
        match = HEADING_RE.match(raw)
        if match is None:
            i += 1
            continue
        level = len(match.group(1))
        heading = match.group(2)
        while sections and sections[-1].level >= level:
            sections.pop()
        section = _Section(level, blocked=SKIPPED if skip else None)
        sections.append(section)
        context, blocked = current()
        if blocked == SKIPPED:
            i += 1
            continue
        spans = CODE_SPAN_RE.findall(heading)
        signatures: list[tuple[str, str, DocParams]] = []
        references: list[str] = []
        for span in spans:
            parsed = parse_signature_text(span)
            if parsed is not None and BARE_REFERENCE_RE.match(span.strip()):
                references.append(parsed[0])
            elif parsed is not None:
                signatures.append((span.strip(), *parsed))
        for span, target, params in signatures:
            yield DocSignature(i + 1, target, params, span, context, blocked)
        if blocked is None:
            if len(signatures) == 1:
                # ``### `Pipeline(name: str)` `` documents the class itself.
                if kind_of(signatures[0][1]) == "class":
                    section.context = signatures[0][1]
            elif not signatures:
                candidate: tuple[str, bool] | None
                if len(spans) == 1 and references:
                    candidate = (references[0], True)
                else:
                    candidate = _heading_class_candidate(heading)
                if candidate is not None:
                    name, strong = candidate
                    kind = kind_of(name)
                    if kind in ("class", "module"):
                        section.context = name
                    elif kind is None and strong:
                        section.blocked = UNRESOLVED_SECTION
        i += 1


# ---------------------------------------------------------------------------
# Resolution against the package
# ---------------------------------------------------------------------------


def _is_dunder(name: str) -> bool:
    return name.startswith("__") and name.endswith("__")


def _is_module(name: str) -> bool:
    """True when ``name`` is an importable module or regular package."""
    if name.startswith(EXCLUDED_MODULES):
        return False
    try:
        spec = importlib.util.find_spec(name)
    except (ImportError, ValueError):
        return False
    if spec is None or spec.origin in (None, "namespace"):
        return False
    return True


class PackageResolver:
    """Resolve documented names inside one ``codomyrmex`` package.

    A name is looked up in the package namespace first, then among the
    top-level ``def``/``class`` statements of the package's own source files
    (found statically, so unrelated submodules are never imported). A name
    defined in more than one submodule is ambiguous and left unresolved.
    """

    def __init__(self, package: str) -> None:
        self.package = package
        self._module: ModuleType | None = None
        self._import_error: str | None = None
        self._index: dict[str, list[str]] | None = None
        self._cache: dict[str, object] = {}

    @property
    def module(self) -> ModuleType | None:
        if self._module is None and self._import_error is None:
            try:
                self._module = importlib.import_module(self.package)
            except Exception as exc:  # report any import-time failure
                self._import_error = f"{type(exc).__name__}: {exc}"[:200]
        return self._module

    @property
    def import_error(self) -> str | None:
        _ = self.module
        return self._import_error

    def _static_index(self) -> dict[str, list[str]]:
        """Map top-level ``def``/``class`` names to the submodules defining them."""
        if self._index is not None:
            return self._index
        index: dict[str, list[str]] = {}
        for base in getattr(self.module, "__path__", None) or []:
            base_path = Path(base)
            for py in sorted(base_path.rglob("*.py")):
                parts = list(py.relative_to(base_path).with_suffix("").parts)
                if EXCLUDED_PARTS.intersection(parts) or "__main__" in parts:
                    continue
                # Only files inside regular packages are importable modules.
                if any(
                    not (base_path / Path(*parts[:depth]) / "__init__.py").is_file()
                    for depth in range(1, len(parts))
                ):
                    continue
                if parts[-1] == "__init__":
                    parts = parts[:-1]
                dotted = ".".join([self.package, *parts])
                if dotted.startswith(EXCLUDED_MODULES):
                    continue
                try:
                    tree = ast.parse(py.read_text(encoding="utf-8", errors="replace"))
                except SyntaxError:
                    continue
                for node in tree.body:
                    if isinstance(
                        node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                    ):
                        owners = index.setdefault(node.name, [])
                        if dotted not in owners:
                            owners.append(dotted)
        self._index = index
        return index

    def _lookup(self, name: str) -> object | None:
        if name in self._cache:
            return self._cache[name]
        found: object | None = None
        module = self.module
        # Every module object has ``__lt__``, ``__init__``...; a documented
        # dunder only makes sense on a class.
        if module is not None and not _is_dunder(name):
            if hasattr(module, name):
                found = getattr(module, name)
            else:
                owners = self._static_index().get(name, [])
                if len(owners) == 1:
                    try:
                        found = getattr(importlib.import_module(owners[0]), name, None)
                    except Exception:
                        found = None
        self._cache[name] = found
        return found

    def resolve(self, dotted: str, context: str | None = None) -> object | None:
        """Resolve ``dotted`` (optionally relative to a class/module ``context``)."""
        parts = dotted.split(".")
        if dotted.startswith(self.package + "."):
            # Longest importable prefix (down to the package itself) wins.
            for cut in range(len(parts), self.package.count("."), -1):
                with contextlib.suppress(Exception):
                    obj: object = importlib.import_module(".".join(parts[:cut]))
                    for attr in parts[cut:]:
                        obj = getattr(obj, attr)
                    return obj
            return None
        if context is not None and len(parts) == 1:
            owner = self.resolve(context)
            if owner is None or (_is_dunder(parts[0]) and not inspect.isclass(owner)):
                return None
            if inspect.isclass(owner):
                try:
                    inspect.getattr_static(owner, parts[0])
                except AttributeError:
                    return None
            return getattr(owner, parts[0], None)
        found = self._lookup(parts[0])
        rest = parts[1:]
        if found is None and self.module is not None:
            # ``graphy.signatures`` names a submodule of the package.
            for cut in range(len(parts), 0, -1):
                name = ".".join([self.package, *parts[:cut]])
                if _is_module(name):
                    with contextlib.suppress(Exception):
                        found = importlib.import_module(name)
                        rest = parts[cut:]
                        break
        for attr in rest:
            if found is None:
                return None
            found = getattr(found, attr, None)
        return found

    def context_kind(self, name: str) -> str | None:
        found = self.resolve(name)
        if found is None:
            return None
        if inspect.isclass(found):
            return "class"
        if inspect.ismodule(found):
            return "module"
        return "other"


@dataclass(frozen=True)
class RealParams:
    """Parameter names of the real callable (``self``/``cls`` removed)."""

    names: tuple[str, ...]
    required: tuple[str, ...]
    var_positional: str | None
    var_keyword: str | None
    text: str


def _owner_and_attr(sig: DocSignature) -> tuple[str | None, str]:
    parts = sig.target.split(".")
    if len(parts) > 1:
        return ".".join(parts[:-1]), parts[-1]
    return sig.context, parts[0]


def real_params(
    resolver: PackageResolver, sig: DocSignature
) -> tuple[RealParams, DocParams] | str:
    """Return the real and the comparable documented parameters.

    A string return value is the reason the signature was skipped.
    """
    owner_name, attr = _owner_and_attr(sig)
    if owner_name is not None and owner_name.split(".")[-1] == sig.target:
        # ``ClassName(...)`` shown inside the ``ClassName`` section.
        owner_name = None
    owner = resolver.resolve(owner_name) if owner_name else None
    if owner_name is not None and owner is None:
        return "not found"
    target = (
        resolver.resolve(attr, owner_name) if owner_name else resolver.resolve(attr)
    )
    if target is None:
        return "not found"

    drop_first = False
    if inspect.isclass(owner):
        static = inspect.getattr_static(owner, attr)
        if isinstance(static, (staticmethod, classmethod)):
            pass  # getattr() already unwrapped or bound these
        elif inspect.isfunction(static):
            drop_first = True
        elif not callable(static):
            return "property or attribute"
    method_like = inspect.isclass(owner) or inspect.isclass(target)
    documented = sig.params
    if documented.leading_self is not None:
        if method_like:
            documented = documented.without_self()
        elif documented.leading_self == "self":
            return "documented with self but not a method"
    if inspect.isclass(target):
        # ``PlotType(Enum)`` names base classes; it is not a constructor call.
        bases = {base.__name__ for base in target.__mro__}
        if documented.names and set(documented.names) <= bases:
            return "base-class list"
    if not callable(target):
        return "not callable"
    try:
        signature = inspect.signature(target)
    except (TypeError, ValueError):
        return "no introspectable signature"

    params = list(signature.parameters.values())
    positional = (
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
    )
    if drop_first and params and params[0].kind in positional:
        params = params[1:]
    names: list[str] = []
    required: list[str] = []
    var_positional = var_keyword = None
    for param in params:
        if param.kind is inspect.Parameter.VAR_POSITIONAL:
            var_positional = param.name
        elif param.kind is inspect.Parameter.VAR_KEYWORD:
            var_keyword = param.name
        else:
            names.append(param.name)
            if param.default is inspect.Parameter.empty:
                required.append(param.name)
    real = RealParams(
        tuple(names),
        tuple(required),
        var_positional,
        var_keyword,
        f"{attr}{_names_only(params)}",
    )
    return real, documented


def _names_only(params: list[inspect.Parameter]) -> str:
    """Render parameters by name only, e.g. ``(a, b=…, *, c, **kw)``."""
    pieces = []
    star_shown = False
    for param in params:
        if param.kind is inspect.Parameter.VAR_POSITIONAL:
            pieces.append(f"*{param.name}")
            star_shown = True
        elif param.kind is inspect.Parameter.VAR_KEYWORD:
            pieces.append(f"**{param.name}")
        else:
            if param.kind is inspect.Parameter.KEYWORD_ONLY and not star_shown:
                pieces.append("*")
                star_shown = True
            default = "" if param.default is inspect.Parameter.empty else "=…"
            pieces.append(f"{param.name}{default}")
    return f"({', '.join(pieces)})"


def compare(doc: DocParams, real: RealParams) -> tuple[list[str], list[str]]:
    """Return ``(not_accepted, missing_required)`` parameter names."""
    known = set(real.names) | ({real.var_positional, real.var_keyword} - {None})
    not_accepted: list[str] = []
    if real.var_keyword is None:
        not_accepted.extend(name for name in doc.names if name not in known)
        if doc.var_keyword is not None:
            not_accepted.append(f"**{doc.var_keyword}")
    if doc.var_positional is not None and real.var_positional is None:
        not_accepted.append(f"*{doc.var_positional}")
    documented = set(doc.names) | ({doc.var_positional, doc.var_keyword} - {None})
    missing = [name for name in real.required if name not in documented]
    return not_accepted, missing


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------


@dataclass
class Finding:
    path: str
    line: int
    package: str
    target: str
    documented: str
    actual: str
    not_accepted: list[str]
    missing: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "location": f"{self.path}:{self.line}",
            "package": self.package,
            "target": self.target,
            "documented": self.documented,
            "actual": self.actual,
            "not_accepted": self.not_accepted,
            "missing_required": self.missing,
        }


@dataclass
class Report:
    files_scanned: int = 0
    signatures_found: int = 0
    signatures_checked: int = 0
    findings: list[Finding] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)
    skipped_files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "files_scanned": self.files_scanned,
            "signatures_found": self.signatures_found,
            "signatures_checked": self.signatures_checked,
            "broken_signatures": len(self.findings),
            "broken": [finding.to_dict() for finding in self.findings],
            "unresolved_signatures": len(self.unresolved),
            "unresolved": self.unresolved,
            "skipped_files": self.skipped_files,
        }


def iter_spec_files(repo_root: Path) -> Iterator[Path]:
    for path in sorted(repo_root.rglob(SPEC_NAME)):
        rel = path.relative_to(repo_root)
        if EXCLUDED_PARTS.intersection(rel.parts):
            continue
        if rel.as_posix().startswith(EXCLUDED_PREFIXES):
            continue
        yield path


def _is_package(name: str) -> bool:
    """True for a regular package (a directory with ``__init__.py``).

    Plain folders such as ``docs/`` import as namespace packages; they are
    not the code a specification documents.
    """
    try:
        spec = importlib.util.find_spec(name)
    except (ImportError, ValueError):
        return False
    return (
        spec is not None
        and spec.submodule_search_locations is not None
        and (spec.origin or "").endswith("__init__.py")
    )


def package_for(rel: Path) -> str | None:
    """Map a spec path (relative to the repo root) to the package it documents.

    ``src/codomyrmex/<pkg…>/API_SPECIFICATION.md`` documents
    ``codomyrmex.<pkg…>`` (a ``docs/`` folder documents its parent) and
    ``docs/modules/<module>/API_SPECIFICATION.md`` mirrors
    ``codomyrmex.<module>``.
    """
    parts = rel.parts[:-1]
    if parts[:2] == ("src", "codomyrmex"):
        pkg_parts = list(parts[1:])
        if (
            len(pkg_parts) > 2
            and pkg_parts[-1] == "docs"
            and not _is_package(".".join(pkg_parts))
        ):
            pkg_parts = pkg_parts[:-1]
    elif parts[:2] == ("docs", "modules") and len(parts) == 3:
        pkg_parts = ["codomyrmex", parts[2]]
    else:
        return None
    if not all(IDENT_RE.match(part) for part in pkg_parts):
        return None
    name = ".".join(pkg_parts)
    if name.startswith(EXCLUDED_MODULES) or not _is_package(name):
        return None
    return name


def _display_target(sig: DocSignature) -> str:
    owner, attr = _owner_and_attr(sig)
    if owner is None or owner.split(".")[-1] == sig.target:
        return sig.target
    return f"{owner}.{attr}"


def check_text(
    text: str,
    package: str,
    rel_path: str,
    report: Report,
    resolvers: dict[str, PackageResolver] | None = None,
) -> None:
    """Check one specification's text against ``package``."""
    resolvers = {} if resolvers is None else resolvers
    resolver = resolvers.setdefault(package, PackageResolver(package))
    if resolver.import_error is not None:
        report.skipped_files.append(f"{rel_path}: {resolver.import_error}")
        return
    for sig in extract_signatures(text, resolver.context_kind):
        report.signatures_found += 1
        where = f"{rel_path}:{sig.line} {_display_target(sig)}"
        if sig.blocked is not None:
            report.unresolved.append(f"{where} ({sig.blocked})")
            continue
        result = real_params(resolver, sig)
        if isinstance(result, str):
            report.unresolved.append(f"{where} ({result})")
            continue
        real, documented = result
        report.signatures_checked += 1
        not_accepted, missing = compare(documented, real)
        if not_accepted or missing:
            report.findings.append(
                Finding(
                    path=rel_path,
                    line=sig.line,
                    package=package,
                    target=_display_target(sig),
                    documented=sig.text,
                    actual=real.text,
                    not_accepted=not_accepted,
                    missing=missing,
                )
            )


def scan(repo_root: Path, files: Iterable[Path] | None = None) -> Report:
    report = Report()
    resolvers: dict[str, PackageResolver] = {}
    # Some modules print on import; keep stdout clean for --format json.
    with contextlib.redirect_stdout(sys.stderr):
        for path in files if files is not None else iter_spec_files(repo_root):
            report.files_scanned += 1
            rel = path.relative_to(repo_root)
            package = package_for(rel)
            if package is None:
                report.skipped_files.append(f"{rel.as_posix()}: no matching package")
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            check_text(text, package, rel.as_posix(), report, resolvers)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--output", type=Path, help="Also write the JSON report here")
    parser.add_argument(
        "--fail-on-broken",
        action="store_true",
        help="Exit 1 when any documented signature disagrees with the code",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="API_SPECIFICATION.md files to check (default: all)",
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
            f"Scanned {data['files_scanned']} API specifications: "
            f"{data['signatures_checked']} of {data['signatures_found']} documented "
            f"signatures resolved and checked, {data['broken_signatures']} broken "
            f"({data['unresolved_signatures']} skipped as unresolved)."
        )
        for finding in report.findings:
            print(f"\n  {finding.path}:{finding.line}  {finding.target}")
            print(f"    documented: {finding.documented}")
            print(f"    actual:     {finding.actual}")
            if finding.not_accepted:
                print(
                    f"    not accepted by the code: {', '.join(finding.not_accepted)}"
                )
            if finding.missing:
                print(f"    required but undocumented: {', '.join(finding.missing)}")
    return 1 if args.fail_on_broken and report.findings else 0


if __name__ == "__main__":
    sys.exit(main())
