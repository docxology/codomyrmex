# Multimodal Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Vision, audio, and image processing for multimodal AI applications. Provides a unified content model for handling multiple media types (image, audio, video, text) with base64 encoding/decoding, file I/O, and format validation. Includes specialized processors for image and audio content, a fluent message builder for constructing multimodal LLM messages, and media-specific content containers with metadata like dimensions, duration, and sample rate.


## Installation

```bash
pip install codomyrmex
```

## Key Features

- **Unified Media Model**: `MediaContent` base class handles all media types with automatic format detection from file extensions
- **Image Processing**: Validate image format and size, process image metadata, and handle resize requirements
- **Audio Processing**: Validate audio format and duration limits with sample rate and channel tracking
- **Base64 Encoding/Decoding**: Seamless conversion between raw bytes and base64 strings for API transport
- **File I/O**: Load media content directly from files with automatic type inference (PNG, JPEG, GIF, WEBP, WAV, MP3, OGG, FLAC, MP4, and more)
- **Multimodal Messages**: Compose messages containing text, images, and audio in a single `MultimodalMessage` structure
- **Fluent Builder API**: `MultimodalMessageBuilder` provides a chainable interface for constructing multimodal messages
- **API-Ready Serialization**: Convert multimodal messages to dictionary format compatible with LLM API calls


## Key Components

| Component | Description |
|-----------|-------------|
| `MediaContent` | Base container for media content with type detection, base64 conversion, hashing, and file loading |
| `ImageContent` | Image-specific content container with width, height, dimensions, and aspect ratio properties |
| `AudioContent` | Audio-specific content container with duration, sample rate, and channel properties |
| `MultimodalMessage` | A message containing multiple media types (text, images, audio) with API serialization |
| `ImageProcessor` | Image validation and processing with configurable size limits and supported format lists |
| `AudioProcessor` | Audio validation and processing with configurable duration limits and supported format lists |
| `MultimodalProcessor` | Abstract base class for implementing custom media processors |
| `MultimodalMessageBuilder` | Fluent builder for constructing multimodal messages from text, image bytes/files/base64, and audio |
| `MediaType` | Enum of media types: IMAGE, AUDIO, VIDEO, TEXT |
| `ImageFormat` | Enum of supported image formats: PNG, JPEG, GIF, WEBP |
| `AudioFormat` | Enum of supported audio formats: WAV, MP3, OGG, FLAC |

## Quick Start

```python
from codomyrmex.multimodal import (
    MultimodalMessageBuilder, ImageProcessor, MediaContent
)

# Build a multimodal message with the fluent API
message = (
    MultimodalMessageBuilder("msg_1")
    .text("What's in this image?")
    .image_file("/path/to/photo.png")
    .build()
)

# Convert to API-ready format
api_payload = message.to_dict()
print(message.has_images)    # True
print(message.image_count)   # 1
```

```python
from codomyrmex.multimodal import MediaContent, ImageProcessor

# Load media from file
content = MediaContent.from_file("/path/to/image.jpeg")
print(content.media_type)    # MediaType.IMAGE
print(content.size_bytes)    # file size in bytes

# Validate with processor
processor = ImageProcessor(max_size_bytes=5 * 1024 * 1024)
valid, message = processor.validate(content)
print(f"Valid: {valid}, {message}")
```

```python
from codomyrmex.multimodal import AudioContent, AudioProcessor, MediaType

# Create audio content
audio = AudioContent(
    data=b"audio_bytes_here",
    format="wav",
    duration_seconds=30.0,
    sample_rate=44100,
    channels=2,
    media_type=MediaType.AUDIO,
)

# Validate audio
processor = AudioProcessor(max_duration_seconds=300.0)
result = processor.process(audio)
print(result)  # {"valid": True, "duration_seconds": 30.0, ...}
```

## Related Modules

- [model_ops](../model_ops/) - Model operations that may process multimodal inputs
- [prompt_testing](../prompt_testing/) - Test prompts that include multimodal content

## Navigation

- **Source**: [src/codomyrmex/multimodal/](../../../src/codomyrmex/multimodal/)
- **Parent**: [docs/modules/](../README.md)
