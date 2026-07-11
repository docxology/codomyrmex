"""
TDD regression tests for P3 CodeQL missing-super-init remediation.

Verifies that audio provider subclasses properly call ``super().__init__()``
so the MRO chain is intact. Since optional dependencies (edge-tts, pyttsx3,
faster-whisper) may not be installed, tests verify the import/class structure
rather than requiring instantiation of providers that depend on external libs.

Zero-Mock compliant.
"""

import inspect

import pytest

from codomyrmex.audio.speech_to_text.providers.base import STTProvider

# ── Base classes ───────────────────────────────────────────────────────
from codomyrmex.audio.text_to_speech.providers.base import TTSProvider


@pytest.mark.unit
class TestTTSProviderSuperInit:
    """Verify TTS provider subclasses call super().__init__()."""

    def test_edge_tts_provider_has_super_init_call(self):
        """EdgeTTSProvider.__init__ must contain super().__init__() call."""
        from codomyrmex.audio.text_to_speech.providers.edge_tts_provider import (
            EdgeTTSProvider,
        )

        source = inspect.getsource(EdgeTTSProvider.__init__)
        assert "super().__init__()" in source, (
            "EdgeTTSProvider.__init__ must call super().__init__()"
        )

    def test_pyttsx3_provider_has_super_init_call(self):
        """Pyttsx3Provider.__init__ must contain super().__init__() call."""
        from codomyrmex.audio.text_to_speech.providers.pyttsx3_provider import (
            Pyttsx3Provider,
        )

        source = inspect.getsource(Pyttsx3Provider.__init__)
        assert "super().__init__()" in source, (
            "Pyttsx3Provider.__init__ must call super().__init__()"
        )

    def test_edge_tts_provider_is_subclass_of_tts_provider(self):
        """EdgeTTSProvider must be a subclass of TTSProvider."""
        from codomyrmex.audio.text_to_speech.providers.edge_tts_provider import (
            EdgeTTSProvider,
        )

        assert issubclass(EdgeTTSProvider, TTSProvider)

    def test_pyttsx3_provider_is_subclass_of_tts_provider(self):
        """Pyttsx3Provider must be a subclass of TTSProvider."""
        from codomyrmex.audio.text_to_speech.providers.pyttsx3_provider import (
            Pyttsx3Provider,
        )

        assert issubclass(Pyttsx3Provider, TTSProvider)


@pytest.mark.unit
class TestSTTProviderSuperInit:
    """Verify STT provider subclasses call super().__init__()."""

    def test_whisper_provider_has_super_init_call(self):
        """WhisperProvider.__init__ must contain super().__init__() call."""
        from codomyrmex.audio.speech_to_text.providers.whisper_provider import (
            WhisperProvider,
        )

        source = inspect.getsource(WhisperProvider.__init__)
        assert "super().__init__()" in source, (
            "WhisperProvider.__init__ must call super().__init__()"
        )

    def test_whisper_provider_is_subclass_of_stt_provider(self):
        """WhisperProvider must be a subclass of STTProvider."""
        from codomyrmex.audio.speech_to_text.providers.whisper_provider import (
            WhisperProvider,
        )

        assert issubclass(WhisperProvider, STTProvider)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
