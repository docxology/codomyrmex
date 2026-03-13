# Vision - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `vision` module provides local-first visual understanding using Vision-Language Models via Ollama (llava/bakllava). Includes image analysis, PDF text extraction, and structured annotation extraction. All implementations are Zero-Mock compliant.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `VLMClient` | Vision-Language Model client for image analysis via Ollama |
| `PDFExtractor` | Text extraction from PDF documents |
| `AnnotationExtractor` | Structured annotation extraction from images |

### 2.2 Data Models

| Class | Description |
|-------|-------------|
| `VLMConfig` | Configuration for VLM inference (model name, temperature, max tokens) |
| `VLMResponse` | Response from VLM analysis (text, tokens, latency) |
| `Annotation` | Structured annotation with label and bounding box |
| `BoundingBox` | Bounding box coordinates (x, y, width, height) |
| `PageContent` | Extracted page content from PDFs |

## 3. Usage Example

```python
from codomyrmex.vision import VLMClient, VLMConfig

client = VLMClient(VLMConfig(model="llava"))
response = client.analyze_image("screenshot.png", prompt="Describe this UI")
print(response.text)
```

## 4. Related Modules

| Module | Relationship |
|--------|-------------|
| `image` | Reserved namespace for image metadata extraction |
| `multimodal` | Image generation via `ImageGenerator` |

## 5. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
