"""Document metadata operations."""

from .extractor import extract_metadata
from .manager import get_metadata, update_metadata
from .versioning import get_document_version, set_document_version

__all__ = [
    "extract_metadata",
    "update_metadata",
    "get_metadata",
    "get_document_version",
    "set_document_version",
]



