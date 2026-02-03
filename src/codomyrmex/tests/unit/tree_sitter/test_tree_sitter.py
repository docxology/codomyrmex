"""Unit tests for tree_sitter module."""

import pytest
from unittest.mock import MagicMock, patch
from codomyrmex.tree_sitter import TreeSitterParser, LanguageManager

@pytest.mark.unit
def test_parser_initialization():
    """Test parser initialization with a mock language."""
    mock_language = MagicMock()
    with patch('tree_sitter.Parser') as mock_parser_cls:
        mock_instance = MagicMock()
        mock_parser_cls.return_value = mock_instance
        
        parser = TreeSitterParser(mock_language)
        mock_instance.set_language.assert_called_once_with(mock_language)

@pytest.mark.unit
def test_parse_call():
    """Test parse call delegation."""
    mock_language = MagicMock()
    with patch('tree_sitter.Parser') as mock_parser_cls:
        mock_instance = MagicMock()
        mock_parser_cls.return_value = mock_instance
        
        parser = TreeSitterParser(mock_language)
        parser.parse("print('hello')")
        
        # Verify it was called with bytes
        mock_instance.parse.assert_called_once_with(b"print('hello')")

@pytest.mark.unit
def test_language_manager():
    """Test language manager loading logic."""
    with patch('tree_sitter.Language') as mock_lang_cls:
        mock_instance = MagicMock()
        mock_lang_cls.return_value = mock_instance
        
        success = LanguageManager.load_language("/path/to/lib.so", "python")
        assert success is True
        assert LanguageManager.get_language("python") == mock_instance
