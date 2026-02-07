# Multimodal — Functional Specification

**Module**: `codomyrmex.multimodal`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Vision and audio processing for multimodal AI applications.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `MediaType` | Class | Types of media. |
| `ImageFormat` | Class | Supported image formats. |
| `AudioFormat` | Class | Supported audio formats. |
| `MediaContent` | Class | Container for media content. |
| `ImageContent` | Class | Image-specific content. |
| `AudioContent` | Class | Audio-specific content. |
| `MultimodalMessage` | Class | A message containing multiple media types. |
| `MultimodalProcessor` | Class | Base class for multimodal processing. |
| `ImageProcessor` | Class | Image processing utilities. |
| `AudioProcessor` | Class | Audio processing utilities. |
| `size_bytes()` | Function | Get content size in bytes. |
| `hash()` | Function | Get content hash. |
| `to_base64()` | Function | Convert to base64 string. |
| `from_base64()` | Function | Create from base64 string. |
| `from_file()` | Function | Create from file. |

## 3. Dependencies

See `src/codomyrmex/multimodal/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.multimodal import MediaType, ImageFormat, AudioFormat, MediaContent, ImageContent
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k multimodal -v
```
