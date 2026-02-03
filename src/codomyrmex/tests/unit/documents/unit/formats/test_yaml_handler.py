import pytest

import unittest
import sys
from unittest.mock import patch, mock_open, MagicMock
from codomyrmex.documents.formats.yaml_handler import read_yaml, write_yaml

@pytest.mark.unit
class TestYamlHandler(unittest.TestCase):
    def test_read_yaml_mocked(self):
        """Test reading YAML with mocked yaml module."""
        mock_yaml = MagicMock()
        mock_yaml.safe_load.return_value = {"key": "value"}
        
        with patch.dict(sys.modules, {'yaml': mock_yaml}):
            with patch("builtins.open", new_callable=mock_open, read_data="key: value"):
                data = read_yaml("test.yaml")
                self.assertEqual(data, {"key": "value"})

    def test_write_yaml_mocked(self):
        """Test writing YAML with mocked yaml module."""
        mock_yaml = MagicMock()
        data = {"key": "value"}
        
        with patch.dict(sys.modules, {'yaml': mock_yaml}):
            with patch("builtins.open", new_callable=mock_open):
                canary = MagicMock() # To verify parent creation
                with patch('pathlib.Path.parent', new_callable=lambda: canary):
                    write_yaml(data, "test.yaml")
        
        mock_yaml.dump.assert_called()
