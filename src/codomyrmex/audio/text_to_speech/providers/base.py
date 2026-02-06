"""Abstract base class for text-to-speech providers.

This module defines the interface that all TTS providers must implement.
"""

from abc import ABC, abstractmethod

from ..models import SynthesisResult, TTSConfig, VoiceInfo


class TTSProvider(ABC):
    """Abstract base class for text-to-speech providers.

    All TTS providers must implement this interface to ensure consistent
    behavior across different synthesis backends.

    Attributes:
        name: Provider name for identification
        is_available: Whether the provider's dependencies are installed
    """

    name: str = "base"
    is_available: bool = False

    @abstractmethod
    def __init__(self, **kwargs: object) -> None:
        """Initialize the TTS provider.

        Args:
            **kwargs: Provider-specific configuration
        """
        pass

    @abstractmethod
    def synthesize(
        self,
        text: str,
        config: TTSConfig | None = None,
    ) -> SynthesisResult:
        """Synthesize speech from text.

        Args:
            text: Text to synthesize
            config: Synthesis configuration options

        Returns:
            SynthesisResult with audio data

        Raises:
            SynthesisError: If synthesis fails
            VoiceNotFoundError: If requested voice is not available
        """
        pass

    @abstractmethod
    async def synthesize_async(
        self,
        text: str,
        config: TTSConfig | None = None,
    ) -> SynthesisResult:
        """Synthesize speech asynchronously.

        Args:
            text: Text to synthesize
            config: Synthesis configuration options

        Returns:
            SynthesisResult with audio data
        """
        pass

    @abstractmethod
    def list_voices(
        self,
        language: str | None = None,
    ) -> list[VoiceInfo]:
        """List available voices.

        Args:
            language: Filter by language code (e.g., "en-US")

        Returns:
            List of available VoiceInfo objects
        """
        pass

    @abstractmethod
    def get_voice(self, voice_id: str) -> VoiceInfo | None:
        """Get information about a specific voice.

        Args:
            voice_id: Voice identifier

        Returns:
            VoiceInfo if found, None otherwise
        """
        pass

    @abstractmethod
    def get_supported_languages(self) -> list[str]:
        """Get list of supported language codes.

        Returns:
            List of language codes (e.g., ["en-US", "es-ES"])
        """
        pass

    @property
    @abstractmethod
    def default_voice(self) -> str:
        """Get the default voice ID for this provider.

        Returns:
            Default voice identifier
        """
        pass


__all__ = ["TTSProvider"]
