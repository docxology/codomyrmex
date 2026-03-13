"""Zero-mock tests for coding.pattern_matching module.

Verifies ASTMatcher and its pattern detection logic using real Python code.
No mocks.
"""

import textwrap

import pytest

from codomyrmex.coding.pattern_matching.ast_matcher import ASTMatcher


@pytest.fixture
def matcher():
    return ASTMatcher()

@pytest.mark.unit
class TestASTMatcher:
    """Tests for ASTMatcher pattern and anti-pattern detection."""

    def test_parse_code(self, matcher):
        code = "def foo(): pass"
        result = matcher.parse_code(code)
        assert result["language"] == "python"
        assert result["node_count"] > 0
        assert any(n["name"] == "foo" for n in result["top_level"])

    def test_find_singleton_pattern(self, matcher):
        code = textwrap.dedent("""\
            class MySingleton:
                _instance = None
                def __new__(cls):
                    if cls._instance is None:
                        cls._instance = super().__new__(cls)
                    return cls._instance
        """)
        results = matcher.find_pattern(code, "singleton")
        assert len(results) >= 1
        assert results[0].pattern_name == "singleton"
        assert results[0].name == "MySingleton"

    def test_find_factory_pattern(self, matcher):
        code = "def create_user(): return User()"
        results = matcher.find_pattern(code, "factory")
        assert len(results) == 1
        assert results[0].name == "create_user"

    def test_find_context_manager_pattern(self, matcher):
        code = textwrap.dedent("""\
            class MyContext:
                def __enter__(self): pass
                def __exit__(self, *args): pass
        """)
        results = matcher.find_pattern(code, "context_manager")
        assert len(results) == 1
        assert results[0].name == "MyContext"

    def test_find_antipattern_bare_except(self, matcher):
        code = textwrap.dedent("""\
            try:
                do_something()
            except:
                pass
        """)
        results = matcher.find_antipatterns(code)
        assert any(r.pattern_name == "bare_except" for r in results)

    def test_find_antipattern_mutable_default(self, matcher):
        code = "def foo(items=[]): pass"
        results = matcher.find_antipatterns(code)
        assert any(r.pattern_name == "mutable_default_arg" for r in results)

    def test_match_structure_success(self, matcher):
        code = "def a(): pass\ndef b(): pass"
        template = "def f1(): ...\ndef f2(): ..."
        assert matcher.match_structure(code, template) is True

    def test_match_structure_failure(self, matcher):
        code = "class A: pass"
        template = "def f(): pass"
        assert matcher.match_structure(code, template) is False
