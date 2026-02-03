"""Unit tests for the audio module.

Tests cover:
- Module imports and availability flags
- Exception classes
- Data models (TranscriptionResult, SynthesisResult, etc.)
- Transcriber and Synthesizer initialization
- Model serialization (to_srt, to_vtt, to_json)
"""

import pytest
from pathlib import Path

# Test imports
def test_audio_module_imports() -> None:
    """Test that audio module can be imported."""
    from codomyrmex import audio
    assert hasattr(audio, "__version__")


def test_audio_exceptions_import() -> None:
    """Test that all exception classes can be imported."""
    from codomyrmex.audio.exceptions import (
        AudioError,
        TranscriptionError,
        SynthesisError,
        AudioFormatError,
        ModelNotLoadedError,
        ProviderNotAvailableError,
        VoiceNotFoundError,
    )

    # Verify exception hierarchy
    assert issubclass(TranscriptionError, AudioError)
    assert issubclass(SynthesisError, AudioError)
    assert issubclass(AudioFormatError, AudioError)
    assert issubclass(ModelNotLoadedError, AudioError)
    assert issubclass(ProviderNotAvailableError, AudioError)
    assert issubclass(VoiceNotFoundError, AudioError)


def test_audio_exception_context() -> None:
    """Test that exceptions properly store context."""
    from codomyrmex.audio.exceptions import TranscriptionError

    error = TranscriptionError(
        "Test error",
        audio_path="/path/to/audio.mp3",
        language="en",
        model_size="base",
    )

    assert error.context.get("audio_path") == "/path/to/audio.mp3"
    assert error.context.get("language") == "en"
    assert error.context.get("model_size") == "base"
    assert "Test error" in str(error)


def test_synthesis_error_text_truncation() -> None:
    """Test that SynthesisError truncates long text in context."""
    from codomyrmex.audio.exceptions import SynthesisError

    long_text = "A" * 200
    error = SynthesisError("Test", text=long_text)

    # Should be truncated to 100 chars + "..."
    assert len(error.context.get("text", "")) == 103


def test_availability_flags() -> None:
    """Test that availability flags are defined."""
    from codomyrmex.audio import (
        STT_AVAILABLE,
        TTS_AVAILABLE,
    )

    # These should be boolean values
    assert isinstance(STT_AVAILABLE, bool)
    assert isinstance(TTS_AVAILABLE, bool)


# Speech-to-text model tests
class TestTranscriptionModels:
    """Tests for speech-to-text data models."""

    def test_whisper_model_size_enum(self) -> None:
        """Test WhisperModelSize enum values."""
        from codomyrmex.audio.speech_to_text.models import WhisperModelSize

        assert WhisperModelSize.TINY.value == "tiny"
        assert WhisperModelSize.BASE.value == "base"
        assert WhisperModelSize.SMALL.value == "small"
        assert WhisperModelSize.MEDIUM.value == "medium"
        assert WhisperModelSize.LARGE.value == "large"
        assert WhisperModelSize.LARGE_V2.value == "large-v2"
        assert WhisperModelSize.LARGE_V3.value == "large-v3"

    def test_word_dataclass(self) -> None:
        """Test Word dataclass."""
        from codomyrmex.audio.speech_to_text.models import Word

        word = Word(word="hello", start=0.0, end=0.5, probability=0.95)

        assert word.word == "hello"
        assert word.start == 0.0
        assert word.end == 0.5
        assert word.probability == 0.95
        assert word.duration == 0.5

    def test_segment_dataclass(self) -> None:
        """Test Segment dataclass."""
        from codomyrmex.audio.speech_to_text.models import Segment, Word

        words = [
            Word(word="hello", start=0.0, end=0.5, probability=0.95),
            Word(word="world", start=0.6, end=1.0, probability=0.90),
        ]

        segment = Segment(
            id=0,
            start=0.0,
            end=1.0,
            text="hello world",
            words=words,
        )

        assert segment.id == 0
        assert segment.duration == 1.0
        assert len(segment.words) == 2

    def test_segment_to_srt_format(self) -> None:
        """Test Segment SRT formatting."""
        from codomyrmex.audio.speech_to_text.models import Segment

        segment = Segment(
            id=0,
            start=1.5,
            end=4.2,
            text="Hello, this is a test.",
        )

        srt = segment.to_srt_format(1)

        assert "1\n" in srt
        assert "00:00:01,500 --> 00:00:04,200" in srt
        assert "Hello, this is a test." in srt

    def test_segment_to_vtt_format(self) -> None:
        """Test Segment VTT formatting."""
        from codomyrmex.audio.speech_to_text.models import Segment

        segment = Segment(
            id=0,
            start=1.5,
            end=4.2,
            text="Hello, this is a test.",
        )

        vtt = segment.to_vtt_format()

        assert "00:00:01.500 --> 00:00:04.200" in vtt
        assert "Hello, this is a test." in vtt

    def test_transcription_result_dataclass(self) -> None:
        """Test TranscriptionResult dataclass."""
        from codomyrmex.audio.speech_to_text.models import (
            TranscriptionResult,
            Segment,
            WhisperModelSize,
        )

        segments = [
            Segment(id=0, start=0.0, end=2.0, text="Hello world."),
            Segment(id=1, start=2.5, end=5.0, text="How are you?"),
        ]

        result = TranscriptionResult(
            text="Hello world. How are you?",
            segments=segments,
            language="en",
            duration=5.0,
            processing_time=1.2,
            model_size=WhisperModelSize.BASE,
        )

        assert result.word_count == 5
        assert result.segment_count == 2
        assert result.language == "en"

    def test_transcription_result_to_srt(self) -> None:
        """Test TranscriptionResult SRT export."""
        from codomyrmex.audio.speech_to_text.models import (
            TranscriptionResult,
            Segment,
        )

        segments = [
            Segment(id=0, start=0.0, end=2.0, text="Hello world."),
            Segment(id=1, start=2.5, end=5.0, text="Goodbye world."),
        ]

        result = TranscriptionResult(
            text="Hello world. Goodbye world.",
            segments=segments,
        )

        srt = result.to_srt()

        assert "1\n" in srt
        assert "2\n" in srt
        assert "Hello world." in srt
        assert "Goodbye world." in srt

    def test_transcription_result_to_vtt(self) -> None:
        """Test TranscriptionResult VTT export."""
        from codomyrmex.audio.speech_to_text.models import (
            TranscriptionResult,
            Segment,
        )

        segments = [
            Segment(id=0, start=0.0, end=2.0, text="Hello world."),
        ]

        result = TranscriptionResult(
            text="Hello world.",
            segments=segments,
        )

        vtt = result.to_vtt()

        assert vtt.startswith("WEBVTT")
        assert "Hello world." in vtt

    def test_transcription_result_to_json(self) -> None:
        """Test TranscriptionResult JSON export."""
        from codomyrmex.audio.speech_to_text.models import (
            TranscriptionResult,
            Segment,
            WhisperModelSize,
        )

        segments = [
            Segment(id=0, start=0.0, end=2.0, text="Hello."),
        ]

        result = TranscriptionResult(
            text="Hello.",
            segments=segments,
            language="en",
            model_size=WhisperModelSize.BASE,
        )

        data = result.to_json()

        assert data["text"] == "Hello."
        assert data["language"] == "en"
        assert data["model_size"] == "base"
        assert len(data["segments"]) == 1

    def test_transcription_config(self) -> None:
        """Test TranscriptionConfig defaults."""
        from codomyrmex.audio.speech_to_text.models import TranscriptionConfig

        config = TranscriptionConfig()

        assert config.language is None  # Auto-detect
        assert config.task == "transcribe"
        assert config.beam_size == 5
        assert config.word_timestamps is True
        assert config.vad_filter is True


# Text-to-speech model tests
class TestSynthesisModels:
    """Tests for text-to-speech data models."""

    def test_audio_format_enum(self) -> None:
        """Test AudioFormat enum values."""
        from codomyrmex.audio.text_to_speech.models import AudioFormat

        assert AudioFormat.WAV.value == "wav"
        assert AudioFormat.MP3.value == "mp3"
        assert AudioFormat.OGG.value == "ogg"
        assert AudioFormat.FLAC.value == "flac"

    def test_voice_gender_enum(self) -> None:
        """Test VoiceGender enum values."""
        from codomyrmex.audio.text_to_speech.models import VoiceGender

        assert VoiceGender.MALE.value == "male"
        assert VoiceGender.FEMALE.value == "female"
        assert VoiceGender.NEUTRAL.value == "neutral"

    def test_voice_info_dataclass(self) -> None:
        """Test VoiceInfo dataclass."""
        from codomyrmex.audio.text_to_speech.models import VoiceInfo, VoiceGender

        voice = VoiceInfo(
            id="en-US-AriaNeural",
            name="Aria",
            language="en-US",
            gender=VoiceGender.FEMALE,
            is_neural=True,
            provider="edge-tts",
        )

        assert voice.id == "en-US-AriaNeural"
        assert voice.is_neural is True

        data = voice.to_dict()
        assert data["gender"] == "female"

    def test_synthesis_result_dataclass(self) -> None:
        """Test SynthesisResult dataclass."""
        from codomyrmex.audio.text_to_speech.models import (
            SynthesisResult,
            AudioFormat,
        )

        result = SynthesisResult(
            audio_data=b"test audio data",
            format=AudioFormat.WAV,
            duration=1.5,
            sample_rate=22050,
            voice_id="test-voice",
            text="Hello world",
            provider="test",
            processing_time=0.5,
        )

        assert result.size_bytes == 15
        assert result.size_kb == 15 / 1024

        data = result.to_dict()
        assert data["format"] == "wav"
        assert data["voice_id"] == "test-voice"

    def test_synthesis_result_save(self, tmp_path: Path) -> None:
        """Test SynthesisResult save method."""
        from codomyrmex.audio.text_to_speech.models import SynthesisResult

        result = SynthesisResult(
            audio_data=b"fake audio data",
        )

        output_path = tmp_path / "output.wav"
        saved_path = result.save(output_path)

        assert saved_path.exists()
        assert saved_path.read_bytes() == b"fake audio data"

    def test_tts_config(self) -> None:
        """Test TTSConfig defaults."""
        from codomyrmex.audio.text_to_speech.models import TTSConfig, AudioFormat

        config = TTSConfig()

        assert config.voice is None
        assert config.language == "en-US"
        assert config.rate == 1.0
        assert config.pitch == 1.0
        assert config.volume == 1.0
        assert config.format == AudioFormat.WAV


# Provider tests
class TestProviders:
    """Tests for STT and TTS providers."""

    def test_stt_provider_interface(self) -> None:
        """Test STTProvider abstract interface."""
        from codomyrmex.audio.speech_to_text.providers.base import STTProvider
        import abc

        # Verify it's an abstract class
        assert hasattr(STTProvider, "__abstractmethods__")

        # Check required methods
        assert "transcribe" in STTProvider.__abstractmethods__
        assert "transcribe_async" in STTProvider.__abstractmethods__
        assert "detect_language" in STTProvider.__abstractmethods__

    def test_tts_provider_interface(self) -> None:
        """Test TTSProvider abstract interface."""
        from codomyrmex.audio.text_to_speech.providers.base import TTSProvider

        # Verify it's an abstract class
        assert hasattr(TTSProvider, "__abstractmethods__")

        # Check required methods
        assert "synthesize" in TTSProvider.__abstractmethods__
        assert "synthesize_async" in TTSProvider.__abstractmethods__
        assert "list_voices" in TTSProvider.__abstractmethods__

    def test_whisper_provider_availability(self) -> None:
        """Test WhisperProvider availability flag."""
        from codomyrmex.audio.speech_to_text.providers import WHISPER_AVAILABLE

        assert isinstance(WHISPER_AVAILABLE, bool)

    def test_pyttsx3_provider_availability(self) -> None:
        """Test Pyttsx3Provider availability flag."""
        from codomyrmex.audio.text_to_speech.providers import PYTTSX3_AVAILABLE

        assert isinstance(PYTTSX3_AVAILABLE, bool)

    def test_edge_tts_provider_availability(self) -> None:
        """Test EdgeTTSProvider availability flag."""
        from codomyrmex.audio.text_to_speech.providers import EDGE_TTS_AVAILABLE

        assert isinstance(EDGE_TTS_AVAILABLE, bool)


# Integration-style unit tests (mock-based)
class TestTranscriber:
    """Tests for Transcriber class."""

    def test_transcriber_import(self) -> None:
        """Test Transcriber can be imported."""
        from codomyrmex.audio.speech_to_text.transcriber import Transcriber
        assert Transcriber is not None

    def test_get_supported_languages(self) -> None:
        """Test that Whisper supported languages are defined."""
        from codomyrmex.audio.speech_to_text.providers.whisper_provider import (
            WHISPER_LANGUAGES,
        )

        assert isinstance(WHISPER_LANGUAGES, list)
        assert "en" in WHISPER_LANGUAGES
        assert "es" in WHISPER_LANGUAGES
        assert "fr" in WHISPER_LANGUAGES
        assert len(WHISPER_LANGUAGES) > 50  # 99+ languages


class TestSynthesizer:
    """Tests for Synthesizer class."""

    def test_synthesizer_import(self) -> None:
        """Test Synthesizer can be imported."""
        from codomyrmex.audio.text_to_speech.synthesizer import Synthesizer
        assert Synthesizer is not None

    def test_popular_voices_defined(self) -> None:
        """Test that popular Edge TTS voices are defined."""
        try:
            from codomyrmex.audio.text_to_speech.providers.edge_tts_provider import (
                POPULAR_VOICES,
            )

            assert isinstance(POPULAR_VOICES, dict)
            assert "en-US" in POPULAR_VOICES
            assert "en-US-AriaNeural" in POPULAR_VOICES["en-US"]
        except ImportError:
            pytest.skip("edge-tts not installed")
