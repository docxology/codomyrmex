"""Documents Module Exception Classes

This module defines all exception classes used within the Documents module.
"""

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class DocumentsError(CodomyrmexError):
    """Base exception class for all Documents module errors."""
    pass


class DocumentReadError(DocumentsError):
    """Raised when document reading fails."""
    
    def __init__(self, message: str, file_path: str = None, **kwargs):
        super().__init__(message, **kwargs)
        if file_path:
            self.context["file_path"] = file_path


class DocumentWriteError(DocumentsError):
    """Raised when document writing fails."""
    
    def __init__(self, message: str, file_path: str = None, **kwargs):
        super().__init__(message, **kwargs)
        if file_path:
            self.context["file_path"] = file_path


class DocumentParseError(DocumentsError):
    """Raised when document parsing fails."""
    pass


class DocumentValidationError(DocumentsError):
    """Raised when document validation fails."""
    
    def __init__(self, message: str, validation_errors: list = None, **kwargs):
        super().__init__(message, **kwargs)
        if validation_errors:
            self.context["validation_errors"] = validation_errors


class DocumentConversionError(DocumentsError):
    """Raised when document format conversion fails."""
    pass


class UnsupportedFormatError(DocumentsError):
    """Raised when an unsupported document format is requested."""
    
    def __init__(self, message: str, format: str = None, **kwargs):
        super().__init__(message, **kwargs)
        if format:
            self.context["format"] = format


class EncodingError(DocumentsError):
    """Raised when encoding detection or conversion fails."""
    pass


class MetadataError(DocumentsError):
    """Raised when metadata operations fail."""
    pass

