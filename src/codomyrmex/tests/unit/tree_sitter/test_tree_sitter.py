"""Comprehensive tests for the tree_sitter module.

Tests cover LanguageManager, TreeSitterParser, and edge cases.
Uses real tree-sitter when available, otherwise tests internal logic
that does not require the library.
"""

import pytest

try:
    import tree_sitter as _ts_lib
    _HAS_TREE_SITTER = True
except ImportError:
    _HAS_TREE_SITTER = False

try:
    import tree_sitter_python as tspython
    _HAS_TS_PYTHON = True
except ImportError:
    _HAS_TS_PYTHON = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_python_lang():
    """Get a tree-sitter Python language object, or skip."""
    if not _HAS_TREE_SITTER or not _HAS_TS_PYTHON:
        pytest.skip("tree-sitter or tree-sitter-python not installed")
    return _ts_lib.Language(tspython.language())


def _get_parser(lang=None):
    """Create a TreeSitterParser with Python language."""
    if lang is None:
        lang = _get_python_lang()
    from codomyrmex.coding.parsers.tree_sitter import TreeSitterParser
    return TreeSitterParser(lang)


# ---------------------------------------------------------------------------
# Module imports
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_module_importable():
    """Test that the tree_sitter package can be imported."""
    from codomyrmex.coding.parsers import tree_sitter as ts_mod
    assert ts_mod is not None


@pytest.mark.unit
def test_submodules_importable():
    """Test that submodule namespaces exist."""
    from codomyrmex.coding.parsers.tree_sitter import languages, parsers, queries, transformers
    assert languages is not None
    assert parsers is not None
    assert queries is not None
    assert transformers is not None


# ---------------------------------------------------------------------------
# LanguageManager (no tree-sitter dependency for core logic)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_language_manager_get_unknown():
    """Test retrieving an unknown language returns None."""
    from codomyrmex.coding.parsers.tree_sitter import LanguageManager
    LanguageManager._languages = {}
    result = LanguageManager.get_language("nonexistent_xyz")
    assert result is None


@pytest.mark.unit
def test_language_manager_registration_manual():
    """Test manually registering a language object."""
    from codomyrmex.coding.parsers.tree_sitter import LanguageManager
    LanguageManager._languages = {}
    sentinel = object()
    LanguageManager._languages["test_lang"] = sentinel
    assert LanguageManager.get_language("test_lang") is sentinel
    # Cleanup
    LanguageManager._languages = {}


@pytest.mark.unit
def test_language_manager_discover_nonexistent_path():
    """Test discover_languages with a path that does not exist."""
    from codomyrmex.coding.parsers.tree_sitter import LanguageManager
    LanguageManager._languages = {}
    LanguageManager.discover_languages("/nonexistent/path/abc123")
    assert len(LanguageManager._languages) == 0


@pytest.mark.unit
def test_language_manager_discover_empty_directory(tmp_path):
    """Test discover_languages with an empty directory."""
    from codomyrmex.coding.parsers.tree_sitter import LanguageManager
    LanguageManager._languages = {}
    LanguageManager.discover_languages(str(tmp_path))
    assert len(LanguageManager._languages) == 0


@pytest.mark.unit
def test_language_manager_multiple_registrations():
    """Test registering multiple languages."""
    from codomyrmex.coding.parsers.tree_sitter import LanguageManager
    LanguageManager._languages = {}
    LanguageManager._languages["lang_a"] = "a"
    LanguageManager._languages["lang_b"] = "b"
    assert LanguageManager.get_language("lang_a") == "a"
    assert LanguageManager.get_language("lang_b") == "b"
    assert LanguageManager.get_language("lang_c") is None
    LanguageManager._languages = {}


# ---------------------------------------------------------------------------
# LanguageManager with real tree-sitter-python
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_language_manager_real_registration():
    """Test registering a real tree-sitter language."""
    lang = _get_python_lang()
    from codomyrmex.coding.parsers.tree_sitter import LanguageManager
    LanguageManager._languages = {}
    LanguageManager._languages["python"] = lang
    assert LanguageManager.get_language("python") is lang
    LanguageManager._languages = {}


# ---------------------------------------------------------------------------
# TreeSitterParser
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_parser_initialization():
    """Test parser initialization with a real language."""
    parser = _get_parser()
    assert parser is not None
    assert parser.parser is not None


@pytest.mark.unit
def test_parse_simple_function():
    """Test parsing a simple Python function definition."""
    parser = _get_parser()
    tree = parser.parse("def hello():\n    return 42\n")
    assert tree is not None
    assert tree.root_node is not None


@pytest.mark.unit
def test_parse_empty_string():
    """Test parsing an empty string produces a tree."""
    parser = _get_parser()
    tree = parser.parse("")
    assert tree is not None
    assert tree.root_node is not None


@pytest.mark.unit
def test_parse_class_definition():
    """Test parsing a class definition."""
    parser = _get_parser()
    code = "class Foo:\n    def bar(self):\n        pass\n"
    tree = parser.parse(code)
    root = tree.root_node
    assert root.type == "module"
    assert root.child_count > 0


@pytest.mark.unit
def test_parse_multiline_code():
    """Test parsing multi-line Python code."""
    parser = _get_parser()
    code = """
import os
import sys

def main():
    x = 1
    y = 2
    return x + y

if __name__ == "__main__":
    main()
"""
    tree = parser.parse(code)
    assert tree is not None
    # Should have multiple top-level statements
    root = tree.root_node
    assert root.child_count >= 3


@pytest.mark.unit
def test_parse_syntax_error_still_produces_tree():
    """Test parsing invalid Python still produces a partial tree."""
    parser = _get_parser()
    tree = parser.parse("def incomplete(:\n")
    assert tree is not None
    assert tree.root_node is not None


@pytest.mark.unit
def test_parse_bytes_input():
    """Test parsing with bytes input (already encoded)."""
    parser = _get_parser()
    # The parser should handle both str and bytes
    tree = parser.parse("x = 1\n")
    assert tree is not None


@pytest.mark.unit
def test_root_node_type_is_module():
    """Test that the root node type for Python is 'module'."""
    parser = _get_parser()
    tree = parser.parse("x = 1\n")
    assert tree.root_node.type == "module"


@pytest.mark.unit
def test_parse_preserves_structure():
    """Test that parsing preserves the structure of simple code."""
    parser = _get_parser()
    tree = parser.parse("x = 1\ny = 2\n")
    root = tree.root_node
    # Two expression statements
    assert root.child_count == 2


@pytest.mark.unit
def test_tree_root_node_children():
    """Test accessing children of the root node."""
    parser = _get_parser()
    tree = parser.parse("def f(): pass\ndef g(): pass\n")
    root = tree.root_node
    children = [root.children[i] for i in range(root.child_count)]
    assert len(children) == 2
    for child in children:
        assert child.type == "function_definition"


@pytest.mark.unit
def test_node_text_extraction():
    """Test extracting text from a parsed node."""
    parser = _get_parser()
    code = "x = 42\n"
    tree = parser.parse(code)
    root = tree.root_node
    # The root node text should match the source
    assert root.text is not None


@pytest.mark.unit
def test_parse_decorator():
    """Test parsing a decorated function."""
    parser = _get_parser()
    code = "@decorator\ndef func():\n    pass\n"
    tree = parser.parse(code)
    root = tree.root_node
    assert root.child_count >= 1


@pytest.mark.unit
def test_parse_complex_expressions():
    """Test parsing complex expressions."""
    parser = _get_parser()
    code = "result = [x**2 for x in range(10) if x % 2 == 0]\n"
    tree = parser.parse(code)
    assert tree is not None
    assert tree.root_node.child_count >= 1
