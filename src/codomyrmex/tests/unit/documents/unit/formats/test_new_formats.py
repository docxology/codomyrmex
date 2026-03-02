"""Zero-mock tests for new document formats (HTML, XML, CSV)."""

import pytest

from codomyrmex.documents.exceptions import DocumentReadError
from codomyrmex.documents.formats.csv_handler import read_csv, write_csv
from codomyrmex.documents.formats.html_handler import (
    read_html,
    strip_html_tags,
    write_html,
)
from codomyrmex.documents.formats.xml_handler import read_xml, write_xml


@pytest.mark.unit
class TestHtmlHandler:
    def test_html_roundtrip(self, tmp_path):
        f = tmp_path / "test.html"
        content = "<html><body><h1>Hello</h1></body></html>"
        write_html(content, f)
        assert f.exists()
        assert read_html(f) == content

    def test_strip_html(self):
        html = "<p>Hello <b>World</b></p>"
        assert strip_html_tags(html) == "Hello World"

@pytest.mark.unit
class TestXmlHandler:
    def test_xml_roundtrip(self, tmp_path):
        f = tmp_path / "test.xml"
        content = "<root><child>data</child></root>"
        write_xml(content, f)
        assert f.exists()
        assert read_xml(f) == content

    def test_invalid_xml(self, tmp_path):
        f = tmp_path / "bad.xml"
        f.write_text("<unclosed>", encoding="utf-8")
        with pytest.raises(DocumentReadError):
            read_xml(f)

@pytest.mark.unit
class TestCsvHandler:
    def test_csv_roundtrip(self, tmp_path):
        f = tmp_path / "test.csv"
        data = [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]
        write_csv(data, f)
        assert f.exists()
        read_data = read_csv(f)
        assert read_data == data
