# Codomyrmex Agents — src/codomyrmex/llm/multimodal

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Multi-modal content handling for LLM interactions. Provides data models for images and audio, a fluent message builder for composing multimodal prompts, and validation/processing utilities for media content.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `models.py` | `MediaType` | Enum: IMAGE, AUDIO, VIDEO, TEXT |
| `models.py` | `ImageFormat` | Enum: PNG, JPEG, GIF, WEBP |
| `models.py` | `AudioFormat` | Enum: WAV, MP3, OGG, FLAC |
| `models.py` | `MediaContent` | Base dataclass for media; supports `to_base64()`, `from_base64()`, `from_file()` |
| `models.py` | `ImageContent` | Extends `MediaContent` with `width`, `height`, `aspect_ratio` |
| `models.py` | `AudioContent` | Extends `MediaContent` with `duration_seconds`, `sample_rate`, `channels` |
| `models.py` | `MultimodalMessage` | Aggregates text + multiple media contents; `to_dict()` for API payloads |
| `builder.py` | `MultimodalMessageBuilder` | Fluent builder: `.text()`, `.image()`, `.image_file()`, `.audio()`, `.build()` |
| `processors.py` | `MultimodalProcessor` | Abstract base for media processing (`process(content) -> dict`) |
| `processors.py` | `ImageProcessor` | Validates image size/format, returns metadata dict |
| `processors.py` | `AudioProcessor` | Validates audio format/duration, returns metadata dict |
| `__init__.py` | `cli_commands` | CLI integration returning `modalities` and `process` sub-commands |

## Operating Contracts

- `MediaContent.from_file()` auto-detects media type from file extension.
- `MultimodalMessage.add_image()` accepts `bytes`, `str` (base64 or file path), or `ImageContent`.
- `ImageProcessor.validate()` rejects images exceeding `max_size_bytes` (default 10 MB).
- `AudioProcessor.validate()` rejects audio exceeding `max_duration_seconds` (default 300s).
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Standard library (`base64`, `hashlib`, `os`, `pathlib`, `abc`, `dataclasses`, `enum`)
- **Depends on (optional)**: `codomyrmex.validation.schemas` (Result, ResultStatus -- gracefully skipped if absent)
- **Used by**: `codomyrmex.llm` parent module, LLM providers supporting vision/audio inputs

## Navigation

- **Parent**: [llm](../README.md)
- **Root**: [Root](../../../../README.md)
