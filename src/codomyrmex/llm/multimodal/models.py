"""
Multimodal Models

Data classes and enums for multimodal content.
"""

import base64
import hashlib
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


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
        """post Init ."""
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
        """post Init ."""
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
