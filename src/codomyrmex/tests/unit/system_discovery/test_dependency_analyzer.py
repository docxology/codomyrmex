"""Tests for system_discovery.core.dependency_analyzer — zero-mock.

Covers: DependencyAnalyzer (get_function_signature_from_ast).
"""

import ast
from pathlib import Path

import pytest

from codomyrmex.system_discovery.core.dependency_analyzer import DependencyAnalyzer


@pytest.mark.unit
class TestDependencyAnalyzerGetFunctionSignatureFromAst:
    """Test get_function_signature_from_ast in DependencyAnalyzer."""

    def test_simple_args(self):
        analyzer = DependencyAnalyzer(Path("."), Path("."))
        code = "def foo(a, b): pass"
        tree = ast.parse(code)
        func_node = tree.body[0]
        sig = analyzer.get_function_signature_from_ast(func_node)
        assert sig == "foo(a, b)"

    def test_defaults(self):
        analyzer = DependencyAnalyzer(Path("."), Path("."))
        code = "def bar(x, y=10, z='hello'): pass"
        tree = ast.parse(code)
        func_node = tree.body[0]
        sig = analyzer.get_function_signature_from_ast(func_node)
        assert sig == "bar(x, y=10, z='hello')"

    def test_varargs_and_kwargs(self):
        analyzer = DependencyAnalyzer(Path("."), Path("."))
        code = "def baz(*args, **kwargs): pass"
        tree = ast.parse(code)
        func_node = tree.body[0]
        sig = analyzer.get_function_signature_from_ast(func_node)
        assert sig == "baz(*args, **kwargs)"

    def test_no_args(self):
        analyzer = DependencyAnalyzer(Path("."), Path("."))
        code = "def noop(): pass"
        tree = ast.parse(code)
        func_node = tree.body[0]
        sig = analyzer.get_function_signature_from_ast(func_node)
        assert sig == "noop()"

    def test_complex_args(self):
        analyzer = DependencyAnalyzer(Path("."), Path("."))
        code = "def complex_func(a, b, c=1, d=2, *args, **kwargs): pass"
        tree = ast.parse(code)
        func_node = tree.body[0]
        sig = analyzer.get_function_signature_from_ast(func_node)
        assert sig == "complex_func(a, b, c=1, d=2, *args, **kwargs)"
