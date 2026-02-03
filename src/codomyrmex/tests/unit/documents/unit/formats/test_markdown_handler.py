import pytest

import unittest
from unittest.mock import patch, mock_open, MagicMock
from codomyrmex.documents.formats.markdown_handler import read_markdown, write_markdown

@pytest.mark.unit
class TestMarkdownHandler(unittest.TestCase):
    def test_read_markdown(self):
        """Test reading markdown."""
        with patch("builtins.open", new_callable=mock_open, read_data="# Header\nContent"):
            content = read_markdown("test.md")
            self.assertEqual(content, "# Header\nContent")

    def test_write_markdown(self):
        """Test writing markdown."""
        content = "# Header\nContent"
        with patch("builtins.open", new_callable=mock_open) as mock_file:
            # We must also mock parent.mkdir because write_markdown calls it
            # mocking Path.parent is tricky, but often not needed if mkdir doesnt crash
            # But the code does file_path.parent.mkdir(...)
            # If we pass a string "test.md", Path("test.md").parent is "."
            # Path(".").mkdir works or is skipped? No, mkdir(parents=True, exist_ok=True)
            # We should mock mkdir to be safe
            with patch('pathlib.Path.mkdir'):
                write_markdown(content, "test.md")
            
            mock_file.assert_called_with(unittest.mock.ANY, 'w', encoding='utf-8')
            handle = mock_file()
            handle.write.assert_called_with(content)
