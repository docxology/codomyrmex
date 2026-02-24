"""
Multimodal Processors

Image and audio processing utilities.
"""

from abc import ABC, abstractmethod
from typing import Any

from .models import AudioContent, MediaContent, MediaType


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
        """Execute   Init   operations natively."""
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
        """Execute   Init   operations natively."""
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
