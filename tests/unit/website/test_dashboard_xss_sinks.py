"""Regression tests for DOM XSS sinks in the website dashboard.

The dashboard pages build markup in inline ``<script>`` blocks (and in
``assets/js/app.js``) from API responses, repository files, tool output, LLM
responses and user input. Every value interpolated into an HTML sink must go
through the shared ``escapeHtml`` helper defined in ``templates/base.html`` (or
``DOMPurify.sanitize`` for rendered markdown); constant markup is allowed.

The checker is a small JavaScript tokenizer plus a conservative expression
classifier. Anything it cannot prove safe is reported, so a new sink that
interpolates a variable without escaping fails this suite. Variables named
``html`` or ``*Html`` are treated as holding markup: every ``=``/``+=`` to them
is checked like a sink, and binding them as a function parameter or loop
variable is reported.

Zero-mock: the checks read the real templates and render them with the real
Jinja2 environment used by ``WebsiteGenerator``. Node.js checks run only when a
``node`` binary is installed.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

import pytest

from codomyrmex.website.generator import WebsiteGenerator

WEBSITE_DIR = Path(__file__).resolve().parents[3] / "src" / "codomyrmex" / "website"
TEMPLATES_DIR = WEBSITE_DIR / "templates"
APP_JS = WEBSITE_DIR / "assets" / "js" / "app.js"
TEMPLATE_FILES = sorted(TEMPLATES_DIR.glob("*.html"))
SCRIPT_SOURCES = [*TEMPLATE_FILES, APP_JS]

ESCAPE_HELPER = "escapeHtml"
# Variables named ``html`` or ``...Html`` hold markup; every assignment to one is
# checked like a sink, so reading them back into innerHTML is safe.
HTML_VAR_RE = re.compile(r"^(?:html|[A-Za-z_$][\w$]*Html)$")
HTML_PROPERTIES = {"innerHTML", "outerHTML"}

requires_node = pytest.mark.skipif(
    shutil.which("node") is None, reason="node binary not installed"
)


# ---------------------------------------------------------------------------
# Script extraction
# ---------------------------------------------------------------------------

_SCRIPT_RE = re.compile(r"<script\b([^>]*)>(.*?)</script>", re.DOTALL | re.IGNORECASE)


@dataclass(frozen=True)
class Script:
    path: Path
    start_line: int
    source: str


def extract_scripts(path: Path) -> list[Script]:
    """Return the inline scripts of a template, or the whole file for ``.js``."""
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".js":
        return [Script(path, 1, text)]
    scripts = []
    for match in _SCRIPT_RE.finditer(text):
        if re.search(r"\bsrc\s*=", match.group(1)):
            continue
        start_line = text.count("\n", 0, match.start(2)) + 1
        scripts.append(Script(path, start_line, match.group(2)))
    return scripts


# ---------------------------------------------------------------------------
# Minimal JavaScript tokenizer
# ---------------------------------------------------------------------------


@dataclass
class Token:
    kind: str  # name | num | str | tpl | regex | punct
    value: str
    line: int
    # For template literals: one token list per ``${...}`` interpolation.
    parts: list[list[Token]] = field(default_factory=list)


# cast: with key=len, ty infers list[Sized] for sorted().
_PUNCTUATORS = cast("list[str]", sorted(
    [
        ">>>=", "...", "===", "!==", "**=", "<<=", ">>=", ">>>", "&&=", "||=",
        "??=", "=>", "==", "!=", "<=", ">=", "&&", "||", "??", "?.", "++", "--",
        "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "**", "<<", ">>", "{",
        "}", "(", ")", "[", "]", ";", ",", "<", ">", "+", "-", "*", "/", "%",
        "&", "|", "^", "!", "~", "?", ":", "=", ".",
    ],
    key=len,
    reverse=True,
))  # fmt: skip
_NAME_RE = re.compile(r"[A-Za-z_$][\w$]*")
_NUM_RE = re.compile(r"0[xX][0-9a-fA-F]+|(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?")
# After these keywords a ``/`` starts a regex literal rather than a division.
_REGEX_PREFIX_KEYWORDS = {
    "return", "typeof", "case", "in", "of", "new", "delete", "void", "throw",
    "instanceof", "yield", "await", "else", "do",
}  # fmt: skip


class JSTokenizeError(ValueError):
    pass


class _Tokenizer:
    def __init__(self, src: str, line: int) -> None:
        self.src = src
        self.pos = 0
        self.line = line

    def _advance(self, new_pos: int) -> None:
        self.line += self.src.count("\n", self.pos, new_pos)
        self.pos = new_pos

    def _error(self, message: str) -> JSTokenizeError:
        return JSTokenizeError(f"line {self.line}: {message}")

    def tokenize(self, *, until_brace: bool = False) -> list[Token]:
        """Tokenize until EOF, or until the ``}`` closing a ``${`` interpolation."""
        tokens: list[Token] = []
        depth = 0
        src = self.src
        while True:
            self._skip_space_and_comments()
            if self.pos >= len(src):
                if until_brace:
                    raise self._error("unterminated template interpolation")
                return tokens
            ch = src[self.pos]
            if until_brace and ch == "}" and depth == 0:
                self._advance(self.pos + 1)
                return tokens
            if ch in "'\"":
                tokens.append(self._string(ch))
            elif ch == "`":
                tokens.append(self._template())
            elif ch == "/" and self._regex_allowed(tokens):
                tokens.append(self._regex())
            elif (m := _NUM_RE.match(src, self.pos)) and (
                ch.isdigit()
                or (ch == "." and src[self.pos + 1 : self.pos + 2].isdigit())
            ):
                tokens.append(Token("num", m.group(), self.line))
                self._advance(m.end())
            elif m := _NAME_RE.match(src, self.pos):
                tokens.append(Token("name", m.group(), self.line))
                self._advance(m.end())
            else:
                punct = next(
                    (p for p in _PUNCTUATORS if src.startswith(p, self.pos)), None
                )
                if punct is None:
                    raise self._error(f"unexpected character {ch!r}")
                if punct == "?." and src[self.pos + 2 : self.pos + 3].isdigit():
                    punct = "?"
                if punct in "([{":
                    depth += 1
                elif punct in ")]}":
                    depth -= 1
                tokens.append(Token("punct", punct, self.line))
                self._advance(self.pos + len(punct))

    def _skip_space_and_comments(self) -> None:
        src = self.src
        while self.pos < len(src):
            if src[self.pos].isspace():
                self._advance(self.pos + 1)
            elif src.startswith("//", self.pos):
                end = src.find("\n", self.pos)
                self._advance(len(src) if end == -1 else end)
            elif src.startswith("/*", self.pos):
                end = src.find("*/", self.pos + 2)
                if end == -1:
                    raise self._error("unterminated block comment")
                self._advance(end + 2)
            else:
                return

    @staticmethod
    def _regex_allowed(tokens: list[Token]) -> bool:
        if not tokens:
            return True
        prev = tokens[-1]
        if prev.kind == "name":
            return prev.value in _REGEX_PREFIX_KEYWORDS
        if prev.kind == "punct":
            return prev.value not in {")", "]", "}"}
        return False

    def _string(self, quote: str) -> Token:
        src, i, line = self.src, self.pos + 1, self.line
        chars = []
        while i < len(src) and src[i] != quote:
            if src[i] == "\n":
                raise self._error("newline in string literal")
            if src[i] == "\\":
                chars.append(src[i : i + 2])
                i += 2
                continue
            chars.append(src[i])
            i += 1
        if i >= len(src):
            raise self._error("unterminated string literal")
        self._advance(i + 1)
        return Token("str", "".join(chars), line)

    def _template(self) -> Token:
        token = Token("tpl", "", self.line)
        chars = []
        self._advance(self.pos + 1)
        src = self.src
        while True:
            if self.pos >= len(src):
                raise self._error("unterminated template literal")
            ch = src[self.pos]
            if ch == "\\":
                chars.append(src[self.pos : self.pos + 2])
                self._advance(self.pos + 2)
            elif ch == "`":
                self._advance(self.pos + 1)
                token.value = "".join(chars)
                return token
            elif src.startswith("${", self.pos):
                self._advance(self.pos + 2)
                token.parts.append(self.tokenize(until_brace=True))
                chars.append("${}")
            else:
                chars.append(ch)
                self._advance(self.pos + 1)

    def _regex(self) -> Token:
        src, i, line = self.src, self.pos + 1, self.line
        in_class = False
        while i < len(src):
            ch = src[i]
            if ch == "\\":
                i += 2
                continue
            if ch == "\n":
                break
            if ch == "[":
                in_class = True
            elif ch == "]":
                in_class = False
            elif ch == "/" and not in_class:
                end = i + 1
                while end < len(src) and (src[end].isalpha()):
                    end += 1
                body = src[self.pos : end]
                self._advance(end)
                return Token("regex", body, line)
            i += 1
        raise self._error("unterminated regex literal")


def tokenize(src: str, line: int = 1) -> list[Token]:
    return _Tokenizer(src, line).tokenize()


# ---------------------------------------------------------------------------
# Expression helpers
# ---------------------------------------------------------------------------

_OPENERS = {"(": ")", "[": "]", "{": "}"}
_CLOSERS = {")", "]", "}"}


def _is_punct(token: Token, value: str) -> bool:
    return token.kind == "punct" and token.value == value


def _match(tokens: list[Token], start: int) -> int:
    """Index of the bracket closing the opener at ``start``."""
    depth = 0
    for i in range(start, len(tokens)):
        tok = tokens[i]
        if tok.kind != "punct":
            continue
        if tok.value in _OPENERS:
            depth += 1
        elif tok.value in _CLOSERS:
            depth -= 1
            if depth == 0:
                return i
    msg = f"unbalanced bracket at line {tokens[start].line}"
    raise JSTokenizeError(msg)


def _top_level(tokens: list[Token]):
    """Yield ``(index, token)`` for tokens at bracket depth zero."""
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        yield i, tok
        if tok.kind == "punct" and tok.value in _OPENERS:
            i = _match(tokens, i)
        i += 1


def _opener_of(tokens: list[Token], close: int) -> int:
    """Index of the bracket opening the closer at ``close``."""
    depth = 0
    for i in range(close, -1, -1):
        tok = tokens[i]
        if tok.kind != "punct":
            continue
        if tok.value in _CLOSERS:
            depth += 1
        elif tok.value in _OPENERS:
            depth -= 1
            if depth == 0:
                return i
    msg = f"unbalanced bracket at line {tokens[close].line}"
    raise JSTokenizeError(msg)


def _strip_parens(tokens: list[Token]) -> list[Token]:
    while tokens and _is_punct(tokens[0], "(") and _match(tokens, 0) == len(tokens) - 1:
        tokens = tokens[1:-1]
    return tokens


def _split_top_level(tokens: list[Token], sep: str) -> list[list[Token]]:
    pieces, start = [], 0
    for i, tok in _top_level(tokens):
        if _is_punct(tok, sep):
            pieces.append(tokens[start:i])
            start = i + 1
    pieces.append(tokens[start:])
    return pieces


def _split_ternary(tokens: list[Token]):
    question = None
    nesting = 0
    for i, tok in _top_level(tokens):
        if _is_punct(tok, "?"):
            if question is None:
                question = i
            else:
                nesting += 1
        elif _is_punct(tok, ":") and question is not None:
            if nesting == 0:
                return tokens[:question], tokens[question + 1 : i], tokens[i + 1 :]
            nesting -= 1
    return None


def _is_call_of(tokens: list[Token], callee: list[str]) -> bool:
    """True when ``tokens`` is exactly ``callee(...)`` (e.g. ``escapeHtml(x)``)."""
    n = len(callee)
    if len(tokens) < n + 2 or not _is_punct(tokens[n], "("):
        return False
    for tok, want in zip(tokens[:n], callee, strict=True):
        if tok.value != want or tok.kind not in {"name", "punct"}:
            return False
    return _match(tokens, n) == len(tokens) - 1


_NON_MARKUP_OPERATORS = {
    "||", "&&", "??", ",", "=", "+=", "==", "===", "!=", "!==", "<", ">", "<=",
    ">=", "-", "*", "/", "%", "=>",
}  # fmt: skip


def is_safe_markup(tokens: list[Token]) -> bool:
    """Whether an expression can only produce constant or escaped markup."""
    tokens = _strip_parens(tokens)
    if not tokens:
        return False
    ternary = _split_ternary(tokens)
    if ternary is not None:
        _condition, consequent, alternative = ternary
        return is_safe_markup(consequent) and is_safe_markup(alternative)
    if any(
        tok.kind == "punct" and tok.value in _NON_MARKUP_OPERATORS
        for _, tok in _top_level(tokens)
    ):
        return False
    operands = _split_top_level(tokens, "+")
    if len(operands) > 1:
        return all(is_safe_markup(op) for op in operands)
    return _is_safe_operand(tokens)


def _is_safe_operand(tokens: list[Token]) -> bool:
    if len(tokens) == 1:
        tok = tokens[0]
        if tok.kind in {"str", "num"}:
            return True
        if tok.kind == "tpl":
            return all(is_safe_markup(part) for part in tok.parts)
        return tok.kind == "name" and bool(HTML_VAR_RE.match(tok.value))
    if _is_call_of(tokens, [ESCAPE_HELPER]):
        return True
    if _is_call_of(tokens, ["DOMPurify", ".", "sanitize"]):
        return True
    return _is_safe_map_join(tokens)


def _is_safe_map_join(tokens: list[Token]) -> bool:
    """``items.map(callback).join(sep)`` where the callback returns safe markup."""
    tail = [t.value for t in tokens[-5:]]
    if len(tokens) >= 5 and tail[:3] == [".", "join", "("] and tail[4] == ")":
        if tokens[-2].kind != "str":
            return False
        map_close = len(tokens) - 6
    elif len(tokens) >= 4 and [t.value for t in tokens[-4:]] == [".", "join", "(", ")"]:
        map_close = len(tokens) - 5
    else:
        return False
    if map_close < 0 or not _is_punct(tokens[map_close], ")"):
        return False
    map_open = _opener_of(tokens, map_close)
    if map_open < 2:
        return False
    if not (
        _is_punct(tokens[map_open - 2], ".") and tokens[map_open - 1].value == "map"
    ):
        return False
    return _callback_returns_safe_markup(tokens[map_open + 1 : map_close])


def _callback_returns_safe_markup(callback: list[Token]) -> bool:
    if callback and callback[0].value == "function":
        params_open = next(i for i, t in enumerate(callback) if _is_punct(t, "("))
        body_open = _match(callback, params_open) + 1
        if not _is_punct(callback[body_open], "{"):
            return False
        return _returns_safe_markup(
            callback[body_open + 1 : _match(callback, body_open)]
        )
    arrow = next(
        (i for i, t in _top_level(callback) if _is_punct(t, "=>")),
        None,
    )
    if arrow is None:
        return False
    body = callback[arrow + 1 :]
    if body and _is_punct(body[0], "{") and _match(body, 0) == len(body) - 1:
        return _returns_safe_markup(body[1:-1])
    return is_safe_markup(body)


def _returns_safe_markup(body: list[Token]) -> bool:
    """Check every ``return`` of a function body, skipping nested functions."""
    returns = []
    i = 0
    while i < len(body):
        tok = body[i]
        if tok.kind == "name" and tok.value == "function":
            params_open = next(
                j for j in range(i, len(body)) if _is_punct(body[j], "(")
            )
            i = _match(body, _match(body, params_open) + 1) + 1
            continue
        if _is_punct(tok, "=>"):
            if i + 1 < len(body) and _is_punct(body[i + 1], "{"):
                i = _match(body, i + 1) + 1
                continue
        if tok.kind == "name" and tok.value == "return":
            end = _expression_end(body, i + 1)
            returns.append(body[i + 1 : end])
            i = end
            continue
        if tok.kind == "punct" and tok.value in _OPENERS and tok.value != "{":
            # Expressions in parentheses/brackets cannot contain a ``return``
            # of this function; nested callbacks inside them are skipped.
            i = _match(body, i) + 1
            continue
        i += 1
    return bool(returns) and all(is_safe_markup(expr) for expr in returns)


def _expression_end(tokens: list[Token], start: int) -> int:
    """Index just past an expression starting at ``start``."""
    i = start
    while i < len(tokens):
        tok = tokens[i]
        if tok.kind == "punct":
            if tok.value in {";", ","} or tok.value in _CLOSERS:
                return i
            if tok.value in _OPENERS:
                i = _match(tokens, i)
        i += 1
    return i


# ---------------------------------------------------------------------------
# Sink detection
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Violation:
    path: str
    line: int
    sink: str
    expression: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.sink} {self.expression}"


def _render(tokens: list[Token]) -> str:
    out = []
    for tok in tokens:
        if tok.kind == "str":
            out.append(repr(tok.value))
        elif tok.kind == "tpl":
            chunks = tok.value.split("${}")
            text = chunks[0]
            for part, chunk in zip(tok.parts, chunks[1:], strict=False):
                text += "${" + _render(part) + "}" + chunk
            out.append(f"`{text}`")
        else:
            out.append(tok.value)
    return re.sub(r"\s+", " ", " ".join(out))[:200]


def _unchecked_html_bindings(tokens: list[Token]) -> list[Token]:
    """HTML-named identifiers bound by parameters or loops, not by ``=``."""
    found = []
    for i, tok in enumerate(tokens):
        params: list[Token] = []
        if tok.kind == "name" and tok.value in {"function", "catch"}:
            j = i + 1
            if j < len(tokens) and tokens[j].kind == "name":
                j += 1
            if j < len(tokens) and _is_punct(tokens[j], "("):
                params = tokens[j + 1 : _match(tokens, j)]
        elif _is_punct(tok, "=>") and i:
            prev = tokens[i - 1]
            if prev.kind == "name":
                params = [prev]
            elif _is_punct(prev, ")"):
                params = tokens[_opener_of(tokens, i - 1) + 1 : i - 1]
        elif (
            tok.kind == "name"
            and i + 1 < len(tokens)
            and tokens[i + 1].value in {"of", "in"}
            and tokens[i + 1].kind == "name"
        ):
            params = [tok]
        found.extend(
            p for p in params if p.kind == "name" and HTML_VAR_RE.match(p.value)
        )
    return found


def _iter_token_lists(tokens: list[Token]):
    yield tokens
    for tok in tokens:
        for part in tok.parts:
            yield from _iter_token_lists(part)


def find_unsafe_sinks(
    src: str, label: str = "<script>", line: int = 1
) -> list[Violation]:
    """Report HTML sinks whose value is not provably constant or escaped."""
    violations = []
    for tokens in _iter_token_lists(tokenize(src, line)):
        for i, tok in enumerate(tokens):
            prev = tokens[i - 1] if i else None
            nxt = tokens[i + 1] if i + 1 < len(tokens) else None
            if tok.kind != "name" or nxt is None:
                continue
            assigned = nxt.kind == "punct" and nxt.value in {"=", "+="}
            after_dot = prev is not None and _is_punct(prev, ".")
            if tok.value in HTML_PROPERTIES and after_dot and assigned:
                sink, values = (
                    f".{tok.value} {nxt.value}",
                    [tokens[i + 2 : _expression_end(tokens, i + 2)]],
                )
            elif HTML_VAR_RE.match(tok.value) and not after_dot and assigned:
                sink, values = (
                    f"{tok.value} {nxt.value}",
                    [tokens[i + 2 : _expression_end(tokens, i + 2)]],
                )
            elif tok.value == "insertAdjacentHTML" and _is_punct(nxt, "("):
                args = _split_top_level(tokens[i + 2 : _match(tokens, i + 1)], ",")
                sink, values = ".insertAdjacentHTML(_,", args[1:2] or [[]]
            elif (
                tok.value in {"write", "writeln"}
                and after_dot
                and i >= 2
                and tokens[i - 2].value == "document"
                and _is_punct(nxt, "(")
            ):
                sink = f"document.{tok.value}("
                values = _split_top_level(tokens[i + 2 : _match(tokens, i + 1)], ",")
            else:
                continue
            violations.extend(
                Violation(label, tok.line, sink, _render(value))
                for value in values
                if not is_safe_markup(value)
            )
        violations.extend(
            Violation(label, tok.line, "unchecked binding of", tok.value)
            for tok in _unchecked_html_bindings(tokens)
        )
    return violations


def _unsafe_sinks_in(path: Path) -> list[Violation]:
    rel = path.relative_to(WEBSITE_DIR).as_posix()
    found = []
    for script in extract_scripts(path):
        found.extend(find_unsafe_sinks(script.source, rel, script.start_line))
    return found


# ---------------------------------------------------------------------------
# Checker self-tests: known-vulnerable shapes are flagged, safe shapes pass.
# The vulnerable snippets are taken from the pre-fix dashboard templates.
# ---------------------------------------------------------------------------

VULNERABLE_SNIPPETS = [
    "container.innerHTML = `<p>Security posture unavailable: ${data.error}</p>`;",
    "content.innerHTML = '<p>Error: ' + (data.error || resp.status) + '</p>';",
    "content.innerHTML = renderMarkdown(data.content || '');",
    "function renderMarkdown(raw) { return '<pre>' + raw + '</pre>'; }\n"
    "content.innerHTML = renderMarkdown(x);",
    "card.innerHTML = '<span class=\"tool-name\">' + tool.name + '</span>';",
    "let html = ''; html += '<span>' + name + '</span>'; c.innerHTML = html;",
    "html += `<div>${turn.content.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</div>`;",
    "el.innerHTML = names.map(function (n) { return '<i>' + n + '</i>'; }).join('');",
    "el.innerHTML = items.map(s => '<li>' + s.name + '</li>').join('');",
    "var tags = list.map(function (t) { return t; }).join(' ');\n"
    "el.innerHTML = '<div>' + tags + '</div>';",
    "const rawHtml = marked.parse(data.content); el.innerHTML = rawHtml;",
    "el.innerHTML += '<b>' + x + '</b>';",
    "el.outerHTML = '<b>' + x + '</b>';",
    "el.insertAdjacentHTML('beforeend', '<b>' + x + '</b>');",
    "document.write('<b>' + x + '</b>');",
    "el.innerHTML = `<b>${cond ? x : 'y'}</b>`;",
    "el.innerHTML = escapeHtml(a) + b;",
    "el.innerHTML = escapeHtml(a).replace('x', b);",
    "function render(html) { el.innerHTML = html; }",
    "items.forEach(rowHtml => { el.innerHTML = rowHtml; });",
    "items.forEach((i, html) => { el.innerHTML = html; });",
    "for (const html of list) { el.innerHTML = html; }",
]

SAFE_SNIPPETS = [
    "el.innerHTML = '';",
    "el.innerHTML = '<span class=\"loader\"></span> Running...';",
    "el.innerHTML = '<p>a</p>' +\n    '<p>b</p>';",
    "el.innerHTML = `<p>${escapeHtml(err.message)}</p>`;",
    "el.innerHTML = '<p>' + escapeHtml(data.error || resp.status) + '</p>';",
    "el.innerHTML = DOMPurify.sanitize(marked.parse(raw));",
    "el.innerHTML = `<b class=\"${ok ? 'a' : 'b'}\">${ok ? 'PASS' : 'FAIL'}</b>`;",
    "el.innerHTML = items.map(b => '<i>' + escapeHtml(b.label) + '</i>').join('');",
    "el.innerHTML = names.map(function (n) {\n"
    "    var label = n.replace(/\\b\\w/g, function (l) { return l.toUpperCase(); });\n"
    "    return '<i>' + escapeHtml(label) + '</i>';\n"
    "}).join('');",
    "let html = ''; html += '<b>' + escapeHtml(n) + '</b>'; el.innerHTML = html;",
    "var tagsHtml = t.map(function (x) { return '<i>' + escapeHtml(x) + '</i>'; }).join(' ');\n"
    "el.innerHTML = (tagsHtml ? '<div>' + tagsHtml + '</div>' : '');",
    "let html; html = '<b>' + escapeHtml(x) + '</b>'; el.innerHTML = html;",
    "el.textContent = '<b>' + x + '</b>';",
    "if (a.innerHTML === b) { f(); }",
]


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.parametrize("snippet", VULNERABLE_SNIPPETS)
def test_checker_flags_unescaped_sink(snippet):
    assert find_unsafe_sinks(snippet), f"checker missed: {snippet}"


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.parametrize("snippet", SAFE_SNIPPETS)
def test_checker_accepts_escaped_or_constant_markup(snippet):
    assert find_unsafe_sinks(snippet) == []


# ---------------------------------------------------------------------------
# The real dashboard sources
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.parametrize("path", SCRIPT_SOURCES, ids=lambda p: p.name)
def test_no_unescaped_html_sinks(path):
    violations = _unsafe_sinks_in(path)
    assert not violations, "Unescaped HTML sinks:\n" + "\n".join(map(str, violations))


@pytest.mark.unit
@pytest.mark.security
def test_checker_sees_the_dashboard_sinks():
    """Guard against a vacuous pass: the sources really contain HTML sinks."""
    sink_count = 0
    for path in SCRIPT_SOURCES:
        for script in extract_scripts(path):
            tokens = tokenize(script.source, script.start_line)
            sink_count += sum(
                1
                for i, tok in enumerate(tokens[1:], start=1)
                if tok.value in HTML_PROPERTIES and _is_punct(tokens[i - 1], ".")
            )
    assert sink_count >= 50


@pytest.mark.unit
@pytest.mark.security
def test_escape_helper_defined_once_in_base_head():
    base = (TEMPLATES_DIR / "base.html").read_text(encoding="utf-8")
    head = base.split("</head>", 1)[0]
    helper_at = head.find(f"function {ESCAPE_HELPER}(")
    assert helper_at != -1, "escapeHtml must be defined in base.html <head>"
    # Before page-specific head scripts and before any page script in <body>.
    assert helper_at < head.find("{% block extra_head %}")

    body = head[helper_at:]
    body = body[: body.find("}") + 1]
    replacements = re.findall(r"\.replace\(/(.)/g, '([^']+)'\)", body)
    assert replacements == [
        ("&", "&amp;"),
        ("<", "&lt;"),
        (">", "&gt;"),
        ('"', "&quot;"),
        ("'", "&#39;"),
    ]

    for path in SCRIPT_SOURCES:
        if path.name == "base.html":
            continue
        text = path.read_text(encoding="utf-8")
        assert not re.search(
            rf"\b{ESCAPE_HELPER}\s*=|function\s+{ESCAPE_HELPER}\b", text
        ), f"{path.name} must not redefine {ESCAPE_HELPER}"


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.parametrize("path", TEMPLATE_FILES, ids=lambda p: p.name)
def test_templates_do_not_bypass_autoescape(path):
    text = path.read_text(encoding="utf-8")
    assert not re.search(r"\|\s*safe\b", text), "Jinja |safe disables autoescaping"
    # Autoescaped values are HTML-decoded before an inline handler runs, so a
    # quote in the value would break out of a JS string literal.
    assert not re.search(r"\son\w+\s*=\s*\"[^\"]*\{\{", text)
    assert not re.search(r"\son\w+\s*=\s*'[^']*\{\{", text)


# ---------------------------------------------------------------------------
# Real Jinja rendering of file-controlled data
# ---------------------------------------------------------------------------

PAYLOAD = "</div><img src=x onerror=alert(1)>"


@pytest.fixture
def jinja_env(tmp_path):
    return WebsiteGenerator(
        output_dir=str(tmp_path / "out"), root_dir=str(tmp_path)
    ).env


@pytest.mark.unit
@pytest.mark.security
def test_mermaid_graph_is_escaped_in_awareness_page(jinja_env):
    # Shape of the payload returned by the PAI PM server's /api/awareness, whose
    # ``mermaid_graph`` is passed through to the template unmodified.
    awareness = {
        "missions": [
            {
                "id": "m1",
                "title": "Mission",
                "status": "active",
                "priority": "high",
                "completion_percentage": 0,
            }
        ],
        "projects": [],
        "telos": [],
        "memory": {"directories": [], "total_files": 0, "work_sessions_count": 0},
        "metrics": {},
        "mermaid_graph": f'graph TD\n    M_m1["{PAYLOAD}"]',
    }
    html = jinja_env.get_template("awareness.html").render(awareness=awareness)
    assert PAYLOAD not in html
    assert "&lt;/div&gt;&lt;img src=x onerror=alert(1)&gt;" in html


@pytest.mark.unit
@pytest.mark.security
def test_module_name_is_not_interpolated_into_onclick(jinja_env):
    name = "x');alert(1);//"
    modules = [
        {
            "name": name,
            "status": "active",
            "description": "d",
            "submodules": [],
            "path": "p",
        }
    ]
    html = jinja_env.get_template("modules.html").render(modules=modules)
    assert 'onclick="showModuleDetail(this.dataset.name)"' in html
    assert 'data-name="x&#39;);alert(1);//"' in html
    assert "alert(1);//')" not in html


# ---------------------------------------------------------------------------
# Node.js checks (syntax of every script, behaviour of the helper)
# ---------------------------------------------------------------------------


@requires_node
@pytest.mark.unit
@pytest.mark.parametrize("path", SCRIPT_SOURCES, ids=lambda p: p.name)
def test_scripts_are_valid_javascript(path, tmp_path):
    for index, script in enumerate(extract_scripts(path)):
        js_file = tmp_path / f"{path.stem}_{index}.js"
        js_file.write_text(script.source, encoding="utf-8")
        result = subprocess.run(
            ["node", "--check", str(js_file)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, (
            f"{path.name}:{script.start_line}\n{result.stderr}"
        )


@requires_node
@pytest.mark.unit
@pytest.mark.security
def test_escape_helper_behaviour(tmp_path):
    base_scripts = extract_scripts(TEMPLATES_DIR / "base.html")
    helper = next(s.source for s in base_scripts if ESCAPE_HELPER in s.source)
    inputs = [PAYLOAD, "a & b \"c\" 'd'", 42, None, "&lt;"]
    js_file = tmp_path / "escape_check.js"
    js_file.write_text(
        helper
        + f"\nprocess.stdout.write(JSON.stringify({json.dumps(inputs)}.map(escapeHtml)));\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        ["node", str(js_file)], capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == [
        "&lt;/div&gt;&lt;img src=x onerror=alert(1)&gt;",
        "a &amp; b &quot;c&quot; &#39;d&#39;",
        "42",
        "null",
        "&amp;lt;",
    ]
