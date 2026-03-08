# Vision Module — Agentic Guide

**Module**: `codomyrmex.vision` | **Version**: v1.1.9

## Quick Reference

```python
from codomyrmex.vision import VLMClient, PDFExtractor, AnnotationExtractor
```

## Agent Instructions

1. **Check availability** before using VLM: `VLMClient().is_available()`
2. **PDF text**: Use `PDFExtractor.extract_text()` first; fall back to `extract_with_vlm()` for scanned docs
3. **Annotations**: Parse JSON from VLM responses; fallback produces `raw_description` annotations
4. **Local-only**: All VLM calls go through local Ollama — no external API keys required
5. **Zero-Mock**: All tests use real file I/O, real JSON parsing, and real Ollama (when available)

## Capabilities

| Capability | Tool | Notes |
|-----------|------|-------|
| Image analysis | `VLMClient.analyze_image()` | Requires Ollama + llava |
| Text extraction | `VLMClient.extract_text()` | OCR-like via VLM prompt |
| PDF parsing | `PDFExtractor.extract_text()` | Requires pymupdf |
| Annotation | `AnnotationExtractor.extract_annotations()` | JSON response parsing |

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/test_vision.py -v --no-cov
```
