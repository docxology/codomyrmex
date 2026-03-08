# Vision

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

**Module**: `codomyrmex.vision` | **Status**: Active

## Overview

Image analysis and document parsing module using Vision-Language Models (VLMs) via local Ollama backends. Provides image analysis, text extraction (OCR-like), structured annotation extraction, and PDF text parsing with VLM fallback for scanned documents.

## Key Exports

- **`VLMClient`** — Ollama-based Vision-Language Model client (llava, bakllava).
- **`PDFExtractor`** — Text extraction from PDF documents using pymupdf.
- **`AnnotationExtractor`** — Structured annotation extraction from images.
- **`VLMConfig`** — Configuration for VLM connections.
- **`VLMResponse`** — VLM analysis response data.
- **`BoundingBox`** — Spatial annotation with area and center calculation.
- **`Annotation`** — Structured annotation with label, bounding box, confidence.
- **`PageContent`** — Extracted page content with text, images, annotations.

## Quick Start

```python
from codomyrmex.vision import VLMClient, VLMConfig

client = VLMClient(VLMConfig(model_name="llava"))
if client.is_available():
    response = client.analyze_image("photo.jpg", "What is in this image?")
    print(response.text)
```

## Dependencies

- **Required**: None (core models are dependency-free)
- **Optional**: `pymupdf` (for PDF extraction), Ollama server (for VLM analysis)

## Navigation

- **🏠 Root**: [codomyrmex](../../../../README.md)
