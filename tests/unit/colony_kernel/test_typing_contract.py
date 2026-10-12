"""Guard actual PEP 561 markers and unsafe bare typing suppressions."""

from __future__ import annotations

import io
import re
import tokenize
from importlib.resources import files
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("package", ["research", "falsification"])
def test_kernel_subpackages_publish_inline_typing_marker(package: str) -> None:
    """Real importable packages declare their inline typing to consumers."""
    marker = files(f"codomyrmex.colony_kernel.{package}").joinpath("py.typed")
    assert marker.is_file()
    assert marker.read_text().strip() == ""


def test_kernel_has_no_bare_type_ignores() -> None:
    """A broad suppression must not hide future shared-contract regressions."""
    package = Path(__file__).resolve().parents[3] / "src/codomyrmex/colony_kernel"
    violations = []
    for source in package.rglob("*.py"):
        tokens = tokenize.generate_tokens(io.StringIO(source.read_text()).readline)
        for token in tokens:
            if token.type == tokenize.COMMENT and re.search(
                r"\btype:\s*ignore(?!\[)", token.string
            ):
                violations.append(f"{source.relative_to(package)}:{token.start[0]}")
    assert not violations, violations
