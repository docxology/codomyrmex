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

# Provider imports
from .providers import (
    WHISPER_AVAILABLE,
    STTProvider,
    get_provider,
)
from .transcriber import Transcriber

# Conditionally export WhisperProvider
try:
    from .providers import WhisperProvider
except ImportError:
    pass


__all__ = [
    "WHISPER_AVAILABLE",
    # Providers
    "STTProvider",
    "Segment",
    # Main interface
    "Transcriber",
    "TranscriptionConfig",
    # Models
    "TranscriptionResult",
    "WhisperModelSize",
    "WhisperProvider",
    "Word",
    "get_provider",
]
