"""Abstract base class for speech-to-text providers.

This module defines the interface that all STT providers must implement.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from pathlib import Path

from ..models import TranscriptionConfig, TranscriptionResult, WhisperModelSize


class STTProvider(ABC):
    """Abstract base class for speech-to-text providers.

    All STT providers must implement this interface to ensure consistent
    behavior across different transcription backends.

    Attributes:
        name: Provider name for identification
        is_available: Whether the provider's dependencies are installed
    """

    name: str = "base"
    is_available: bool = False

    @abstractmethod
    def __init__(
        self,
        model_size: WhisperModelSize = WhisperModelSize.BASE,
        device: str = "auto",
        compute_type: str = "auto",
        **kwargs: object,
    ) -> None:
        """Initialize the STT provider.

        Args:
            model_size: Size of the model to use
            device: Device to run on ("auto", "cpu", "cuda")
            compute_type: Computation type ("auto", "float16", "int8")
            **kwargs: Additional provider-specific arguments
        """
        pass

    @abstractmethod
    def transcribe(
        self,
        audio_path: str | Path,
        config: TranscriptionConfig | None = None,
    ) -> TranscriptionResult:
        """Transcribe an audio file.

        Args:
            audio_path: Path to the audio file
            config: Transcription configuration options

        Returns:
            TranscriptionResult with text and segments

        Raises:
            TranscriptionError: If transcription fails
            AudioFormatError: If audio format is not supported
        """
        pass

    @abstractmethod
    async def transcribe_async(
        self,
        audio_path: str | Path,
        config: TranscriptionConfig | None = None,
    ) -> TranscriptionResult:
        """Transcribe an audio file asynchronously.

        Args:
            audio_path: Path to the audio file
            config: Transcription configuration options

        Returns:
            TranscriptionResult with text and segments

        Raises:
            TranscriptionError: If transcription fails
        """
        pass

    @abstractmethod
    async def transcribe_stream(
        self,
        audio_path: str | Path,
        config: TranscriptionConfig | None = None,
    ) -> AsyncIterator[TranscriptionResult]:
        """Stream transcription results as they become available.

        Args:
            audio_path: Path to the audio file
            config: Transcription configuration options

        Yields:
            Partial TranscriptionResult as segments complete

        Raises:
            TranscriptionError: If transcription fails
        """
        pass
        yield  # Make this a generator

    @abstractmethod
    def detect_language(
        self,
        audio_path: str | Path,
    ) -> tuple[str, float]:
        """Detect the language of an audio file.

        Args:
            audio_path: Path to the audio file

        Returns:
            Tuple of (language_code, probability)

        Raises:
            TranscriptionError: If detection fails
        """
        pass

    @abstractmethod
    def get_supported_languages(self) -> list[str]:
        """Get list of supported language codes.

        Returns:
            List of ISO 639-1 language codes
        """
        pass

    @property
    @abstractmethod
    def is_loaded(self) -> bool:
        """Check if the model is loaded and ready.

        Returns:
            True if model is loaded
        """
        pass

    @abstractmethod
    def unload(self) -> None:
        """Unload the model to free memory."""
        pass


__all__ = ["STTProvider"]
