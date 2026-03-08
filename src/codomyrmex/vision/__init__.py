"""Vision module for image analysis and document parsing.

Provides:
- ``VLMClient``: Vision-Language Model client (Ollama llava/bakllava).
- ``PDFExtractor``: Text extraction from PDF documents.
- ``AnnotationExtractor``: Structured annotation extraction from images.

All implementations use real backends (Zero-Mock compliant).
"""

from .annotation_extractor import AnnotationExtractor
from .models import Annotation, BoundingBox, PageContent, VLMConfig, VLMResponse
from .pdf_extractor import PDFExtractor
from .vlm_client import VLMClient

__all__ = [
    "Annotation",
    "AnnotationExtractor",
    "BoundingBox",
    "PDFExtractor",
    "PageContent",
    "VLMClient",
    "VLMConfig",
    "VLMResponse",
]
