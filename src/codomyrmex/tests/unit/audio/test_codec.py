"""Unit tests for audio codec/format detection and routing.

Tests cover:
- AudioFormat enum values and completeness
- SUPPORTED_FORMATS input format set from whisper_provider
- AudioFormatError exception with format context
- Format detection from file extensions
- Codec routing via provider get_provider factories
"""

from pathlib import Path

import pytest


@pytest.mark.unit
class TestAudioFormatEnum:
    """Tests for the AudioFormat output format enum."""

    def test_audio_format_wav(self) -> None:
        """Test WAV format enum value."""
        from codomyrmex.audio.text_to_speech.models import AudioFormat

        assert AudioFormat.WAV.value == "wav"

    def test_audio_format_mp3(self) -> None:
        """Test MP3 format enum value."""
        from codomyrmex.audio.text_to_speech.models import AudioFormat

        assert AudioFormat.MP3.value == "mp3"

    def test_audio_format_ogg(self) -> None:
        """Test OGG format enum value."""
        from codomyrmex.audio.text_to_speech.models import AudioFormat

        assert AudioFormat.OGG.value == "ogg"

    def test_audio_format_flac(self) -> None:
        """Test FLAC format enum value."""
        from codomyrmex.audio.text_to_speech.models import AudioFormat

        assert AudioFormat.FLAC.value == "flac"

    def test_audio_format_has_four_members(self) -> None:
        """Test that AudioFormat has exactly four output formats."""
        from codomyrmex.audio.text_to_speech.models import AudioFormat

        members = list(AudioFormat)
        assert len(members) == 4

    def test_audio_format_values_are_lowercase(self) -> None:
        """Test that all AudioFormat values are lowercase strings."""
        from codomyrmex.audio.text_to_speech.models import AudioFormat

        for fmt in AudioFormat:
            assert fmt.value == fmt.value.lower()
            assert isinstance(fmt.value, str)


@pytest.mark.unit
class TestSupportedInputFormats:
    """Tests for SUPPORTED_FORMATS set from the whisper provider module."""

    def test_supported_formats_is_a_set(self) -> None:
        """Test that SUPPORTED_FORMATS is a set type."""
        from codomyrmex.audio.speech_to_text.providers import SUPPORTED_FORMATS

        assert isinstance(SUPPORTED_FORMATS, set)

    def test_wav_in_supported_formats(self) -> None:
        """Test that .wav is a supported input format."""
        from codomyrmex.audio.speech_to_text.providers import SUPPORTED_FORMATS

        assert ".wav" in SUPPORTED_FORMATS

    def test_mp3_in_supported_formats(self) -> None:
        """Test that .mp3 is a supported input format."""
        from codomyrmex.audio.speech_to_text.providers import SUPPORTED_FORMATS

        assert ".mp3" in SUPPORTED_FORMATS

    def test_flac_in_supported_formats(self) -> None:
        """Test that .flac is a supported input format."""
        from codomyrmex.audio.speech_to_text.providers import SUPPORTED_FORMATS

        assert ".flac" in SUPPORTED_FORMATS

    def test_ogg_in_supported_formats(self) -> None:
        """Test that .ogg is a supported input format."""
        from codomyrmex.audio.speech_to_text.providers import SUPPORTED_FORMATS

        assert ".ogg" in SUPPORTED_FORMATS

    def test_m4a_in_supported_formats(self) -> None:
        """Test that .m4a is a supported input format."""
        from codomyrmex.audio.speech_to_text.providers import SUPPORTED_FORMATS

        assert ".m4a" in SUPPORTED_FORMATS

    def test_webm_in_supported_formats(self) -> None:
        """Test that .webm is a supported input format."""
        from codomyrmex.audio.speech_to_text.providers import SUPPORTED_FORMATS

        assert ".webm" in SUPPORTED_FORMATS

    def test_opus_in_supported_formats(self) -> None:
        """Test that .opus is a supported input format."""
        from codomyrmex.audio.speech_to_text.providers import SUPPORTED_FORMATS

        assert ".opus" in SUPPORTED_FORMATS

    def test_all_formats_start_with_dot(self) -> None:
        """Test that all supported format strings start with a dot."""
        from codomyrmex.audio.speech_to_text.providers import SUPPORTED_FORMATS

        for fmt in SUPPORTED_FORMATS:
            assert fmt.startswith("."), f"Format {fmt!r} does not start with '.'"

    def test_minimum_format_count(self) -> None:
        """Test that there are at least 8 supported input formats."""
        from codomyrmex.audio.speech_to_text.providers import SUPPORTED_FORMATS

        assert len(SUPPORTED_FORMATS) >= 8


@pytest.mark.unit
class TestAudioFormatError:
    """Tests for AudioFormatError exception with format context."""

    def test_audio_format_error_basic(self) -> None:
        """Test basic AudioFormatError creation."""
        from codomyrmex.audio.exceptions import AudioFormatError

        error = AudioFormatError("Unsupported format")
        assert "Unsupported format" in str(error)

    def test_audio_format_error_with_format_type(self) -> None:
        """Test AudioFormatError stores format_type in context."""
        from codomyrmex.audio.exceptions import AudioFormatError

        error = AudioFormatError(
            "Unsupported format: .xyz",
            format_type=".xyz",
        )
        assert error.context["format_type"] == ".xyz"

    def test_audio_format_error_with_supported_formats(self) -> None:
        """Test AudioFormatError stores supported_formats list."""
        from codomyrmex.audio.exceptions import AudioFormatError

        supported = [".wav", ".mp3", ".flac"]
        error = AudioFormatError(
            "Unsupported format",
            supported_formats=supported,
        )
        assert error.context["supported_formats"] == supported

    def test_audio_format_error_with_all_context(self) -> None:
        """Test AudioFormatError with both format_type and supported_formats."""
        from codomyrmex.audio.exceptions import AudioFormatError

        error = AudioFormatError(
            "Unsupported audio format: .aac",
            format_type=".aac",
            supported_formats=[".wav", ".mp3"],
        )
        assert error.context["format_type"] == ".aac"
        assert ".wav" in error.context["supported_formats"]
        assert ".mp3" in error.context["supported_formats"]

    def test_audio_format_error_inherits_audio_error(self) -> None:
        """Test that AudioFormatError is a subclass of AudioError."""
        from codomyrmex.audio.exceptions import AudioError, AudioFormatError

        assert issubclass(AudioFormatError, AudioError)

    def test_audio_format_error_without_optional_args(self) -> None:
        """Test AudioFormatError context is clean when no optional args."""
        from codomyrmex.audio.exceptions import AudioFormatError

        error = AudioFormatError("bad format")
        assert "format_type" not in error.context
        assert "supported_formats" not in error.context


@pytest.mark.unit
class TestSTTProviderGetProvider:
    """Tests for STT provider factory routing."""

    def test_get_provider_unknown_raises_value_error(self) -> None:
        """Test that get_provider raises ValueError for unknown provider."""
        from codomyrmex.audio.speech_to_text.providers import get_provider

        with pytest.raises(ValueError, match="Unknown provider"):
            get_provider("nonexistent_provider")

    def test_get_provider_error_includes_available(self) -> None:
        """Test that ValueError message lists available providers."""
        from codomyrmex.audio.speech_to_text.providers import get_provider

        with pytest.raises(ValueError, match="whisper"):
            get_provider("invalid")


@pytest.mark.unit
class TestTTSProviderGetProvider:
    """Tests for TTS provider factory routing."""

    def test_tts_get_provider_unknown_raises_value_error(self) -> None:
        """Test that TTS get_provider raises ValueError for unknown provider."""
        from codomyrmex.audio.text_to_speech.providers import get_provider

        with pytest.raises(ValueError, match="Unknown provider"):
            get_provider("nonexistent_provider")

    def test_tts_get_provider_error_includes_available(self) -> None:
        """Test that ValueError message lists available TTS providers."""
        from codomyrmex.audio.text_to_speech.providers import get_provider

        with pytest.raises(ValueError, match="pyttsx3"):
            get_provider("invalid")

    def test_tts_provider_accepts_edge_tts_variants(self) -> None:
        """Test that TTS provider factory recognizes edge-tts name variants."""
        from codomyrmex.audio.text_to_speech.providers import get_provider

        # These should not raise ValueError (they may raise
        # ProviderNotAvailableError if edge-tts is not installed)
        for name in ("edge-tts", "edge_tts", "edgetts"):
            try:
                get_provider(name)
            except ValueError:
                pytest.fail(f"get_provider rejected valid name: {name!r}")
            except Exception:
                # ProviderNotAvailableError is acceptable -- means name was recognized
                pass
