# Multimodal -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Data models, builders, and processors for multimodal LLM inputs. Enables constructing messages that combine text with images and audio for vision-capable and audio-capable LLM providers.

## Architecture

Three-layer design: **Models** define the data structures (`MediaContent`, `ImageContent`, `AudioContent`, `MultimodalMessage`); **Builder** (`MultimodalMessageBuilder`) provides a fluent API for constructing messages; **Processors** (`ImageProcessor`, `AudioProcessor`) validate and extract metadata from media content.

## Key Classes

### `MediaContent`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `to_base64` | -- | `str` | Base64-encode raw bytes |
| `from_base64` | `b64_string, media_type, format` | `MediaContent` | Class method to create from base64 string |
| `from_file` | `file_path: str` | `MediaContent` | Class method; auto-detects type from extension |

Properties: `size_bytes`, `hash` (SHA-256 truncated to 16 chars)

### `MultimodalMessage`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_text` | `text: str` | `self` | Sets text content |
| `add_image` | `image: bytes \| str \| ImageContent` | `self` | Adds image (auto-detects input type) |
| `add_audio` | `audio: bytes \| str \| AudioContent` | `self` | Adds audio content |
| `to_dict` | -- | `dict` | Serializes to API-compatible format with `role` and `content` array |

Properties: `has_images`, `has_audio`, `image_count`

### `MultimodalMessageBuilder`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `text` | `content: str` | `self` | Set text content |
| `image` | `data: bytes, format: str` | `self` | Add image from bytes |
| `image_base64` | `b64: str, format: str` | `self` | Add image from base64 |
| `image_file` | `path: str` | `self` | Add image from file path |
| `audio` | `data: bytes, format: str` | `self` | Add audio from bytes |
| `audio_file` | `path: str` | `self` | Add audio from file path |
| `build` | -- | `MultimodalMessage` | Finalize and return message |

### `ImageProcessor`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `validate` | `content: MediaContent` | `tuple[bool, str]` | Checks type, size, format |
| `process` | `content: MediaContent` | `dict[str, Any]` | Returns metadata: valid, size_bytes, format, hash |
| `resize_if_needed` | `content, max_bytes` | `MediaContent` | Marks content for resize (placeholder -- PIL required for actual resize) |

### `AudioProcessor`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `validate` | `content: MediaContent` | `tuple[bool, str]` | Checks type, format, duration |
| `process` | `content: MediaContent` | `dict[str, Any]` | Returns metadata including duration_seconds, sample_rate |

## Dependencies

- **Internal**: `codomyrmex.validation.schemas` (optional, gracefully skipped)
- **External**: Standard library only (`base64`, `hashlib`, `os`, `pathlib`, `abc`, `dataclasses`, `datetime`, `enum`)

## Constraints

- `ImageProcessor.resize_if_needed` is a placeholder -- actual resizing requires PIL/Pillow.
- `to_dict()` returns a single content object if only one part, or an array for multiple parts.
- Zero-mock: real data only; `NotImplementedError` for unimplemented paths.

## Error Handling

- Processors return `(False, reason)` from `validate()` rather than raising exceptions.
- `from_file()` raises standard `FileNotFoundError` / `IOError` on missing paths.
- All errors logged before propagation.
