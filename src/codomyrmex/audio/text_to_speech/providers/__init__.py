"""Text-to-speech provider implementations.

Available providers:
- Pyttsx3Provider: Offline TTS using system voices (SAPI5/NSSpeech/espeak)
- EdgeTTSProvider: Free Microsoft Edge neural TTS (requires internet)
"""

from .base import TTSProvider

# Conditionally import providers based on availability
try:
    from .pyttsx3_provider import Pyttsx3Provider, PYTTSX3_AVAILABLE
except ImportError:
    Pyttsx3Provider = None  # type: ignore
    PYTTSX3_AVAILABLE = False

try:
    from .edge_tts_provider import (
        EdgeTTSProvider,
        EDGE_TTS_AVAILABLE,
        POPULAR_VOICES,
    )
except ImportError:
    EdgeTTSProvider = None  # type: ignore
    EDGE_TTS_AVAILABLE = False
    POPULAR_VOICES = {}


def get_provider(
    provider_name: str = "pyttsx3",
    **kwargs: object,
) -> TTSProvider:
    """Get a TTS provider by name.

    Args:
        provider_name: Name of the provider ("pyttsx3", "edge-tts")
        **kwargs: Arguments to pass to the provider

    Returns:
        Initialized TTS provider

    Raises:
        ValueError: If provider name is not recognized
        ProviderNotAvailableError: If provider dependencies are missing
    """
    providers = {
        "pyttsx3": Pyttsx3Provider,
        "edge-tts": EdgeTTSProvider,
        "edge_tts": EdgeTTSProvider,
        "edgetts": EdgeTTSProvider,
    }

    provider_class = providers.get(provider_name.lower())
    if provider_class is None:
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            f"Available providers: pyttsx3, edge-tts"
        )

    return provider_class(**kwargs)


__all__ = [
    "TTSProvider",
    "Pyttsx3Provider",
    "EdgeTTSProvider",
    "PYTTSX3_AVAILABLE",
    "EDGE_TTS_AVAILABLE",
    "POPULAR_VOICES",
    "get_provider",
]
