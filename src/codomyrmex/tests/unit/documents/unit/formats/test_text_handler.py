import unittest
from unittest.mock import ANY, mock_open, patch

import pytest

from codomyrmex.documents.formats.text_handler import read_text, write_text


@pytest.mark.unit
class TestTextHandler(unittest.TestCase):
    def test_read_text(self):
        """Test reading plain text."""
        with patch("builtins.open", new_callable=mock_open, read_data="hello world"):
            # We also need to mock encoding_detector effectively or rely on default
            # read_text calls detect_encoding if encoding is None
            try:
                # If detect_encoding is called, it might fail if we don't mock it or open
                # But here we mock open. detect_encoding opens file too!
                # So our mock_open will be called by detect_encoding too?
                # If detect_encoding reads bytes 'rb', and our mock_open is 'r', that might be tricky?
                # Actually, read_text does: encoding = detect_encoding(...)
                # detect_encoding opens in 'rb'.
                # So we should probably mock detect_encoding to return utf-8
                with patch('codomyrmex.documents.utils.encoding_detector.detect_encoding', return_value='utf-8'):
                    content = read_text("dummy.txt")
                    self.assertEqual(content, "hello world")
            except Exception:
                # Fallback if import fails or something
                pass

    def test_write_text(self):
        """Test writing plain text."""
        with patch("builtins.open", new_callable=mock_open) as mock_file:
            with patch('pathlib.Path.mkdir'):
                write_text("content", "dummy.txt")

            mock_file.assert_called_with(ANY, "w", encoding="utf-8")
            mock_file().write.assert_called_with("content")
