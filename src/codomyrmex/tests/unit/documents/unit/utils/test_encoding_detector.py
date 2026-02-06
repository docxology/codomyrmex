import sys
import unittest
from unittest.mock import MagicMock, mock_open, patch

import pytest

from codomyrmex.documents.utils.encoding_detector import detect_encoding


@pytest.mark.unit
class TestEncodingDetector(unittest.TestCase):
    def test_detect_encoding_utf8_bom(self):
        """Test detecting UTF-8 with BOM using mock because no chardet."""
        # The BOM (\xef\xbb\xbf) is correctly detected as UTF-8-SIG
        with patch("builtins.open", new_callable=mock_open, read_data=b'\xef\xbb\xbfcontent'):
             enc = detect_encoding("test.txt")
             self.assertEqual(enc, "UTF-8-SIG") # Correct encoding for UTF-8 with BOM

    def test_detect_encoding_chardet(self):
        """Test delegation to chardet (mocked)."""
        mock_chardet = MagicMock()
        mock_chardet.detect.return_value = {'encoding': 'ascii', 'confidence': 1.0}

        with patch.dict(sys.modules, {'chardet': mock_chardet}):
            with patch("builtins.open", new_callable=mock_open, read_data=b'content'):
                enc = detect_encoding("test.txt")
                self.assertEqual(enc, "ascii")
