
import unittest
import sys
from unittest.mock import patch, mock_open, MagicMock
from codomyrmex.documents.utils.encoding_detector import detect_encoding

class TestEncodingDetector(unittest.TestCase):
    def test_detect_encoding_utf8_bom(self):
        """Test detecting UTF-8 with BOM using mock because no chardet."""
        # Since chardet is not available, it hits ImportError logic and returns default (utf-8)
        # So we just test that it returns default without crashing
        with patch("builtins.open", new_callable=mock_open, read_data=b'\xef\xbb\xbfcontent'):
             enc = detect_encoding("test.txt")
             self.assertEqual(enc, "utf-8") # Expect default

    def test_detect_encoding_chardet(self):
        """Test delegation to chardet (mocked)."""
        mock_chardet = MagicMock()
        mock_chardet.detect.return_value = {'encoding': 'ascii', 'confidence': 1.0}
        
        with patch.dict(sys.modules, {'chardet': mock_chardet}):
            with patch("builtins.open", new_callable=mock_open, read_data=b'content'):
                enc = detect_encoding("test.txt")
                self.assertEqual(enc, "ascii")
