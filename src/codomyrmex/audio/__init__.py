"""Audio processing module for Codomyrmex.

This module provides audio processing capabilities including:
- Speech-to-text (STT) transcription using Whisper
- Text-to-speech (TTS) synthesis using pyttsx3 and Edge TTS

Submodules:
    - speech_to_text: Audio transcription and language detection
    - text_to_speech: Speech synthesis and voice management

Installation:
    Install audio dependencies with:
    ```bash
    uv sync --extra audio
    ```

Quick Start:
    ```python
    from codomyrmex.audio import Transcriber, Synthesizer, WhisperModelSize

    # Speech-to-text
    transcriber = Transcriber(model_size=WhisperModelSize.BASE)
    result = transcriber.transcribe("interview.mp3")
    print(result.text)

    # Export as subtitles
    result.save_srt("subtitles.srt")

    # Text-to-speech (offline)
    synth = Synthesizer(provider="pyttsx3")
    result = synth.synthesize("Hello world!")
    result.save("hello.wav")

    # Text-to-speech (neural, requires internet)
    synth = Synthesizer(provider="edge-tts")
    result = synth.synthesize("Hello!", voice="en-US-AriaNeural")
    result.save("hello.mp3")
    ```
"""

__version__ = "0.1.0"

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

# Import exceptions
from .exceptions import (
    AudioError,
    AudioFormatError,
    ModelNotLoadedError,
    ProviderNotAvailableError,
    SynthesisError,
    TranscriptionError,
    VoiceNotFoundError,
)

# Speech-to-text imports
try:
    from .speech_to_text import (
        WHISPER_AVAILABLE,
        Segment,
        STTProvider,
        Transcriber,
        TranscriptionConfig,
        TranscriptionResult,
        WhisperModelSize,
        Word,
    )
    STT_AVAILABLE = True
except ImportError:
    Transcriber = None  # type: ignore
    TranscriptionResult = None  # type: ignore
    TranscriptionConfig = None  # type: ignore
    Segment = None  # type: ignore
    Word = None  # type: ignore
    WhisperModelSize = None  # type: ignore
    STTProvider = None  # type: ignore
    WHISPER_AVAILABLE = False
    STT_AVAILABLE = False

# Text-to-speech imports
try:
    from .text_to_speech import (
        EDGE_TTS_AVAILABLE,
        PYTTSX3_AVAILABLE,
        AudioFormat,
        SynthesisResult,
        Synthesizer,
        TTSConfig,
        TTSProvider,
        VoiceGender,
        VoiceInfo,
    )
    TTS_AVAILABLE = True
except ImportError:
    Synthesizer = None  # type: ignore
    SynthesisResult = None  # type: ignore
    TTSConfig = None  # type: ignore
    AudioFormat = None  # type: ignore
    VoiceInfo = None  # type: ignore
    VoiceGender = None  # type: ignore
    TTSProvider = None  # type: ignore
    PYTTSX3_AVAILABLE = False
    EDGE_TTS_AVAILABLE = False
    TTS_AVAILABLE = False


def cli_commands():
    """Return CLI commands for the audio module."""
    return {
        "formats": {
            "help": "List supported audio formats and capabilities",
            "handler": lambda **kwargs: print(
                f"Audio Module v{__version__}\n"
                f"  STT available: {STT_AVAILABLE}"
                + (f" (Whisper: {WHISPER_AVAILABLE})" if STT_AVAILABLE else "") + "\n"
                f"  TTS available: {TTS_AVAILABLE}"
                + (f" (pyttsx3: {PYTTSX3_AVAILABLE}, Edge TTS: {EDGE_TTS_AVAILABLE})" if TTS_AVAILABLE else "") + "\n"
                "  Supported operations: transcribe, synthesize"
            ),
        },
        "process": {
            "help": "Process an audio file",
            "handler": lambda **kwargs: print(
                "Audio Processing\n"
                "  STT: Use Transcriber(model_size) then transcriber.transcribe(path)\n"
                "  TTS: Use Synthesizer(provider) then synth.synthesize(text)\n"
                "  Export: result.save(path) or result.save_srt(path)"
            ),
        },
    }


# Build __all__ dynamically
__all__ = [
    # CLI integration
    "cli_commands",
    # Version
    "__version__",
    # Exceptions (always available)
    "AudioError",
    "TranscriptionError",
    "SynthesisError",
    "AudioFormatError",
    "ModelNotLoadedError",
    "ProviderNotAvailableError",
    "VoiceNotFoundError",
    # Availability flags
    "STT_AVAILABLE",
    "TTS_AVAILABLE",
    "WHISPER_AVAILABLE",
    "PYTTSX3_AVAILABLE",
    "EDGE_TTS_AVAILABLE",
]

if STT_AVAILABLE:
    __all__.extend([
        "Transcriber",
        "TranscriptionResult",
        "TranscriptionConfig",
        "Segment",
        "Word",
        "WhisperModelSize",
        "STTProvider",
    ])

if TTS_AVAILABLE:
    __all__.extend([
        "Synthesizer",
        "SynthesisResult",
        "TTSConfig",
        "AudioFormat",
        "VoiceInfo",
        "VoiceGender",
        "TTSProvider",
    ])
