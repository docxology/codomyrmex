"""``iter_statements`` must find exactly what ``ast.walk`` finds, faster.

Agent PR #539 replaced ``ast.walk`` with ``tree.body`` in
``ModuleIntrospector.scan_module``; that silently stopped counting nested
classes and ``__all__`` assigned inside ``try``/``if`` blocks. The statement
walker skips only expression subtrees, so the definitions it yields (and
their order, which decides which ``__all__`` wins) must match ``ast.walk``.
"""

from __future__ import annotations

import ast
import textwrap
from pathlib import Path

import pytest

from codomyrmex.system_discovery import module_introspector
from codomyrmex.system_discovery.module_introspector import (
    ModuleIntrospector,
    iter_statements,
)

DEFINITIONS = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef, ast.Assign)

SOURCE = textwrap.dedent(
    """
    import sys

    try:
        __all__ = ["a"]
    except ImportError:
        class Fallback:
            class Inner:
                pass
    else:
        X = 1
    finally:
        Y = 2

    if sys.version_info >= (3, 11):
        def top_in_if():
            class InFunction:
                pass
    else:
        __all__ = ["b"]

    match sys.platform:
        case "linux":
            class OnLinux:
                pass
        case _:
            Z = 3

    async def coroutine():
        async with ctx() as c:
            for item in c:
                while item:
                    class Deep:
                        pass
                    break

    def decorated(fn=lambda: [x for x in range(3)]):
        return fn

    __all__ = ["a", "b", "top_in_if"]
    """
)


def _signature(nodes) -> list[tuple[str, int, int]]:
    return [
        (type(node).__name__, node.lineno, node.col_offset)
        for node in nodes
        if isinstance(node, DEFINITIONS)
    ]


@pytest.mark.unit
def test_matches_ast_walk_on_every_statement_form() -> None:
    tree = ast.parse(SOURCE)
    expected = _signature(ast.walk(tree))
    assert _signature(iter_statements(tree)) == expected
    names = {
        node.name for node in iter_statements(tree) if isinstance(node, ast.ClassDef)
    }
    assert names == {"Fallback", "Inner", "InFunction", "OnLinux", "Deep"}


@pytest.mark.unit
def test_matches_ast_walk_on_the_package_sources() -> None:
    package = Path(module_introspector.__file__).resolve().parents[1]
    files = sorted(package.glob("*/**/*.py"))[::7]  # spread across modules
    assert len(files) > 100
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        assert _signature(iter_statements(tree)) == _signature(ast.walk(tree)), path


@pytest.mark.unit
def test_scan_module_counts_nested_and_conditional_definitions(tmp_path: Path) -> None:
    module = tmp_path / "sample"
    module.mkdir()
    (module / "__init__.py").write_text(SOURCE, encoding="utf-8")
    info = ModuleIntrospector().scan_module(module)
    assert info.classes == 5
    # Module-level functions only (col_offset 0), as before.
    assert info.functions == 1
    # The source-last __all__ is the one in effect; walk order (which put the
    # nested else-branch assignment last) used to win.
    assert info.exports == ["a", "b", "top_in_if"]


@pytest.mark.unit
def test_statement_walk_visits_far_fewer_nodes() -> None:
    path = Path(module_introspector.__file__)
    tree = ast.parse(path.read_text(encoding="utf-8"))
    walked = sum(1 for _ in ast.walk(tree))
    statements = sum(1 for _ in iter_statements(tree))
    assert statements * 3 < walked
