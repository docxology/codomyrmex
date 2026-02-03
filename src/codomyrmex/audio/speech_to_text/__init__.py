"""Speech-to-text (STT) transcription module.

This module provides speech-to-text functionality using local Whisper models
via the faster-whisper library.

Example:
    ```python
    from codomyrmex.audio.speech_to_text import Transcriber, WhisperModelSize

    # Basic transcription
    transcriber = Transcriber()
    result = transcriber.transcribe("audio.mp3")
    print(result.text)

    # With larger model
    transcriber = Transcriber(model_size=WhisperModelSize.LARGE_V3)
    result = transcriber.transcribe("spanish.wav", language="es")

    # Export subtitles
    result.save_srt("output.srt")
    ```
"""

from .models import (
    Segment,
    TranscriptionConfig,
    TranscriptionResult,
    WhisperModelSize,
    Word,
)
from .transcriber import Transcriber

# Provider imports
from .providers import (
    STTProvider,
    WHISPER_AVAILABLE,
    get_provider,
)

# Conditionally export WhisperProvider
try:
    from .providers import WhisperProvider
except ImportError:
    WhisperProvider = None  # type: ignore


__all__ = [
    # Main interface
    "Transcriber",
    # Models
    "TranscriptionResult",
    "TranscriptionConfig",
    "Segment",
    "Word",
    "WhisperModelSize",
    # Providers
    "STTProvider",
    "WhisperProvider",
    "WHISPER_AVAILABLE",
    "get_provider",
]
