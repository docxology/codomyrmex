"""
Multimodal Module

Vision and audio processing for multimodal AI applications.
"""

__version__ = "0.1.0"

import base64
import hashlib
import os
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


class MediaType(Enum):
    """Types of media."""
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"


class ImageFormat(Enum):
    """Supported image formats."""
    PNG = "png"
    JPEG = "jpeg"
    GIF = "gif"
    WEBP = "webp"


class AudioFormat(Enum):
    """Supported audio formats."""
    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    FLAC = "flac"


@dataclass
class MediaContent:
    """Container for media content."""
    media_type: MediaType
    data: bytes
    format: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def size_bytes(self) -> int:
        """Get content size in bytes."""
        return len(self.data)

    @property
    def hash(self) -> str:
        """Get content hash."""
        return hashlib.sha256(self.data).hexdigest()[:16]

    def to_base64(self) -> str:
        """Convert to base64 string."""
        return base64.b64encode(self.data).decode('utf-8')

    @classmethod
    def from_base64(
        cls,
        b64_string: str,
        media_type: MediaType,
        format: str = "",
    ) -> "MediaContent":
        """Create from base64 string."""
        data = base64.b64decode(b64_string)
        return cls(media_type=media_type, data=data, format=format)

    @classmethod
    def from_file(cls, file_path: str) -> "MediaContent":
        """Create from file."""
        path = Path(file_path)
        data = path.read_bytes()

        # Determine type from extension
        ext = path.suffix.lower().lstrip('.')

        if ext in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
            media_type = MediaType.IMAGE
        elif ext in ['wav', 'mp3', 'ogg', 'flac']:
            media_type = MediaType.AUDIO
        elif ext in ['mp4', 'webm', 'avi']:
            media_type = MediaType.VIDEO
        else:
            media_type = MediaType.TEXT

        return cls(
            media_type=media_type,
            data=data,
            format=ext,
            metadata={"source": file_path},
        )


@dataclass
class ImageContent(MediaContent):
    """Image-specific content."""
    width: int = 0
    height: int = 0

    def __post_init__(self):
        self.media_type = MediaType.IMAGE

    @property
    def dimensions(self) -> tuple[int, int]:
        """Get image dimensions."""
        return (self.width, self.height)

    @property
    def aspect_ratio(self) -> float:
        """Get aspect ratio."""
        if self.height == 0:
            return 0
        return self.width / self.height


@dataclass
class AudioContent(MediaContent):
    """Audio-specific content."""
    duration_seconds: float = 0.0
    sample_rate: int = 44100
    channels: int = 2

    def __post_init__(self):
        self.media_type = MediaType.AUDIO


@dataclass
class MultimodalMessage:
    """A message containing multiple media types."""
    id: str
    contents: list[MediaContent] = field(default_factory=list)
    text: str = ""
    role: str = "user"
    created_at: datetime = field(default_factory=datetime.now)

    def add_text(self, text: str) -> "MultimodalMessage":
        """Add text content."""
        self.text = text
        return self

    def add_image(self, image: bytes | str | ImageContent) -> "MultimodalMessage":
        """Add image content."""
        if isinstance(image, ImageContent):
            self.contents.append(image)
        elif isinstance(image, bytes):
            self.contents.append(ImageContent(data=image, media_type=MediaType.IMAGE))
        elif isinstance(image, str):
            # Assume base64 or file path
            if os.path.exists(image):
                self.contents.append(MediaContent.from_file(image))
            else:
                self.contents.append(MediaContent.from_base64(image, MediaType.IMAGE))
        return self

    def add_audio(self, audio: bytes | str | AudioContent) -> "MultimodalMessage":
        """Add audio content."""
        if isinstance(audio, AudioContent):
            self.contents.append(audio)
        elif isinstance(audio, bytes):
            self.contents.append(AudioContent(data=audio, media_type=MediaType.AUDIO))
        elif isinstance(audio, str) and os.path.exists(audio):
            self.contents.append(MediaContent.from_file(audio))
        return self

    @property
    def has_images(self) -> bool:
        """Check if message contains images."""
        return any(c.media_type == MediaType.IMAGE for c in self.contents)

    @property
    def has_audio(self) -> bool:
        """Check if message contains audio."""
        return any(c.media_type == MediaType.AUDIO for c in self.contents)

    @property
    def image_count(self) -> int:
        """Get number of images."""
        return sum(1 for c in self.contents if c.media_type == MediaType.IMAGE)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API calls."""
        parts = []

        if self.text:
            parts.append({"type": "text", "text": self.text})

        for content in self.contents:
            if content.media_type == MediaType.IMAGE:
                parts.append({
                    "type": "image",
                    "data": content.to_base64(),
                    "format": content.format,
                })
            elif content.media_type == MediaType.AUDIO:
                parts.append({
                    "type": "audio",
                    "data": content.to_base64(),
                    "format": content.format,
                })

        return {
            "role": self.role,
            "content": parts if len(parts) > 1 else parts[0] if parts else {"type": "text", "text": ""},
        }


class MultimodalProcessor(ABC):
    """Base class for multimodal processing."""

    @abstractmethod
    def process(self, content: MediaContent) -> dict[str, Any]:
        """Process media content."""
        pass


class ImageProcessor(MultimodalProcessor):
    """
    Image processing utilities.

    Usage:
        processor = ImageProcessor()

        # Resize image
        resized = processor.resize(image_content, max_width=1024)

        # Get description
        result = processor.process(image_content)
    """

    def __init__(
        self,
        max_size_bytes: int = 10 * 1024 * 1024,  # 10MB
        supported_formats: list[str] | None = None,
    ):
        self.max_size_bytes = max_size_bytes
        self.supported_formats = supported_formats or ['png', 'jpeg', 'gif', 'webp']

    def validate(self, content: MediaContent) -> tuple[bool, str]:
        """Validate image content."""
        if content.media_type != MediaType.IMAGE:
            return False, "Not an image"

        if content.size_bytes > self.max_size_bytes:
            return False, f"Image too large: {content.size_bytes} > {self.max_size_bytes}"

        if content.format and content.format not in self.supported_formats:
            return False, f"Unsupported format: {content.format}"

        return True, "Valid"

    def process(self, content: MediaContent) -> dict[str, Any]:
        """Process image and return metadata."""
        valid, message = self.validate(content)

        return {
            "valid": valid,
            "message": message,
            "size_bytes": content.size_bytes,
            "format": content.format,
            "hash": content.hash,
        }

    def resize_if_needed(
        self,
        content: MediaContent,
        max_bytes: int = 5 * 1024 * 1024,
    ) -> MediaContent:
        """
        Resize image if it exceeds size limit.
        Note: This is a placeholder - actual resizing requires PIL/pillow.
        """
        if content.size_bytes <= max_bytes:
            return content

        # In production, use PIL to actually resize
        # For now, just return as-is with a warning
        content.metadata["resize_needed"] = True
        content.metadata["original_size"] = content.size_bytes
        return content


class AudioProcessor(MultimodalProcessor):
    """
    Audio processing utilities.

    Usage:
        processor = AudioProcessor()
        result = processor.process(audio_content)
    """

    def __init__(
        self,
        max_duration_seconds: float = 300.0,  # 5 minutes
        supported_formats: list[str] | None = None,
    ):
        self.max_duration_seconds = max_duration_seconds
        self.supported_formats = supported_formats or ['wav', 'mp3', 'ogg', 'flac']

    def validate(self, content: MediaContent) -> tuple[bool, str]:
        """Validate audio content."""
        if content.media_type != MediaType.AUDIO:
            return False, "Not audio"

        if content.format and content.format not in self.supported_formats:
            return False, f"Unsupported format: {content.format}"

        if isinstance(content, AudioContent):
            if content.duration_seconds > self.max_duration_seconds:
                return False, f"Audio too long: {content.duration_seconds}s"

        return True, "Valid"

    def process(self, content: MediaContent) -> dict[str, Any]:
        """Process audio and return metadata."""
        valid, message = self.validate(content)

        result = {
            "valid": valid,
            "message": message,
            "size_bytes": content.size_bytes,
            "format": content.format,
        }

        if isinstance(content, AudioContent):
            result["duration_seconds"] = content.duration_seconds
            result["sample_rate"] = content.sample_rate

        return result


class MultimodalMessageBuilder:
    """
    Fluent builder for multimodal messages.

    Usage:
        message = (MultimodalMessageBuilder("msg_1")
            .text("What's in this image?")
            .image_file("/path/to/image.png")
            .build())
    """

    def __init__(self, message_id: str, role: str = "user"):
        self._message = MultimodalMessage(id=message_id, role=role)

    def text(self, content: str) -> "MultimodalMessageBuilder":
        """Add text content."""
        self._message.text = content
        return self

    def image(self, data: bytes, format: str = "png") -> "MultimodalMessageBuilder":
        """Add image from bytes."""
        self._message.add_image(ImageContent(data=data, format=format, media_type=MediaType.IMAGE))
        return self

    def image_base64(self, b64: str, format: str = "png") -> "MultimodalMessageBuilder":
        """Add image from base64."""
        data = base64.b64decode(b64)
        self._message.add_image(ImageContent(data=data, format=format, media_type=MediaType.IMAGE))
        return self

    def image_file(self, path: str) -> "MultimodalMessageBuilder":
        """Add image from file path."""
        content = MediaContent.from_file(path)
        self._message.contents.append(content)
        return self

    def audio(self, data: bytes, format: str = "wav") -> "MultimodalMessageBuilder":
        """Add audio from bytes."""
        self._message.add_audio(AudioContent(data=data, format=format, media_type=MediaType.AUDIO))
        return self

    def audio_file(self, path: str) -> "MultimodalMessageBuilder":
        """Add audio from file path."""
        content = MediaContent.from_file(path)
        self._message.contents.append(content)
        return self

    def build(self) -> MultimodalMessage:
        """Build the message."""
        return self._message


__all__ = [
    # Enums
    "MediaType",
    "ImageFormat",
    "AudioFormat",
    # Data classes
    "MediaContent",
    "ImageContent",
    "AudioContent",
    "MultimodalMessage",
    # Processors
    "MultimodalProcessor",
    "ImageProcessor",
    "AudioProcessor",
    # Builder
    "MultimodalMessageBuilder",
]
