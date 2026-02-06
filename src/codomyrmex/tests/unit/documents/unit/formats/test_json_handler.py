import unittest
from unittest.mock import ANY, mock_open, patch

import pytest

from codomyrmex.documents.formats.json_handler import read_json, write_json


@pytest.mark.unit
class TestJsonHandler(unittest.TestCase):
    def test_read_json(self):
        """Test reading JSON."""
        # read_json uses json.load(f)
        with patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}'):
            data = read_json("test.json")
            self.assertEqual(data, {"key": "value"})

    def test_write_json(self):
        """Test writing JSON."""
        data = {"key": "value"}
        with patch("builtins.open", new_callable=mock_open) as mock_file:
            with patch('pathlib.Path.mkdir'):
                write_json(data, "test.json")

            mock_file.assert_called_with(ANY, 'w', encoding='utf-8')
            # Verify json.dump called write on the handle
            # json.dump usually does multiple writes or one write
            # We can check that at least something was written
            mock_file().write.assert_called()
