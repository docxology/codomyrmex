"""Format-specific document handlers."""

# Import handlers conditionally
try:
    from .markdown_handler import read_markdown, write_markdown

    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False

try:
    from .json_handler import read_json, write_json

    JSON_AVAILABLE = True
except ImportError:
    JSON_AVAILABLE = False

try:
    from .yaml_handler import read_yaml, write_yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    from .text_handler import read_text, write_text

    TEXT_AVAILABLE = True
except ImportError:
    TEXT_AVAILABLE = False

try:
    from .pdf_handler import PDFDocument, read_pdf, write_pdf

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from .html_handler import read_html, strip_html_tags, write_html

    HTML_AVAILABLE = True
except ImportError:
    HTML_AVAILABLE = False

try:
    from .xml_handler import read_xml, write_xml

    XML_AVAILABLE = True
except ImportError:
    XML_AVAILABLE = False

try:
    from .csv_handler import read_csv, write_csv

    CSV_AVAILABLE = True
except ImportError:
    CSV_AVAILABLE = False

__all__ = []

if MARKDOWN_AVAILABLE:
    __all__.extend(["read_markdown", "write_markdown"])

if JSON_AVAILABLE:
    __all__.extend(["read_json", "write_json"])

if YAML_AVAILABLE:
    __all__.extend(["read_yaml", "write_yaml"])

if TEXT_AVAILABLE:
    __all__.extend(["read_text", "write_text"])

if PDF_AVAILABLE:
    __all__.extend(["PDFDocument", "read_pdf", "write_pdf"])

if HTML_AVAILABLE:
    __all__.extend(["read_html", "strip_html_tags", "write_html"])

if XML_AVAILABLE:
    __all__.extend(["read_xml", "write_xml"])

if CSV_AVAILABLE:
    __all__.extend(["read_csv", "write_csv"])
