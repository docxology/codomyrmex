"""Format-specific document handlers."""

# Import handlers conditionally
try:
    from .markdown_handler import read_markdown, write_markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    read_markdown = None
    write_markdown = None
    MARKDOWN_AVAILABLE = False

try:
    from .json_handler import read_json, write_json
    JSON_AVAILABLE = True
except ImportError:
    read_json = None
    write_json = None
    JSON_AVAILABLE = False

try:
    from .yaml_handler import read_yaml, write_yaml
    YAML_AVAILABLE = True
except ImportError:
    read_yaml = None
    write_yaml = None
    YAML_AVAILABLE = False

try:
    from .text_handler import read_text, write_text
    TEXT_AVAILABLE = True
except ImportError:
    read_text = None
    write_text = None
    TEXT_AVAILABLE = False

try:
    from .pdf_handler import read_pdf, write_pdf, PDFDocument
    PDF_AVAILABLE = True
except ImportError:
    read_pdf = None
    write_pdf = None
    PDFDocument = None
    PDF_AVAILABLE = False

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
    __all__.extend(["read_pdf", "write_pdf", "PDFDocument"])



