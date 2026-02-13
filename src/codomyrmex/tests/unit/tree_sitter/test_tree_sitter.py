"""Zero-Mock tests for tree_sitter module.

Uses real tree-sitter parser when available (skipif not installed).
"""

import pytest

try:
    import tree_sitter
    from codomyrmex.tree_sitter import LanguageManager, TreeSitterParser
    _HAS_TREE_SITTER = True
except ImportError:
    _HAS_TREE_SITTER = False

if not _HAS_TREE_SITTER:
    pytest.skip("tree_sitter not available", allow_module_level=True)


@pytest.mark.unit
def test_language_manager_registration():
    """Test LanguageManager load and retrieval."""
    # Test with the built-in Python language if tree-sitter-python is available
    try:
        import tree_sitter_python as tspython
        lang = tree_sitter.Language(tspython.language())
        LanguageManager._languages = {}  # Reset
        LanguageManager._languages["python"] = lang
        assert LanguageManager.get_language("python") is lang
    except ImportError:
        pytest.skip("tree-sitter-python not installed")


@pytest.mark.unit
def test_parser_initialization():
    """Test parser initialization with a real language."""
    try:
        import tree_sitter_python as tspython
        lang = tree_sitter.Language(tspython.language())
        parser = TreeSitterParser(lang)
        assert parser is not None
    except ImportError:
        pytest.skip("tree-sitter-python not installed")


@pytest.mark.unit
def test_parse_python_code():
    """Test parsing real Python code."""
    try:
        import tree_sitter_python as tspython
        lang = tree_sitter.Language(tspython.language())
        parser = TreeSitterParser(lang)
        tree = parser.parse("def hello():\n    return 42\n")
        assert tree is not None
    except ImportError:
        pytest.skip("tree-sitter-python not installed")


@pytest.mark.unit
def test_language_manager_unknown():
    """Test retrieving unknown language."""
    LanguageManager._languages = {}  # Reset
    result = LanguageManager.get_language("unknown_lang_xyz")
    assert result is None
