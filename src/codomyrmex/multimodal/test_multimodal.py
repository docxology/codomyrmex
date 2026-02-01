"""
Tests for Multimodal Module
"""

import pytest
import base64
from codomyrmex.multimodal import (
    MediaType,
    MediaContent,
    ImageContent,
    AudioContent,
    MultimodalMessage,
    ImageProcessor,
    AudioProcessor,
    MultimodalMessageBuilder,
)


class TestMediaContent:
    """Tests for MediaContent."""
    
    def test_create(self):
        """Should create media content."""
        data = b"test data"
        content = MediaContent(
            media_type=MediaType.IMAGE,
            data=data,
            format="png",
        )
        
        assert content.media_type == MediaType.IMAGE
        assert content.size_bytes == len(data)
    
    def test_to_base64(self):
        """Should convert to base64."""
        data = b"hello"
        content = MediaContent(media_type=MediaType.TEXT, data=data)
        
        b64 = content.to_base64()
        decoded = base64.b64decode(b64)
        assert decoded == data
    
    def test_from_base64(self):
        """Should create from base64."""
        original = b"hello world"
        b64 = base64.b64encode(original).decode()
        
        content = MediaContent.from_base64(b64, MediaType.TEXT)
        assert content.data == original
    
    def test_hash(self):
        """Should generate hash."""
        content = MediaContent(media_type=MediaType.TEXT, data=b"test")
        assert len(content.hash) == 16


class TestImageContent:
    """Tests for ImageContent."""
    
    def test_dimensions(self):
        """Should track dimensions."""
        img = ImageContent(data=b"", width=1920, height=1080, media_type=MediaType.IMAGE)
        
        assert img.dimensions == (1920, 1080)
        assert img.aspect_ratio == 1920 / 1080


class TestAudioContent:
    """Tests for AudioContent."""
    
    def test_properties(self):
        """Should track audio properties."""
        audio = AudioContent(
            data=b"",
            duration_seconds=120.0,
            sample_rate=48000,
            media_type=MediaType.AUDIO,
        )
        
        assert audio.duration_seconds == 120.0
        assert audio.sample_rate == 48000


class TestMultimodalMessage:
    """Tests for MultimodalMessage."""
    
    def test_add_text(self):
        """Should add text."""
        msg = MultimodalMessage(id="m1")
        msg.add_text("Hello world")
        
        assert msg.text == "Hello world"
    
    def test_add_image(self):
        """Should add image."""
        msg = MultimodalMessage(id="m1")
        msg.add_image(b"image_bytes")
        
        assert msg.has_images
        assert msg.image_count == 1
    
    def test_add_audio(self):
        """Should add audio."""
        msg = MultimodalMessage(id="m1")
        audio = AudioContent(data=b"audio", media_type=MediaType.AUDIO)
        msg.add_audio(audio)
        
        assert msg.has_audio
    
    def test_to_dict(self):
        """Should convert to dict."""
        msg = MultimodalMessage(id="m1", role="user")
        msg.add_text("What's in this?")
        msg.add_image(ImageContent(data=b"img", format="png", media_type=MediaType.IMAGE))
        
        d = msg.to_dict()
        assert d["role"] == "user"
        assert len(d["content"]) == 2


class TestImageProcessor:
    """Tests for ImageProcessor."""
    
    def test_validate_valid(self):
        """Should validate valid image."""
        processor = ImageProcessor()
        content = MediaContent(media_type=MediaType.IMAGE, data=b"x" * 100, format="png")
        
        valid, msg = processor.validate(content)
        assert valid is True
    
    def test_validate_size_limit(self):
        """Should reject large images."""
        processor = ImageProcessor(max_size_bytes=100)
        content = MediaContent(media_type=MediaType.IMAGE, data=b"x" * 200)
        
        valid, msg = processor.validate(content)
        assert valid is False
        assert "too large" in msg.lower()
    
    def test_process(self):
        """Should return metadata."""
        processor = ImageProcessor()
        content = MediaContent(media_type=MediaType.IMAGE, data=b"img", format="png")
        
        result = processor.process(content)
        assert result["valid"] is True
        assert result["format"] == "png"


class TestAudioProcessor:
    """Tests for AudioProcessor."""
    
    def test_validate_valid(self):
        """Should validate valid audio."""
        processor = AudioProcessor()
        content = AudioContent(data=b"audio", format="wav", media_type=MediaType.AUDIO)
        
        valid, msg = processor.validate(content)
        assert valid is True
    
    def test_validate_duration(self):
        """Should reject long audio."""
        processor = AudioProcessor(max_duration_seconds=60)
        content = AudioContent(
            data=b"audio",
            duration_seconds=120,
            media_type=MediaType.AUDIO,
        )
        
        valid, msg = processor.validate(content)
        assert valid is False


class TestMultimodalMessageBuilder:
    """Tests for MultimodalMessageBuilder."""
    
    def test_fluent_api(self):
        """Should support fluent building."""
        message = (MultimodalMessageBuilder("msg_1")
            .text("What is this?")
            .image(b"img_data", format="png")
            .build())
        
        assert message.text == "What is this?"
        assert message.has_images
    
    def test_image_base64(self):
        """Should add base64 image."""
        b64 = base64.b64encode(b"test").decode()
        
        message = (MultimodalMessageBuilder("msg_1")
            .image_base64(b64)
            .build())
        
        assert message.image_count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
