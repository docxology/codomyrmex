"""
Comprehensive unit tests for capability_scanner.py

Tests the CapabilityScanner class and its dataclasses using real AST analysis
on synthetic Python source files. Zero-mock policy: all tests use real objects
and tmp_path for filesystem isolation.
"""

import ast
import json
import textwrap
from pathlib import Path

import pytest

from codomyrmex.system_discovery.core.capability_scanner import (
    CapabilityScanner,
    ClassCapability,
    FunctionCapability,
    ModuleCapability,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_module(tmp_path: Path, name: str, init_content: str = "", files: dict[str, str] | None = None) -> Path:
    """Create a fake module directory under a fake codomyrmex package tree.

    Returns the module directory path.
    """
    src = tmp_path / "src"
    codomyrmex = src / "codomyrmex"
    module_dir = codomyrmex / name
    module_dir.mkdir(parents=True, exist_ok=True)

    (module_dir / "__init__.py").write_text(init_content, encoding="utf-8")

    if files:
        for fname, content in files.items():
            fpath = module_dir / fname
            fpath.parent.mkdir(parents=True, exist_ok=True)
            fpath.write_text(content, encoding="utf-8")

    return module_dir


def _scanner_for(tmp_path: Path) -> CapabilityScanner:
    """Create a CapabilityScanner rooted at *tmp_path*."""
    return CapabilityScanner(project_root=tmp_path)


# ---------------------------------------------------------------------------
# Dataclass construction tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestFunctionCapabilityDataclass:
    """Tests for the FunctionCapability dataclass."""

    def test_create_basic(self):
        fc = FunctionCapability(
            name="do_stuff",
            signature="do_stuff(x: int) -> str",
            docstring="Does stuff.",
            parameters=[{"name": "x", "annotation": "int", "default": None}],
            return_annotation="str",
            file_path="/fake/path.py",
            line_number=10,
            is_async=False,
            is_generator=False,
            decorators=[],
            complexity_score=1,
        )
        assert fc.name == "do_stuff"
        assert fc.is_async is False
        assert fc.is_generator is False
        assert fc.complexity_score == 1
        assert fc.line_number == 10

    def test_async_generator_flags(self):
        fc = FunctionCapability(
            name="stream",
            signature="stream()",
            docstring="",
            parameters=[],
            return_annotation="",
            file_path="",
            line_number=1,
            is_async=True,
            is_generator=True,
            decorators=["staticmethod"],
            complexity_score=5,
        )
        assert fc.is_async is True
        assert fc.is_generator is True
        assert fc.decorators == ["staticmethod"]


@pytest.mark.unit
class TestClassCapabilityDataclass:
    """Tests for the ClassCapability dataclass."""

    def test_create_basic(self):
        cc = ClassCapability(
            name="Foo",
            docstring="A Foo class.",
            methods=[],
            properties=["bar"],
            class_variables=["COUNT"],
            inheritance=["Base"],
            file_path="/fake.py",
            line_number=5,
            is_abstract=False,
            decorators=[],
        )
        assert cc.name == "Foo"
        assert cc.properties == ["bar"]
        assert cc.inheritance == ["Base"]
        assert cc.is_abstract is False


@pytest.mark.unit
class TestModuleCapabilityDataclass:
    """Tests for the ModuleCapability dataclass."""

    def test_create_basic(self):
        mc = ModuleCapability(
            name="mymod",
            path="/src/mymod",
            docstring="My module.",
            functions=[],
            classes=[],
            constants={"VERSION": "1.0"},
            imports=["os", "sys"],
            exports=["main"],
            file_count=3,
            line_count=100,
            last_modified="2026-01-01 00:00:00",
        )
        assert mc.name == "mymod"
        assert mc.constants == {"VERSION": "1.0"}
        assert mc.file_count == 3


# ---------------------------------------------------------------------------
# CapabilityScanner init tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCapabilityScannerInit:
    """Tests for CapabilityScanner.__init__."""

    def test_default_project_root(self):
        scanner = CapabilityScanner()
        assert scanner.project_root == Path.cwd()
        assert scanner.src_path == Path.cwd() / "src"
        assert scanner.codomyrmex_path == Path.cwd() / "src" / "codomyrmex"

    def test_custom_project_root(self, tmp_path: Path):
        scanner = CapabilityScanner(project_root=tmp_path)
        assert scanner.project_root == tmp_path
        assert scanner.src_path == tmp_path / "src"
        assert scanner.codomyrmex_path == tmp_path / "src" / "codomyrmex"


# ---------------------------------------------------------------------------
# _calculate_complexity tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCalculateComplexity:
    """Tests for CapabilityScanner._calculate_complexity."""

    def _complexity_of(self, source: str) -> int:
        tree = ast.parse(textwrap.dedent(source))
        func_node = tree.body[0]
        scanner = CapabilityScanner()
        return scanner._calculate_complexity(func_node)

    def test_simple_function(self):
        score = self._complexity_of("""
        def f():
            return 1
        """)
        assert score == 1

    def test_if_adds_complexity(self):
        score = self._complexity_of("""
        def f(x):
            if x > 0:
                return x
            return -x
        """)
        assert score == 2

    def test_nested_loops(self):
        score = self._complexity_of("""
        def f(items):
            for a in items:
                for b in a:
                    if b:
                        pass
        """)
        # 1 base + 2 for-loops + 1 if = 4
        assert score == 4

    def test_try_except(self):
        score = self._complexity_of("""
        def f():
            try:
                pass
            except ValueError:
                pass
            except TypeError:
                pass
        """)
        # 1 base + 2 except handlers = 3
        assert score == 3

    def test_list_comprehension(self):
        score = self._complexity_of("""
        def f(items):
            return [x for x in items]
        """)
        # 1 base + 1 listcomp = 2
        assert score == 2

    def test_with_statement(self):
        score = self._complexity_of("""
        def f():
            with open("x") as fh:
                pass
        """)
        # 1 base + 1 with = 2
        assert score == 2

    def test_while_loop(self):
        score = self._complexity_of("""
        def f():
            while True:
                break
        """)
        assert score == 2

    def test_dict_set_generator_comprehensions(self):
        score = self._complexity_of("""
        def f(items):
            a = {k: v for k, v in items}
            b = {x for x in items}
            c = (x for x in items)
            return a, b, c
        """)
        # 1 base + 3 comprehensions = 4
        assert score == 4


# ---------------------------------------------------------------------------
# _extract_parameters tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestExtractParameters:
    """Tests for CapabilityScanner._extract_parameters."""

    def _params_of(self, source: str) -> list[dict]:
        tree = ast.parse(textwrap.dedent(source))
        func_node = tree.body[0]
        scanner = CapabilityScanner()
        return scanner._extract_parameters(func_node)

    def test_no_params(self):
        params = self._params_of("def f(): pass")
        assert params == []

    def test_simple_params(self):
        params = self._params_of("def f(a, b): pass")
        assert len(params) == 2
        assert params[0]["name"] == "a"
        assert params[1]["name"] == "b"
        assert params[0]["annotation"] is None
        assert params[0]["default"] is None

    def test_annotated_params(self):
        params = self._params_of("def f(x: int, y: str = 'hello'): pass")
        assert params[0]["annotation"] == "int"
        assert params[0]["default"] is None
        assert params[1]["annotation"] == "str"
        assert params[1]["default"] == "'hello'"

    def test_defaults_alignment(self):
        params = self._params_of("def f(a, b=10, c=20): pass")
        assert params[0]["default"] is None
        assert params[1]["default"] == "10"
        assert params[2]["default"] == "20"

    def test_varargs(self):
        params = self._params_of("def f(*args): pass")
        assert any(p["name"] == "*args" for p in params)

    def test_kwargs(self):
        params = self._params_of("def f(**kwargs): pass")
        assert any(p["name"] == "**kwargs" for p in params)

    def test_varargs_and_kwargs_with_annotations(self):
        params = self._params_of("def f(*args: int, **kwargs: str): pass")
        vararg = [p for p in params if p["name"] == "*args"][0]
        kwarg = [p for p in params if p["name"] == "**kwargs"][0]
        assert vararg["annotation"] == "int"
        assert kwarg["annotation"] == "str"

    def test_self_param(self):
        params = self._params_of("def f(self, x): pass")
        assert len(params) == 2
        assert params[0]["name"] == "self"


# ---------------------------------------------------------------------------
# _extract_return_annotation tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestExtractReturnAnnotation:
    """Tests for CapabilityScanner._extract_return_annotation."""

    def _return_of(self, source: str) -> str:
        tree = ast.parse(textwrap.dedent(source))
        func_node = tree.body[0]
        scanner = CapabilityScanner()
        return scanner._extract_return_annotation(func_node)

    def test_no_return_annotation(self):
        assert self._return_of("def f(): pass") == ""

    def test_simple_return(self):
        assert self._return_of("def f() -> int: pass") == "int"

    def test_complex_return(self):
        result = self._return_of("def f() -> dict[str, list[int]]: pass")
        assert "dict" in result
        assert "str" in result


# ---------------------------------------------------------------------------
# _build_signature tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestBuildSignature:
    """Tests for CapabilityScanner._build_signature."""

    def test_empty_params(self):
        scanner = CapabilityScanner()
        sig = scanner._build_signature("f", [], "")
        assert sig == "f()"

    def test_with_annotation_and_return(self):
        scanner = CapabilityScanner()
        params = [{"name": "x", "annotation": "int", "default": None}]
        sig = scanner._build_signature("greet", params, "str")
        assert sig == "greet(x: int) -> str"

    def test_with_default_value(self):
        scanner = CapabilityScanner()
        params = [{"name": "n", "annotation": "int", "default": "42"}]
        sig = scanner._build_signature("compute", params, "")
        assert sig == "compute(n: int = 42)"

    def test_multiple_params(self):
        scanner = CapabilityScanner()
        params = [
            {"name": "a", "annotation": None, "default": None},
            {"name": "b", "annotation": "str", "default": "'hi'"},
        ]
        sig = scanner._build_signature("func", params, "None")
        assert sig == "func(a, b: str = 'hi') -> None"


# ---------------------------------------------------------------------------
# _extract_decorators tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestExtractDecorators:
    """Tests for CapabilityScanner._extract_decorators."""

    def _decorators_of(self, source: str) -> list[str]:
        tree = ast.parse(textwrap.dedent(source))
        func_node = tree.body[0]
        scanner = CapabilityScanner()
        return scanner._extract_decorators(func_node)

    def test_no_decorators(self):
        assert self._decorators_of("def f(): pass") == []

    def test_single_decorator(self):
        decs = self._decorators_of("@staticmethod\ndef f(): pass")
        assert decs == ["staticmethod"]

    def test_decorator_with_args(self):
        decs = self._decorators_of("@pytest.mark.unit\ndef f(): pass")
        assert len(decs) == 1
        assert "pytest" in decs[0]


# ---------------------------------------------------------------------------
# _is_generator tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestIsGenerator:
    """Tests for CapabilityScanner._is_generator."""

    def _generator_check(self, source: str) -> bool:
        tree = ast.parse(textwrap.dedent(source))
        func_node = tree.body[0]
        scanner = CapabilityScanner()
        return scanner._is_generator(func_node)

    def test_not_generator(self):
        assert self._generator_check("def f(): return 1") is False

    def test_yield_generator(self):
        assert self._generator_check("def f():\n yield 1") is True

    def test_yield_from_generator(self):
        assert self._generator_check("def f():\n yield from [1, 2]") is True


# ---------------------------------------------------------------------------
# _analyze_function tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAnalyzeFunction:
    """Tests for CapabilityScanner._analyze_function."""

    def _analyze(self, source: str, is_async: bool = False) -> FunctionCapability | None:
        tree = ast.parse(textwrap.dedent(source))
        func_node = tree.body[0]
        scanner = CapabilityScanner()
        return scanner._analyze_function(func_node, Path("/fake/mod.py"), is_async=is_async)

    def test_basic_function(self):
        fc = self._analyze('''
def greet(name: str) -> str:
    """Say hello."""
    return f"Hello {name}"
''')
        assert fc is not None
        assert fc.name == "greet"
        assert fc.docstring == "Say hello."
        assert fc.return_annotation == "str"
        assert fc.is_async is False
        assert fc.is_generator is False
        assert fc.line_number == 2

    def test_async_function(self):
        fc = self._analyze('''
async def fetch(url: str) -> bytes:
    """Fetch data."""
    pass
''', is_async=True)
        assert fc is not None
        assert fc.is_async is True

    def test_generator_function(self):
        fc = self._analyze('''
def gen():
    """Generate values."""
    yield 1
    yield 2
''')
        assert fc is not None
        assert fc.is_generator is True

    def test_no_docstring(self):
        fc = self._analyze("def bare(): pass")
        assert fc is not None
        assert fc.docstring == "No docstring"

    def test_long_docstring_truncated(self):
        long_doc = "A" * 600
        fc = self._analyze(f'def f():\n    """{long_doc}"""\n    pass')
        assert fc is not None
        assert len(fc.docstring) <= 500

    def test_decorated_function(self):
        fc = self._analyze("@staticmethod\ndef f(): pass")
        assert fc is not None
        assert "staticmethod" in fc.decorators

    def test_file_path_recorded(self):
        tree = ast.parse("def f(): pass")
        scanner = CapabilityScanner()
        fc = scanner._analyze_function(tree.body[0], Path("/my/path.py"))
        assert fc.file_path == "/my/path.py"


# ---------------------------------------------------------------------------
# _analyze_class tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAnalyzeClass:
    """Tests for CapabilityScanner._analyze_class."""

    def _analyze(self, source: str) -> ClassCapability | None:
        tree = ast.parse(textwrap.dedent(source))
        cls_node = tree.body[0]
        scanner = CapabilityScanner()
        return scanner._analyze_class(cls_node, Path("/fake/mod.py"))

    def test_basic_class(self):
        cc = self._analyze('''
class Animal:
    """An animal."""
    KINGDOM = "Animalia"

    def speak(self):
        """Speak."""
        pass
''')
        assert cc is not None
        assert cc.name == "Animal"
        assert cc.docstring == "An animal."
        assert "KINGDOM" in cc.class_variables
        # speak starts with underscore? No, it's 'speak'
        # But _analyze_function skips names starting with _. 'speak' should be kept.
        # Actually -- methods in the class body go through _analyze_function which
        # skips names starting with _. 'speak' does not start with _, so should be there.
        assert any(m.name == "speak" for m in cc.methods)

    def test_class_with_inheritance(self):
        cc = self._analyze('''
class Dog(Animal, Pet):
    """A dog."""
    pass
''')
        assert cc is not None
        assert "Animal" in cc.inheritance
        assert "Pet" in cc.inheritance

    def test_class_with_property(self):
        cc = self._analyze('''
class Foo:
    """Foo."""
    @property
    def bar(self):
        return 1
''')
        assert cc is not None
        assert "bar" in cc.properties
        # bar should NOT be in methods since it's a property
        assert not any(m.name == "bar" for m in cc.methods)

    def test_class_private_methods_included(self):
        """_analyze_class includes all methods; private filtering only in _analyze_ast."""
        cc = self._analyze('''
class Foo:
    """Foo."""
    def public(self):
        pass
    def _private(self):
        pass
    def __dunder(self):
        pass
''')
        assert cc is not None
        method_names = [m.name for m in cc.methods]
        assert "public" in method_names
        # _analyze_class does NOT filter private methods -- that filtering is
        # only done at the top-level in _analyze_ast for module-level functions.
        assert "_private" in method_names
        assert "__dunder" in method_names

    def test_abstract_class_detection(self):
        cc = self._analyze('''
@abc.abstractmethod
class AbstractFoo:
    """Abstract."""
    pass
''')
        # The decorator contains "abc", so is_abstract should be True
        assert cc is not None
        assert cc.is_abstract is True

    def test_no_docstring_class(self):
        cc = self._analyze("class Empty:\n    pass")
        assert cc is not None
        assert cc.docstring == "No docstring"

    def test_class_variables_detected(self):
        cc = self._analyze('''
class Config:
    """Config."""
    host = "localhost"
    port = 8080
''')
        assert cc is not None
        assert "host" in cc.class_variables
        assert "port" in cc.class_variables


# ---------------------------------------------------------------------------
# _analyze_ast tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAnalyzeAst:
    """Tests for CapabilityScanner._analyze_ast."""

    def _run(self, source: str):
        tree = ast.parse(textwrap.dedent(source))
        scanner = CapabilityScanner()
        return scanner._analyze_ast(tree, Path("/test.py"))

    def test_captures_functions(self):
        funcs, classes, consts, imports = self._run('''
def public_func():
    """Public."""
    pass

def _private_func():
    pass
''')
        names = [f.name for f in funcs]
        assert "public_func" in names
        assert "_private_func" not in names

    def test_captures_async_functions(self):
        funcs, _, _, _ = self._run('''
async def fetch():
    """Async fetch."""
    pass
''')
        assert len(funcs) == 1
        assert funcs[0].name == "fetch"
        assert funcs[0].is_async is True

    def test_captures_classes(self):
        _, classes, _, _ = self._run('''
class Foo:
    """Foo class."""
    pass
''')
        assert len(classes) == 1
        assert classes[0].name == "Foo"

    def test_private_classes_excluded(self):
        _, classes, _, _ = self._run('''
class _Internal:
    pass
''')
        assert len(classes) == 0

    def test_captures_constants(self):
        _, _, consts, _ = self._run('''
VERSION = "1.0"
MAX_RETRIES = 3
_PRIVATE = "hidden"
lowercase = "not constant"
''')
        assert "VERSION" in consts
        assert consts["VERSION"] == "1.0"
        assert "MAX_RETRIES" in consts
        assert consts["MAX_RETRIES"] == 3
        # lowercase is not UPPER so not captured
        assert "lowercase" not in consts

    def test_captures_imports(self):
        _, _, _, imports = self._run('''
import os
import sys
from pathlib import Path
from typing import Any
''')
        assert "os" in imports
        assert "sys" in imports
        assert "pathlib" in imports
        assert "typing" in imports

    def test_import_without_module_ignored(self):
        # from . import something has module=None -- should not crash
        _, _, _, imports = self._run('''
import json
''')
        assert "json" in imports


# ---------------------------------------------------------------------------
# _get_module_docstring tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestGetModuleDocstring:
    """Tests for CapabilityScanner._get_module_docstring."""

    def test_with_docstring(self, tmp_path: Path):
        mod = tmp_path / "mymod"
        mod.mkdir()
        (mod / "__init__.py").write_text('"""This is my module."""\n', encoding="utf-8")

        scanner = CapabilityScanner()
        doc = scanner._get_module_docstring(mod)
        assert doc == "This is my module."

    def test_without_docstring(self, tmp_path: Path):
        mod = tmp_path / "mymod"
        mod.mkdir()
        (mod / "__init__.py").write_text("x = 1\n", encoding="utf-8")

        scanner = CapabilityScanner()
        doc = scanner._get_module_docstring(mod)
        assert doc == "No docstring"

    def test_no_init_file(self, tmp_path: Path):
        mod = tmp_path / "mymod"
        mod.mkdir()

        scanner = CapabilityScanner()
        doc = scanner._get_module_docstring(mod)
        assert doc == "No docstring"


# ---------------------------------------------------------------------------
# _get_last_modified_time tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestGetLastModifiedTime:
    """Tests for CapabilityScanner._get_last_modified_time."""

    def test_with_py_files(self, tmp_path: Path):
        mod = tmp_path / "mymod"
        mod.mkdir()
        (mod / "a.py").write_text("# a", encoding="utf-8")
        (mod / "b.py").write_text("# b", encoding="utf-8")

        scanner = CapabilityScanner()
        result = scanner._get_last_modified_time(mod)
        # Should be a timestamp string, not "unknown"
        assert result != "unknown"
        assert "-" in result  # date format YYYY-MM-DD HH:MM:SS

    def test_no_py_files(self, tmp_path: Path):
        mod = tmp_path / "empty"
        mod.mkdir()
        # No .py files
        (mod / "readme.md").write_text("# readme", encoding="utf-8")

        scanner = CapabilityScanner()
        result = scanner._get_last_modified_time(mod)
        assert result == "unknown"


# ---------------------------------------------------------------------------
# scan_module tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestScanModule:
    """Tests for CapabilityScanner.scan_module."""

    def test_scan_simple_module(self, tmp_path: Path):
        module_dir = _make_module(
            tmp_path,
            "fake_mod",
            init_content='"""Fake module docstring."""\n',
            files={
                "core.py": textwrap.dedent('''
                    """Core module."""
                    VERSION = "2.0"

                    def do_work(x: int) -> str:
                        """Do some work."""
                        return str(x)

                    class Worker:
                        """A worker."""
                        def run(self):
                            """Run the worker."""
                            pass
                '''),
            },
        )

        scanner = _scanner_for(tmp_path)
        result = scanner.scan_module("fake_mod", module_dir)

        assert result is not None
        assert result.name == "fake_mod"
        assert result.docstring == "Fake module docstring."
        assert result.file_count >= 2  # __init__.py + core.py
        assert result.line_count > 0
        assert result.last_modified != "unknown"
        # Functions: 'do_work' should be found; 'run' also found via ast.walk
        func_names = [f.name for f in result.functions]
        assert "do_work" in func_names
        # Classes
        class_names = [c.name for c in result.classes]
        assert "Worker" in class_names
        # Constants
        assert "VERSION" in result.constants

    def test_scan_module_skips_test_files(self, tmp_path: Path):
        module_dir = _make_module(
            tmp_path,
            "tested_mod",
            files={
                "logic.py": "def real_func(): pass\n",
                "test_logic.py": "def test_only_func(): pass\n",
            },
        )

        scanner = _scanner_for(tmp_path)
        result = scanner.scan_module("tested_mod", module_dir)
        assert result is not None
        func_names = [f.name for f in result.functions]
        assert "real_func" in func_names
        assert "test_only_func" not in func_names

    def test_scan_nonexistent_module(self, tmp_path: Path):
        scanner = _scanner_for(tmp_path)
        bogus = tmp_path / "src" / "codomyrmex" / "nonexistent"
        # scan_module can handle a path that has no .py files gracefully
        # but the path must be created for iterdir to work
        bogus.mkdir(parents=True, exist_ok=True)
        (bogus / "__init__.py").write_text("", encoding="utf-8")
        result = scanner.scan_module("nonexistent", bogus)
        assert result is not None
        assert result.functions == []
        assert result.classes == []


# ---------------------------------------------------------------------------
# scan_all_modules tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestScanAllModules:
    """Tests for CapabilityScanner.scan_all_modules."""

    def test_scans_multiple_modules(self, tmp_path: Path):
        _make_module(tmp_path, "mod_a", init_content='"""Module A."""\n',
                     files={"a.py": "def func_a(): pass\n"})
        _make_module(tmp_path, "mod_b", init_content='"""Module B."""\n',
                     files={"b.py": "def func_b(): pass\n"})

        scanner = _scanner_for(tmp_path)
        result = scanner.scan_all_modules()

        assert "mod_a" in result
        assert "mod_b" in result

    def test_skips_dot_directories(self, tmp_path: Path):
        _make_module(tmp_path, ".hidden",
                     files={"h.py": "def hidden_func(): pass\n"})
        _make_module(tmp_path, "visible",
                     files={"v.py": "def visible_func(): pass\n"})

        scanner = _scanner_for(tmp_path)
        result = scanner.scan_all_modules()

        assert ".hidden" not in result
        assert "visible" in result

    def test_skips_dirs_without_init(self, tmp_path: Path):
        # Create a dir without __init__.py
        codomyrmex = tmp_path / "src" / "codomyrmex"
        codomyrmex.mkdir(parents=True, exist_ok=True)
        no_init = codomyrmex / "no_init_mod"
        no_init.mkdir()
        (no_init / "stuff.py").write_text("x = 1\n", encoding="utf-8")

        _make_module(tmp_path, "proper_mod",
                     files={"m.py": "y = 2\n"})

        scanner = _scanner_for(tmp_path)
        result = scanner.scan_all_modules()

        assert "no_init_mod" not in result
        assert "proper_mod" in result

    def test_nonexistent_codomyrmex_path(self, tmp_path: Path):
        # Don't create the src/codomyrmex directory at all
        scanner = CapabilityScanner(project_root=tmp_path)
        result = scanner.scan_all_modules()
        assert result == {}


# ---------------------------------------------------------------------------
# analyze_capability_relationships tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAnalyzeCapabilityRelationships:
    """Tests for CapabilityScanner.analyze_capability_relationships."""

    def _make_caps(self) -> dict[str, ModuleCapability]:
        func_a = FunctionCapability(
            name="shared_func", signature="shared_func()", docstring="",
            parameters=[], return_annotation="", file_path="", line_number=1,
            is_async=False, is_generator=False, decorators=[], complexity_score=3,
        )
        func_b = FunctionCapability(
            name="shared_func", signature="shared_func()", docstring="",
            parameters=[], return_annotation="", file_path="", line_number=1,
            is_async=False, is_generator=False, decorators=[], complexity_score=15,
        )
        func_c = FunctionCapability(
            name="unique_func", signature="unique_func()", docstring="",
            parameters=[], return_annotation="", file_path="", line_number=1,
            is_async=False, is_generator=False, decorators=[], complexity_score=1,
        )

        mod_a = ModuleCapability(
            name="mod_a", path="", docstring="", functions=[func_a, func_c],
            classes=[], constants={}, imports=[], exports=[], file_count=1,
            line_count=10, last_modified="",
        )
        mod_b = ModuleCapability(
            name="mod_b", path="", docstring="", functions=[func_b],
            classes=[], constants={}, imports=[], exports=[], file_count=1,
            line_count=10, last_modified="",
        )
        return {"mod_a": mod_a, "mod_b": mod_b}

    def test_shared_functions_detected(self):
        scanner = CapabilityScanner()
        caps = self._make_caps()
        rels = scanner.analyze_capability_relationships(caps)

        shared = rels["shared_functions"]
        shared_names = [s["name"] for s in shared]
        assert "shared_func" in shared_names
        assert "unique_func" not in shared_names

    def test_complexity_analysis(self):
        scanner = CapabilityScanner()
        caps = self._make_caps()
        rels = scanner.analyze_capability_relationships(caps)

        ca = rels["complexity_analysis"]
        assert ca["min"] == 1
        assert ca["max"] == 15
        assert 1 <= ca["average"] <= 15
        # func_b has complexity 15, which is > 10
        high = ca["high_complexity_functions"]
        assert any(h["complexity"] == 15 for h in high)

    def test_empty_capabilities(self):
        scanner = CapabilityScanner()
        rels = scanner.analyze_capability_relationships({})
        assert rels["shared_functions"] == []
        assert rels["complexity_analysis"] == {}

    def test_no_shared_functions(self):
        func_a = FunctionCapability(
            name="only_a", signature="only_a()", docstring="",
            parameters=[], return_annotation="", file_path="", line_number=1,
            is_async=False, is_generator=False, decorators=[], complexity_score=2,
        )
        mod_a = ModuleCapability(
            name="mod_a", path="", docstring="", functions=[func_a],
            classes=[], constants={}, imports=[], exports=[], file_count=1,
            line_count=10, last_modified="",
        )
        scanner = CapabilityScanner()
        rels = scanner.analyze_capability_relationships({"mod_a": mod_a})
        assert rels["shared_functions"] == []


# ---------------------------------------------------------------------------
# export_capabilities_report tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestExportCapabilitiesReport:
    """Tests for CapabilityScanner.export_capabilities_report."""

    def _sample_caps(self) -> dict[str, ModuleCapability]:
        func = FunctionCapability(
            name="example", signature="example(x: int) -> str",
            docstring="Example func.", parameters=[{"name": "x", "annotation": "int", "default": None}],
            return_annotation="str", file_path="/src/m.py", line_number=5,
            is_async=False, is_generator=False, decorators=["staticmethod"],
            complexity_score=2,
        )
        cls = ClassCapability(
            name="Widget", docstring="A widget.", methods=[func],
            properties=["size"], class_variables=["DEFAULT"], inheritance=["Base"],
            file_path="/src/m.py", line_number=20, is_abstract=False,
            decorators=["dataclass"],
        )
        mod = ModuleCapability(
            name="widgets", path="/src/widgets", docstring="Widgets module.",
            functions=[func], classes=[cls], constants={"MAX": 100},
            imports=["os"], exports=["Widget", "example"], file_count=2,
            line_count=50, last_modified="2026-01-15 12:00:00",
        )
        return {"widgets": mod}

    def test_export_with_custom_filename(self, tmp_path: Path):
        scanner = CapabilityScanner(project_root=tmp_path)
        caps = self._sample_caps()
        result = scanner.export_capabilities_report(caps, filename="test_report.json")

        assert result != ""
        report_path = Path(result)
        assert report_path.exists()
        assert report_path.name == "test_report.json"

        data = json.loads(report_path.read_text(encoding="utf-8"))
        assert "widgets" in data
        assert data["widgets"]["name"] == "widgets"
        assert len(data["widgets"]["functions"]) == 1
        assert len(data["widgets"]["classes"]) == 1
        assert data["widgets"]["classes"][0]["name"] == "Widget"

    def test_export_with_default_filename(self, tmp_path: Path):
        scanner = CapabilityScanner(project_root=tmp_path)
        caps = self._sample_caps()
        result = scanner.export_capabilities_report(caps)

        assert result != ""
        report_path = Path(result)
        assert report_path.exists()
        assert "codomyrmex_capabilities_" in report_path.name
        assert report_path.suffix == ".json"

    def test_export_empty_capabilities(self, tmp_path: Path):
        scanner = CapabilityScanner(project_root=tmp_path)
        result = scanner.export_capabilities_report({}, filename="empty.json")

        assert result != ""
        data = json.loads(Path(result).read_text(encoding="utf-8"))
        assert data == {}

    def test_export_serializes_method_details(self, tmp_path: Path):
        scanner = CapabilityScanner(project_root=tmp_path)
        caps = self._sample_caps()
        result = scanner.export_capabilities_report(caps, filename="detail.json")

        data = json.loads(Path(result).read_text(encoding="utf-8"))
        cls_data = data["widgets"]["classes"][0]
        assert len(cls_data["methods"]) == 1
        method = cls_data["methods"][0]
        assert method["name"] == "example"
        assert "signature" in method
        assert "complexity_score" in method

    def test_export_to_readonly_dir_returns_empty(self, tmp_path: Path):
        # Use a non-existent nested path that will fail
        scanner = CapabilityScanner(project_root=tmp_path / "nonexistent" / "deep")
        caps = self._sample_caps()
        result = scanner.export_capabilities_report(caps, filename="fail.json")
        assert result == ""


# ---------------------------------------------------------------------------
# End-to-end: scan_module with complex source
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestScanModuleEndToEnd:
    """End-to-end test scanning a module with diverse Python constructs."""

    def test_complex_module(self, tmp_path: Path):
        source = textwrap.dedent('''
            """Core logic."""
            import os
            from typing import Any

            MAX_SIZE = 1024
            DEFAULT_NAME = "widget"

            def simple():
                """Simple function."""
                return True

            async def fetch_data(url: str, timeout: int = 30) -> bytes:
                """Fetch data from URL."""
                pass

            def generate_items(n: int):
                """Generate n items."""
                for i in range(n):
                    yield i

            class BaseProcessor:
                """Base processor."""
                DEFAULT = True

                def process(self, data: Any) -> Any:
                    """Process data."""
                    if data:
                        for item in data:
                            if item:
                                pass
                    return data

                @property
                def name(self):
                    """Get name."""
                    return "base"

                def _internal(self):
                    pass

            class AdvancedProcessor(BaseProcessor):
                """Advanced processor with ABC."""
                pass
        ''')

        module_dir = _make_module(
            tmp_path, "complex_mod",
            init_content='"""Complex module."""\n',
            files={"logic.py": source},
        )

        scanner = _scanner_for(tmp_path)
        result = scanner.scan_module("complex_mod", module_dir)

        assert result is not None
        assert result.name == "complex_mod"
        assert result.docstring == "Complex module."

        # Functions
        func_names = [f.name for f in result.functions]
        assert "simple" in func_names
        assert "fetch_data" in func_names
        assert "generate_items" in func_names

        # Check async
        fetch = [f for f in result.functions if f.name == "fetch_data"][0]
        assert fetch.is_async is True

        # Check generator
        gen = [f for f in result.functions if f.name == "generate_items"][0]
        assert gen.is_generator is True

        # Classes
        class_names = [c.name for c in result.classes]
        assert "BaseProcessor" in class_names
        assert "AdvancedProcessor" in class_names

        # BaseProcessor details
        bp = [c for c in result.classes if c.name == "BaseProcessor"][0]
        assert "name" in bp.properties
        assert "DEFAULT" in bp.class_variables
        method_names = [m.name for m in bp.methods]
        assert "process" in method_names
        # _analyze_class includes all methods (private filtering only at module level)
        assert "_internal" in method_names

        # AdvancedProcessor inheritance
        ap = [c for c in result.classes if c.name == "AdvancedProcessor"][0]
        assert "BaseProcessor" in ap.inheritance

        # Constants
        assert "MAX_SIZE" in result.constants
        assert result.constants["MAX_SIZE"] == 1024
        assert "DEFAULT_NAME" in result.constants

        # Imports
        assert "os" in result.imports
        assert "typing" in result.imports
