"""
Multimodal Message Builder

Fluent builder for constructing multimodal messages.
"""

import base64

from .models import (
    AudioContent,
    ImageContent,
    MediaContent,
    MediaType,
    MultimodalMessage,
)


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
        """Execute   Init   operations natively."""
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
