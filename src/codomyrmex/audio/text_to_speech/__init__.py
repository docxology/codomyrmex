"""Text-to-speech (TTS) synthesis module.

This module provides text-to-speech functionality using multiple providers:
- pyttsx3: Offline synthesis using system voices
- edge-tts: Free Microsoft Edge neural voices (requires internet)

Example:
    ```python
    from codomyrmex.audio.text_to_speech import Synthesizer

    # Offline synthesis (fast, uses system voices)
    synth = Synthesizer(provider="pyttsx3")
    result = synth.synthesize("Hello world!")
    result.save("hello.wav")

    # Neural TTS (high quality, requires internet)
    synth = Synthesizer(provider="edge-tts")
    result = synth.synthesize("Hello!", voice="en-US-AriaNeural")
    result.save("hello.mp3")
    ```
"""

from .models import (
    AudioFormat,
    SynthesisResult,
    TTSConfig,
    VoiceGender,
    VoiceInfo,
    SSMLOptions,
)
from .synthesizer import Synthesizer

# Provider imports
from .providers import (
    TTSProvider,
    PYTTSX3_AVAILABLE,
    EDGE_TTS_AVAILABLE,
    get_provider,
)

# Conditionally export providers
try:
    from .providers import Pyttsx3Provider
except ImportError:
    Pyttsx3Provider = None  # type: ignore

try:
    from .providers import EdgeTTSProvider, POPULAR_VOICES
except ImportError:
    EdgeTTSProvider = None  # type: ignore
    POPULAR_VOICES = {}


__all__ = [
    # Main interface
    "Synthesizer",
    # Models
    "AudioFormat",
    "SynthesisResult",
    "TTSConfig",
    "VoiceGender",
    "VoiceInfo",
    "SSMLOptions",
    # Providers
    "TTSProvider",
    "Pyttsx3Provider",
    "EdgeTTSProvider",
    "PYTTSX3_AVAILABLE",
    "EDGE_TTS_AVAILABLE",
    "POPULAR_VOICES",
    "get_provider",
]
