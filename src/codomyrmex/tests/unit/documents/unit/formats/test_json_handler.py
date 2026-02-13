"""Zero-Mock tests for JSON handler — uses real file I/O via tmp_path."""

import json

import pytest

from codomyrmex.documents.formats.json_handler import read_json, write_json


@pytest.mark.unit
class TestJsonHandler:
    def test_read_json(self, tmp_path):
        """Test reading JSON from a real file."""
        f = tmp_path / "test.json"
        f.write_text('{"key": "value"}', encoding="utf-8")

        data = read_json(str(f))
        assert data == {"key": "value"}

    def test_write_json(self, tmp_path):
        """Test writing JSON to a real file."""
        f = tmp_path / "test.json"
        data = {"key": "value"}

        write_json(data, str(f))

        assert f.exists()
        written = json.loads(f.read_text(encoding="utf-8"))
        assert written == data

    def test_roundtrip(self, tmp_path):
        """Test JSON write then read roundtrip."""
        f = tmp_path / "roundtrip.json"
        original = {"nested": {"list": [1, 2, 3]}, "flag": True}

        write_json(original, str(f))
        result = read_json(str(f))

        assert result == original
