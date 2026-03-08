# Vision Module - Programmable AI Interface (PAI)

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Module Identity

- **Name**: vision
- **Category**: Media Processing / AI Intelligence
- **Dependencies**: logging_monitoring, environment_setup, llm

## Capabilities

### Primary Functions

1. **Visual Language Model (VLM) Inference**
   - Input: Image path + text prompt
   - Output: `VLMResponse` with generated text description/analysis
   - Provider: Ollama (local-first; moondream, llava, bakllava models)

2. **PDF Text Extraction**
   - Input: PDF file path
   - Output: Extracted text content (text-layer first, VLM fallback for scanned docs)
   - Provider: pdfplumber + VLM fallback

3. **Structured Annotation Extraction**
   - Input: Image path + annotation schema
   - Output: Structured JSON annotations (bounding boxes, labels, descriptions)
   - Provider: VLM with JSON-mode parsing

### Availability Flags

```python
VLM_AVAILABLE      # Vision-Language Model available via Ollama
PDF_AVAILABLE      # PDF extraction available (pdfplumber)
```

## Interface Contracts

### VLMClient

```python
class VLMClient:
    def __init__(model: str = "moondream", base_url: str = "http://localhost:11434")
    def analyze_image(image_path: Path, prompt: str, **kwargs) -> VLMResponse
    def describe_image(image_path: Path) -> VLMResponse
    def list_models() -> list[str]
```

### PDFExtractor

```python
class PDFExtractor:
    def extract_text(pdf_path: Path) -> str
    def extract_pages(pdf_path: Path) -> list[str]
    def extract_with_vlm_fallback(pdf_path: Path, vlm_client: VLMClient) -> str
```

### AnnotationExtractor

```python
class AnnotationExtractor:
    def extract_annotations(image_path: Path, schema: dict) -> list[Annotation]
    def extract_bounding_boxes(image_path: Path) -> list[BoundingBox]
```

## Data Models

### VLMResponse

```python
VLMResponse:
    text: str                    # Generated response text
    model: str                   # Model name used
    processing_time: float       # Seconds
    image_path: Optional[Path]   # Source image
    prompt: str                  # Input prompt
```

### Annotation

```python
Annotation:
    label: str                   # Category/type label
    description: str             # Free-text description
    bounding_box: Optional[BoundingBox]
    confidence: float            # 0.0-1.0
```

### BoundingBox

```python
BoundingBox:
    x: int                       # Top-left X
    y: int                       # Top-left Y
    width: int
    height: int
    label: Optional[str]
```

## Error Handling

### Exception Hierarchy

```
VisionError (base)
├── VLMConnectionError     # Ollama not available
├── ModelNotFoundError     # Requested model not pulled
├── ImageFormatError       # Unsupported image format
├── PDFExtractionError     # PDF parsing failure
└── AnnotationParseError   # JSON parse failure from VLM
```

## Configuration

```python
VisionConfig:
    model: str = "moondream"         # Ollama model name
    base_url: str = "http://localhost:11434"
    timeout: float = 30.0            # Request timeout
    max_image_size_mb: float = 10.0  # Max image size
    pdf_dpi: int = 300               # PDF render DPI for VLM fallback
```

## Integration Points

### Upstream Dependencies

- `logging_monitoring` — Logging infrastructure
- `environment_setup` — Dependency validation
- `llm` — Ollama connectivity patterns

### Downstream Consumers

- `documents` — PDF processing pipeline
- `scrape` — Screenshot analysis in web scraping
- `agents` — Visual task understanding

## Resource Management

### Memory

- VLM models: 2-8GB VRAM depending on model
- Models loaded on-demand via Ollama

### Network

- Requires Ollama server running locally (default: :11434)
- No external API calls

### Thread Safety

- Create separate `VLMClient` instances per thread
- Ollama handles concurrent requests internally

## MCP Tools

This module does not expose MCP tools directly. Access via:

- Direct Python import: `from codomyrmex.vision import VLMClient, PDFExtractor, AnnotationExtractor`

## Versioning

- Added in v1.1.9 ("Multimodal & Streaming")
- Part of the Specialized architectural layer
