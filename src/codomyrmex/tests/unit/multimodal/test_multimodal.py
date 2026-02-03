"""Unit tests for multimodal module."""
import pytest
import base64


@pytest.mark.unit
class TestMultimodalImports:
    """Test suite for multimodal module imports."""

    def test_module_imports(self):
        """Verify module can be imported without errors."""
        from codomyrmex import multimodal
        assert multimodal is not None

    def test_public_api_exists(self):
        """Verify expected public API is available."""
        from codomyrmex.multimodal import __all__
        expected_exports = [
            "MediaType",
            "ImageFormat",
            "AudioFormat",
            "MediaContent",
            "ImageContent",
            "AudioContent",
            "MultimodalMessage",
            "MultimodalProcessor",
            "ImageProcessor",
            "AudioProcessor",
            "MultimodalMessageBuilder",
        ]
        for export in expected_exports:
            assert export in __all__, f"Missing export: {export}"


@pytest.mark.unit
class TestMediaType:
    """Test suite for MediaType enum."""

    def test_media_type_values(self):
        """Verify all media types are available."""
        from codomyrmex.multimodal import MediaType

        assert MediaType.IMAGE.value == "image"
        assert MediaType.AUDIO.value == "audio"
        assert MediaType.VIDEO.value == "video"
        assert MediaType.TEXT.value == "text"


@pytest.mark.unit
class TestImageFormat:
    """Test suite for ImageFormat enum."""

    def test_image_format_values(self):
        """Verify all image formats are available."""
        from codomyrmex.multimodal import ImageFormat

        assert ImageFormat.PNG.value == "png"
        assert ImageFormat.JPEG.value == "jpeg"
        assert ImageFormat.GIF.value == "gif"
        assert ImageFormat.WEBP.value == "webp"


@pytest.mark.unit
class TestAudioFormat:
    """Test suite for AudioFormat enum."""

    def test_audio_format_values(self):
        """Verify all audio formats are available."""
        from codomyrmex.multimodal import AudioFormat

        assert AudioFormat.WAV.value == "wav"
        assert AudioFormat.MP3.value == "mp3"
        assert AudioFormat.OGG.value == "ogg"
        assert AudioFormat.FLAC.value == "flac"


@pytest.mark.unit
class TestMediaContent:
    """Test suite for MediaContent dataclass."""

    def test_content_creation(self):
        """Verify MediaContent can be created."""
        from codomyrmex.multimodal import MediaContent, MediaType

        content = MediaContent(
            media_type=MediaType.IMAGE,
            data=b"fake image data",
            format="png",
        )

        assert content.media_type == MediaType.IMAGE
        assert content.format == "png"

    def test_content_size_bytes(self):
        """Verify size calculation."""
        from codomyrmex.multimodal import MediaContent, MediaType

        data = b"x" * 1000
        content = MediaContent(media_type=MediaType.IMAGE, data=data)

        assert content.size_bytes == 1000

    def test_content_hash(self):
        """Verify hash generation."""
        from codomyrmex.multimodal import MediaContent, MediaType

        content = MediaContent(media_type=MediaType.IMAGE, data=b"test data")

        assert len(content.hash) == 16  # Truncated hash

    def test_content_to_base64(self):
        """Verify base64 encoding."""
        from codomyrmex.multimodal import MediaContent, MediaType

        data = b"hello world"
        content = MediaContent(media_type=MediaType.TEXT, data=data)

        b64 = content.to_base64()
        decoded = base64.b64decode(b64)

        assert decoded == data

    def test_content_from_base64(self):
        """Verify base64 decoding."""
        from codomyrmex.multimodal import MediaContent, MediaType

        original = b"test content"
        b64 = base64.b64encode(original).decode('utf-8')

        content = MediaContent.from_base64(b64, MediaType.IMAGE, format="png")

        assert content.data == original
        assert content.media_type == MediaType.IMAGE


@pytest.mark.unit
class TestImageContent:
    """Test suite for ImageContent dataclass."""

    def test_image_content_creation(self):
        """Verify ImageContent can be created."""
        from codomyrmex.multimodal import ImageContent, MediaType

        image = ImageContent(
            data=b"fake png data",
            format="png",
            width=800,
            height=600,
            media_type=MediaType.IMAGE,
        )

        assert image.width == 800
        assert image.height == 600
        assert image.media_type == MediaType.IMAGE

    def test_image_content_dimensions(self):
        """Verify dimensions property."""
        from codomyrmex.multimodal import ImageContent, MediaType

        image = ImageContent(
            data=b"data",
            width=1920,
            height=1080,
            media_type=MediaType.IMAGE,
        )

        assert image.dimensions == (1920, 1080)

    def test_image_content_aspect_ratio(self):
        """Verify aspect ratio calculation."""
        from codomyrmex.multimodal import ImageContent, MediaType

        image = ImageContent(
            data=b"data",
            width=1600,
            height=900,
            media_type=MediaType.IMAGE,
        )

        assert abs(image.aspect_ratio - 16/9) < 0.01


@pytest.mark.unit
class TestAudioContent:
    """Test suite for AudioContent dataclass."""

    def test_audio_content_creation(self):
        """Verify AudioContent can be created."""
        from codomyrmex.multimodal import AudioContent, MediaType

        audio = AudioContent(
            data=b"fake audio data",
            format="wav",
            duration_seconds=30.5,
            sample_rate=48000,
            channels=2,
            media_type=MediaType.AUDIO,
        )

        assert audio.duration_seconds == 30.5
        assert audio.sample_rate == 48000
        assert audio.channels == 2


@pytest.mark.unit
class TestMultimodalMessage:
    """Test suite for MultimodalMessage dataclass."""

    def test_message_creation(self):
        """Verify MultimodalMessage can be created."""
        from codomyrmex.multimodal import MultimodalMessage

        message = MultimodalMessage(
            id="msg_1",
            text="What is in this image?",
            role="user",
        )

        assert message.id == "msg_1"
        assert message.text == "What is in this image?"

    def test_message_add_text(self):
        """Verify text addition."""
        from codomyrmex.multimodal import MultimodalMessage

        message = MultimodalMessage(id="msg_1")
        message.add_text("Hello!")

        assert message.text == "Hello!"

    def test_message_add_image_bytes(self):
        """Verify image addition from bytes."""
        from codomyrmex.multimodal import MultimodalMessage

        message = MultimodalMessage(id="msg_1")
        message.add_image(b"fake image data")

        assert message.has_images is True
        assert message.image_count == 1

    def test_message_has_images(self):
        """Verify has_images property."""
        from codomyrmex.multimodal import MultimodalMessage

        message = MultimodalMessage(id="msg_1")
        assert message.has_images is False

        message.add_image(b"data")
        assert message.has_images is True

    def test_message_to_dict(self):
        """Verify message serialization."""
        from codomyrmex.multimodal import MultimodalMessage

        message = MultimodalMessage(id="msg_1", text="Test", role="assistant")
        result = message.to_dict()

        assert result["role"] == "assistant"

    def test_message_chaining(self):
        """Verify method chaining."""
        from codomyrmex.multimodal import MultimodalMessage

        message = (
            MultimodalMessage(id="msg_1")
            .add_text("Describe this")
            .add_image(b"image data")
        )

        assert message.text == "Describe this"
        assert message.has_images is True


@pytest.mark.unit
class TestImageProcessor:
    """Test suite for ImageProcessor."""

    def test_processor_creation(self):
        """Verify ImageProcessor can be created."""
        from codomyrmex.multimodal import ImageProcessor

        processor = ImageProcessor(
            max_size_bytes=5 * 1024 * 1024,
            supported_formats=["png", "jpeg"],
        )

        assert processor.max_size_bytes == 5 * 1024 * 1024

    def test_processor_validate_valid(self):
        """Verify validation of valid image."""
        from codomyrmex.multimodal import ImageProcessor, MediaContent, MediaType

        processor = ImageProcessor()
        content = MediaContent(
            media_type=MediaType.IMAGE,
            data=b"small image",
            format="png",
        )

        valid, message = processor.validate(content)
        assert valid is True

    def test_processor_validate_wrong_type(self):
        """Verify validation rejects non-image."""
        from codomyrmex.multimodal import ImageProcessor, MediaContent, MediaType

        processor = ImageProcessor()
        content = MediaContent(
            media_type=MediaType.AUDIO,
            data=b"audio data",
        )

        valid, message = processor.validate(content)
        assert valid is False
        assert "Not an image" in message

    def test_processor_validate_too_large(self):
        """Verify validation rejects oversized image."""
        from codomyrmex.multimodal import ImageProcessor, MediaContent, MediaType

        processor = ImageProcessor(max_size_bytes=100)
        content = MediaContent(
            media_type=MediaType.IMAGE,
            data=b"x" * 200,
        )

        valid, message = processor.validate(content)
        assert valid is False
        assert "too large" in message

    def test_processor_process(self):
        """Verify processing returns metadata."""
        from codomyrmex.multimodal import ImageProcessor, MediaContent, MediaType

        processor = ImageProcessor()
        content = MediaContent(
            media_type=MediaType.IMAGE,
            data=b"image data",
            format="png",
        )

        result = processor.process(content)

        assert "valid" in result
        assert "size_bytes" in result
        assert "hash" in result


@pytest.mark.unit
class TestAudioProcessor:
    """Test suite for AudioProcessor."""

    def test_processor_creation(self):
        """Verify AudioProcessor can be created."""
        from codomyrmex.multimodal import AudioProcessor

        processor = AudioProcessor(
            max_duration_seconds=60.0,
            supported_formats=["wav", "mp3"],
        )

        assert processor.max_duration_seconds == 60.0

    def test_processor_validate_valid(self):
        """Verify validation of valid audio."""
        from codomyrmex.multimodal import AudioProcessor, AudioContent, MediaType

        processor = AudioProcessor()
        content = AudioContent(
            media_type=MediaType.AUDIO,
            data=b"audio data",
            format="wav",
            duration_seconds=30.0,
        )

        valid, message = processor.validate(content)
        assert valid is True

    def test_processor_validate_too_long(self):
        """Verify validation rejects long audio."""
        from codomyrmex.multimodal import AudioProcessor, AudioContent, MediaType

        processor = AudioProcessor(max_duration_seconds=60.0)
        content = AudioContent(
            media_type=MediaType.AUDIO,
            data=b"audio",
            duration_seconds=120.0,
        )

        valid, message = processor.validate(content)
        assert valid is False
        assert "too long" in message


@pytest.mark.unit
class TestMultimodalMessageBuilder:
    """Test suite for MultimodalMessageBuilder."""

    def test_builder_basic(self):
        """Verify basic builder usage."""
        from codomyrmex.multimodal import MultimodalMessageBuilder

        message = (
            MultimodalMessageBuilder("msg_1")
            .text("What is this?")
            .build()
        )

        assert message.id == "msg_1"
        assert message.text == "What is this?"

    def test_builder_with_image(self):
        """Verify builder with image."""
        from codomyrmex.multimodal import MultimodalMessageBuilder

        message = (
            MultimodalMessageBuilder("msg_1")
            .text("Describe the image")
            .image(b"fake image data", format="png")
            .build()
        )

        assert message.has_images is True
        assert message.image_count == 1

    def test_builder_with_audio(self):
        """Verify builder with audio."""
        from codomyrmex.multimodal import MultimodalMessageBuilder

        message = (
            MultimodalMessageBuilder("msg_1")
            .text("Transcribe this audio")
            .audio(b"fake audio data", format="wav")
            .build()
        )

        assert message.has_audio is True

    def test_builder_with_base64_image(self):
        """Verify builder with base64 image."""
        from codomyrmex.multimodal import MultimodalMessageBuilder
        import base64

        b64_data = base64.b64encode(b"image bytes").decode('utf-8')

        message = (
            MultimodalMessageBuilder("msg_1")
            .image_base64(b64_data, format="jpeg")
            .build()
        )

        assert message.has_images is True
