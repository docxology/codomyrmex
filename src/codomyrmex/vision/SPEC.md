# Vision Module Specification

**Version**: v1.1.9 | **Status**: Active

## Architecture

```
vision/
├── __init__.py            # Package exports
├── models.py              # VLMConfig, VLMResponse, BoundingBox, Annotation, PageContent
├── vlm_client.py          # VLMClient — Ollama VLM backend
├── pdf_extractor.py       # PDFExtractor — pymupdf + VLM fallback
└── annotation_extractor.py # AnnotationExtractor — structured image annotations
```

## API Reference

### VLMClient

| Method | Args | Returns | Description |
|--------|------|---------|-------------|
| `is_available()` | — | `bool` | Check Ollama server + model availability |
| `analyze_image()` | `image_path, prompt` | `VLMResponse` | Analyze image with VLM prompt |
| `extract_text()` | `image_path` | `str` | OCR-like text extraction via VLM |
| `describe_for_annotation()` | `image_path, prompt` | `VLMResponse` | Structured annotation analysis |

### PDFExtractor

| Method | Args | Returns | Description |
|--------|------|---------|-------------|
| `is_available()` | — | `bool` | Check pymupdf installation |
| `extract_text()` | `pdf_path` | `list[PageContent]` | Text extraction from PDF |
| `extract_with_vlm()` | `pdf_path, vlm_client` | `list[PageContent]` | VLM-based extraction for scanned PDFs |
| `get_metadata()` | `pdf_path` | `dict` | PDF metadata extraction |

### AnnotationExtractor

| Method | Args | Returns | Description |
|--------|------|---------|-------------|
| `extract_annotations()` | `image_path, vlm_client` | `list[Annotation]` | Extract structured annotations |
| `extract_text_regions()` | `image_path, vlm_client` | `list[Annotation]` | Extract text-only regions |

## Data Models

- **`BoundingBox`**: Normalized coordinates (0–1) with `area` and `center` properties
- **`Annotation`**: Label + BoundingBox + confidence + attributes
- **`PageContent`**: Page number, text, images, annotations, metadata

## Error Handling

- `FileNotFoundError` for missing images/PDFs
- `ImportError` for missing `pymupdf`
- `RuntimeError` for Ollama connection failures
- JSON parse fallback for malformed VLM responses
