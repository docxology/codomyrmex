"""Zero-Mock tests for YAML handler — uses real file I/O via tmp_path."""

import pytest
import yaml

from codomyrmex.documents.formats.yaml_handler import read_yaml, write_yaml


@pytest.mark.unit
class TestYamlHandler:
    """Test suite for YamlHandler."""
    def test_read_yaml(self, tmp_path):
        """Test reading YAML from a real file."""
        f = tmp_path / "test.yaml"
        f.write_text("key: value\n", encoding="utf-8")

        data = read_yaml(str(f))
        assert data == {"key": "value"}

    def test_write_yaml(self, tmp_path):
        """Test writing YAML to a real file."""
        f = tmp_path / "test.yaml"
        data = {"key": "value"}

        write_yaml(data, str(f))

        assert f.exists()
        written = yaml.safe_load(f.read_text(encoding="utf-8"))
        assert written == data

    def test_roundtrip(self, tmp_path):
        """Test YAML write then read roundtrip."""
        f = tmp_path / "roundtrip.yaml"
        original = {"nested": {"list": [1, 2, 3]}, "flag": True}

        write_yaml(original, str(f))
        result = read_yaml(str(f))

        assert result == original
