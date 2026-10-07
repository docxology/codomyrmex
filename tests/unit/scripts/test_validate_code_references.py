"""Tests for scripts/documentation/validate_code_references.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
from tests.support.repo_paths import REPO_ROOT

SCRIPT = REPO_ROOT / "scripts" / "documentation" / "validate_code_references.py"


def _load():
    spec = importlib.util.spec_from_file_location("validate_code_references", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses resolve annotations via sys.modules
    spec.loader.exec_module(module)
    return module


vcr = _load()

DOC = """\
# Example

```python
from codomyrmex.logging_monitoring import get_logger, not_a_real_name
import codomyrmex.validation
from codomyrmex.validation import (
    is_valid,
    validate,
)
x = 1  # unrelated code
```

```pycon
>>> from codomyrmex.exceptions import CodomyrmexError
```

<!-- docs-check: skip-imports -->
```python
from codomyrmex.my_new_module import Thing
```

```bash
from codomyrmex.ignored import shell_lines_are_not_python
```
"""


def _refs(text: str) -> list[tuple[int, str, str | None]]:
    out = []
    for first_line, block in vcr.iter_python_blocks(text):
        for offset, ref in vcr.extract_references(block):
            out.append((first_line + offset, ref.module, ref.name))
    return out


@pytest.mark.unit
def test_extracts_imports_with_line_numbers() -> None:
    assert _refs(DOC) == [
        (4, "codomyrmex.logging_monitoring", "get_logger"),
        (4, "codomyrmex.logging_monitoring", "not_a_real_name"),
        (5, "codomyrmex.validation", None),
        (6, "codomyrmex.validation", "is_valid"),
        (6, "codomyrmex.validation", "validate"),
        (14, "codomyrmex.exceptions", "CodomyrmexError"),
    ]


@pytest.mark.unit
def test_skip_marker_and_non_python_fences_are_ignored() -> None:
    modules = {module for _, module, _ in _refs(DOC)}
    assert "codomyrmex.my_new_module" not in modules
    assert "codomyrmex.ignored" not in modules


@pytest.mark.unit
def test_resolve_reports_missing_names_and_modules() -> None:
    assert (
        vcr.resolve(vcr.Reference("codomyrmex.exceptions", "CodomyrmexError")) is None
    )
    assert vcr.resolve(vcr.Reference("codomyrmex.exceptions", None)) is None
    missing_name = vcr.resolve(vcr.Reference("codomyrmex.exceptions", "NoSuchThing"))
    assert missing_name is not None and "NoSuchThing" in missing_name
    missing_module = vcr.resolve(vcr.Reference("codomyrmex.no_such_module", None))
    assert missing_module is not None and "ModuleNotFoundError" in missing_module


@pytest.mark.unit
def test_scan_and_cli_exit_code(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    good = tmp_path / "good.md"
    good.write_text(
        "```python\nfrom codomyrmex.exceptions import CodomyrmexError\n```\n"
    )
    bad = tmp_path / "bad.md"
    bad.write_text("```python\nfrom codomyrmex.exceptions import NoSuchThing\n```\n")

    report = vcr.scan(tmp_path, [good, bad])
    assert report.files_scanned == 2
    assert [ref.name for ref in report.broken] == ["NoSuchThing"]
    assert report.to_dict()["broken"][0]["locations"] == ["bad.md:2"]

    assert vcr.main(["--repo-root", str(tmp_path), str(good)]) == 0
    assert vcr.main(["--repo-root", str(tmp_path), "--fail-on-broken", str(bad)]) == 1
    assert "NoSuchThing" in capsys.readouterr().out
