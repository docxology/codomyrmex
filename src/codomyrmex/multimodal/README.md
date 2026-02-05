# multimodal

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Vision and audio processing for multimodal AI applications. Provides typed media containers for images, audio, and video with base64 encoding/decoding, file loading with automatic format detection, and content hashing. Includes image and audio processors for validation and metadata extraction, a `MultimodalMessage` class for composing multi-part messages with mixed media types, and a fluent `MultimodalMessageBuilder` for constructing API-ready payloads.

## Key Exports

### Enums

- **`MediaType`** -- Types of media: IMAGE, AUDIO, VIDEO, TEXT
- **`ImageFormat`** -- Supported image formats: PNG, JPEG, GIF, WEBP
- **`AudioFormat`** -- Supported audio formats: WAV, MP3, OGG, FLAC

### Data Classes

- **`MediaContent`** -- Base container for media content with type, raw bytes, format, and metadata; provides `size_bytes`, `hash` (SHA-256), `to_base64()`, and class methods `from_base64()` and `from_file()` with auto-detection of media type from file extension
- **`ImageContent`** -- Image-specific content extending MediaContent with width, height, `dimensions` tuple, and `aspect_ratio` computation
- **`AudioContent`** -- Audio-specific content extending MediaContent with duration, sample rate, and channel count
- **`MultimodalMessage`** -- A message containing multiple media types and text; supports fluent `add_text()`, `add_image()`, `add_audio()` methods accepting bytes, base64 strings, file paths, or typed content objects; includes `has_images`, `has_audio`, and `image_count` properties; serializes to API-compatible dict via `to_dict()`

### Processors

- **`MultimodalProcessor`** -- Abstract base class for media processing with a `process()` method
- **`ImageProcessor`** -- Image validation and metadata extraction; checks size limits and format support; includes `resize_if_needed()` placeholder for PIL-based resizing
- **`AudioProcessor`** -- Audio validation and metadata extraction; checks format support and duration limits

### Builder

- **`MultimodalMessageBuilder`** -- Fluent builder for constructing `MultimodalMessage` instances; supports chained `.text()`, `.image()`, `.image_base64()`, `.image_file()`, `.audio()`, `.audio_file()`, and `.build()` methods

## Directory Contents

- `__init__.py` -- Module implementation with media containers, processors, message builder, and data models
- `README.md` -- This file
- `AGENTS.md` -- Agent integration documentation
- `API_SPECIFICATION.md` -- Programmatic API specification
- `MCP_TOOL_SPECIFICATION.md` -- Model Context Protocol tool definitions
- `PAI.md` -- PAI integration notes
- `SPEC.md` -- Module specification
- `py.typed` -- PEP 561 type stub marker

## Navigation

- **Full Documentation**: [docs/modules/multimodal/](../../../docs/modules/multimodal/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
