"""Speech-to-text provider implementations.

Available providers:
- WhisperProvider: Local transcription using faster-whisper (CTranslate2)
"""

from .base import STTProvider

# The provider module guards its optional dependency itself (it only probes
# for faster_whisper), so importing it never fails; WhisperProvider raises
# ProviderNotAvailableError on construction when the dependency is missing.
from .whisper_provider import (
    FASTER_WHISPER_AVAILABLE,
    SUPPORTED_FORMATS,
    WHISPER_LANGUAGES,
    WhisperProvider,
)

WHISPER_AVAILABLE = FASTER_WHISPER_AVAILABLE


# Hoisted static mapping to prevent per-call allocation overhead
_PROVIDERS = {
    "whisper": WhisperProvider,
}


def get_provider(
    provider_name: str = "whisper",
    **kwargs: object,
) -> STTProvider:
    """Get an STT provider by name.

    Args:
        provider_name: Name of the provider ("whisper")
        **kwargs: Arguments to pass to the provider

    Returns:
        Initialized STT provider

    Raises:
        ValueError: If provider name is not recognized
        ProviderNotAvailableError: If provider dependencies are missing

    """
    provider_class = _PROVIDERS.get(provider_name.lower())
    if provider_class is None:
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            f"Available providers: {list(_PROVIDERS.keys())}"
        )

    return provider_class(**kwargs)


__all__ = [
    "SUPPORTED_FORMATS",
    "WHISPER_AVAILABLE",
    "WHISPER_LANGUAGES",
    "STTProvider",
    "WhisperProvider",
    "get_provider",
]
