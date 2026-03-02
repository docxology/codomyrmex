"""Unit tests for audio streaming and synthesis configuration.

Tests cover:
- SSMLOptions dataclass defaults and fields
- TTSConfig rate/pitch/volume parameters and defaults
- SynthesisResult serialization and file I/O
- VoiceInfo dataclass and to_dict serialization
- VoiceGender enum values and completeness

Note: No dedicated streaming buffer module exists in the audio package.
These tests cover the TTS model layer that underpins streaming synthesis.
"""

from pathlib import Path

import pytest


@pytest.mark.unit
class TestSSMLOptions:
    """Tests for SSMLOptions dataclass defaults and fields."""

    def test_ssml_options_default_use_ssml(self) -> None:
        """Test SSMLOptions default use_ssml is False."""
        from codomyrmex.audio.text_to_speech.models import SSMLOptions

        opts = SSMLOptions()
        assert opts.use_ssml is False

    def test_ssml_options_default_auto_breaks(self) -> None:
        """Test SSMLOptions default auto_breaks is True."""
        from codomyrmex.audio.text_to_speech.models import SSMLOptions

        opts = SSMLOptions()
        assert opts.auto_breaks is True

    def test_ssml_options_default_emphasis(self) -> None:
        """Test SSMLOptions default emphasis is moderate."""
        from codomyrmex.audio.text_to_speech.models import SSMLOptions

        opts = SSMLOptions()
        assert opts.emphasis == "moderate"

    def test_ssml_options_default_prosody(self) -> None:
        """Test SSMLOptions default prosody is empty dict."""
        from codomyrmex.audio.text_to_speech.models import SSMLOptions

        opts = SSMLOptions()
        assert opts.prosody == {}
        assert isinstance(opts.prosody, dict)

    def test_ssml_options_custom_values(self) -> None:
        """Test SSMLOptions with custom values."""
        from codomyrmex.audio.text_to_speech.models import SSMLOptions

        opts = SSMLOptions(
            use_ssml=True,
            auto_breaks=False,
            emphasis="strong",
            prosody={"rate": "slow", "pitch": "high"},
        )
        assert opts.use_ssml is True
        assert opts.auto_breaks is False
        assert opts.emphasis == "strong"
        assert opts.prosody["rate"] == "slow"

    def test_ssml_options_prosody_does_not_share_state(self) -> None:
        """Test that SSMLOptions prosody dict is not shared between instances."""
        from codomyrmex.audio.text_to_speech.models import SSMLOptions

        opts1 = SSMLOptions()
        opts2 = SSMLOptions()
        opts1.prosody["rate"] = "fast"
        assert "rate" not in opts2.prosody


@pytest.mark.unit
class TestTTSConfigParameters:
    """Tests for TTSConfig rate, pitch, volume, and format defaults."""

    def test_tts_config_default_voice_is_none(self) -> None:
        """Test TTSConfig default voice is None."""
        from codomyrmex.audio.text_to_speech.models import TTSConfig

        config = TTSConfig()
        assert config.voice is None

    def test_tts_config_default_language(self) -> None:
        """Test TTSConfig default language is en-US."""
        from codomyrmex.audio.text_to_speech.models import TTSConfig

        config = TTSConfig()
        assert config.language == "en-US"

    def test_tts_config_default_rate(self) -> None:
        """Test TTSConfig default rate is 1.0."""
        from codomyrmex.audio.text_to_speech.models import TTSConfig

        config = TTSConfig()
        assert config.rate == 1.0

    def test_tts_config_default_pitch(self) -> None:
        """Test TTSConfig default pitch is 1.0."""
        from codomyrmex.audio.text_to_speech.models import TTSConfig

        config = TTSConfig()
        assert config.pitch == 1.0

    def test_tts_config_default_volume(self) -> None:
        """Test TTSConfig default volume is 1.0."""
        from codomyrmex.audio.text_to_speech.models import TTSConfig

        config = TTSConfig()
        assert config.volume == 1.0

    def test_tts_config_default_format_is_wav(self) -> None:
        """Test TTSConfig default format is WAV."""
        from codomyrmex.audio.text_to_speech.models import AudioFormat, TTSConfig

        config = TTSConfig()
        assert config.format == AudioFormat.WAV

    def test_tts_config_default_sample_rate(self) -> None:
        """Test TTSConfig default sample_rate is 22050."""
        from codomyrmex.audio.text_to_speech.models import TTSConfig

        config = TTSConfig()
        assert config.sample_rate == 22050

    def test_tts_config_style_default_is_none(self) -> None:
        """Test TTSConfig default style is None."""
        from codomyrmex.audio.text_to_speech.models import TTSConfig

        config = TTSConfig()
        assert config.style is None

    def test_tts_config_emotion_default_is_none(self) -> None:
        """Test TTSConfig default emotion is None."""
        from codomyrmex.audio.text_to_speech.models import TTSConfig

        config = TTSConfig()
        assert config.emotion is None

    def test_tts_config_custom_values(self) -> None:
        """Test TTSConfig with custom values."""
        from codomyrmex.audio.text_to_speech.models import AudioFormat, TTSConfig

        config = TTSConfig(
            voice="en-US-AriaNeural",
            language="en-US",
            rate=1.5,
            pitch=0.8,
            volume=0.7,
            format=AudioFormat.MP3,
            sample_rate=48000,
            style="cheerful",
            emotion="happy",
        )
        assert config.voice == "en-US-AriaNeural"
        assert config.rate == 1.5
        assert config.pitch == 0.8
        assert config.volume == 0.7
        assert config.format == AudioFormat.MP3
        assert config.sample_rate == 48000
        assert config.style == "cheerful"
        assert config.emotion == "happy"


@pytest.mark.unit
class TestSynthesisResultSerialization:
    """Tests for SynthesisResult to_dict and save methods."""

    def test_synthesis_result_to_dict_excludes_audio_data(self) -> None:
        """Test that to_dict does not include raw audio bytes."""
        from codomyrmex.audio.text_to_speech.models import SynthesisResult

        result = SynthesisResult(audio_data=b"\x00" * 100)
        data = result.to_dict()
        assert "audio_data" not in data

    def test_synthesis_result_to_dict_format_is_string(self) -> None:
        """Test that to_dict serializes format enum to string value."""
        from codomyrmex.audio.text_to_speech.models import AudioFormat, SynthesisResult

        result = SynthesisResult(audio_data=b"test", format=AudioFormat.MP3)
        data = result.to_dict()
        assert data["format"] == "mp3"
        assert isinstance(data["format"], str)

    def test_synthesis_result_to_dict_contains_size_bytes(self) -> None:
        """Test that to_dict includes computed size_bytes."""
        from codomyrmex.audio.text_to_speech.models import SynthesisResult

        result = SynthesisResult(audio_data=b"x" * 256)
        data = result.to_dict()
        assert data["size_bytes"] == 256

    def test_synthesis_result_to_dict_all_fields(self) -> None:
        """Test that to_dict includes all expected fields."""
        from codomyrmex.audio.text_to_speech.models import SynthesisResult

        result = SynthesisResult(
            audio_data=b"test",
            duration=2.0,
            sample_rate=44100,
            voice_id="voice-1",
            text="hello",
            provider="test-provider",
            processing_time=0.3,
        )
        data = result.to_dict()
        expected_keys = {
            "format", "duration", "sample_rate", "voice_id",
            "text", "provider", "processing_time", "size_bytes",
        }
        assert expected_keys == set(data.keys())

    def test_synthesis_result_save_creates_file(self, tmp_path: Path) -> None:
        """Test that save writes audio bytes to disk."""
        from codomyrmex.audio.text_to_speech.models import SynthesisResult

        content = b"RIFF\x00\x00\x00\x00WAVEfmt "
        result = SynthesisResult(audio_data=content)
        output = tmp_path / "test_output.wav"
        saved = result.save(output)
        assert saved.exists()
        assert saved.read_bytes() == content

    def test_synthesis_result_save_returns_path_object(self, tmp_path: Path) -> None:
        """Test that save returns a Path object."""
        from codomyrmex.audio.text_to_speech.models import SynthesisResult

        result = SynthesisResult(audio_data=b"data")
        output = tmp_path / "out.wav"
        saved = result.save(output)
        assert isinstance(saved, Path)

    def test_synthesis_result_save_accepts_string_path(self, tmp_path: Path) -> None:
        """Test that save accepts a string path argument."""
        from codomyrmex.audio.text_to_speech.models import SynthesisResult

        result = SynthesisResult(audio_data=b"data")
        output = str(tmp_path / "string_path.wav")
        saved = result.save(output)
        assert Path(saved).exists()

    def test_synthesis_result_size_bytes_property(self) -> None:
        """Test size_bytes computed property."""
        from codomyrmex.audio.text_to_speech.models import SynthesisResult

        result = SynthesisResult(audio_data=b"\x00" * 1024)
        assert result.size_bytes == 1024

    def test_synthesis_result_size_kb_property(self) -> None:
        """Test size_kb computed property."""
        from codomyrmex.audio.text_to_speech.models import SynthesisResult

        result = SynthesisResult(audio_data=b"\x00" * 2048)
        assert result.size_kb == 2.0


@pytest.mark.unit
class TestVoiceInfoSerialization:
    """Tests for VoiceInfo dataclass and to_dict output."""

    def test_voice_info_to_dict_has_all_fields(self) -> None:
        """Test VoiceInfo to_dict includes all expected fields."""
        from codomyrmex.audio.text_to_speech.models import VoiceInfo

        voice = VoiceInfo(id="v1", name="Test Voice", language="en-US")
        data = voice.to_dict()
        expected_keys = {
            "id", "name", "language", "gender", "is_neural",
            "provider", "description", "sample_rate", "styles",
        }
        assert expected_keys == set(data.keys())

    def test_voice_info_gender_serialized_as_string(self) -> None:
        """Test VoiceInfo to_dict serializes gender enum to string."""
        from codomyrmex.audio.text_to_speech.models import VoiceGender, VoiceInfo

        voice = VoiceInfo(
            id="v1", name="Voice", language="en",
            gender=VoiceGender.FEMALE,
        )
        data = voice.to_dict()
        assert data["gender"] == "female"

    def test_voice_info_default_gender_is_unknown(self) -> None:
        """Test VoiceInfo default gender is UNKNOWN."""
        from codomyrmex.audio.text_to_speech.models import VoiceGender, VoiceInfo

        voice = VoiceInfo(id="v1", name="Voice", language="en")
        assert voice.gender == VoiceGender.UNKNOWN

    def test_voice_info_default_styles_is_empty_list(self) -> None:
        """Test VoiceInfo default styles is an empty list."""
        from codomyrmex.audio.text_to_speech.models import VoiceInfo

        voice = VoiceInfo(id="v1", name="Voice", language="en")
        assert voice.styles == []
        assert isinstance(voice.styles, list)

    def test_voice_info_styles_not_shared_between_instances(self) -> None:
        """Test VoiceInfo styles list is not shared between instances."""
        from codomyrmex.audio.text_to_speech.models import VoiceInfo

        v1 = VoiceInfo(id="v1", name="V1", language="en")
        v2 = VoiceInfo(id="v2", name="V2", language="en")
        v1.styles.append("cheerful")
        assert "cheerful" not in v2.styles

    def test_voice_info_default_sample_rate(self) -> None:
        """Test VoiceInfo default sample_rate is 22050."""
        from codomyrmex.audio.text_to_speech.models import VoiceInfo

        voice = VoiceInfo(id="v1", name="Voice", language="en")
        assert voice.sample_rate == 22050


@pytest.mark.unit
class TestVoiceGenderEnum:
    """Tests for VoiceGender enum values and completeness."""

    def test_voice_gender_male(self) -> None:
        """Test VoiceGender MALE value."""
        from codomyrmex.audio.text_to_speech.models import VoiceGender

        assert VoiceGender.MALE.value == "male"

    def test_voice_gender_female(self) -> None:
        """Test VoiceGender FEMALE value."""
        from codomyrmex.audio.text_to_speech.models import VoiceGender

        assert VoiceGender.FEMALE.value == "female"

    def test_voice_gender_neutral(self) -> None:
        """Test VoiceGender NEUTRAL value."""
        from codomyrmex.audio.text_to_speech.models import VoiceGender

        assert VoiceGender.NEUTRAL.value == "neutral"

    def test_voice_gender_unknown(self) -> None:
        """Test VoiceGender UNKNOWN value."""
        from codomyrmex.audio.text_to_speech.models import VoiceGender

        assert VoiceGender.UNKNOWN.value == "unknown"

    def test_voice_gender_has_four_members(self) -> None:
        """Test that VoiceGender has exactly four members."""
        from codomyrmex.audio.text_to_speech.models import VoiceGender

        assert len(list(VoiceGender)) == 4
