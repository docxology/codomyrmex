"""Text-to-speech provider implementations.

Available providers:
- Pyttsx3Provider: Offline TTS using system voices (SAPI5/NSSpeech/espeak)
- EdgeTTSProvider: Free Microsoft Edge neural TTS (requires internet)
"""

from .base import TTSProvider

# The provider modules guard their optional dependencies themselves, so these
# imports never fail; each provider raises ProviderNotAvailableError on
# construction when its dependency is missing.
from .edge_tts_provider import (
    EDGE_TTS_AVAILABLE,
    POPULAR_VOICES,
    EdgeTTSProvider,
)
from .pyttsx3_provider import PYTTSX3_AVAILABLE, Pyttsx3Provider

# Hoisted static mapping to prevent per-call allocation overhead
_PROVIDERS = {
    "pyttsx3": Pyttsx3Provider,
    "edge-tts": EdgeTTSProvider,
    "edge_tts": EdgeTTSProvider,
    "edgetts": EdgeTTSProvider,
}


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
    provider_class = _PROVIDERS.get(provider_name.lower())
    if provider_class is None:
        raise ValueError(
            f"Unknown provider: {provider_name}. Available providers: pyttsx3, edge-tts"
        )

    return provider_class(**kwargs)


__all__ = [
    "EDGE_TTS_AVAILABLE",
    "POPULAR_VOICES",
    "PYTTSX3_AVAILABLE",
    "EdgeTTSProvider",
    "Pyttsx3Provider",
    "TTSProvider",
    "get_provider",
]
