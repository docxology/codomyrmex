"""
Multimodal Processors

Image and audio processing utilities.
"""

import dataclasses
import io
import math
from abc import ABC, abstractmethod
from typing import Any

from .models import AudioContent, ImageContent, MediaContent, MediaType


class MultimodalProcessor(ABC):
    """Base class for multimodal processing."""

    @abstractmethod
    def process(self, content: MediaContent) -> dict[str, Any]:
        """Process media content."""


class ImageProcessor(MultimodalProcessor):
    """
    Image processing utilities.

    Usage:
        processor = ImageProcessor()

        # Downscale image to fit a byte budget
        resized = processor.resize_if_needed(image_content, max_bytes=1_000_000)

        # Get description
        result = processor.process(image_content)
    """

    def __init__(
        self,
        max_size_bytes: int = 10 * 1024 * 1024,  # 10MB
        supported_formats: list[str] | None = None,
    ):
        self.max_size_bytes = max_size_bytes
        self.supported_formats = supported_formats or ["png", "jpeg", "gif", "webp"]

    def validate(self, content: MediaContent) -> tuple[bool, str]:
        """Validate image content."""
        if content.media_type != MediaType.IMAGE:
            return False, "Not an image"

        if content.size_bytes > self.max_size_bytes:
            return (
                False,
                f"Image too large: {content.size_bytes} > {self.max_size_bytes}",
            )

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
        """Downscale an image until its encoded size is at most ``max_bytes``.

        Content already within the limit is returned unchanged. Otherwise the
        image is decoded with Pillow, scaled down (aspect ratio kept) and
        re-encoded in its original format, shrinking further until it fits.
        A new object of the same class is returned; its metadata adds
        ``original_size``, ``original_dimensions`` and ``dimensions``, and an
        :class:`ImageContent` also gets the new ``width``/``height``.

        Raises:
            ValueError: If ``max_bytes`` is not positive, the content is not an
                image, or even a 1x1 re-encoding exceeds ``max_bytes``.
            ImportError: If Pillow is not installed.
        """
        if max_bytes <= 0:
            raise ValueError(f"max_bytes must be positive, got {max_bytes}")
        if content.size_bytes <= max_bytes:
            return content
        if content.media_type != MediaType.IMAGE:
            raise ValueError(
                f"Only images can be resized, got {content.media_type.value}"
            )
        try:
            from PIL import Image
        except ImportError as exc:
            raise ImportError(
                "Pillow is required to resize images (pip package 'pillow')."
            ) from exc

        with Image.open(io.BytesIO(content.data)) as image:
            image.load()
            image_format = image.format
            original_dimensions = image.size
            width, height = image.size
            # Encoded size scales roughly with pixel count, i.e. with scale**2.
            scale = math.sqrt(max_bytes / content.size_bytes)
            while True:
                scale *= 0.9
                new_size = (max(1, int(width * scale)), max(1, int(height * scale)))
                buffer = io.BytesIO()
                image.resize(new_size, Image.Resampling.LANCZOS).save(
                    buffer, format=image_format
                )
                data = buffer.getvalue()
                if len(data) <= max_bytes:
                    break
                if new_size == (1, 1):
                    raise ValueError(
                        f"Cannot reduce {image_format} image below {max_bytes} "
                        f"bytes (1x1 encodes to {len(data)} bytes)"
                    )

        metadata = {
            **content.metadata,
            "original_size": content.size_bytes,
            "original_dimensions": original_dimensions,
            "dimensions": new_size,
        }
        if isinstance(content, ImageContent):
            return dataclasses.replace(
                content,
                data=data,
                metadata=metadata,
                width=new_size[0],
                height=new_size[1],
            )
        return dataclasses.replace(content, data=data, metadata=metadata)


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
        self.supported_formats = supported_formats or ["wav", "mp3", "ogg", "flac"]

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

        result: dict[str, Any] = {
            "valid": valid,
            "message": message,
            "size_bytes": content.size_bytes,
            "format": content.format,
        }

        if isinstance(content, AudioContent):
            result["duration_seconds"] = content.duration_seconds
            result["sample_rate"] = content.sample_rate

        return result
