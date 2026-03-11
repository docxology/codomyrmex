"""Unit tests for the high-level Synthesizer interface.

Covers:
- Synthesizer initialization
- Provider selection
- Voice listing
- Error handling for invalid voices or providers
"""

import pytest

from codomyrmex.audio.text_to_speech.synthesizer import Synthesizer
from codomyrmex.audio.text_to_speech.providers import PYTTSX3_AVAILABLE, EDGE_TTS_AVAILABLE
from codomyrmex.audio.exceptions import ProviderNotAvailableError, VoiceNotFoundError


@pytest.mark.unit
class TestSynthesizerInterface:
    """Tests for Synthesizer high-level API."""

    def test_synthesizer_instantiation_pyttsx3(self):
        """Test Synthesizer with pyttsx3."""
        try:
            synth = Synthesizer(provider="pyttsx3")
            assert synth is not None
        except ProviderNotAvailableError:
            pytest.skip("pyttsx3 not available")

    def test_synthesizer_instantiation_edge_tts(self):
        """Test Synthesizer with edge-tts."""
        try:
            synth = Synthesizer(provider="edge-tts")
            assert synth is not None
        except ProviderNotAvailableError:
            pytest.skip("edge-tts not available")

    def test_synthesizer_invalid_provider(self):
        """Test that invalid provider raises ValueError."""
        with pytest.raises(ValueError, match="Unknown provider"):
            Synthesizer(provider="invalid_provider")

    @pytest.mark.skipif(not PYTTSX3_AVAILABLE, reason="pyttsx3 not available")
    def test_list_voices_pyttsx3(self):
        """Test listing voices with pyttsx3."""
        synth = Synthesizer(provider="pyttsx3")
        voices = synth.list_voices()
        assert isinstance(voices, list)
        if voices:
            assert hasattr(voices[0], "id")
            assert hasattr(voices[0], "name")

    @pytest.mark.skipif(not PYTTSX3_AVAILABLE, reason="pyttsx3 not available")
    def test_synthesize_invalid_voice_pyttsx3(self):
        """Test synthesis with invalid voice on pyttsx3."""
        synth = Synthesizer(provider="pyttsx3")
        with pytest.raises(VoiceNotFoundError):
            synth.synthesize("Hello", voice="nonexistent_voice_id_12345")
