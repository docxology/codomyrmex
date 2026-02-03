"""Speech-to-text provider implementations.

Available providers:
- WhisperProvider: Local transcription using faster-whisper (CTranslate2)
"""

from .base import STTProvider

# Conditionally import providers based on availability
try:
    from .whisper_provider import (
        WhisperProvider,
        WHISPER_LANGUAGES,
        SUPPORTED_FORMATS,
    )
    WHISPER_AVAILABLE = True
except ImportError:
    WhisperProvider = None  # type: ignore
    WHISPER_LANGUAGES = []
    SUPPORTED_FORMATS = set()
    WHISPER_AVAILABLE = False


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
    providers = {
        "whisper": WhisperProvider,
    }

    provider_class = providers.get(provider_name.lower())
    if provider_class is None:
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            f"Available providers: {list(providers.keys())}"
        )

    return provider_class(**kwargs)


__all__ = [
    "STTProvider",
    "WhisperProvider",
    "WHISPER_AVAILABLE",
    "WHISPER_LANGUAGES",
    "SUPPORTED_FORMATS",
    "get_provider",
]
