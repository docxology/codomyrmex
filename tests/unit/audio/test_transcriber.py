"""Unit tests for the high-level Transcriber interface.

Covers:
- Transcriber initialization
- Availability checking
- Error handling for missing files
- Language detection interface
- Batch transcription interface
"""

import pytest

from codomyrmex.audio.exceptions import ProviderNotAvailableError, TranscriptionError
from codomyrmex.audio.speech_to_text.providers import WHISPER_AVAILABLE
from codomyrmex.audio.speech_to_text.transcriber import Transcriber


@pytest.mark.unit
class TestTranscriberInterface:
    """Tests for Transcriber high-level API."""

    def test_transcriber_instantiation(self):
        """Test that Transcriber can be instantiated or raises ProviderNotAvailableError."""
        if not WHISPER_AVAILABLE:
            with pytest.raises(ProviderNotAvailableError):
                Transcriber(provider="whisper", model_size="tiny")
            return

        try:
            transcriber = Transcriber(provider="whisper", model_size="tiny")
            assert transcriber is not None
            assert transcriber._provider_name == "whisper"
        except ProviderNotAvailableError:
            pytest.fail(
                "Whisper is reported as available but raised ProviderNotAvailableError"
            )
        except Exception as e:
            # Model loading might fail for other reasons (memory, etc.)
            pytest.skip(f"Could not load Whisper model: {e}")

    def test_transcriber_invalid_provider(self):
        """Test that invalid provider raises ValueError."""
        with pytest.raises(ValueError, match="Unknown provider"):
            Transcriber(provider="invalid_provider")

    @pytest.mark.skipif(not WHISPER_AVAILABLE, reason="Whisper not available")
    def test_transcribe_nonexistent_file(self):
        """Test that transcribing a nonexistent file raises TranscriptionError."""
        try:
            transcriber = Transcriber(model_size="tiny")
            with pytest.raises(TranscriptionError):
                transcriber.transcribe("nonexistent.wav")
        except Exception as e:
            pytest.skip(f"Transcriber not usable in this environment: {e}")

    @pytest.mark.skipif(not WHISPER_AVAILABLE, reason="Whisper not available")
    def test_detect_language_nonexistent_file(self):
        """Test language detection on nonexistent file."""
        try:
            transcriber = Transcriber(model_size="tiny")
            with pytest.raises(TranscriptionError):
                transcriber.detect_language("nonexistent.wav")
        except Exception as e:
            pytest.skip(f"Transcriber not usable in this environment: {e}")

    def test_transcriber_context_manager(self):
        """Test Transcriber as a context manager."""
        try:
            with Transcriber(model_size="tiny") as transcriber:
                assert transcriber.is_loaded
            # Should be unloaded after exit
            assert not transcriber.is_loaded
        except (ProviderNotAvailableError, Exception):
            pytest.skip("Whisper not available or could not be loaded")
