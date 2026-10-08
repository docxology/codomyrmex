"""Tests for scripts/documentation/validate_api_signatures.py."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
from tests.support.repo_paths import REPO_ROOT

SCRIPT = REPO_ROOT / "scripts" / "documentation" / "validate_api_signatures.py"


def _load():
    spec = importlib.util.spec_from_file_location("validate_api_signatures", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses resolve annotations via sys.modules
    spec.loader.exec_module(module)
    return module


vas = _load()

PACKAGE = "codomyrmex.exceptions"


def _check(text: str) -> vas.Report:
    report = vas.Report()
    vas.check_text(text, PACKAGE, "spec.md", report)
    return report


def _targets(text: str) -> list[tuple[int, str]]:
    return [(sig.line, sig.target) for sig in vas.extract_signatures(text)]


@pytest.mark.unit
def test_parse_signature_text() -> None:
    target, params = vas.parse_signature_text(
        "Pipeline.run(self, name: str, /, *, flag: bool = False, **extra) -> Result"
    )
    assert target == "Pipeline.run"
    assert params.names == ("self", "name", "flag")
    assert params.leading_self == "self"
    assert params.without_self().names == ("name", "flag")
    assert params.var_keyword == "extra"
    assert vas.parse_signature_text("chain(*tasks: Task) -> Workflow")[
        1
    ].var_positional == ("tasks")
    # Not confidently parseable: ellipsis, prose, trailing text, call syntax.
    for text in (
        "run(...)",
        "run(path, see below)",
        "run(path) returns a dict",
        "run(path) -> dict extra",
        "GET /api/items",
    ):
        assert vas.parse_signature_text(text) is None, text


DOC = """\
# Example

## Functions

### Function: `format_exception_chain(exception: Exception) -> str`

### `create_error_context()`

```python
def documented(value: int, *, strict: bool = False) -> int: ...

def example(value):
    return value * 2
```

```python
Thing(value: int = 1)
```

```python
run(path)
```

```python
helper(path: str) -> bool
    \"\"\"One-line listing entry.\"\"\"

other(count: int) -> int
```

<!-- docs-check: skip-signatures -->
### `planned(x: int) -> int`

#### `nested(y: int) -> int`

<!-- docs-check: skip-signatures -->
```python
def skipped_block(z: int) -> int: ...
```

```pycon
>>> def session(a): ...
```

```bash
def shell(a: int) -> int
```
"""


@pytest.mark.unit
def test_extract_signatures_from_headings_and_fences() -> None:
    assert _targets(DOC) == [
        (5, "format_exception_chain"),
        (10, "documented"),
        (17, "Thing"),
        (25, "helper"),
        (28, "other"),
    ]


@pytest.mark.unit
def test_class_and_module_sections_scope_bare_names() -> None:
    report = vas.Report()
    text = """\
### Class: `CodomyrmexError`

#### `to_dict() -> dict`

#### `to_dict(verbose: bool) -> dict`

### `base`

#### `format_exception_chain(exc: Exception) -> str`

### `NoSuchClass`

#### `to_dict() -> dict`

### Methods

#### `to_dict() -> dict`
"""
    vas.check_text(text, PACKAGE, "spec.md", report)
    broken = {(f.line, f.target): (f.not_accepted, f.missing) for f in report.findings}
    assert broken == {
        (5, "CodomyrmexError.to_dict"): (["verbose"], []),
        (9, "base.format_exception_chain"): (["exc"], ["exception"]),
    }
    # The unresolvable class blocks its method; a plain "Methods" heading at
    # module level does not resolve to_dict, so it is skipped too.
    assert report.signatures_checked == 3
    assert report.unresolved == [
        "spec.md:13 to_dict (section names unresolved code)",
        "spec.md:17 to_dict (not found)",
    ]


@pytest.mark.unit
def test_findings_for_unknown_and_missing_parameters() -> None:
    report = _check(
        """\
### `format_exception_chain(exception: Exception) -> str`

### `format_exception_chain(error: Exception, depth: int = 3) -> str`

### `CodomyrmexError(message: str, anything: int = 0)`

### `CodomyrmexError(context: dict | None = None)`

### `create_error_context(**kwargs) -> dict`

### `format_exception_chain(exception, **kwargs) -> str`
"""
    )
    broken = {f.line: (f.not_accepted, f.missing) for f in report.findings}
    assert report.signatures_checked == 6
    assert broken == {
        3: (["error", "depth"], ["exception"]),
        # CodomyrmexError takes **kwargs, so `anything` is accepted ...
        # ... but its required `message` must still be documented.
        7: ([], ["message"]),
        11: (["**kwargs"], []),
    }
    finding = next(f for f in report.findings if f.line == 3)
    assert finding.actual == "format_exception_chain(exception)"
    assert finding.to_dict()["location"] == "spec.md:3"


@pytest.mark.unit
def test_methods_classes_and_skips() -> None:
    report = _check(
        """\
```python
class CodomyrmexError:
    def to_dict(self) -> dict: ...
    def to_dict(self, flat: bool) -> dict: ...
    @property
    def code(self) -> str: ...
```

### `CodomyrmexError(Exception)`

### `format_exception_chain(self, exception: Exception) -> str`

### `no_such_function(a: int) -> int`

### `__lt__(other: object) -> bool`
"""
    )
    assert [(f.line, f.target, f.not_accepted) for f in report.findings] == [
        (4, "CodomyrmexError.to_dict", ["flat"]),
    ]
    reasons = sorted(u.split(" (", 1)[1] for u in report.unresolved)
    assert reasons == [
        "base-class list)",
        "documented with self but not a method)",
        "not found)",
        "not found)",
    ]


@pytest.mark.unit
def test_compare() -> None:
    real = vas.RealParams(("a", "b", "c"), ("a", "b"), None, None, "f(a, b, c=…)")
    assert vas.compare(vas.DocParams(("a", "b", "c")), real) == ([], [])
    assert vas.compare(vas.DocParams(("a",)), real) == ([], ["b"])
    assert vas.compare(vas.DocParams(("a", "b", "x"), "args", "kw"), real) == (
        ["x", "**kw", "*args"],
        [],
    )
    with_kwargs = vas.RealParams(
        ("a",), ("a",), "rest", "options", "f(a, *rest, **options)"
    )
    assert vas.compare(vas.DocParams(("a", "rest", "anything")), with_kwargs) == (
        [],
        [],
    )


@pytest.mark.unit
def test_static_index_resolves_unique_names_only(tmp_path: Path) -> None:
    name = "validate_api_signatures_fixture_pkg"
    package = tmp_path / name
    package.mkdir()
    (package / "__init__.py").write_text("from .core import exported\n")
    (package / "core.py").write_text(
        "def exported(a, b=1):\n    return a\n\n\ndef hidden(x, *, y):\n    return x\n"
    )
    (package / "one.py").write_text("def twice(a):\n    return a\n")
    (package / "two.py").write_text("def twice(b):\n    return b\n")
    (package / "notes").mkdir()
    (package / "notes" / "loose.py").write_text("def loose(q):\n    return q\n")

    sys.path.insert(0, str(tmp_path))
    try:
        resolver = vas.PackageResolver(name)
        assert resolver.import_error is None
        assert resolver.resolve("exported").__name__ == "exported"
        assert resolver.resolve("hidden").__module__ == f"{name}.core"
        assert resolver.resolve("twice") is None  # defined twice: ambiguous
        assert resolver.resolve("loose") is None  # not inside a regular package
        assert resolver.resolve("core.hidden").__name__ == "hidden"
        assert resolver.context_kind("core") == "module"
        assert resolver.context_kind("exported") == "other"
        assert resolver.context_kind("missing") is None
    finally:
        sys.path.remove(str(tmp_path))
        for module in [m for m in sys.modules if m.startswith(name)]:
            del sys.modules[module]


@pytest.mark.unit
def test_package_for() -> None:
    assert vas.package_for(Path("src/codomyrmex/exceptions/API_SPECIFICATION.md")) == (
        "codomyrmex.exceptions"
    )
    assert vas.package_for(Path("docs/modules/exceptions/API_SPECIFICATION.md")) == (
        "codomyrmex.exceptions"
    )
    assert vas.package_for(
        Path("src/codomyrmex/git_operations/docs/API_SPECIFICATION.md")
    ) == ("codomyrmex.git_operations")
    assert (
        vas.package_for(Path("docs/modules/no_such_module/API_SPECIFICATION.md"))
        is None
    )
    assert vas.package_for(Path("scripts/pai/API_SPECIFICATION.md")) is None


@pytest.mark.unit
def test_scan_and_cli(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    good = tmp_path / "docs" / "modules" / "exceptions" / "API_SPECIFICATION.md"
    good.parent.mkdir(parents=True)
    good.write_text("### `format_exception_chain(exception: Exception) -> str`\n")
    bad = tmp_path / "docs" / "modules" / "exceptions" / "copy" / "API_SPECIFICATION.md"
    bad.parent.mkdir()
    bad.write_text("x\n")
    broken = tmp_path / "docs" / "modules" / "validation" / "API_SPECIFICATION.md"
    broken.parent.mkdir()
    broken.write_text("### `no_such_function(a: int) -> int`\n")

    report = vas.scan(tmp_path)
    assert report.files_scanned == 3
    assert report.signatures_checked == 1
    assert report.findings == []
    assert report.skipped_files == [
        "docs/modules/exceptions/copy/API_SPECIFICATION.md: no matching package"
    ]
    assert report.unresolved == [
        "docs/modules/validation/API_SPECIFICATION.md:1 no_such_function (not found)"
    ]

    good.write_text(
        "### `format_exception_chain(exception: Exception) -> str`\n\n"
        "### `format_exception_chain(error: Exception) -> str`\n"
    )
    output = tmp_path / "out" / "report.json"
    args = ["--repo-root", str(tmp_path), str(good)]
    assert vas.main(args) == 0
    assert "1 broken" in capsys.readouterr().out
    assert (
        vas.main(
            [*args, "--fail-on-broken", "--format", "json", "--output", str(output)]
        )
        == 1
    )
    data = json.loads(capsys.readouterr().out)
    assert data["broken_signatures"] == 1
    assert (
        data["broken"][0]["location"]
        == "docs/modules/exceptions/API_SPECIFICATION.md:3"
    )
    assert data["broken"][0]["missing_required"] == ["exception"]
    assert json.loads(output.read_text()) == data
