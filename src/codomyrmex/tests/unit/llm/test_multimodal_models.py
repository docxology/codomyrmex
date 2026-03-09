"""Tests for llm.multimodal.models."""

import base64

from codomyrmex.llm.multimodal.models import (
    AudioContent,
    AudioFormat,
    ImageContent,
    ImageFormat,
    MediaContent,
    MediaType,
    MultimodalMessage,
)


class TestMediaType:
    def test_all_values(self):
        values = {t.value for t in MediaType}
        assert "image" in values
        assert "audio" in values
        assert "video" in values
        assert "text" in values


class TestImageFormat:
    def test_values(self):
        assert ImageFormat.PNG.value == "png"
        assert ImageFormat.JPEG.value == "jpeg"


class TestAudioFormat:
    def test_values(self):
        assert AudioFormat.WAV.value == "wav"
        assert AudioFormat.MP3.value == "mp3"


class TestMediaContent:
    def _make_content(self, data: bytes = b"hello") -> MediaContent:
        return MediaContent(media_type=MediaType.TEXT, data=data)

    def test_size_bytes(self):
        mc = self._make_content(b"hello")
        assert mc.size_bytes == 5

    def test_hash_is_16_chars(self):
        mc = self._make_content(b"data")
        assert len(mc.hash) == 16

    def test_hash_deterministic(self):
        mc1 = self._make_content(b"same")
        mc2 = self._make_content(b"same")
        assert mc1.hash == mc2.hash

    def test_hash_different_data(self):
        mc1 = self._make_content(b"aaa")
        mc2 = self._make_content(b"bbb")
        assert mc1.hash != mc2.hash

    def test_to_base64(self):
        data = b"hello world"
        mc = MediaContent(media_type=MediaType.TEXT, data=data)
        b64 = mc.to_base64()
        assert base64.b64decode(b64) == data

    def test_from_base64(self):
        data = b"test binary data"
        b64 = base64.b64encode(data).decode("utf-8")
        mc = MediaContent.from_base64(b64, MediaType.IMAGE, format="png")
        assert mc.data == data
        assert mc.media_type == MediaType.IMAGE
        assert mc.format == "png"

    def test_from_base64_roundtrip(self):
        original = b"roundtrip test"
        mc1 = MediaContent(media_type=MediaType.TEXT, data=original)
        b64 = mc1.to_base64()
        mc2 = MediaContent.from_base64(b64, MediaType.TEXT)
        assert mc2.data == original

    def test_independent_default_metadata(self):
        mc1 = MediaContent(media_type=MediaType.IMAGE, data=b"x")
        mc2 = MediaContent(media_type=MediaType.IMAGE, data=b"y")
        mc1.metadata["key"] = "val"
        assert mc2.metadata == {}


class TestImageContent:
    def test_construction(self):
        img = ImageContent(
            media_type=MediaType.IMAGE, data=b"img_data", width=800, height=600
        )
        assert img.media_type == MediaType.IMAGE  # set by __post_init__
        assert img.width == 800
        assert img.height == 600

    def test_dimensions(self):
        img = ImageContent(
            media_type=MediaType.IMAGE, data=b"x", width=1920, height=1080
        )
        assert img.dimensions == (1920, 1080)

    def test_aspect_ratio(self):
        img = ImageContent(media_type=MediaType.IMAGE, data=b"x", width=16, height=9)
        assert abs(img.aspect_ratio - 16 / 9) < 0.01

    def test_aspect_ratio_zero_height(self):
        img = ImageContent(media_type=MediaType.IMAGE, data=b"x", width=100, height=0)
        assert img.aspect_ratio == 0

    def test_inherits_media_content(self):
        img = ImageContent(media_type=MediaType.IMAGE, data=b"abc")
        assert img.size_bytes == 3


class TestAudioContent:
    def test_construction(self):
        audio = AudioContent(
            media_type=MediaType.AUDIO, data=b"audio_data", duration_seconds=3.5
        )
        assert audio.media_type == MediaType.AUDIO  # set by __post_init__
        assert audio.duration_seconds == 3.5
        assert audio.sample_rate == 44100
        assert audio.channels == 2

    def test_defaults(self):
        audio = AudioContent(media_type=MediaType.AUDIO, data=b"x")
        assert audio.duration_seconds == 0.0
        assert audio.channels == 2


class TestMultimodalMessage:
    def test_construction(self):
        msg = MultimodalMessage(id="m1", role="user")
        assert msg.id == "m1"
        assert msg.role == "user"
        assert msg.contents == []
        assert msg.text == ""

    def test_add_text_chainable(self):
        msg = MultimodalMessage(id="m1")
        result = msg.add_text("hello world")
        assert result is msg
        assert msg.text == "hello world"

    def test_add_image_from_bytes_chainable(self):
        msg = MultimodalMessage(id="m1")
        result = msg.add_image(b"\x89PNG")
        assert result is msg
        assert len(msg.contents) == 1

    def test_add_image_from_image_content(self):
        msg = MultimodalMessage(id="m1")
        img = ImageContent(
            media_type=MediaType.IMAGE, data=b"img", width=100, height=100
        )
        msg.add_image(img)
        assert len(msg.contents) == 1
        assert msg.contents[0] is img

    def test_add_audio_from_bytes(self):
        msg = MultimodalMessage(id="m1")
        msg.add_audio(b"RIFF...")
        assert len(msg.contents) == 1
        assert msg.contents[0].media_type == MediaType.AUDIO

    def test_add_audio_from_audio_content(self):
        msg = MultimodalMessage(id="m1")
        audio = AudioContent(
            media_type=MediaType.AUDIO, data=b"audio", duration_seconds=1.0
        )
        msg.add_audio(audio)
        assert msg.contents[0] is audio

    def test_has_images_true(self):
        msg = MultimodalMessage(id="m1")
        msg.add_image(b"img")
        assert msg.has_images is True

    def test_has_images_false(self):
        msg = MultimodalMessage(id="m1")
        assert msg.has_images is False

    def test_has_audio_true(self):
        msg = MultimodalMessage(id="m1")
        msg.add_audio(b"audio")
        assert msg.has_audio is True

    def test_has_audio_false(self):
        msg = MultimodalMessage(id="m1")
        assert msg.has_audio is False

    def test_image_count(self):
        msg = MultimodalMessage(id="m1")
        msg.add_image(b"img1")
        msg.add_image(b"img2")
        msg.add_audio(b"audio")
        assert msg.image_count == 2

    def test_to_dict_text_only(self):
        msg = MultimodalMessage(id="m1", role="user")
        msg.add_text("hello")
        d = msg.to_dict()
        assert d["role"] == "user"
        content = d["content"]
        assert content["type"] == "text"
        assert content["text"] == "hello"

    def test_to_dict_with_image(self):
        msg = MultimodalMessage(id="m1")
        msg.add_text("describe this")
        msg.add_image(
            ImageContent(media_type=MediaType.IMAGE, data=b"img", format="png")
        )
        d = msg.to_dict()
        content = d["content"]
        assert isinstance(content, list)
        types = [c["type"] for c in content]
        assert "text" in types
        assert "image" in types

    def test_to_dict_empty_message(self):
        msg = MultimodalMessage(id="m1")
        d = msg.to_dict()
        # Empty message returns empty text
        assert d["content"]["type"] == "text"
        assert d["content"]["text"] == ""

    def test_independent_default_contents(self):
        m1 = MultimodalMessage(id="a")
        m2 = MultimodalMessage(id="b")
        m1.contents.append(ImageContent(media_type=MediaType.IMAGE, data=b"x"))
        assert len(m2.contents) == 0
